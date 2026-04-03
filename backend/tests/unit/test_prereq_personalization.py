from app.services.reasoning.prereq_scoring import (
    compute_topic_prereq_state,
    normalize_prereq_edges,
)


def test_normalize_prereq_edges_supports_legacy_and_weighted_shapes():
    edges = normalize_prereq_edges(
        [
            "TOP-A",
            {"uid": "TOP-B", "weight": 0.9, "is_hard": True},
        ]
    )
    assert len(edges) == 2
    assert edges[0]["uid"] == "TOP-A"
    assert edges[0]["weight"] == 0.5
    assert edges[1]["uid"] == "TOP-B"
    assert edges[1]["is_hard"] is True


def test_compute_topic_prereq_state_uses_personal_factors_without_mutating_graph_weights():
    topic_uid = "TOP-C"
    prereqs = normalize_prereq_edges(
        [
            {"uid": "TOP-A", "weight": 0.8, "is_hard": False},
            {"uid": "TOP-B", "weight": 0.2, "is_hard": False},
        ]
    )
    progress = {"TOP-A": 0.2, "TOP-B": 1.0}

    baseline = compute_topic_prereq_state(
        topic_uid=topic_uid,
        prereq_edges=prereqs,
        progress=progress,
        personal_factors={},
        readiness_threshold=0.6,
    )
    personalized = compute_topic_prereq_state(
        topic_uid=topic_uid,
        prereq_edges=prereqs,
        progress=progress,
        personal_factors={(topic_uid, "TOP-A"): 0.0},
        readiness_threshold=0.6,
    )

    # With factor=0 for weak prereq TOP-A, readiness should increase for this user.
    assert personalized["readiness"] > baseline["readiness"]
    # Static graph data remains untouched: only effective readiness changes.
    assert prereqs[0]["weight"] == 0.8

