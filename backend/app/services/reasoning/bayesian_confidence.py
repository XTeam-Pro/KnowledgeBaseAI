"""Bayesian confidence estimator using Beta-Bernoulli model."""

import math


def bayesian_confidence(
    correct: int,
    total: int,
    prior_a: float = 1.0,
    prior_b: float = 1.0,
    variance_threshold: float = 0.02,
) -> dict:
    """Estimate student mastery confidence using Beta distribution.

    Uses Beta(a, b) prior with Bernoulli likelihood updates.
    Confidence is the posterior mean, and we use variance to determine
    whether we have enough information to stop.

    Args:
        correct: Number of correct answers.
        total: Total number of answers.
        prior_a: Beta prior alpha (default 1.0 = uniform).
        prior_b: Beta prior beta (default 1.0 = uniform).
        variance_threshold: Stop when variance drops below this.

    Returns:
        Dict with keys: confidence, variance, should_stop, posterior_a, posterior_b.
    """
    a = prior_a + correct
    b = prior_b + (total - correct)

    # Posterior mean = a / (a + b)
    confidence = a / (a + b)

    # Posterior variance = ab / ((a+b)^2 * (a+b+1))
    variance = (a * b) / ((a + b) ** 2 * (a + b + 1))

    should_stop = variance < variance_threshold

    return {
        "confidence": round(confidence, 4),
        "variance": round(variance, 6),
        "should_stop": should_stop,
        "posterior_a": round(a, 2),
        "posterior_b": round(b, 2),
    }


def difficulty_weighted_bayesian(
    answers: list[dict],
    prior_a: float = 1.0,
    prior_b: float = 1.0,
    variance_threshold: float = 0.02,
) -> dict:
    """Bayesian confidence with difficulty weighting.

    Each answer contributes proportionally to its difficulty level.

    Args:
        answers: List of dicts with 'correct' (bool) and 'difficulty' (float, 1-10).
        prior_a: Beta prior alpha.
        prior_b: Beta prior beta.
        variance_threshold: Stopping threshold.

    Returns:
        Same as bayesian_confidence plus effective_n.
    """
    if not answers:
        return {
            "confidence": 0.5,
            "variance": 0.25,
            "should_stop": False,
            "posterior_a": prior_a,
            "posterior_b": prior_b,
            "effective_n": 0,
        }

    a = prior_a
    b = prior_b

    for ans in answers:
        weight = max(0.1, ans.get("difficulty", 5.0)) / 10.0
        if ans.get("correct", False):
            a += weight
        else:
            b += weight

    confidence = a / (a + b)
    variance = (a * b) / ((a + b) ** 2 * (a + b + 1))
    effective_n = a + b - prior_a - prior_b

    return {
        "confidence": round(confidence, 4),
        "variance": round(variance, 6),
        "should_stop": variance < variance_threshold,
        "posterior_a": round(a, 2),
        "posterior_b": round(b, 2),
        "effective_n": round(effective_n, 2),
    }
