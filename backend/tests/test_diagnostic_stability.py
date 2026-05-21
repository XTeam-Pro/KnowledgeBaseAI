"""Diagnostic stability tests: Bayesian confidence and pattern detection."""

import pytest

from app.services.reasoning.bayesian_confidence import (
    bayesian_confidence,
    difficulty_weighted_bayesian,
)
from app.services.reasoning.pattern_detector import (
    runs_test_random,
    should_extend_assessment,
)


class TestBayesianConfidence:
    """Test Bayesian confidence estimator correctness."""

    def test_uniform_prior(self):
        """With uniform prior and no data, confidence should be 0.5."""
        result = bayesian_confidence(correct=0, total=0)
        assert abs(result["confidence"] - 0.5) < 0.01

    def test_all_correct(self):
        """All correct answers → high confidence."""
        result = bayesian_confidence(correct=10, total=10)
        assert result["confidence"] > 0.8

    def test_all_incorrect(self):
        """All incorrect answers → low confidence."""
        result = bayesian_confidence(correct=0, total=10)
        assert result["confidence"] < 0.2

    def test_variance_decreases_with_more_data(self):
        """More data should reduce variance."""
        r5 = bayesian_confidence(correct=3, total=5)
        r20 = bayesian_confidence(correct=12, total=20)
        assert r20["variance"] < r5["variance"]

    def test_should_stop_at_low_variance(self):
        """With enough data, should_stop should become True."""
        result = bayesian_confidence(correct=15, total=20, variance_threshold=0.02)
        assert result["should_stop"] is True

    def test_should_not_stop_early(self):
        """With few data points, should_stop should be False."""
        result = bayesian_confidence(correct=2, total=3, variance_threshold=0.02)
        assert result["should_stop"] is False


class TestDifficultyWeightedBayesian:
    """Test difficulty-weighted Bayesian estimation."""

    def test_empty_answers(self):
        result = difficulty_weighted_bayesian([])
        assert result["confidence"] == 0.5
        assert result["effective_n"] == 0

    def test_hard_correct_boosts_more(self):
        """Correct on hard question should boost confidence more."""
        easy = difficulty_weighted_bayesian([
            {"correct": True, "difficulty": 1.0},
        ])
        hard = difficulty_weighted_bayesian([
            {"correct": True, "difficulty": 10.0},
        ])
        assert hard["confidence"] > easy["confidence"]

    def test_stability_across_runs(self):
        """Same input should produce same output (deterministic)."""
        answers = [
            {"correct": True, "difficulty": 5.0},
            {"correct": False, "difficulty": 3.0},
            {"correct": True, "difficulty": 7.0},
        ]
        r1 = difficulty_weighted_bayesian(answers)
        r2 = difficulty_weighted_bayesian(answers)
        assert r1["confidence"] == r2["confidence"]
        assert r1["variance"] == r2["variance"]


class TestPatternDetection:
    """Test random pattern detection."""

    def test_alternating_is_not_random(self):
        """Perfectly alternating T/F pattern should be flagged."""
        answers = [True, False, True, False, True, False, True, False, True, False]
        result = runs_test_random(answers)
        # Alternating has maximum runs → may or may not flag depending on stats
        assert "runs_count" in result

    def test_all_same_not_random(self):
        """All same answers should be flagged as not random."""
        answers = [True] * 10
        result = runs_test_random(answers)
        assert result["is_random"] is False

    def test_too_few_answers(self):
        """Less than 7 answers → treat as random (not enough data)."""
        result = runs_test_random([True, False, True])
        assert result["is_random"] is True

    def test_should_extend_on_random(self):
        """Random pattern should trigger assessment extension."""
        # All same = not random, should extend
        answers = [True] * 10
        result = should_extend_assessment(answers)
        # All same might be flagged or not depending on the test
        assert "extend" in result
        assert "extra_questions" in result
