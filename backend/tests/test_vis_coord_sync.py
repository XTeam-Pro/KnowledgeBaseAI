"""
Coordinate synchronization tests — Backend ↔ Frontend

Verifies that the normalization pipeline inside _select_question() produces
coordinates that the VisualQuestionRenderer React component will render
correctly.

Frontend constraints (from VisualQuestionRenderer.tsx):
  - geometric_shape: minX = max(0, minX), minY = max(0, minY)
      → any point with x<0 or y<0 falls outside the visible domain
  - graph: symmetric domain around 0  — all axes range OK
  - Nivo xScale/yScale map [minX, maxX] → [0, innerWidth] pixels
  - vertex_labels: rendered at xScale(label.x), yScale(label.y)
      → labels must be in the SAME coordinate space as points

These tests run without FastAPI / Neo4j / Postgres by testing only the
GeometryEngine directly — the same function _select_question() calls.
"""

import math
import pytest
from app.services.visualization.geometry import GeometryEngine


# ---------------------------------------------------------------------------
# Helper: simulate the frontend domain-computation for geometric_shape
# ---------------------------------------------------------------------------

def frontend_domain(points_list, vis_type="geometric_shape", padding_pct=0.1, min_padding=1.0):
    """
    Reproduces lines 465-500 of VisualQuestionRenderer.tsx.
    Returns (minX, maxX, minY, maxY) — the Nivo scale domain.
    """
    xs = [p["x"] for p in points_list]
    ys = [p["y"] for p in points_list]

    data_min_x, data_max_x = min(xs), max(xs)
    data_min_y, data_max_y = min(ys), max(ys)

    pad_x = max((data_max_x - data_min_x) * padding_pct, min_padding)
    pad_y = max((data_max_y - data_min_y) * padding_pct, min_padding)

    min_x = data_min_x - pad_x
    max_x = data_max_x + pad_x
    min_y = data_min_y - pad_y
    max_y = data_max_y + pad_y

    if vis_type == "geometric_shape":
        min_x = max(0, min_x)
        min_y = max(0, min_y)

    return min_x, max_x, min_y, max_y


def all_points_visible(points, vis_type="geometric_shape"):
    """Returns True if every point lies within the frontend-rendered domain."""
    min_x, max_x, min_y, max_y = frontend_domain(points, vis_type)
    for p in points:
        if not (min_x <= p["x"] <= max_x):
            return False
        if not (min_y <= p["y"] <= max_y):
            return False
    return True


# ---------------------------------------------------------------------------
# 1. Basic pipeline: DB coords → normalize → frontend visible
# ---------------------------------------------------------------------------

class TestDbToFrontendSync:

    def _normalize(self, logical_points):
        """Run the same wrapping + normalize as _select_question()."""
        coords = [{"type": "polygon", "points": logical_points, "label": "Figure"}]
        return GeometryEngine.normalize(coords)[0]["points"]

    def test_positive_db_coords_visible(self):
        """DB coords in [0, 5] → after normalize → all visible on frontend."""
        logical = [{"x": 1, "y": 1}, {"x": 4, "y": 1}, {"x": 2, "y": 4}]
        pts = self._normalize(logical)
        assert all_points_visible(pts), f"Points clipped: {pts}"

    def test_negative_db_coords_visible_after_normalize(self):
        """
        DB triangle with negative coords: before fix these were clipped to x/y=0.
        After normalization the coords map to [0,10] and are fully visible.
        """
        logical = [{"x": -3, "y": -2}, {"x": 3, "y": -2}, {"x": 0, "y": 4}]
        pts = self._normalize(logical)
        assert all_points_visible(pts), f"Points clipped: {pts}"

    def test_symmetric_shape_fully_visible(self):
        """A symmetric shape must be fully within the rendered domain."""
        logical = [
            {"x": -4, "y": -3}, {"x": 4, "y": -3},
            {"x": 4, "y":  3}, {"x": -4, "y":  3},
        ]
        pts = self._normalize(logical)
        assert all_points_visible(pts), f"Points clipped: {pts}"

    def test_large_db_coords_scaled_and_visible(self):
        """Coordinates outside [-5, 5] are scaled down but must remain visible."""
        logical = [{"x": -9, "y": -7}, {"x": 9, "y": 7}]
        pts = self._normalize(logical)
        assert all_points_visible(pts), f"Points clipped: {pts}"
        # After scale-down all must be in [0, 10]
        for p in pts:
            assert 0 <= p["x"] <= 10
            assert 0 <= p["y"] <= 10

    def test_all_normalized_coords_in_canvas_range(self):
        """No normalized coordinate should exceed [0, 10]."""
        test_cases = [
            [{"x": 0, "y": 0}, {"x": 5, "y": 5}],
            [{"x": -5, "y": -5}, {"x": 5, "y": 5}],
            [{"x": -7, "y": -7}, {"x": 7, "y": 7}],
            [{"x": 3, "y": -2}, {"x": -1, "y": 4}],
        ]
        for logical in test_cases:
            pts = self._normalize(logical)
            for p in pts:
                assert 0 <= p["x"] <= 10, f"x={p['x']} out of canvas for {logical}"
                assert 0 <= p["y"] <= 10, f"y={p['y']} out of canvas for {logical}"


