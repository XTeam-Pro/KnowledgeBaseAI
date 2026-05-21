"""
Tests for GeometryEngine.normalize() in app.services.visualization.geometry.

Coordinate convention:
  - Logical origin (0,0) maps to physical canvas center (5,5)
  - Logical range [-5, 5] → physical [0, 10] with scale=1 (identity + translation)
  - If max_abs_coord > 5: scale = 5 / max_abs_coord (scale-down only, no upscaling)
  - Small shapes (max_abs ≤ 5) are NOT scaled up — only translated to physical space
"""
import pytest
from app.services.visualization.geometry import GeometryEngine


# ---------------------------------------------------------------------------
# Basic normalisation behaviour
# ---------------------------------------------------------------------------

def test_normalization_bounds():
    """All output coordinates must lie within [0, 10]."""
    shapes = [
        {"points": [{"x": 15, "y": 20}, {"x": -5, "y": 0}]}
    ]
    normalized = GeometryEngine.normalize(shapes)
    for shape in normalized:
        for p in shape["points"]:
            assert 0 <= p["x"] <= 10.1
            assert 0 <= p["y"] <= 10.1


def test_origin_maps_to_center():
    """Logical (0,0) must always map to physical (5,5)."""
    shapes = [{"points": [{"x": 0, "y": 0}]}]
    normalized = GeometryEngine.normalize(shapes)
    p = normalized[0]["points"][0]
    assert p["x"] == 5
    assert p["y"] == 5


def test_centering_translation_only():
    """
    For a shape well within [-5, 5] the normaliser applies translation only
    (scale=1). Origin (0,0) → (5,5), so every point shifts by +5.
    """
    shapes = [{"points": [{"x": 0, "y": 0}, {"x": 2, "y": 0}, {"x": 1, "y": 1}]}]
    normalized = GeometryEngine.normalize(shapes)
    pts = normalized[0]["points"]

    # (0,0) → (5,5)
    assert abs(pts[0]["x"] - 5) < 0.01
    assert abs(pts[0]["y"] - 5) < 0.01
    # (2,0) → (7,5)
    assert abs(pts[1]["x"] - 7) < 0.01
    assert abs(pts[1]["y"] - 5) < 0.01
    # (1,1) → (6,6)
    assert abs(pts[2]["x"] - 6) < 0.01
    assert abs(pts[2]["y"] - 6) < 0.01


def test_max_objects():
    """More than MAX_OBJECTS shapes must raise ValueError."""
    shapes = [{"id": i} for i in range(4)]
    with pytest.raises(ValueError, match="Too many objects"):
        GeometryEngine.validate(shapes)


def test_scaling_large_shape():
    """
    Shapes whose coordinates exceed [-5, 5] are scaled down so that
    max_abs maps exactly to 5, then shifted to physical space.

    Input: [(-10,-10), (10,10)] → max_abs=10, scale=5/10=0.5
      (-10,-10): nx = -10*0.5 + 5 = 0,  ny = 0
      (10,10):   nx = 10*0.5  + 5 = 10, ny = 10
    """
    shapes = [{"points": [{"x": -10, "y": -10}, {"x": 10, "y": 10}]}]
    normalized = GeometryEngine.normalize(shapes)

    p1 = normalized[0]["points"][0]
    p2 = normalized[0]["points"][1]

    assert abs(p1["x"] - 0.0) < 0.1
    assert abs(p1["y"] - 0.0) < 0.1
    assert abs(p2["x"] - 10.0) < 0.1
    assert abs(p2["y"] - 10.0) < 0.1

    width = p2["x"] - p1["x"]
    assert abs(width - 10.0) < 0.1


def test_small_shape_no_upscale():
    """
    Small shapes (max_abs ≤ 5) are NOT scaled up — only translated.
    A 1×1 unit shape stays 1×1 after normalisation.
    """
    shapes = [{"points": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]}]
    normalized = GeometryEngine.normalize(shapes)

    p1 = normalized[0]["points"][0]  # (5,5)
    p2 = normalized[0]["points"][1]  # (6,6)

    width = p2["x"] - p1["x"]
    height = p2["y"] - p1["y"]
    assert abs(width - 1.0) < 0.01
    assert abs(height - 1.0) < 0.01


