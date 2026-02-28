#!/usr/bin/env python3
"""Export all graph entities and relationships to JSONL files."""
import sys, json
from datetime import datetime, date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.services.graph.neo4j_repo import Neo4jRepo

TENANT_ID = "default"
LABELS = ["Subject", "Section", "Subsection", "Topic", "Skill", "Method", "Example"]

class _Encoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'iso_format'):
            return o.iso_format()
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        return super().default(o)


def export(entities_path: str, rels_path: str):
    repo = Neo4jRepo()
    drv = repo.driver
    entity_count = 0
    rel_count = 0

    try:
        with drv.session() as s, \
             open(entities_path, "w", encoding="utf-8") as ef, \
             open(rels_path, "w", encoding="utf-8") as rf:

            # Export entities
            for label in LABELS:
                rows = s.run(
                    f"MATCH (n:{label} {{tenant_id: $tid}}) RETURN properties(n) AS props",
                    tid=TENANT_ID
                ).data()
                for row in rows:
                    props = row["props"]
                    props["_label"] = label
                    ef.write(json.dumps(props, ensure_ascii=False, cls=_Encoder) + "\n")
                    entity_count += 1
                print(f"  {label:12s}: {len(rows)} entities")

            # Export ALL relationships
            rows = s.run("""
                MATCH (a {tenant_id: $tid})-[r]->(b {tenant_id: $tid})
                RETURN a.uid AS from_uid, type(r) AS rel_type, b.uid AS to_uid
            """, tid=TENANT_ID).data()
            for row in rows:
                rf.write(json.dumps(row, ensure_ascii=False) + "\n")
                rel_count += 1

            # Summary by rel type
            summary = s.run("""
                MATCH (a {tenant_id: $tid})-[r]->(b {tenant_id: $tid})
                RETURN type(r) AS rel_type, count(*) AS cnt
                ORDER BY cnt DESC
            """, tid=TENANT_ID).data()
            for row in summary:
                print(f"  {row['rel_type']:20s}: {row['cnt']} rels")

    finally:
        repo.close()

    print(f"\nExported: {entity_count} entities -> {entities_path}")
    print(f"Exported: {rel_count} relationships -> {rels_path}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--entities", default="/tmp/graph_entities.jsonl")
    p.add_argument("--rels", default="/tmp/graph_relationships.jsonl")
    args = p.parse_args()
    export(args.entities, args.rels)