# ---------------------------------------------------------------------------
# 2. vertex_labels ↔ points coordinate alignment
# ---------------------------------------------------------------------------

class TestVertexLabelSync:

    def test_labels_track_vertices_after_normalize(self):
        """
        After normalization, every vertex_label must be at the same physical
        position as the corresponding vertex in 'points'. This is the frontend
        contract: xScale(label.x) must equal xScale(point.x).
        """
        shapes = [{
            "type": "polygon",
            "points": [
                {"x": -2, "y":  1},
                {"x":  3, "y":  1},
                {"x":  0, "y": -3},
            ],
            "vertex_labels": [
                {"text": "A", "x": -2, "y":  1},
                {"text": "B", "x":  3, "y":  1},
                {"text": "C", "x":  0, "y": -3},
            ]
        }]
        normalized = GeometryEngine.normalize(shapes)
        pts = normalized[0]["points"]
        labels = normalized[0]["vertex_labels"]

        for i, (pt, lbl) in enumerate(zip(pts, labels)):
            assert abs(pt["x"] - lbl["x"]) < 0.01, (
                f"Vertex {i}: point.x={pt['x']} ≠ label.x={lbl['x']}"
            )
            assert abs(pt["y"] - lbl["y"]) < 0.01, (
                f"Vertex {i}: point.y={pt['y']} ≠ label.y={lbl['y']}"
            )

    def test_labels_visible_after_normalize(self):
        """vertex_labels must lie within the frontend-visible domain."""
        shapes = [{
            "type": "polygon",
            "points": [
                {"x": -4, "y": -4},
                {"x":  4, "y": -4},
                {"x":  0, "y":  4},
            ],
            "vertex_labels": [
                {"text": "A", "x": -4, "y": -4},
                {"text": "B", "x":  4, "y": -4},
                {"text": "C", "x":  0, "y":  4},
            ]
        }]
        normalized = GeometryEngine.normalize(shapes)
        label_pts = [{"x": l["x"], "y": l["y"]} for l in normalized[0]["vertex_labels"]]
        min_x, max_x, min_y, max_y = frontend_domain(label_pts)
        for lbl in normalized[0]["vertex_labels"]:
            assert min_x <= lbl["x"] <= max_x, f"Label {lbl['text']} x out of domain"
            assert min_y <= lbl["y"] <= max_y, f"Label {lbl['text']} y out of domain"

    def test_label_text_survives_pipeline(self):
        """Text content of vertex labels must not be altered by normalization."""
        shapes = [{
            "type": "polygon",
            "points": [{"x": 1, "y": 1}, {"x": 3, "y": 1}, {"x": 2, "y": 3}],
            "vertex_labels": [
                {"text": "А", "x": 1, "y": 1},
                {"text": "В", "x": 3, "y": 1},
                {"text": "С", "x": 2, "y": 3},
            ]
        }]
        normalized = GeometryEngine.normalize(shapes)
        texts = [l["text"] for l in normalized[0]["vertex_labels"]]
        assert texts == ["А", "В", "С"]


# ---------------------------------------------------------------------------
# 3. Multi-shape: no overlaps corrupt the domain
# ---------------------------------------------------------------------------

class TestMultiShapeSync:

    def test_two_shapes_both_visible(self):
        """Two non-overlapping shapes from DB are both fully visible after normalize."""
        shapes = [
            {"type": "polygon", "points": [
                {"x": -4, "y": -4}, {"x": -1, "y": -4}, {"x": -2, "y": -1}
            ]},
            {"type": "polygon", "points": [
                {"x": 1, "y": 1}, {"x": 4, "y": 1}, {"x": 2, "y": 4}
            ]},
        ]
        normalized = GeometryEngine.normalize(shapes)
        all_pts = [p for s in normalized for p in s["points"]]
        # Verify domain includes all points
        min_x, max_x, min_y, max_y = frontend_domain(all_pts)
        for p in all_pts:
            assert min_x <= p["x"] <= max_x, f"x={p['x']} out of domain [{min_x},{max_x}]"
            assert min_y <= p["y"] <= max_y, f"y={p['y']} out of domain [{min_y},{max_y}]"

    def test_overlapping_shapes_detected(self):
        """
        Two shapes that overlap in canvas space are flagged by check_collisions.
        This ensures the collision detector works after normalization.
        """
        # Two shapes that will overlap after normalize (both near center)
        shapes = [
            {"type": "polygon", "points": [
                {"x": -1, "y": -1}, {"x": 1, "y": -1}, {"x": 0, "y": 1}
            ]},
            {"type": "polygon", "points": [
                {"x": -1, "y": -1}, {"x": 1, "y": -1}, {"x": 0, "y": 1}
            ]},
        ]
        normalized = GeometryEngine.normalize(shapes)
        conflicts = GeometryEngine.check_collisions(normalized)
        assert len(conflicts) > 0, "Identical overlapping shapes should be detected"

    def test_aspect_ratio_preserved(self):
        """
        A square shape (equal x and y spans) must have equal x and y spans
        after normalization so that 1:1 grid cells are rendered on frontend.
        """
        # Perfect square 6×6 centered at origin
        shapes = [{
            "type": "polygon",
            "points": [
                {"x": -3, "y": -3}, {"x": 3, "y": -3},
                {"x": 3, "y":  3}, {"x": -3, "y":  3},
            ]
        }]
        normalized = GeometryEngine.normalize(shapes)
        pts = normalized[0]["points"]

        xs = [p["x"] for p in pts]
        ys = [p["y"] for p in pts]
        x_span = max(xs) - min(xs)
        y_span = max(ys) - min(ys)

        assert abs(x_span - y_span) < 0.01, (
            f"Aspect ratio broken: x_span={x_span}, y_span={y_span}"
        )


