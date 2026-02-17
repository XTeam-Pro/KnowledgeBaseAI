#!/usr/bin/env python3
"""
Enrich algebra topics in KnowledgeBaseAI graph with pedagogical metadata.

Reads pedagogy_algebra_7_9.csv, builds UPDATE_NODE proposals for each topic,
submits them via the /v1/proposals endpoint, then auto-approves and commits.

Usage:
    python scripts/enrich_algebra_50_topics.py                     # submit and commit
    python scripts/enrich_algebra_50_topics.py --dry-run           # preview only
    python scripts/enrich_algebra_50_topics.py --base-url http://localhost:8000
"""

import argparse
import csv
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Dict, List

try:
    import httpx
except ImportError:
    print("ERROR: httpx is required. Install with: pip install httpx")
    sys.exit(1)


DEFAULT_BASE_URL = os.environ.get("KB_BASE_URL", "http://localhost:8000")
DEFAULT_TENANT_ID = os.environ.get("KB_TENANT_ID", "default")
DEFAULT_TOKEN = os.environ.get("KB_AUTH_TOKEN", "enrichment-script-token")

CSV_PATH = Path(__file__).parent / "pedagogy_algebra_7_9.csv"


def load_csv(csv_path: Path) -> List[Dict]:
    """Read the pedagogical metadata CSV and return list of row dicts."""
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def build_operations(rows: List[Dict]) -> List[Dict]:
    """
    Build UPDATE_NODE operations for the KB proposal pipeline.

    Each row becomes one UPDATE_NODE operation that sets pedagogical
    metadata properties on the matching Topic node.
    """
    operations = []
    for row in rows:
        topic_uid = row["topic_uid"].strip()
        if not topic_uid:
            continue

        # Parse pipe-delimited fields into lists
        learning_objectives = [
            obj.strip()
            for obj in row.get("learning_objectives", "").split("|")
            if obj.strip()
        ]
        misconceptions = [
            m.strip()
            for m in row.get("misconceptions", "").split("|")
            if m.strip()
        ]

        # Parse numeric fields
        try:
            estimated_minutes = int(row.get("estimated_minutes", 0))
        except (ValueError, TypeError):
            estimated_minutes = 0

        try:
            difficulty = int(row.get("difficulty", 5))
        except (ValueError, TypeError):
            difficulty = 5

        pedagogical_notes = row.get("pedagogical_notes", "").strip()

        op = {
            "op_id": f"enrich-{topic_uid}-{uuid.uuid4().hex[:6]}",
            "op_type": "UPDATE_NODE",
            "target_id": topic_uid,
            "properties_delta": {
                "estimated_minutes": estimated_minutes,
                "difficulty": difficulty,
                "pedagogical_notes": pedagogical_notes,
                "learning_objectives": learning_objectives,
                "misconceptions": misconceptions,
            },
            "match_criteria": {"uid": topic_uid},
            "evidence": {
                "source": "pedagogy_algebra_7_9.csv",
                "script": "enrich_algebra_50_topics.py",
            },
            "semantic_impact": "ENRICHMENT",
            "requires_review": False,
        }
        operations.append(op)

    return operations


def submit_proposal(
    base_url: str,
    tenant_id: str,
    token: str,
    operations: List[Dict],
) -> Dict:
    """Submit a proposal with the given operations via POST /v1/proposals."""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": tenant_id,
        "Content-Type": "application/json",
    }
    payload = {
        "base_graph_version": 0,
        "operations": operations,
    }

    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        resp = client.post("/v1/proposals", json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()


def approve_and_commit(
    base_url: str,
    tenant_id: str,
    token: str,
    proposal_id: str,
) -> Dict:
    """Approve and commit a proposal via POST /v1/proposals/{id}/approve."""
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": tenant_id,
        "Content-Type": "application/json",
    }

    with httpx.Client(base_url=base_url, timeout=60.0) as client:
        resp = client.post(
            f"/v1/proposals/{proposal_id}/approve",
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()


def main():
    parser = argparse.ArgumentParser(
        description="Enrich algebra topics with pedagogical metadata"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview operations without submitting",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"KB API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--tenant-id",
        default=DEFAULT_TENANT_ID,
        help=f"Tenant ID header (default: {DEFAULT_TENANT_ID})",
    )
    parser.add_argument(
        "--token",
        default=DEFAULT_TOKEN,
        help="Bearer token for authentication",
    )
    parser.add_argument(
        "--csv",
        default=str(CSV_PATH),
        help=f"Path to CSV file (default: {CSV_PATH})",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"ERROR: CSV file not found: {csv_path}")
        sys.exit(1)

    print(f"Loading pedagogical data from {csv_path} ...")
    rows = load_csv(csv_path)
    print(f"  Loaded {len(rows)} topic rows")

    operations = build_operations(rows)
    print(f"  Built {len(operations)} UPDATE_NODE operations")

    if args.dry_run:
        print("\n=== DRY RUN MODE ===")
        print("Operations that would be submitted:\n")
        for op in operations:
            print(f"  [{op['op_type']}] {op['target_id']}")
            delta = op["properties_delta"]
            print(f"    estimated_minutes: {delta.get('estimated_minutes')}")
            print(f"    difficulty: {delta.get('difficulty')}")
            print(f"    pedagogical_notes: {delta.get('pedagogical_notes', '')[:60]}...")
            print(f"    learning_objectives: {delta.get('learning_objectives')}")
            print(f"    misconceptions: {delta.get('misconceptions')}")
            print()
        print(f"Total: {len(operations)} operations (not submitted)")
        return

    # Submit proposal
    print(f"\nSubmitting proposal to {args.base_url} ...")
    try:
        result = submit_proposal(
            args.base_url, args.tenant_id, args.token, operations
        )
    except httpx.HTTPStatusError as e:
        print(f"ERROR: Proposal submission failed: {e.response.status_code}")
        print(f"  Response: {e.response.text}")
        sys.exit(1)
    except httpx.ConnectError:
        print(f"ERROR: Cannot connect to {args.base_url}")
        print("  Is the KB API running?")
        sys.exit(1)

    items = result.get("items", [])
    if not items:
        print("ERROR: No proposal returned from API")
        sys.exit(1)

    proposal_id = items[0]["proposal_id"]
    checksum = items[0].get("proposal_checksum", "N/A")
    status = items[0].get("status", "N/A")
    print(f"  Proposal created: {proposal_id}")
    print(f"  Checksum: {checksum}")
    print(f"  Status: {status}")

    # Auto-approve and commit
    print(f"\nApproving and committing proposal {proposal_id} ...")
    try:
        commit_result = approve_and_commit(
            args.base_url, args.tenant_id, args.token, proposal_id
        )
    except httpx.HTTPStatusError as e:
        print(f"ERROR: Approve/commit failed: {e.response.status_code}")
        print(f"  Response: {e.response.text}")
        sys.exit(1)

    commit_items = commit_result.get("items", [])
    if commit_items:
        ok = commit_items[0].get("ok", False)
        commit_status = commit_items[0].get("status", "UNKNOWN")
        graph_version = commit_items[0].get("graph_version", "N/A")
        print(f"  Commit ok: {ok}")
        print(f"  Status: {commit_status}")
        print(f"  Graph version: {graph_version}")
    else:
        print("  WARNING: No commit result items returned")

    print("\nDone. Pedagogical metadata enrichment complete.")


if __name__ == "__main__":
    main()
