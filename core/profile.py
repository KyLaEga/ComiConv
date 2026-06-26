"""Conversion profile (spec PC-7).

A single, source-type-agnostic description of *how* to produce output, threaded
into every Encoder.build. Today's encoders only need the target format; the
extra knobs (quality, resize, flags) are carried now so Wave 1 image encoders
and batch profiling can honor them without changing the encoder signature again.

Defaults are chosen to reproduce current behavior exactly (spec PC-8): no
resize, no re-encoding flags, quality unset.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ConversionProfile:
    target_format: str = ""
    # 1..100 for lossy encoders; None means "encoder default" (current behavior).
    quality: Optional[int] = None
    # Cap the longest image side in px; None means no downscaling.
    max_side: Optional[int] = None
    # Free-form per-encoder switches; absent keys mean "leave as-is".
    flags: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.quality is not None and not (1 <= self.quality <= 100):
            raise ValueError("quality must be within 1..100")
        if self.max_side is not None and self.max_side <= 0:
            raise ValueError("max_side must be positive")

    @property
    def strip_exif(self) -> bool:
        return bool(self.flags.get("strip_exif", False))

    @property
    def grayscale(self) -> bool:
        return bool(self.flags.get("grayscale", False))

    def is_default(self) -> bool:
        """True when the profile asks for no transformation beyond format choice."""
        return (self.quality is None and self.max_side is None
                and not self.flags)
