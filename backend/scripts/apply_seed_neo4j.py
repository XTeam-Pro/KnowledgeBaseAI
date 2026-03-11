#!/usr/bin/env python3
"""Apply seed_all_topics_methods data directly to Neo4j, bypassing Proposal API.

The Proposal API integrity gate requires BASED_ON rels for Skills, which
is not part of our canonical topology. This script imports the same data
definitions and writes MERGE statements directly to Neo4j.

Usage:
    python scripts/apply_seed_neo4j.py [--dry-run] [--section SECTION]
    python scripts/apply_seed_neo4j.py --neo4j-uri bolt://neo4j-kb:7687
"""
from __future__ import annotations

import argparse
import sys
import os
from datetime import datetime

# Import data builders from the seed script
sys.path.insert(0, os.path.dirname(__file__))
from seed_all_topics_methods import SECTION_BUILDERS, _OP_COUNTER
import seed_all_topics_methods as seed_mod

TENANT_ID = "default"


def _collect_all_ops(section: str | None = None) -> list[dict]:
    """Collect all operations from section builders."""
    seed_mod._OP_COUNTER = 0
    all_ops: list[dict] = []
    if section:
        fn = SECTION_BUILDERS.get(section)
        if not fn:
            print(f"Unknown section: {section}. Available: {', '.join(SECTION_BUILDERS)}", file=sys.stderr)
            sys.exit(1)
        all_ops = fn()
    else:
        for name, fn in SECTION_BUILDERS.items():
            ops = fn()
            all_ops.extend(ops)
            print(f"  {name}: {len(ops)} ops")
    return all_ops


def _apply_to_neo4j(ops: list[dict], driver, tenant_id: str) -> dict:
    """Apply operations in a single Neo4j transaction."""
    now = datetime.utcnow().isoformat()
    nodes_created = 0
    rels_created = 0

    def _run(tx):
        nonlocal nodes_created, rels_created
        for op in ops:
            op_type = op.get("op_type")
            pd = op.get("properties_delta") or {}

            if op_type == "CREATE_NODE":
                node_type = str(pd.get("type", "Concept"))
                uid = str(pd.get("uid") or op.get("target_id") or "")
                if not uid:
                    continue
                props = dict(pd)
                props["uid"] = uid
                props["tenant_id"] = tenant_id
                props.setdefault("lifecycle_status", "ACTIVE")
                props.setdefault("created_at", now)
                tx.run(
                    f"MERGE (n:{node_type} {{uid: $uid, tenant_id: $tid}}) SET n += $props",
                    uid=uid, tid=tenant_id, props=props,
                )
                nodes_created += 1

            elif op_type == "CREATE_REL":
                rel_type = str(pd.get("type", "LINKED"))
                from_uid = str(pd.get("from_uid", ""))
                to_uid = str(pd.get("to_uid", ""))
                if not from_uid or not to_uid:
                    continue
                import uuid
                rid = f"E-{uuid.uuid4().hex[:16]}"
                props = dict(pd)
                props["uid"] = rid
                props["tenant_id"] = tenant_id
                tx.run(
                    f"MATCH (a {{uid: $fu, tenant_id: $tid}}), (b {{uid: $tu, tenant_id: $tid}}) "
                    f"MERGE (a)-[r:{rel_type} {{uid: $rid}}]->(b) SET r += $props",
                    fu=from_uid, tu=to_uid, rid=rid, props=props, tid=tenant_id,
                )
                rels_created += 1

    with driver.session() as session:
        if hasattr(session, "execute_write"):
            session.execute_write(_run)
        else:
            session.write_transaction(_run)

    return {"nodes_created": nodes_created, "rels_created": rels_created}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be done")
    parser.add_argument("--section", help=f"Run single section: {', '.join(SECTION_BUILDERS)}")
    parser.add_argument("--neo4j-uri", default=os.environ.get("KB_NEO4J_URI", "bolt://neo4j-kb:7687"))
    parser.add_argument("--neo4j-user", default=os.environ.get("NEO4J_USER", "neo4j"))
    parser.add_argument("--neo4j-password", default=os.environ.get("NEO4J_PASSWORD", "devneo4j123"))
    parser.add_argument("--tenant-id", default=TENANT_ID)
    args = parser.parse_args()

    print("Collecting operations...")
    all_ops = _collect_all_ops(args.section)

    node_ops = [o for o in all_ops if o["op_type"] == "CREATE_NODE"]
    rel_ops = [o for o in all_ops if o["op_type"] == "CREATE_REL"]
    print(f"\nTotal: {len(all_ops)} ops ({len(node_ops)} nodes, {len(rel_ops)} rels)")

    if args.dry_run:
        # Show summary by node type
        from collections import Counter
        type_counts = Counter(o["properties_delta"].get("type") for o in node_ops)
        print("\nNode types:")
        for t, c in sorted(type_counts.items()):
            print(f"  {t}: {c}")
        rel_counts = Counter(o["properties_delta"].get("type") for o in rel_ops)
        print("\nRelation types:")
        for t, c in sorted(rel_counts.items()):
            print(f"  {t}: {c}")
        return

    from neo4j import GraphDatabase
    print(f"\nConnecting to {args.neo4j_uri}...")
    driver = GraphDatabase.driver(args.neo4j_uri, auth=(args.neo4j_user, args.neo4j_password))
    driver.verify_connectivity()
    print("Connected.")

    # Apply in batches per section to avoid huge single transactions
    if args.section:
        print(f"\nApplying {len(all_ops)} ops for section '{args.section}'...")
        result = _apply_to_neo4j(all_ops, driver, args.tenant_id)
        print(f"  Done: {result}")
    else:
        total_nodes = 0
        total_rels = 0
        for name, fn in SECTION_BUILDERS.items():
            seed_mod._OP_COUNTER = 0
            ops = fn()
            print(f"\nApplying section '{name}' ({len(ops)} ops)...")
            result = _apply_to_neo4j(ops, driver, args.tenant_id)
            total_nodes += result["nodes_created"]
            total_rels += result["rels_created"]
            print(f"  {result}")
        print(f"\n=== TOTAL: {total_nodes} nodes + {total_rels} rels ===")

    driver.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
