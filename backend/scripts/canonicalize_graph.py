#!/usr/bin/env python3
"""
Script to canonicalize graph data:
1. Check node labels against ALLOWED_NODE_LABELS
2. Check relationship types against ALLOWED_EDGE_TYPES
3. Normalize text properties
4. Report violations and optionally fix them
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.graph.neo4j_repo import Neo4jRepo
from app.core.canonical import ALLOWED_NODE_LABELS, ALLOWED_EDGE_TYPES, normalize_text
from typing import Dict, List, Set
import json


def check_graph_compliance(repo: Neo4jRepo, tenant_id: str = None) -> Dict:
    """Check graph for canonical compliance."""

    violations = {
        "invalid_node_labels": [],
        "invalid_edge_types": [],
        "nodes_with_unnormalized_text": [],
        "total_nodes": 0,
        "total_edges": 0,
    }

    # Check all node labels
    print("Checking node labels...")
    tenant_filter = "WHERE n.tenant_id = $tid" if tenant_id else ""
    params = {"tid": tenant_id} if tenant_id else {}

    query = f"""
    MATCH (n)
    {tenant_filter}
    RETURN
        labels(n) AS labels,
        n.uid AS uid,
        n.type AS type,
        n.title AS title,
        n.description AS description,
        n.tenant_id AS tenant_id
    LIMIT 10000
    """

    rows = repo.read(query, params)
    violations["total_nodes"] = len(rows)

    for row in rows:
        uid = row.get("uid")
        labels = row.get("labels", [])
        node_type = row.get("type")

        # Check if any label is not in allowed list
        invalid_labels = [l for l in labels if l not in ALLOWED_NODE_LABELS]
        if invalid_labels:
            violations["invalid_node_labels"].append({
                "uid": uid,
                "labels": labels,
                "invalid": invalid_labels,
                "type": node_type,
                "tenant_id": row.get("tenant_id")
            })

        # Check text normalization
        title = row.get("title")
        desc = row.get("description")
        needs_normalization = False

        if title and title != normalize_text(title):
            needs_normalization = True
        if desc and desc != normalize_text(desc):
            needs_normalization = True

        if needs_normalization:
            violations["nodes_with_unnormalized_text"].append({
                "uid": uid,
                "type": node_type,
                "tenant_id": row.get("tenant_id")
            })

    # Check all relationship types
    print("Checking relationship types...")

    rel_query = f"""
    MATCH (a)-[r]->(b)
    {tenant_filter.replace('n.', 'a.')}
    RETURN
        type(r) AS rel_type,
        r.uid AS uid,
        a.uid AS from_uid,
        b.uid AS to_uid,
        a.tenant_id AS tenant_id
    LIMIT 10000
    """

    rel_rows = repo.read(rel_query, params)
    violations["total_edges"] = len(rel_rows)

    for row in rel_rows:
        rel_type = row.get("rel_type")
        if rel_type not in ALLOWED_EDGE_TYPES:
            violations["invalid_edge_types"].append({
                "uid": row.get("uid"),
                "type": rel_type,
                "from_uid": row.get("from_uid"),
                "to_uid": row.get("to_uid"),
                "tenant_id": row.get("tenant_id")
            })

    return violations


def print_report(violations: Dict):
    """Print a human-readable report."""

    print("\n" + "=" * 80)
    print("CANONICALIZATION REPORT")
    print("=" * 80)

    print(f"\nTotal nodes checked: {violations['total_nodes']}")
    print(f"Total edges checked: {violations['total_edges']}")

    print(f"\nInvalid node labels: {len(violations['invalid_node_labels'])}")
    if violations['invalid_node_labels']:
        print("\nAllowed labels:", sorted(ALLOWED_NODE_LABELS))
        print("\nViolations:")
        for v in violations['invalid_node_labels'][:10]:
            print(f"  - Node {v['uid']} (type={v['type']}, tenant={v['tenant_id']})")
            print(f"    Labels: {v['labels']}")
            print(f"    Invalid: {v['invalid']}")
        if len(violations['invalid_node_labels']) > 10:
            print(f"  ... and {len(violations['invalid_node_labels']) - 10} more")

    print(f"\nInvalid edge types: {len(violations['invalid_edge_types'])}")
    if violations['invalid_edge_types']:
        print("\nAllowed edge types:", sorted(ALLOWED_EDGE_TYPES))
        print("\nViolations:")
        for v in violations['invalid_edge_types'][:10]:
            print(f"  - Edge {v['uid']} (type={v['type']}, tenant={v['tenant_id']})")
            print(f"    From: {v['from_uid']} -> To: {v['to_uid']}")
        if len(violations['invalid_edge_types']) > 10:
            print(f"  ... and {len(violations['invalid_edge_types']) - 10} more")

    print(f"\nNodes with unnormalized text: {len(violations['nodes_with_unnormalized_text'])}")
    if violations['nodes_with_unnormalized_text']:
        print("\nViolations:")
        for v in violations['nodes_with_unnormalized_text'][:10]:
            print(f"  - Node {v['uid']} (type={v['type']}, tenant={v['tenant_id']})")
        if len(violations['nodes_with_unnormalized_text']) > 10:
            print(f"  ... and {len(violations['nodes_with_unnormalized_text']) - 10} more")

    print("\n" + "=" * 80)

    # Summary
    total_violations = (
        len(violations['invalid_node_labels']) +
        len(violations['invalid_edge_types']) +
        len(violations['nodes_with_unnormalized_text'])
    )

    if total_violations == 0:
        print("✓ Graph is in canonical form!")
    else:
        print(f"✗ Found {total_violations} violations")

    print("=" * 80 + "\n")


def fix_node_labels(repo: Neo4jRepo, violations: List[Dict], dry_run: bool = True):
    """Fix invalid node labels by removing non-canonical labels."""

    if not violations:
        print("No node label violations to fix.")
        return

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Fixing node labels...")

    for v in violations:
        uid = v['uid']
        invalid_labels = v['invalid']

        for label in invalid_labels:
            query = f"MATCH (n {{uid: $uid}}) REMOVE n:`{label}`"

            if dry_run:
                print(f"  Would remove label '{label}' from node {uid}")
            else:
                repo.write(query, {"uid": uid})
                print(f"  ✓ Removed label '{label}' from node {uid}")


def fix_text_normalization(repo: Neo4jRepo, violations: List[Dict], dry_run: bool = True):
    """Normalize text properties in nodes."""

    if not violations:
        print("No text normalization violations to fix.")
        return

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Normalizing text properties...")

    for v in violations:
        uid = v['uid']

        # Get current properties
        query = "MATCH (n {uid: $uid}) RETURN n.title AS title, n.description AS description"
        rows = repo.read(query, {"uid": uid})

        if not rows:
            continue

        row = rows[0]
        title = row.get("title")
        desc = row.get("description")

        updates = []
        if title and title != normalize_text(title):
            normalized_title = normalize_text(title)
            updates.append(("title", normalized_title))

        if desc and desc != normalize_text(desc):
            normalized_desc = normalize_text(desc)
            updates.append(("description", normalized_desc))

        if updates:
            if dry_run:
                print(f"  Would normalize {len(updates)} properties in node {uid}")
            else:
                for prop, value in updates:
                    query = f"MATCH (n {{uid: $uid}}) SET n.{prop} = $value"
                    repo.write(query, {"uid": uid, "value": value})
                print(f"  ✓ Normalized {len(updates)} properties in node {uid}")


def delete_invalid_edges(repo: Neo4jRepo, violations: List[Dict], dry_run: bool = True):
    """Delete edges with invalid types."""

    if not violations:
        print("No edge type violations to fix.")
        return

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Deleting invalid edges...")

    for v in violations:
        uid = v['uid']
        rel_type = v['type']
        from_uid = v['from_uid']
        to_uid = v['to_uid']

        if dry_run:
            print(f"  Would delete edge {uid} (type={rel_type}, {from_uid} -> {to_uid})")
        else:
            query = "MATCH ()-[r {uid: $uid}]->() DELETE r"
            repo.write(query, {"uid": uid})
            print(f"  ✓ Deleted edge {uid} (type={rel_type})")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Canonicalize graph data")
    parser.add_argument("--tenant-id", help="Filter by tenant ID", default=None)
    parser.add_argument("--fix", action="store_true", help="Apply fixes (default is dry-run)")
    parser.add_argument("--output", help="Save report to JSON file", default=None)
    parser.add_argument("--fix-labels", action="store_true", help="Fix invalid node labels")
    parser.add_argument("--fix-text", action="store_true", help="Normalize text properties")
    parser.add_argument("--delete-edges", action="store_true", help="Delete invalid edges")

    args = parser.parse_args()

    repo = Neo4jRepo()

    try:
        print("Checking graph compliance...")
        violations = check_graph_compliance(repo, args.tenant_id)

        print_report(violations)

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(violations, f, indent=2, ensure_ascii=False)
            print(f"Report saved to {args.output}")

        if args.fix_labels or args.fix_text or args.delete_edges:
            dry_run = not args.fix

            if args.fix_labels:
                fix_node_labels(repo, violations['invalid_node_labels'], dry_run)

            if args.fix_text:
                fix_text_normalization(repo, violations['nodes_with_unnormalized_text'], dry_run)

            if args.delete_edges:
                delete_invalid_edges(repo, violations['invalid_edge_types'], dry_run)

            if dry_run:
                print("\n" + "=" * 80)
                print("This was a DRY RUN. Use --fix to apply changes.")
                print("=" * 80 + "\n")

    finally:
        repo.close()


if __name__ == "__main__":
    main()
