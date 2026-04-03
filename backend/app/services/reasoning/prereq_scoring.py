from __future__ import annotations

from typing import Dict, List, Tuple


def normalize_prereq_edges(raw_prereqs: List[object]) -> List[Dict]:
    """
    Normalizes prereq payloads from different query shapes.

    Supports:
    - list[str] (legacy)
    - list[{"uid": "...", "weight": 0.5, "is_hard": False}]
    """
    result: List[Dict] = []
    for item in raw_prereqs or []:
        if isinstance(item, str):
            result.append({"uid": item, "weight": 0.5, "is_hard": False})
            continue
        if not isinstance(item, dict):
            continue
        uid = item.get("uid") or item.get("to_uid") or item.get("prereq_uid")
        if not uid:
            continue
        try:
            weight = float(item.get("weight", 0.5))
        except (TypeError, ValueError):
            weight = 0.5
        weight = min(1.0, max(0.0, weight))
        is_hard = bool(item.get("is_hard", False))
        result.append({"uid": str(uid), "weight": weight, "is_hard": is_hard})
    return result


def compute_topic_prereq_state(
    topic_uid: str,
    prereq_edges: List[Dict],
    progress: Dict[str, float],
    personal_factors: Dict[Tuple[str, str], float] | None = None,
    readiness_threshold: float = 0.6,
    hard_threshold: float = 0.5,
) -> Dict:
    """
    Computes weighted readiness using static graph weights and per-user PG multipliers.
    """
    if not prereq_edges:
        return {
            "readiness": 1.0,
            "is_unlocked": True,
            "hard_blocked": False,
            "blocking_prereqs": [],
            "soft_missing_prereqs": [],
            "soft_gap": 0.0,
        }

    factors = personal_factors or {}
    total_effective_weight = 0.0
    weighted_mastery = 0.0
    weighted_deficit = 0.0
    hard_blockers: List[str] = []
    soft_missing: List[str] = []

    for edge in prereq_edges:
        prereq_uid = edge["uid"]
        base_weight = float(edge.get("weight", 0.5))
        factor = float(factors.get((topic_uid, prereq_uid), 1.0))
        effective_weight = max(0.0, base_weight * factor)
        mastery = float(progress.get(prereq_uid, 0.0) or 0.0)

        if edge.get("is_hard") and mastery < hard_threshold:
            hard_blockers.append(prereq_uid)

        if effective_weight > 0.0:
            total_effective_weight += effective_weight
            weighted_mastery += effective_weight * mastery
            weighted_deficit += effective_weight * max(0.0, readiness_threshold - mastery)
            if mastery < readiness_threshold:
                soft_missing.append(prereq_uid)

    readiness = (
        weighted_mastery / total_effective_weight if total_effective_weight > 0 else 1.0
    )
    soft_gap = (
        weighted_deficit / total_effective_weight if total_effective_weight > 0 else 0.0
    )
    hard_blocked = bool(hard_blockers)
    is_unlocked = (not hard_blocked) and (readiness >= readiness_threshold)

    return {
        "readiness": readiness,
        "is_unlocked": is_unlocked,
        "hard_blocked": hard_blocked,
        "blocking_prereqs": hard_blockers,
        "soft_missing_prereqs": soft_missing,
        "soft_gap": soft_gap,
    }

