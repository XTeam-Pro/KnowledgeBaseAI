#!/usr/bin/env python3
"""
Seed script: imports knowledge graph and curricula from JSONL dataset files.

Usage:
    python scripts/seed_from_dataset.py [--tenant-id default] [--dry-run]
    python scripts/seed_from_dataset.py --graph-only
    python scripts/seed_from_dataset.py --curricula-only
"""

import sys
import os
import json
import uuid
import argparse
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graph.neo4j_repo import Neo4jRepo
from app.db.pg import get_conn, ensure_tables

KB_DIR = Path(__file__).parent.parent / "app" / "services" / "kb"


def load_jsonl(path: Path) -> List[Dict]:
    """Load JSONL file. Handles both normal and backslash-escaped JSON ({\"key\":...})."""
    records = []
    if not path.exists():
        return records
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                # Some files were written with escaped quotes: {\"key\":\"val\"}
                try:
                    records.append(json.loads(line.replace('\\"', '"')))
                except json.JSONDecodeError as e:
                    print(f"  [WARN] JSON parse error in {path.name}: {e}")
    return records


def _edge_uid(kind: str, from_uid: str, to_uid: str) -> str:
    """Generate a deterministic edge UID."""
    key = f"{kind}:{from_uid}:{to_uid}"
    return f"E-{uuid.uuid5(uuid.NAMESPACE_OID, key).hex[:16]}"


def _chunked(lst: List, size: int) -> List[List]:
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def seed_graph(repo: Neo4jRepo, tenant_id: str, dry_run: bool) -> None:
    """Import nodes and relationships into Neo4j."""

    # --- NODES ---
    node_files = [
        ("subjects.jsonl", "Subject"),
        ("sections.jsonl", "Section"),
        ("subsections.jsonl", "Subsection"),
        ("topics.jsonl", "Topic"),
        ("skills.jsonl", "Skill"),
        ("methods.jsonl", "Method"),
    ]

    total_nodes = 0
    for filename, label in node_files:
        path = KB_DIR / filename
        records = load_jsonl(path)
        if not records:
            print(f"  [SKIP] {filename} (empty or not found)")
            continue

        rows = []
        for rec in records:
            node = dict(rec)
            node["tenant_id"] = tenant_id
            node.setdefault("lifecycle_status", "ACTIVE")
            node.setdefault("type", label)
            rows.append(node)

        if dry_run:
            print(f"  [DRY] Would create/merge {len(rows)} {label} nodes from {filename}")
        else:
            query = (
                f"UNWIND $rows AS row "
                f"MERGE (n:{label} {{uid: row.uid, tenant_id: row.tenant_id}}) "
                f"SET n += row"
            )
            for chunk in _chunked(rows, 200):
                repo.write(query, {"rows": chunk})
            print(f"  [OK] Created/merged {len(rows)} {label} nodes")
        total_nodes += len(rows)

    print(f"\n  Total nodes processed: {total_nodes}")

    # --- RELATIONSHIPS: CONTAINS ---
    contains_records = load_jsonl(KB_DIR / "contains_relationships.jsonl")
    if contains_records:
        rows = [
            {
                "from_uid": r["parent_uid"],
                "to_uid": r["child_uid"],
                "uid": _edge_uid("CONTAINS", r["parent_uid"], r["child_uid"]),
                "tenant_id": tenant_id,
            }
            for r in contains_records
        ]
        if dry_run:
            print(f"  [DRY] Would create {len(rows)} CONTAINS relationships")
        else:
            query = (
                "UNWIND $rows AS row "
                "MATCH (a {uid: row.from_uid, tenant_id: row.tenant_id}) "
                "MATCH (b {uid: row.to_uid, tenant_id: row.tenant_id}) "
                "MERGE (a)-[r:CONTAINS {uid: row.uid}]->(b) "
                "SET r.tenant_id = row.tenant_id"
            )
            for chunk in _chunked(rows, 200):
                repo.write(query, {"rows": chunk})
            print(f"  [OK] Created {len(rows)} CONTAINS relationships")
    else:
        print("  [SKIP] contains_relationships.jsonl (empty or not found)")

    # --- RELATIONSHIPS: PREREQ ---
    prereq_records = load_jsonl(KB_DIR / "prereq_relationships.jsonl")
    if prereq_records:
        rows = [
            {
                "from_uid": r["source_uid"],
                "to_uid": r["target_uid"],
                "uid": _edge_uid("PREREQ", r["source_uid"], r["target_uid"]),
                "tenant_id": tenant_id,
            }
            for r in prereq_records
        ]
        if dry_run:
            print(f"  [DRY] Would create {len(rows)} PREREQ relationships")
        else:
            query = (
                "UNWIND $rows AS row "
                "MATCH (a {uid: row.from_uid, tenant_id: row.tenant_id}) "
                "MATCH (b {uid: row.to_uid, tenant_id: row.tenant_id}) "
                "MERGE (a)-[r:PREREQ {uid: row.uid}]->(b) "
                "SET r.tenant_id = row.tenant_id"
            )
            for chunk in _chunked(rows, 200):
                repo.write(query, {"rows": chunk})
            print(f"  [OK] Created {len(rows)} PREREQ relationships")
    else:
        print("  [SKIP] prereq_relationships.jsonl (empty or not found)")


