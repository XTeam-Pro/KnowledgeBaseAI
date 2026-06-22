"""Unit tests for school quarter curricula seed (RU-SCHOOL-MATH-G*).

Verifies the hard constraint: curriculum nodes reference ONLY existing KB
topic UIDs (graph_entities.jsonl), skip unknown/MISSING, and respect grade
bands. No PostgreSQL / Neo4j required.
"""
import pytest

from scripts import seed_school_curricula as seed


def test_pool_loads_existing_topics():
    pool = seed._load_topic_pool()
    assert len(pool) > 100
    # A known grade-7 topic must be present.
    assert "TOP-7-RATSIONALNYE-CHISLA" in pool


def test_seed_matrix_only_existing_uids_and_grade_consistent():
    """Every node in the shipped matrix must exist in the pool and match grade."""
    pool = seed._load_topic_pool()
    total = 0
    for code, rows in seed.SCHOOL_QUARTER_TOPIC_UIDS.items():
        warnings: list[str] = []
        nodes = seed._build_nodes(code, rows, pool, warnings)
        # Shipped matrix is curated to be clean: zero warnings.
        assert warnings == [], f"{code} produced warnings: {warnings}"
        assert nodes, f"{code} produced no nodes"
        for n in nodes:
            assert n["canonical_uid"] in pool
            assert seed._grade_band_ok(seed.CURRICULUM_GRADE[code], pool[n["canonical_uid"]])
        total += len(nodes)
    assert total > 0


def test_unknown_uid_is_skipped_with_warning():
    pool = seed._load_topic_pool()
    rows = [(1, "TOP-DOES-NOT-EXIST-xyz TOP-7-RATSIONALNYE-CHISLA")]
    warnings: list[str] = []
    nodes = seed._build_nodes("RU-SCHOOL-MATH-G7", rows, pool, warnings)
    uids = [n["canonical_uid"] for n in nodes]
    assert "TOP-DOES-NOT-EXIST-xyz" not in uids
    assert "TOP-7-RATSIONALNYE-CHISLA" in uids
    assert any("отсутствует в пуле" in w for w in warnings)


def test_missing_sentinel_is_skipped():
    pool = seed._load_topic_pool()
    rows = [(1, "MISSING"), (2, "TOP-7-ODNOCHLENY")]
    warnings: list[str] = []
    nodes = seed._build_nodes("RU-SCHOOL-MATH-G7", rows, pool, warnings)
    assert [n["canonical_uid"] for n in nodes] == ["TOP-7-ODNOCHLENY"]


def test_grade_band_mismatch_skipped():
    pool = seed._load_topic_pool()
    # A grade-9-only topic must not land in a grade-7 plan.
    rows = [(1, "TOP-9-GP")]
    warnings: list[str] = []
    nodes = seed._build_nodes("RU-SCHOOL-MATH-G7", rows, pool, warnings)
    assert nodes == []
    assert any("не согласован с классом" in w for w in warnings)


def test_quarter_filter():
    try:
        from app.services.roadmap_planner import _filter_nodes_by_quarter
    except Exception:  # pragma: no cover - heavy import guard
        pytest.skip("roadmap_planner not importable in this env")
    nodes = [
        {"canonical_uid": "A", "quarter": 1},
        {"canonical_uid": "B", "quarter": 2},
        {"canonical_uid": "C", "quarter": 3},
        {"canonical_uid": "D", "quarter": None},  # quarter-agnostic, always kept
    ]
    # quarter=None → no filtering
    assert len(_filter_nodes_by_quarter(nodes, None)) == 4
    # quarter=2 → q1,q2 and NULL kept
    uids = [n["canonical_uid"] for n in _filter_nodes_by_quarter(nodes, 2)]
    assert uids == ["A", "B", "D"]
