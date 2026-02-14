#!/usr/bin/env python3
"""Quick script to check graph statistics."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graph.neo4j_repo import Neo4jRepo
from app.core.canonical import ALLOWED_NODE_LABELS, ALLOWED_EDGE_TYPES

def main():
    repo = Neo4jRepo()

    try:
        print("Connected to Neo4j successfully!")
        print()

        # Count total nodes
        result = repo.read("MATCH (n) RETURN count(n) AS count")
        total_nodes = result[0]['count'] if result else 0
        print(f"Total nodes: {total_nodes}")

        # Count total relationships
        result = repo.read("MATCH ()-[r]->() RETURN count(r) AS count")
        total_rels = result[0]['count'] if result else 0
        print(f"Total relationships: {total_rels}")

        print("\n" + "=" * 60)
        print("NODE LABELS DISTRIBUTION")
        print("=" * 60)

        # Count nodes by label
        result = repo.read("""
            MATCH (n)
            UNWIND labels(n) AS label
            RETURN label, count(*) AS count
            ORDER BY count DESC
        """)

        for row in result:
            label = row['label']
            count = row['count']
            status = "✓" if label in ALLOWED_NODE_LABELS else "✗"
            print(f"{status} {label:20s}: {count:6d}")

        print("\n" + "=" * 60)
        print("RELATIONSHIP TYPES DISTRIBUTION")
        print("=" * 60)

        # Count relationships by type
        result = repo.read("""
            MATCH ()-[r]->()
            RETURN type(r) AS rel_type, count(*) AS count
            ORDER BY count DESC
        """)

        for row in result:
            rel_type = row['rel_type']
            count = row['count']
            status = "✓" if rel_type in ALLOWED_EDGE_TYPES else "✗"
            print(f"{status} {rel_type:20s}: {count:6d}")

        print("\n" + "=" * 60)

    finally:
        repo.close()

if __name__ == "__main__":
    main()
