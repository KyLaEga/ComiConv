"""Shared pipeline helpers (natural sort, unique path, image extension set).

Single source of truth so the legacy converter and the new handler modules
order and name files identically (preserves spec PC-8 parity).
"""
from __future__ import annotations

import re
from pathlib import Path

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp", ".gif")


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(r"(\d+)", str(s))]


def unique_path(path: Path) -> Path:
    """Return a non-existing path, adding a ' (2)', ' (3)'… suffix if needed."""
    path = Path(path)
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    i = 2
    while True:
        candidate = path.with_name(f"{stem} ({i}){suffix}")
        if not candidate.exists():
            return candidate
        i += 1