def test_negative_coords_in_range():
    """Negative logical coordinates in [-5,5] are mapped correctly."""
    shapes = [{"points": [{"x": -3, "y": -4}, {"x": 3, "y": 4}]}]
    normalized = GeometryEngine.normalize(shapes)
    pts = normalized[0]["points"]

    # (-3,-4) → (2, 1)
    assert abs(pts[0]["x"] - 2) < 0.01
    assert abs(pts[0]["y"] - 1) < 0.01
    # (3,4) → (8, 9)
    assert abs(pts[1]["x"] - 8) < 0.01
    assert abs(pts[1]["y"] - 9) < 0.01


def test_symmetric_shape_stays_centered():
    """A shape symmetric around (0,0) must be centered on the canvas at (5,5)."""
    shapes = [{"points": [
        {"x": -3, "y": -3},
        {"x":  3, "y": -3},
        {"x":  3, "y":  3},
        {"x": -3, "y":  3},
    ]}]
    normalized = GeometryEngine.normalize(shapes)
    pts = normalized[0]["points"]

    xs = [p["x"] for p in pts]
    ys = [p["y"] for p in pts]
    bbox_cx = (min(xs) + max(xs)) / 2
    bbox_cy = (min(ys) + max(ys)) / 2

    assert abs(bbox_cx - 5.0) < 0.01
    assert abs(bbox_cy - 5.0) < 0.01


# ---------------------------------------------------------------------------
# vertex_labels normalization (Bug #2 fix)
# ---------------------------------------------------------------------------

def test_vertex_labels_normalized_with_points():
    """
    vertex_labels must receive the same transform as their corresponding
    points so that labels appear at the correct screen position.
    """
    shapes = [{
        "type": "polygon",
        "points": [
            {"x": -2, "y":  3},
            {"x":  4, "y":  3},
            {"x":  1, "y": -1},
        ],
        "vertex_labels": [
            {"text": "A", "x": -2, "y":  3},
            {"text": "B", "x":  4, "y":  3},
            {"text": "C", "x":  1, "y": -1},
        ]
    }]
    normalized = GeometryEngine.normalize(shapes)
    pts = normalized[0]["points"]
    labels = normalized[0]["vertex_labels"]

    assert len(labels) == 3

    # Every label coordinate must match the corresponding point coordinate
    for pt, lbl in zip(pts, labels):
        assert abs(lbl["x"] - pt["x"]) < 0.01, (
            f"Label {lbl['text']}: x={lbl['x']} ≠ point x={pt['x']}"
        )
        assert abs(lbl["y"] - pt["y"]) < 0.01, (
            f"Label {lbl['text']}: y={lbl['y']} ≠ point y={pt['y']}"
        )


def test_vertex_labels_clamped_to_canvas():
    """vertex_labels coordinates must be clamped to [0, 10] just like points."""
    shapes = [{
        "type": "polygon",
        "points": [{"x": 10, "y": 10}, {"x": -10, "y": -10}],
        "vertex_labels": [
            {"text": "A", "x": 10, "y": 10},
            {"text": "B", "x": -10, "y": -10},
        ]
    }]
    normalized = GeometryEngine.normalize(shapes)
    for lbl in normalized[0]["vertex_labels"]:
        assert 0 <= lbl["x"] <= 10
        assert 0 <= lbl["y"] <= 10


def test_vertex_labels_text_preserved():
    """The 'text' field in vertex_labels must not be modified."""
    shapes = [{
        "type": "polygon",
        "points": [{"x": 1, "y": 2}],
        "vertex_labels": [{"text": "X₁", "x": 1, "y": 2, "extra": "meta"}]
    }]
    normalized = GeometryEngine.normalize(shapes)
    lbl = normalized[0]["vertex_labels"][0]
    assert lbl["text"] == "X₁"
    assert lbl.get("extra") == "meta"


