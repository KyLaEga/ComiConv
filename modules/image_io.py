"""Directory-of-images decoder.

A folder whose direct children include images decodes to an ImageSet (no temp
dir — the files already live on disk). Nested image folders are separate targets
at the discovery layer, so this does not recurse (preserves legacy behavior,
spec PC-8).
"""
from __future__ import annotations

import shutil
from pathlib import Path

from core.intermediates import ImageSet, Kind
from core.registry import Decoder, Encoder, decoder, encoder
from core.utils import IMAGE_EXTENSIONS, natural_sort_key, unique_path


@decoder
class DirDecoder(Decoder):
    source_type = "dir"

    def decode(self, source, cancel_check=None):
        source = Path(source)
        images = [p for p in source.iterdir()
                  if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        images.sort(key=lambda x: natural_sort_key(x.name))
        return ImageSet(pages=images, name=source.name or "Images")


@encoder
class DirEncoder(Encoder):
    accepts = Kind.IMAGE_SET
    format_id = "folder"

    def build(self, intermediate: ImageSet, filename, output_dir, profile=None, cancel_check=None):
        images = intermediate.pages
        if not images:
            raise FileNotFoundError("Изображения не найдены.")
        base_dir = intermediate.base_dir
        
        out_path = unique_path(Path(output_dir) / filename)
        out_path.mkdir(parents=True, exist_ok=True)
        
        try:
            for img in images:
                if cancel_check and cancel_check():
                    raise InterruptedError("Операция прервана")
                
                rel_path = img.relative_to(base_dir) if base_dir else Path(img.name)
                dest = out_path / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(img, dest)
        except Exception:
            if out_path.exists():
                shutil.rmtree(out_path, ignore_errors=True)
            raise
        return out_path

