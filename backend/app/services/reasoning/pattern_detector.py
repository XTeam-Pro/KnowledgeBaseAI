"""Detect random/guessing patterns in assessment answer sequences."""

import math


def runs_test_random(answers: list[bool], alpha: float = 0.05) -> dict:
    """Wald-Wolfowitz runs test for randomness.

    A "run" is a consecutive sequence of same values (e.g., [T,T,F,T] has 3 runs).
    Truly random sequences have an expected number of runs. Too few or too many
    runs suggest non-random patterns.

    Args:
        answers: Sequence of correct (True) / incorrect (False) answers.
        alpha: Significance level (default 0.05).

    Returns:
        Dict with is_random, runs_count, expected_runs, z_score, p_suspect.
    """
    n = len(answers)
    if n < 7:
        return {"is_random": True, "runs_count": 0, "reason": "too_few_answers"}

    n1 = sum(answers)
    n2 = n - n1

    if n1 == 0 or n2 == 0:
        return {"is_random": False, "runs_count": 1, "reason": "all_same"}

    # Count runs
    runs = 1
    for i in range(1, n):
        if answers[i] != answers[i - 1]:
            runs += 1

    # Expected runs and standard deviation
    expected = (2 * n1 * n2) / n + 1
    variance = (2 * n1 * n2 * (2 * n1 * n2 - n)) / (n * n * (n - 1))

    if variance <= 0:
        return {"is_random": True, "runs_count": runs, "reason": "zero_variance"}

    std = math.sqrt(variance)
    z = (runs - expected) / std

    # Two-tailed test: |z| > 1.96 at alpha=0.05 suggests non-random
    z_threshold = 1.96 if alpha == 0.05 else 2.576
    is_random = abs(z) <= z_threshold

    return {
        "is_random": is_random,
        "runs_count": runs,
        "expected_runs": round(expected, 2),
        "z_score": round(z, 3),
        "p_suspect": not is_random,
    }


def detect_speed_anomaly(
    time_seconds: list[float],
    min_expected_seconds: float = 3.0,
) -> dict:
    """Detect suspiciously fast answer times.

    Args:
        time_seconds: List of answer times in seconds.
        min_expected_seconds: Minimum expected time per answer.

    Returns:
        Dict with fast_count, fast_ratio, is_suspicious.
    """
    if not time_seconds:
        return {"fast_count": 0, "fast_ratio": 0.0, "is_suspicious": False}

    fast = sum(1 for t in time_seconds if t < min_expected_seconds)
    ratio = fast / len(time_seconds)

    return {
        "fast_count": fast,
        "fast_ratio": round(ratio, 3),
        "is_suspicious": ratio > 0.5,  # More than half are suspiciously fast
    }


def should_extend_assessment(
    answers: list[bool],
    time_seconds: list[float] | None = None,
    extra_questions: int = 3,
) -> dict:
    """Check if assessment should be extended due to suspicious patterns.

    Args:
        answers: Sequence of correct/incorrect.
        time_seconds: Optional list of answer times.
        extra_questions: How many extra questions to add if suspicious.

    Returns:
        Dict with extend (bool), extra_questions (int), reasons (list).
    """
    reasons = []

    randomness = runs_test_random(answers)
    if randomness.get("p_suspect"):
        reasons.append("random_pattern_detected")

    if time_seconds:
        speed = detect_speed_anomaly(time_seconds)
        if speed["is_suspicious"]:
            reasons.append("suspicious_speed")

    return {
        "extend": len(reasons) > 0,
        "extra_questions": extra_questions if reasons else 0,
        "reasons": reasons,
    }