def test_shape_without_vertex_labels_unaffected():
    """Shapes without vertex_labels must not gain a vertex_labels key."""
    shapes = [{"points": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]}]
    normalized = GeometryEngine.normalize(shapes)
    assert "vertex_labels" not in normalized[0]


# ---------------------------------------------------------------------------
# DB visualization normalization (Bug #1 fix) — pure geometry layer
# ---------------------------------------------------------------------------

def test_db_flat_coords_wrapped_and_normalized():
    """
    Simulate the wrapping that _select_question() does for a flat-list DB
    visualization: [{x,y}...] is wrapped into a single polygon shape, then
    normalized. The resulting points must lie within [0, 10].
    """
    # Flat list as might come from DB (logical Cartesian coordinates)
    db_coords = [
        {"x": -3, "y": -2},
        {"x":  3, "y": -2},
        {"x":  0, "y":  4},
    ]
    # Wrap (same logic as engine.py _select_question)
    wrapped = [{"type": "polygon", "points": db_coords, "label": "Figure"}]
    normalized = GeometryEngine.normalize(wrapped)

    for p in normalized[0]["points"]:
        assert 0 <= p["x"] <= 10
        assert 0 <= p["y"] <= 10


def test_db_multi_shape_normalized():
    """Multi-shape DB visualization (list of shape objects) is normalized correctly."""
    shapes = [
        {"type": "polygon", "points": [{"x": -1, "y": -1}, {"x": 1, "y": -1}, {"x": 0, "y": 2}]},
        {"type": "line",    "points": [{"x": -2, "y": 0},  {"x": 2, "y": 0}]},
    ]
    normalized = GeometryEngine.normalize(shapes)

    assert len(normalized) == 2
    for shape in normalized:
        for p in shape["points"]:
            assert 0 <= p["x"] <= 10, f"x={p['x']} out of canvas"
            assert 0 <= p["y"] <= 10, f"y={p['y']} out of canvas"


def test_db_negative_coords_not_clipped():
    """
    Before the fix, a DB question with negative coordinates would appear
    clipped on the frontend (minX clamped to 0). After normalization the
    coords move to [0,10], so no data is lost.
    """
    # Triangle with all-negative logical coordinates
    db_coords = [{"x": -4, "y": -3}, {"x": -1, "y": -3}, {"x": -2, "y": -1}]
    wrapped = [{"type": "polygon", "points": db_coords}]
    normalized = GeometryEngine.normalize(wrapped)

    pts = normalized[0]["points"]
    # After normalization all x,y must be positive (no data hidden by frontend clamp)
    for p in pts:
        assert p["x"] > 0, f"x={p['x']} would be clipped by frontend (minX=0)"
        assert p["y"] > 0, f"y={p['y']} would be clipped by frontend (minY=0)"


# ---------------------------------------------------------------------------
# Collision detection
# ---------------------------------------------------------------------------

def test_no_collision_non_overlapping():
    shapes = [
        {"points": [{"x": 1, "y": 1}, {"x": 3, "y": 1}, {"x": 3, "y": 3}, {"x": 1, "y": 3}]},
        {"points": [{"x": 7, "y": 7}, {"x": 9, "y": 7}, {"x": 9, "y": 9}, {"x": 7, "y": 9}]},
    ]
    conflicts = GeometryEngine.check_collisions(shapes)
    assert conflicts == []


def test_collision_overlapping():
    shapes = [
        {"points": [{"x": 1, "y": 1}, {"x": 6, "y": 1}, {"x": 6, "y": 6}, {"x": 1, "y": 6}]},
        {"points": [{"x": 4, "y": 4}, {"x": 9, "y": 4}, {"x": 9, "y": 9}, {"x": 4, "y": 9}]},
    ]
    conflicts = GeometryEngine.check_collisions(shapes)
    assert len(conflicts) > 0
    assert (0, 1) in conflicts
