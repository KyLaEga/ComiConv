"""TAR encoder — acceptance proof for the plugin core (spec PC-1/PC-6/PC-10).

This whole format is added by ONE new module file plus one capability-manifest
entry, with ZERO edits to the pipeline, registry, or orchestration. It is the
living demonstration that Wave 1/2 formats attach without touching the core.

(Not yet loaded by the base build's _BASE_MODULES — imported on demand by tests;
flipping it on is a one-line change in core/loader.py.)
"""
from __future__ import annotations

import tarfile
from pathlib import Path

from core.capabilities import Capability, register_capability
from core.intermediates import ImageSet, Kind
from core.registry import Encoder, encoder
from core.utils import unique_path


@encoder
class TarEncoder(Encoder):
    format_id = "tar"
    extension = "tar"
    accepts = Kind.IMAGE_SET

    def build(self, intermediate: ImageSet, filename, output_dir, profile=None,
              cancel_check=None):
        images = intermediate.pages
        if not images:
            raise FileNotFoundError("Изображения не найдены.")
        base_dir = intermediate.base_dir
        out_path = unique_path(Path(output_dir) / f"{filename}.tar")
        try:
            with tarfile.open(out_path, "w") as tar:
                for img in images:
                    if cancel_check and cancel_check():
                        raise InterruptedError("Операция прервана")
                    arcname = str(img.relative_to(base_dir)) if base_dir else img.name
                    tar.add(img, arcname=arcname)
        except Exception:
            if out_path.exists():
                out_path.unlink()
            raise
        return out_path


register_capability(Capability("tar", read=False, write=True))
