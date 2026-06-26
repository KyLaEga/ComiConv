"""ZIP/CBZ handlers: decode (extract) and encode (re-archive).

Re-expresses the legacy zip/cbz paths of OptimizedMediaConverter as registry
citizens (spec PC-4/PC-8), preserving Zip-Slip-safe extraction, natural order,
the temp-dir sandbox contract and cancellation checks (spec PC-9).
"""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

from core.intermediates import ImageSet, Kind
from core.registry import Decoder, Encoder, decoder, encoder
from core.utils import IMAGE_EXTENSIONS, natural_sort_key, unique_path


def _extract_zip(source: Path, cancel_check=None) -> ImageSet:
    # Resolve the base: on macOS TMPDIR is a symlink, so an unresolved base
    # would make every member look like a Zip-Slip escape (see converter.py fix).
    temp_extract = Path(tempfile.mkdtemp(prefix=f"comiconv_{source.stem}_")).resolve()
    try:
        with zipfile.ZipFile(source, "r") as zip_ref:
            for member in zip_ref.infolist():
                if cancel_check and cancel_check():
                    raise InterruptedError("Операция прервана")
                target_path = (temp_extract / member.filename).resolve()
                try:
                    target_path.relative_to(temp_extract)
                except ValueError:
                    continue  # outside sandbox -> skip
                zip_ref.extract(member, temp_extract)
    except Exception as e:
        shutil.rmtree(temp_extract, ignore_errors=True)
        if isinstance(e, InterruptedError):
            raise
        raise ValueError(f"Архив поврежден: {source.name}")

    images = [p for p in temp_extract.rglob("*")
              if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
    images.sort(key=lambda x: natural_sort_key(str(x.relative_to(temp_extract))))
    return ImageSet(pages=images, name=source.stem, temp_dir=temp_extract)


@decoder
class ZipDecoder(Decoder):
    source_type = "zip"

    def decode(self, source, cancel_check=None):
        return _extract_zip(Path(source), cancel_check)


@decoder
class CbzDecoder(Decoder):
    source_type = "cbz"

    def decode(self, source, cancel_check=None):
        return _extract_zip(Path(source), cancel_check)


class _ArchiveEncoder(Encoder):
    accepts = Kind.IMAGE_SET

    def build(self, intermediate: ImageSet, filename, output_dir, profile=None,
              cancel_check=None):
        images = intermediate.pages
        if not images:
            raise FileNotFoundError("Изображения не найдены.")
        base_dir = intermediate.base_dir
        out_path = unique_path(Path(output_dir) / f"{filename}.{self.extension}")
        try:
            with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as archive:
                for img in images:
                    if cancel_check and cancel_check():
                        raise InterruptedError("Операция прервана")
                    arcname = str(img.relative_to(base_dir)) if base_dir else img.name
                    archive.write(img, arcname=arcname)
        except Exception:
            if out_path.exists():
                out_path.unlink()
            raise
        return out_path


@encoder
class CbzEncoder(_ArchiveEncoder):
    format_id = "cbz"
    extension = "cbz"


@encoder
class ZipEncoder(_ArchiveEncoder):
    format_id = "zip"
    extension = "zip"
