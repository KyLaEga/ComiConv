"""PDF handlers: decode (render pages -> images) and encode (images -> PDF).

These also act as the graph adapters between Document and ImageSet
intermediates (spec PC-4): PdfDecoder is Document->ImageSet, PdfEncoder is
ImageSet->Document. Ported from OptimizedMediaConverter (spec PC-8).
"""
from __future__ import annotations

import io
import shutil
import tempfile
from pathlib import Path

import fitz

try:
    from PIL import Image
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False

from core.intermediates import ImageSet, Kind
from core.registry import Decoder, Encoder, decoder, encoder
from core.utils import IMAGE_EXTENSIONS, natural_sort_key, unique_path

_RENDER_ZOOM = 1.5  # moderate quality, resource-friendly (matches legacy)


@decoder
class PdfDecoder(Decoder):
    source_type = "pdf"

    def decode(self, source, cancel_check=None):
        source = Path(source)
        temp_extract = Path(
            tempfile.mkdtemp(prefix=f"comiconv_{source.stem}_")
        ).resolve()
        try:
            with fitz.open(source) as doc:
                for page_num in range(len(doc)):
                    if cancel_check and cancel_check():
                        raise InterruptedError("Операция прервана")
                    page = doc.load_page(page_num)
                    mat = fitz.Matrix(_RENDER_ZOOM, _RENDER_ZOOM)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    out_path = temp_extract / f"page_{page_num + 1:04d}.jpg"
                    pix.save(str(out_path))
        except Exception as e:
            shutil.rmtree(temp_extract, ignore_errors=True)
            if isinstance(e, InterruptedError):
                raise
            raise ValueError(f"Ошибка при чтении PDF {source.name}: {e}")

        images = [p for p in temp_extract.rglob("*")
                  if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        images.sort(key=lambda x: natural_sort_key(str(x.relative_to(temp_extract))))
        return ImageSet(pages=images, name=source.stem, temp_dir=temp_extract)


def _image_to_pdf_bytes(img_path):
    """One-page PDF for an image. MuPDF only decodes png/jpeg/pnm/psd/ps, so
    webp/gif/bmp/tiff are re-encoded to PNG via Pillow first."""
    try:
        with fitz.open(img_path) as img_doc:
            return img_doc.convert_to_pdf()
    except Exception:
        if not _HAS_PIL:
            raise
        with Image.open(img_path) as im:
            if im.mode in ("RGBA", "P", "LA"):
                im = im.convert("RGB")
            buf = io.BytesIO()
            im.save(buf, format="PNG")
        with fitz.open("png", buf.getvalue()) as img_doc:
            return img_doc.convert_to_pdf()


@encoder
class PdfEncoder(Encoder):
    format_id = "pdf"
    extension = "pdf"
    accepts = Kind.IMAGE_SET

    def build(self, intermediate: ImageSet, filename, output_dir, profile=None,
              cancel_check=None):
        images_paths = intermediate.pages
        if not images_paths:
            raise FileNotFoundError("Изображения не найдены.")
        pdf_path = unique_path(Path(output_dir) / f"{filename}.pdf")
        try:
            with fitz.open() as doc:
                for img_path in images_paths:
                    if cancel_check and cancel_check():
                        raise InterruptedError("Операция прервана")
                    try:
                        pdf_bytes = _image_to_pdf_bytes(img_path)
                        with fitz.open("pdf", pdf_bytes) as page_doc:
                            doc.insert_pdf(page_doc)
                    except Exception:
                        continue  # skip a single broken image
                if doc.page_count == 0:
                    raise ValueError("Не удалось добавить ни одной страницы в PDF.")
                doc.save(pdf_path)
        except Exception:
            if pdf_path.exists():
                pdf_path.unlink()
            raise
        return pdf_path
