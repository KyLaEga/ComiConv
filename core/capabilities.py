"""Per-platform capability manifest (spec PC-5).

Declarative data — one source of truth shared by the registry (refuse gated
targets) and the UI (grey out unavailable formats). A capability is a
``(format_id, direction)`` pair; ``platforms`` optionally restricts a capability
to specific platforms (``sys.platform`` values: 'darwin', 'win32', 'linux',
plus 'android'/'ios' on mobile mirror).

Absence of a platform restriction means "available everywhere the module is
built in". This is why, e.g., HEIC write can be declared iOS-only without any
code branching.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class Capability:
    format_id: str
    read: bool = False
    write: bool = False
    # None -> all platforms; otherwise a set of allowed platform ids.
    read_platforms: Optional[frozenset] = None
    write_platforms: Optional[frozenset] = None


# Base-build manifest for formats shipping today. Wave 1/2 modules extend this.
_MANIFEST: Dict[str, Capability] = {
    "zip": Capability("zip", read=True, write=True),
    "cbz": Capability("cbz", read=True, write=True),
    "pdf": Capability("pdf", read=True, write=True),
    # Example of a platform-gated future capability (declared, not yet built):
    # "heic": Capability("heic", read=True, write=True,
    #                    write_platforms=frozenset({"darwin", "ios"})),
}


def _current_platform() -> str:
    return sys.platform


def _allowed(platforms: Optional[frozenset], current: str) -> bool:
    return platforms is None or current in platforms


def register_capability(cap: Capability):
    _MANIFEST[cap.format_id] = cap


def can_write(format_id: str, platform: Optional[str] = None) -> bool:
    cap = _MANIFEST.get(format_id)
    if not cap or not cap.write:
        return False
    return _allowed(cap.write_platforms, platform or _current_platform())


def can_read(format_id: str, platform: Optional[str] = None) -> bool:
    cap = _MANIFEST.get(format_id)
    if not cap or not cap.read:
        return False
    return _allowed(cap.read_platforms, platform or _current_platform())


def available_write_formats(platform: Optional[str] = None) -> Tuple[str, ...]:
    """Format ids writable on the given (or current) platform — what the UI offers."""
    plat = platform or _current_platform()
    return tuple(fid for fid in _MANIFEST if can_write(fid, plat))