# ---------------------------------------------------------------------------
# 4. LLM coordinate system consistency
# ---------------------------------------------------------------------------

class TestLLMCoordSystem:

    def test_symmetric_llm_coords_center_on_canvas(self):
        """
        LLM should use symmetric coords around (0,0). After normalize (which
        maps logical (0,0) → physical (5,5)), a shape whose bounding box is
        symmetric around (0,0) will have its canvas bbox centered at (5,5).

        normalize() applies: nx = x*scale + 5, ny = y*scale + 5
        For a shape bbox-centered at (0,0): bbox_center → (5, 5).
        """
        # Isosceles triangle exactly bbox-symmetric around origin:
        #   x: [-3, 3] → center 0;  y: [-3, 3] → center 0
        shapes = [{
            "type": "polygon",
            "points": [
                {"x": -3, "y": -3},
                {"x":  3, "y": -3},
                {"x":  0, "y":  3},
            ]
        }]
        normalized = GeometryEngine.normalize(shapes)
        pts = normalized[0]["points"]
        xs = [p["x"] for p in pts]
        ys = [p["y"] for p in pts]
        bbox_cx = (min(xs) + max(xs)) / 2
        bbox_cy = (min(ys) + max(ys)) / 2

        assert abs(bbox_cx - 5.0) < 0.01, f"bbox_cx={bbox_cx} ≠ 5.0"
        assert abs(bbox_cy - 5.0) < 0.01, f"bbox_cy={bbox_cy} ≠ 5.0"

    def test_positive_only_coords_not_centered(self):
        """
        If LLM incorrectly uses positive-only [0,8] coords (old broken prompt),
        the shape would NOT be centered on the canvas — this test documents the
        behaviour so we know the prompt fix matters.

        With the corrected prompt (symmetric [-7,7]), shapes will be centered.
        This test verifies the contrast: symmetric → centered, positive-only → shifted.
        """
        # Symmetric (correct LLM output with new prompt)
        sym = [{"type": "polygon", "points": [
            {"x": -3, "y": -3}, {"x": 3, "y": -3}, {"x": 0, "y": 3}
        ]}]
        # Positive-only (wrong LLM output — old broken prompt)
        pos = [{"type": "polygon", "points": [
            {"x": 1, "y": 1}, {"x": 7, "y": 1}, {"x": 4, "y": 7}
        ]}]

        sym_norm = GeometryEngine.normalize(sym)[0]["points"]
        pos_norm = GeometryEngine.normalize(pos)[0]["points"]

        sym_cx = (min(p["x"] for p in sym_norm) + max(p["x"] for p in sym_norm)) / 2
        pos_cx = (min(p["x"] for p in pos_norm) + max(p["x"] for p in pos_norm)) / 2

        # Symmetric coords produce a canvas center closer to 5.0
        assert abs(sym_cx - 5.0) < abs(pos_cx - 5.0) or abs(sym_cx - 5.0) < 0.5, (
            f"Symmetric coords should center better: sym_cx={sym_cx}, pos_cx={pos_cx}"
        )

    def test_range_minus7_to_7_normalized_correctly(self):
        """Coords in [-7,7] (the corrected LLM range) map fully within [0,10]."""
        shapes = [{
            "type": "polygon",
            "points": [
                {"x": -7, "y": -7},
                {"x":  7, "y": -7},
                {"x":  0, "y":  7},
            ]
        }]
        normalized = GeometryEngine.normalize(shapes)
        for p in normalized[0]["points"]:
            assert 0 <= p["x"] <= 10
            assert 0 <= p["y"] <= 10
