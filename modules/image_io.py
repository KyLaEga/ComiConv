"""Directory-of-images decoder.

A folder whose direct children include images decodes to an ImageSet (no temp
dir — the files already live on disk). Nested image folders are separate targets
at the discovery layer, so this does not recurse (preserves legacy behavior,
spec PC-8).
"""
from __future__ import annotations

from pathlib import Path

from core.intermediates import ImageSet
from core.registry import Decoder, decoder
from core.utils import IMAGE_EXTENSIONS, natural_sort_key


@decoder
class DirDecoder(Decoder):
    source_type = "dir"

    def decode(self, source, cancel_check=None):
        source = Path(source)
        images = [p for p in source.iterdir()
                  if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        images.sort(key=lambda x: natural_sort_key(x.name))
        return ImageSet(pages=images, name=source.name or "Images")