def seed_curricula(dry_run: bool) -> None:
    """Import curricula and curriculum_nodes into PostgreSQL."""

    curricula = load_jsonl(KB_DIR / "curricula.jsonl")
    curriculum_nodes = load_jsonl(KB_DIR / "curriculum_nodes.jsonl")

    if not curricula:
        print("  [SKIP] curricula.jsonl (empty or not found)")
        return

    if dry_run:
        print(f"  [DRY] Would insert/update {len(curricula)} curricula")
        print(f"  [DRY] Would insert {len(curriculum_nodes)} curriculum_nodes")
        return

    conn = get_conn()
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # Ensure exam_task_number column exists (not in initial migration)
            cur.execute(
                "ALTER TABLE curriculum_nodes "
                "ADD COLUMN IF NOT EXISTS exam_task_number TEXT"
            )

            # Insert curricula; map dataset id -> new PostgreSQL id
            id_map: Dict[int, int] = {}
            for c in curricula:
                cur.execute(
                    """
                    INSERT INTO curricula (code, title, standard, language, status)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (code) DO UPDATE
                      SET title = EXCLUDED.title,
                          status = EXCLUDED.status
                    RETURNING id
                    """,
                    (
                        c["code"],
                        c["title"],
                        c["standard"],
                        c["language"],
                        c.get("status", "draft"),
                    ),
                )
                new_id = cur.fetchone()[0]
                id_map[int(c["id"])] = new_id

            print(f"  [OK] Inserted/updated {len(curricula)} curricula")

            # Insert curriculum_nodes
            inserted = 0
            skipped = 0
            for n in curriculum_nodes:
                old_cid = int(n["curriculum_id"])
                new_cid = id_map.get(old_cid)
                if new_cid is None:
                    print(f"  [WARN] curriculum_id {old_cid} not in id_map, skipping node id={n.get('id')}")
                    skipped += 1
                    continue
                cur.execute(
                    """
                    INSERT INTO curriculum_nodes
                      (curriculum_id, kind, canonical_uid, order_index, is_required, exam_task_number)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    """,
                    (
                        new_cid,
                        n.get("kind", "topic"),
                        n["canonical_uid"],
                        int(n.get("order_index", 0)),
                        bool(n.get("is_required", True)),
                        n.get("exam_task_number"),
                    ),
                )
                inserted += 1

            if skipped:
                print(f"  [WARN] Skipped {skipped} curriculum_nodes with missing curriculum_id")
            print(f"  [OK] Inserted {inserted} curriculum_nodes")

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed knowledge graph and curricula from JSONL dataset"
    )
    parser.add_argument("--tenant-id", default="default", help="Tenant ID (default: default)")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without executing")
    parser.add_argument("--graph-only", action="store_true", help="Only seed Neo4j graph")
    parser.add_argument("--curricula-only", action="store_true", help="Only seed PostgreSQL curricula")
    args = parser.parse_args()

    tenant_id = args.tenant_id
    dry_run = args.dry_run

    print(f"Dataset directory: {KB_DIR}")
    print(f"Tenant ID: {tenant_id}")
    if dry_run:
        print("[DRY RUN MODE - no changes will be made]\n")
    else:
        print()

    ensure_tables()

    if not args.curricula_only:
        print("=== Neo4j Graph ===")
        repo = Neo4jRepo()
        try:
            seed_graph(repo, tenant_id, dry_run)
        finally:
            repo.close()
        print()

    if not args.graph_only:
        print("=== PostgreSQL Curricula ===")
        seed_curricula(dry_run)
        print()

    print("Done!")


if __name__ == "__main__":
    main()
