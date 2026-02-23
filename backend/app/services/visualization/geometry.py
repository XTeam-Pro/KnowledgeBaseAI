import math
import re
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class GeometryEngine:
    CANVAS_MIN = 0.0
    CANVAS_MAX = 10.0
    CANVAS_SIZE = 10.0
    CENTER = 5.0
    MAX_OBJECTS = 3
    MIN_DISTANCE = 1.0
    TARGET_SIZE = 8.0  # Leave 1.0 margin on each side

    @staticmethod
    def validate(shapes: List[Dict[str, Any]]):
        if len(shapes) > GeometryEngine.MAX_OBJECTS:
            raise ValueError(f"Too many objects: {len(shapes)} > {GeometryEngine.MAX_OBJECTS}")
        
        # Additional validation can be added here
        for i, shape in enumerate(shapes):
            points = shape.get("points", shape.get("coordinates", []))
            
            # Allow single point defined with x, y directly
            if not points and "x" in shape and "y" in shape:
                continue
                
            if not points:
                logger.warning(f"Shape {i} has no points")

    @staticmethod
    def normalize(shapes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transforms coordinates from a logical Cartesian system [-5, 5] to the canvas system [0, 10].
        Logical (0,0) maps to Canvas (5,5).
        Preserves the aspect ratio and integer nature of coordinates where possible.
        """
        if not shapes:
            return []

        # 1. Collect all points to check bounds
        all_points = []
        for shape in shapes:
            points = shape.get("points", shape.get("coordinates", []))
            # Handle flat point
            if not points and "x" in shape and "y" in shape:
                points = [{"x": shape["x"], "y": shape["y"]}]
            all_points.extend(points)
        
        if not all_points:
            return shapes

        # 2. Determine Scale
        # We want to map logical [-5, 5] to canvas [0, 10].
        # If points exceed [-5, 5], we scale them down to fit.
        # If they are within range, we keep scale = 1.0 to preserve "integer-ness" as requested.
        max_abs_coord = 0.0
        for p in all_points:
            max_abs_coord = max(max_abs_coord, abs(p["x"]), abs(p["y"]))
        
        # Default logical limit is 5.0. If points go beyond (e.g. 10), we scale down.
        # We allow a small epsilon for floating point noise.
        limit = 5.0
        scale = 1.0
        if max_abs_coord > limit + 0.01:
            scale = limit / max_abs_coord
            
        # 3. Transform
        # Formula: physical = logical * scale + center_offset
        center_offset = GeometryEngine.CENTER # 5.0

        normalized_shapes = []
        for shape in shapes:
            # Deep copy to avoid modifying original
            new_shape = shape.copy()
            if "params" in shape:
                new_shape["params"] = shape["params"].copy()
                
            new_points = []
            points_source = shape.get("points", shape.get("coordinates", []))
            is_flat_point = False
            
            if not points_source and "x" in shape and "y" in shape:
                points_source = [{"x": shape["x"], "y": shape["y"]}]
                is_flat_point = True
            
            for p in points_source:
                # Apply transformation: Logical (0,0) -> Physical (5,5)
                # Note: We do NOT flip Y here. We assume the frontend handles coordinate systems (or Y is up).
                # If Y needs to be flipped for standard screen coords (y-down), it should be done here:
                # ny = center_offset - (p["y"] * scale)
                # But usually math graphs assume Y-up. Let's stick to simple translation for now unless broken.
                
                nx = (p["x"] * scale) + center_offset
                ny = (p["y"] * scale) + center_offset
                
                # Clamp to [CANVAS_MIN, CANVAS_MAX]
                nx = max(GeometryEngine.CANVAS_MIN, min(GeometryEngine.CANVAS_MAX, nx))
                ny = max(GeometryEngine.CANVAS_MIN, min(GeometryEngine.CANVAS_MAX, ny))
                
                # Round to nearest integer (or 0.5) as requested
                # User wants integers mostly.
                # If we didn't scale (scale=1), we try to round to int/0.5
                if scale > 0.99:
                     nx = round(nx * 2) / 2.0
                     ny = round(ny * 2) / 2.0
                     if abs(nx - round(nx)) < 0.01: nx = int(round(nx))
                     if abs(ny - round(ny)) < 0.01: ny = int(round(ny))
                
                new_points.append({"x": nx, "y": ny})

            # Update the shape with new points using the same key as found
            if is_flat_point and new_points:
                new_shape["x"] = new_points[0]["x"]
                new_shape["y"] = new_points[0]["y"]
            elif "points" in shape:
                new_shape["points"] = new_points
            else:
                new_shape["coordinates"] = new_points

            # Normalize vertex_labels using the same transform so labels track their vertices
            if "vertex_labels" in shape and isinstance(shape["vertex_labels"], list):
                new_vertex_labels = []
                for vl in shape["vertex_labels"]:
                    vx = float(vl.get("x", 0))
                    vy = float(vl.get("y", 0))
                    vnx = (vx * scale) + center_offset
                    vny = (vy * scale) + center_offset
                    vnx = max(GeometryEngine.CANVAS_MIN, min(GeometryEngine.CANVAS_MAX, vnx))
                    vny = max(GeometryEngine.CANVAS_MIN, min(GeometryEngine.CANVAS_MAX, vny))
                    if scale > 0.99:
                        vnx = round(vnx * 2) / 2.0
                        vny = round(vny * 2) / 2.0
                        if abs(vnx - round(vnx)) < 0.01:
                            vnx = int(round(vnx))
                        if abs(vny - round(vny)) < 0.01:
                            vny = int(round(vny))
                    new_vertex_labels.append({**vl, "x": vnx, "y": vny})
                new_shape["vertex_labels"] = new_vertex_labels

            normalized_shapes.append(new_shape)
            
        return normalized_shapes

    @staticmethod
    def snap_labels_to_vertices(shape: Dict[str, Any]) -> Dict[str, Any]:
        """Snap every vertex_label to the nearest polygon vertex point.

        LLM sometimes places labels at slightly different coordinates than the
        actual polygon vertices. After normalization the drift can cause labels
        to float in open space instead of sitting on a corner.
        """
        points = shape.get("points") or shape.get("coordinates") or []
        vertex_labels = shape.get("vertex_labels")
        if not points or not vertex_labels:
            return shape

        def _nearest(label_pt: Dict[str, Any]) -> Dict[str, Any]:
            lx, ly = float(label_pt.get("x", 0)), float(label_pt.get("y", 0))
            best = min(points, key=lambda p: (p["x"] - lx) ** 2 + (p["y"] - ly) ** 2)
            return {**label_pt, "x": best["x"], "y": best["y"]}

        new_shape = dict(shape)
        new_shape["vertex_labels"] = [_nearest(vl) for vl in vertex_labels]
        return new_shape

    @staticmethod
    def _angle_at_vertex(prev_p: Dict, curr_p: Dict, next_p: Dict) -> Optional[float]:
        """Interior angle (degrees) at curr_p given the two adjacent vertices."""
        v1 = (prev_p["x"] - curr_p["x"], prev_p["y"] - curr_p["y"])
        v2 = (next_p["x"] - curr_p["x"], next_p["y"] - curr_p["y"])
        mag1 = math.hypot(*v1)
        mag2 = math.hypot(*v2)
        if mag1 < 1e-9 or mag2 < 1e-9:
            return None
        cos_a = max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (mag1 * mag2)))
        return math.degrees(math.acos(cos_a))

    @staticmethod
    def validate_and_relabel_triangle(
        shapes: List[Dict[str, Any]],
        question_text: str,
        angle_tolerance: float = 12.0,
    ) -> List[Dict[str, Any]]:
        """For triangles, extract angle constraints from question text and verify
        that vertex labels are assigned to the correct vertices.

        If labels are wrong, reassign them so the described angles match the
        actual geometry.  Only triangles (3 points) are processed; other shapes
        are returned unchanged.

        ``angle_tolerance`` (degrees) is the allowed deviation between the
        described angle and the computed one (accounts for LLM rounding).
        """
        # Parse "угол X = N" or "угол X равен N" patterns (Cyrillic + Latin labels)
        _ANGLE_RE = re.compile(
            r"(?:угол|угл)\w*\s+([A-Za-zА-Яа-я])\s*(?:=|равен|равн\w*|составляет|равняется)\s*(\d+)",
            re.IGNORECASE,
        )

        constraints: Dict[str, float] = {}
        for m in _ANGLE_RE.finditer(question_text):
            constraints[m.group(1).upper()] = float(m.group(2))

        if not constraints:
            return shapes

        result: List[Dict[str, Any]] = []
        for shape in shapes:
            points = shape.get("points") or shape.get("coordinates") or []
            vertex_labels = shape.get("vertex_labels", [])
            n = len(points)

            if n != 3 or not vertex_labels:
                result.append(shape)
                continue

            # Compute interior angle at each polygon vertex (index 0, 1, 2)
            computed: List[Optional[float]] = []
            for i in range(3):
                a = GeometryEngine._angle_at_vertex(
                    points[(i - 1) % 3], points[i], points[(i + 1) % 3]
                )
                computed.append(a)

            # Current label at each vertex index
            # vertex_labels may have fewer entries than points — pad with None
            label_at: Dict[int, str] = {}
            for vl in vertex_labels:
                # Find which vertex index this label sits at (after snap)
                lx, ly = float(vl.get("x", 0)), float(vl.get("y", 0))
                idx = min(range(3), key=lambda i: (points[i]["x"] - lx) ** 2 + (points[i]["y"] - ly) ** 2)
                label_at[idx] = vl.get("label", "")

            # Build reverse map label→index
            idx_of: Dict[str, int] = {v: k for k, v in label_at.items()}

            # Check each constraint
            mismatch = False
            for label, expected_angle in constraints.items():
                if label not in idx_of:
                    continue
                actual = computed[idx_of[label]]
                if actual is None or abs(actual - expected_angle) > angle_tolerance:
                    mismatch = True
                    break

            if not mismatch:
                result.append(shape)
                continue

            # Try to find a permutation of label assignments that satisfies constraints
            from itertools import permutations

            current_labels = [label_at.get(i, "") for i in range(3)]
            best_assignment: Optional[List[str]] = None

            for perm in permutations(current_labels):
                # perm[i] is the label we'd assign to vertex index i
                ok = True
                for label, expected_angle in constraints.items():
                    try:
                        vi = perm.index(label)
                    except ValueError:
                        continue
                    a = computed[vi]
                    if a is None or abs(a - expected_angle) > angle_tolerance:
                        ok = False
                        break
                if ok:
                    best_assignment = list(perm)
                    break

            if best_assignment is None:
                # No valid relabeling found — keep original but log warning
                logger.warning(
                    "triangle_relabel_failed",
                    constraints=constraints,
                    computed_angles=computed,
                    label_at=label_at,
                )
                result.append(shape)
                continue

            # Rebuild vertex_labels with new assignment (keep offset fields if any)
            old_vl_by_label = {vl.get("label", ""): vl for vl in vertex_labels}
            new_vertex_labels: List[Dict[str, Any]] = []
            for i, new_label in enumerate(best_assignment):
                if not new_label:
                    continue
                old_vl = old_vl_by_label.get(new_label, {})
                new_vertex_labels.append(
                    {**old_vl, "label": new_label, "x": points[i]["x"], "y": points[i]["y"]}
                )

            logger.info(
                "triangle_relabeled",
                old=label_at,
                new={i: l for i, l in enumerate(best_assignment)},
            )
            new_shape = dict(shape)
            new_shape["vertex_labels"] = new_vertex_labels
            result.append(new_shape)

        return result

    @staticmethod
    def check_collisions(shapes: List[Dict[str, Any]]) -> List[Tuple[int, int]]:
        """
        Returns a list of pairs of indices of shapes that overlap or are too close.
        Uses bounding boxes for simplicity.
        """
        conflicts = []
        bboxes = []
        
        for i, shape in enumerate(shapes):
            points = shape.get("points", shape.get("coordinates", []))
            if not points:
                bboxes.append(None)
                continue
            
            xs = [p["x"] for p in points]
            ys = [p["y"] for p in points]
            bboxes.append({
                "min_x": min(xs), "max_x": max(xs),
                "min_y": min(ys), "max_y": max(ys)
            })
            
        for i in range(len(bboxes)):
            if bboxes[i] is None: continue
            for j in range(i + 1, len(bboxes)):
                if bboxes[j] is None: continue
                
                b1 = bboxes[i]
                b2 = bboxes[j]
                
                # Check for overlap with margin
                margin = GeometryEngine.MIN_DISTANCE / 2
                
                overlap_x = (b1["min_x"] - margin < b2["max_x"] + margin) and \
                            (b1["max_x"] + margin > b2["min_x"] - margin)
                
                overlap_y = (b1["min_y"] - margin < b2["max_y"] + margin) and \
                            (b1["max_y"] + margin > b2["min_y"] - margin)
                            
                if overlap_x and overlap_y:
                    conflicts.append((i, j))
                    
        return conflicts
