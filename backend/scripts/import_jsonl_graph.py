#!/usr/bin/env python3
"""Wipe Neo4j tenant graph and import from graph_entities.jsonl + graph_relationships.jsonl.

Usage:
    python scripts/import_jsonl_graph.py --wipe          # Wipe tenant graph, then import
    python scripts/import_jsonl_graph.py --dry-run       # Preview counts only
    python scripts/import_jsonl_graph.py --wipe --neo4j-uri bolt://custom:7687

Dataset files (default: app/services/kb/):
    graph_entities.jsonl       — nodes with _label field for Neo4j label
    graph_relationships.jsonl  — edges with _from_uid / _to_uid / _type fields
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

TENANT_ID = "default"
BATCH_SIZE = 200

# Default JSONL location: sibling of scripts/, inside app/services/kb/
_SCRIPT_DIR = Path(__file__).resolve().parent
_DEFAULT_KB_DIR = _SCRIPT_DIR.parent / "app" / "services" / "kb"

# Internal fields that are NOT node properties
_SKIP_ENTITY_FIELDS = frozenset({"_label", "tenant_id"})
_SKIP_REL_FIELDS = frozenset({"_from_uid", "_to_uid", "_type", "tenant_id"})


def _is_primitive(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) or value is None


def _normalize_property_value(value: Any) -> Any:
    """Neo4j properties must be primitives or arrays of primitives.

    Nested structures are serialized to compact JSON strings.
    """
    if _is_primitive(value):
        return value
    if isinstance(value, list):
        if all(_is_primitive(v) for v in value):
            return value
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _normalize_properties(props: dict[str, Any]) -> dict[str, Any]:
    return {k: _normalize_property_value(v) for k, v in props.items()}


def _load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        print(f"  [WARN] File not found: {path}")
        return records
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"  [WARN] Skipping malformed line {i}: {exc}")
    return records


def _wipe_tenant(session, tenant_id: str) -> int:
    result = session.run(
        "MATCH (n {tenant_id: $tid}) DETACH DELETE n RETURN count(n) AS deleted",
        tid=tenant_id,
    )
    row = result.single()
    return int(row["deleted"]) if row else 0


def _import_entities(session, entities: list[dict], tenant_id: str) -> int:
    merged = 0
    for i in range(0, len(entities), BATCH_SIZE):
        batch = entities[i : i + BATCH_SIZE]

        def _write_batch(tx, batch=batch):
            for rec in batch:
                label = str(rec.get("_label") or rec.get("type") or "Concept")
                uid = str(rec.get("uid") or "")
                if not uid:
                    continue
                props = {k: v for k, v in rec.items() if k not in _SKIP_ENTITY_FIELDS}
                props = _normalize_properties(props)
                props["uid"] = uid
                props["tenant_id"] = tenant_id
                tx.run(
                    f"MERGE (n:{label} {{uid: $uid, tenant_id: $tid}}) SET n += $props",
                    uid=uid,
                    tid=tenant_id,
                    props=props,
                )

        session.execute_write(_write_batch)
        merged += len(batch)
        print(f"    entities: {merged}/{len(entities)}", end="\r")

    print()
    return merged


def _import_relationships(session, rels: list[dict], tenant_id: str) -> tuple[int, int]:
    merged = 0
    skipped = 0
    for i in range(0, len(rels), BATCH_SIZE):
        batch = rels[i : i + BATCH_SIZE]

        def _write_batch(tx, batch=batch):
            nonlocal merged, skipped
            for rec in batch:
                from_uid = str(rec.get("_from_uid") or "")
                to_uid = str(rec.get("_to_uid") or "")
                rel_type = str(rec.get("_type") or "LINKED")
                uid = str(rec.get("uid") or "")
                if not from_uid or not to_uid:
                    skipped += 1
                    continue
                extra = {k: v for k, v in rec.items() if k not in _SKIP_REL_FIELDS}
                extra = _normalize_properties(extra)
                if uid:
                    extra["uid"] = uid
                extra["tenant_id"] = tenant_id
                tx.run(
                    f"MATCH (a {{uid: $fu, tenant_id: $tid}}) "
                    f"MATCH (b {{uid: $tu, tenant_id: $tid}}) "
                    f"MERGE (a)-[r:{rel_type}]->(b) SET r += $props",
                    fu=from_uid,
                    tu=to_uid,
                    tid=tenant_id,
                    props=extra,
                )
                merged += 1

        session.execute_write(_write_batch)
        print(f"    relationships: {merged}/{len(rels)} (skipped={skipped})", end="\r")

    print()
    return merged, skipped


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wipe", action="store_true", help="Delete existing tenant graph before import")
    parser.add_argument("--dry-run", action="store_true", help="Show counts without writing")
    parser.add_argument("--entities", default=str(_DEFAULT_KB_DIR / "graph_entities.jsonl"),
                        help="Path to graph_entities.jsonl")
    parser.add_argument("--rels", default=str(_DEFAULT_KB_DIR / "graph_relationships.jsonl"),
                        help="Path to graph_relationships.jsonl")
    parser.add_argument("--neo4j-uri", default=os.environ.get("KB_NEO4J_URI", "bolt://neo4j-kb:7687"))
    parser.add_argument("--neo4j-user", default=os.environ.get("NEO4J_USER", "neo4j"))
    parser.add_argument("--neo4j-password", default=os.environ.get("NEO4J_PASSWORD", "devneo4j123"))
    parser.add_argument("--tenant-id", default=TENANT_ID)
    args = parser.parse_args()

    print(f"Loading entities from: {args.entities}")
    entities = _load_jsonl(Path(args.entities))

    print(f"Loading relationships from: {args.rels}")
    rels = _load_jsonl(Path(args.rels))

    # Summary by label
    from collections import Counter
    label_counts = Counter(r.get("_label") or r.get("type") for r in entities)
    rel_counts = Counter(r.get("_type") for r in rels)

    print(f"\nDataset summary:")
    print(f"  Total entities : {len(entities)}")
    for lbl, cnt in sorted(label_counts.items()):
        print(f"    {lbl:15s}: {cnt}")
    print(f"  Total rels     : {len(rels)}")
    for rt, cnt in sorted(rel_counts.items()):
        print(f"    {rt:20s}: {cnt}")

    if args.dry_run:
        print("\n[DRY RUN] No changes written.")
        return

    from neo4j import GraphDatabase
    print(f"\nConnecting to {args.neo4j_uri}...")
    driver = GraphDatabase.driver(
        args.neo4j_uri,
        auth=(args.neo4j_user, args.neo4j_password),
    )
    driver.verify_connectivity()
    print("Connected.\n")

    with driver.session() as session:
        if args.wipe:
            print(f"Wiping tenant '{args.tenant_id}' graph...")
            deleted = _wipe_tenant(session, args.tenant_id)
            print(f"  Deleted {deleted} nodes (with all their relationships).\n")

        print("Importing entities...")
        n_entities = _import_entities(session, entities, args.tenant_id)

        print("Importing relationships...")
        n_rels, n_skipped = _import_relationships(session, rels, args.tenant_id)

    driver.close()

    print(f"\n{'=' * 50}")
    print(f"Import complete")
    print(f"  Entities merged  : {n_entities}")
    print(f"  Rels merged      : {n_rels}")
    print(f"  Rels skipped     : {n_skipped} (missing node UIDs)")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
