"""Module loader (spec PC-6, base build).

Importing a handler module is what registers its decoders/encoders, so the set
of imported modules defines a build's capabilities. The base build loads only
light modules; heavy (Wave 2) modules would be added to a separate list / entry
point group and excluded here without affecting the core.

Also wires the cross-intermediate graph adapters (PDF <-> images) that let the
conversion graph resolve image->pdf and pdf->images as ordinary edges.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from .graph import register_adapter
from .intermediates import Document, ImageSet, Kind

# Light modules shipped in the base build. Order is irrelevant (self-registering).
_BASE_MODULES = (
    "modules.image_io",
    "modules.archive_io",
    "modules.pdf_io",
)

_loaded = False


def _register_pdf_adapters():
    # Imported lazily so this module has no hard import cycle with modules.pdf_io.
    from modules.pdf_io import PdfDecoder, PdfEncoder

    def imageset_to_document(img_set: ImageSet, cancel_check=None) -> Document:
        out_dir = Path(tempfile.mkdtemp(prefix="comiconv_adapt_")).resolve()
        path = PdfEncoder().build(img_set, "adapted", out_dir, cancel_check=cancel_check)
        return Document(path=path, name=img_set.name, temp_dir=out_dir)

    def document_to_imageset(doc: Document, cancel_check=None) -> ImageSet:
        return PdfDecoder().decode(doc.path, cancel_check)

    register_adapter(Kind.IMAGE_SET, Kind.DOCUMENT, imageset_to_document)
    register_adapter(Kind.DOCUMENT, Kind.IMAGE_SET, document_to_imageset)


def load_base_modules():
    """Import light handler modules and register graph adapters (idempotent)."""
    global _loaded
    if _loaded:
        return
    import importlib

    for name in _BASE_MODULES:
        importlib.import_module(name)
    _register_pdf_adapters()
    _loaded = True
