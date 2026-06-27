"""Signature (magic-byte) detection (spec PC-3).

Determines the real source type from the leading bytes of a file, ignoring a
possibly-wrong extension. Detectors are registered on the shared registry; the
extension is consulted only as a last resort when no signature matches.

Source-type ids returned here are the keys decoders register under (see
core.registry / the handler modules). Container formats that share a signature
(zip vs cbz, both PKZIP) are disambiguated by extension, since they are the same
bytes with different intent.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from .registry import registry

_HEAD_BYTES = 16


def _sig(head: bytes, ext: str) -> Optional[str]:
    """Built-in signature table for the formats shipping today."""
    # Images
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return "image"
    if head[:3] == b"\xff\xd8\xff":  # JPEG
        return "image"
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return "image"
    if head[:2] == b"BM":  # BMP
        return "image"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image"
    if head[:4] in (b"II*\x00", b"MM\x00*"):  # TIFF
        return "image"
    # Documents
    if head[:5] == b"%PDF-":
        return "pdf"
    # Containers (PKZIP) — zip and cbz are the same bytes; split by extension.
    if head[:4] in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"):
        return "cbz" if ext == ".cbz" else "zip"
    return None


# Extension fallback when the signature is unknown (e.g. truncated head).
_EXT_FALLBACK = {
    ".jpg": "image", ".jpeg": "image", ".png": "image", ".webp": "image",
    ".gif": "image", ".bmp": "image", ".tiff": "image", ".tif": "image",
    ".pdf": "pdf", ".zip": "zip", ".cbz": "cbz",
}


@registry.register_detector
def _builtin_detector(head: bytes, ext: str) -> Optional[str]:
    return _sig(head, ext)


@registry.register_detector
def _extension_detector(head: bytes, ext: str) -> Optional[str]:
    return _EXT_FALLBACK.get(ext)


def detect_path(path) -> Optional[str]:
    """Detect the source type of a file on disk by signature, then extension."""
    p = Path(path)
    try:
        with open(p, "rb") as fh:
            head = fh.read(_HEAD_BYTES)
    except OSError:
        head = b""
    return registry.detect(head, p.suffix.lower())
