"""Server-side graph function evaluator.

Instead of trusting the LLM to compute correct coordinates, we ask the LLM
only for the mathematical formula (Python expression), and compute all points
here. This guarantees:
  - Mathematically correct y-values
  - Smooth curves (configurable step)
  - Proper clamping to the visible window [-7, 7]
  - Vertex of a parabola always included
  - Minimum point count always satisfied
"""

import math
import re
from typing import Any, Dict, List, Optional

# Safe evaluation namespace: only math functions, no builtins.
_SAFE_NS: Dict[str, Any] = {
    "__builtins__": {},
    "x": 0,
    "abs": abs,
    "round": round,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "exp": math.exp,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "pi": math.pi,
    "e": math.e,
}

# Regex that matches anything other than safe characters.
# Allows: digits, letters, spaces, operators +-*/**, parentheses, dot, underscore.
_UNSAFE_RE = re.compile(r"[^a-zA-Z0-9_+\-*/.()\s]")

# Patterns for extracting a, b, c from ax^2 + bx + c (to add vertex point).
_QUAD_RE = re.compile(
    r"^([+-]?\s*\d*\.?\d*)\s*\*?\s*x\s*\*{1,2}\s*2"  # a*x**2 or a*x^2
    r"(?:\s*([+-]\s*\d*\.?\d*)\s*\*?\s*x)?"           # optional +bx
    r"(?:\s*([+-]\s*\d+\.?\d*))?$"                     # optional +c
)


class GraphEngine:
    X_MIN: float = -7.0
    X_MAX: float = 7.0
    Y_MIN: float = -7.0
    Y_MAX: float = 7.0
    STEP: float = 0.5          # x step for dense smooth curves
    MIN_POINTS: int = 9        # minimum required in output

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @classmethod
    def compute_series(cls, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert a list of {formula, label, color?} to series with computed points.

        Returns a list in the same format as the existing ``coordinates`` field:
            [{"type": "line", "label": "y = x²", "points": [{"x": ..., "y": ...}, ...]}]

        Invalid / un-evaluable formulas are skipped silently.
        """
        series: List[Dict[str, Any]] = []
        for func in functions:
            formula = str(func.get("formula", "")).strip()
            label = str(func.get("label", f"y = {formula}"))
            color = func.get("color", "blue")

            points = cls._compute_points(formula)
            if len(points) < cls.MIN_POINTS:
                continue

            entry: Dict[str, Any] = {
                "type": "line",
                "label": label,
                "points": points,
            }
            if color:
                entry["color"] = color
            series.append(entry)

        return series

    @classmethod
    def recompute_series_from_coords(cls, coordinates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-evaluate formulas already embedded in existing series objects.

        If a series has a ``formula`` field we recompute; otherwise we keep
        the existing points (passthrough).  This lets us upgrade old LLM output
        that already has a ``formula`` without breaking series that don't.
        """
        result: List[Dict[str, Any]] = []
        for series in coordinates:
            formula = series.get("formula", "")
            if formula:
                points = cls._compute_points(formula)
                if len(points) >= cls.MIN_POINTS:
                    result.append({**series, "points": points})
            else:
                result.append(series)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _compute_points(cls, formula: str) -> List[Dict[str, float]]:
        """Safely evaluate *formula* over the x grid and return valid points."""
        if not formula:
            return []

        # Strip "y = " prefix that LLM sometimes adds
        formula = re.sub(r"^y\s*=\s*", "", formula, flags=re.IGNORECASE).strip()
        # Replace ^ with ** (LLM sometimes uses ^ instead of **)
        formula = formula.replace("^", "**")

        # Safety check: reject formulas with forbidden tokens
        if _UNSAFE_RE.search(formula):
            return []

        # Build x grid: half-integer steps for smooth curves
        x_values: List[float] = []
        v = cls.X_MIN
        while v <= cls.X_MAX + 1e-9:
            x_values.append(round(v, 4))
            v += cls.STEP

        # Attempt to add the parabola vertex for nicer curves
        vertex_x = cls._extract_vertex_x(formula)
        if vertex_x is not None and cls.X_MIN <= vertex_x <= cls.X_MAX:
            x_values.append(round(vertex_x, 4))

        x_values.sort()

        ns = dict(_SAFE_NS)
        points: List[Dict[str, float]] = []
        for xv in x_values:
            ns["x"] = xv
            try:
                yv = eval(formula, ns)  # noqa: S307 — restricted namespace
                if not isinstance(yv, (int, float)):
                    continue
                if math.isnan(yv) or math.isinf(yv):
                    continue
                if cls.Y_MIN <= yv <= cls.Y_MAX:
                    points.append({"x": round(xv, 2), "y": round(yv, 4)})
            except Exception:
                pass

        return points

    @classmethod
    def _extract_vertex_x(cls, formula: str) -> Optional[float]:
        """Try to extract the vertex x-coordinate for a quadratic ax²+bx+c."""
        formula_clean = formula.replace(" ", "")
        m = _QUAD_RE.match(formula_clean)
        if not m:
            return None
        try:
            a_str = (m.group(1) or "1").replace(" ", "") or "1"
            b_str = (m.group(2) or "0").replace(" ", "") or "0"
            a = float(a_str) if a_str not in ("", "+", "-") else (1.0 if "+" in a_str or a_str == "" else -1.0)
            b = float(b_str) if b_str not in ("", "+", "-") else (1.0 if "+" in b_str else -1.0)
            if a == 0:
                return None
            return -b / (2 * a)
        except Exception:
            return None
