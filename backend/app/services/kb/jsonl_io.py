from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]  # app/
KB_DIR = BASE_DIR / "kb"


def get_path(filename: str) -> str:
    """Return absolute path for KB file, searching recursively if needed."""
    direct = KB_DIR / filename
    if direct.exists():
        return str(direct)

    for root, _dirs, files in os.walk(KB_DIR):
        if filename in files:
            return str(Path(root) / filename)

    return str(direct)


def load_jsonl(path_or_filename: str) -> list[dict[str, Any]]:
    """Load JSONL from an absolute path or KB-relative filename."""
    p = Path(path_or_filename)
    if not p.exists():
        p = Path(get_path(path_or_filename))
    if not p.exists():
        return []

    out: list[dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def make_uid(prefix: str, title: str) -> str:
    """Build deterministic UID from prefix and title."""
    norm = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not norm:
        norm = "item"
    return f"{prefix}-{norm[:64]}".upper()

