from typing import Dict


# Mastery tier thresholds (mastery is 0.0-1.0 here)
_TIER_THRESHOLDS = [
    (0.9, "olympiad"),
    (0.75, "expert"),
    (0.5, "proficient"),
    (0.0, "novice"),
]


def _compute_mastery_tier(mastery: float, difficulty: int = 5) -> str:
    """Compute mastery tier from mastery level and difficulty."""
    if mastery >= 0.9 and difficulty >= 8:
        return "olympiad"
    for threshold, tier in _TIER_THRESHOLDS:
        if mastery >= threshold:
            return tier
    return "novice"


def _suggest_next_difficulty(mastery: float, current_difficulty: int) -> int:
    """Suggest next difficulty level based on mastery."""
    if mastery >= 0.9 and current_difficulty < 10:
        return min(current_difficulty + 2, 10)
    if mastery >= 0.75 and current_difficulty < 9:
        return min(current_difficulty + 1, 10)
    if mastery < 0.4 and current_difficulty > 1:
        return max(current_difficulty - 1, 1)
    return current_difficulty


def update_mastery(
    prior_mastery: float,
    score: float,
    confidence: float | None = None,
    difficulty: int = 5,
) -> Dict:
    pm = max(0.0, min(1.0, float(prior_mastery)))
    sc = max(0.0, min(1.0, float(score)))
    conf = float(confidence) if confidence is not None else 0.7
    diff = max(1, min(10, int(difficulty)))
    alpha = 0.4 * conf
    new_m = pm + alpha * (sc - pm)
    new_m = max(0.0, min(1.0, new_m))
    mastery_tier = _compute_mastery_tier(new_m, diff)
    next_difficulty = _suggest_next_difficulty(new_m, diff)
    return {
        "new_mastery": new_m,
        "delta": new_m - pm,
        "confidence": conf,
        "mastery_tier": mastery_tier,
        "next_suggested_difficulty": next_difficulty,
    }

