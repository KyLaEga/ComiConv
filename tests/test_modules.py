"""T4/T5 — registry handlers parity + graph resolution (spec PC-4/PC-8)."""
import zipfile

import fitz
import pytest

from core.detect import detect_path
from core.graph import NoConversionPath, adapt
from core.intermediates import Kind
from core.loader import load_base_modules
from core.registry import registry


@pytest.fixture(autouse=True)
def _modules():
    load_base_modules()


# --- Decoders (parity with legacy extraction) -------------------------------

def test_cbz_decoder_natural_order(cbz_file):
    path, expected = cbz_file
    dec = registry.decoder_for(detect_path(path))
    img_set = dec.decode(str(path))
    try:
        assert [p.name for p in img_set.pages] == expected
        assert img_set.kind is Kind.IMAGE_SET
        assert img_set.temp_dir is not None
    finally:
        import shutil
        shutil.rmtree(img_set.temp_dir, ignore_errors=True)


def test_pdf_decoder_page_count(pdf_file):
    path, count = pdf_file
    dec = registry.decoder_for(detect_path(path))
    img_set = dec.decode(str(path))
    try:
        assert len(img_set) == count
    finally:
        import shutil
        shutil.rmtree(img_set.temp_dir, ignore_errors=True)


def test_dir_decoder(loose_images):
    folder, expected = loose_images
    dec = registry.decoder_for("dir")
    img_set = dec.decode(str(folder))
    assert [p.name for p in img_set.pages] == expected


# --- Encoders (parity with legacy output) -----------------------------------

def test_cbz_encoder_roundtrip(cbz_file, tmp_path):
    path, expected = cbz_file
    img_set = registry.decoder_for("cbz").decode(str(path))
    try:
        out = registry.encoder_for("cbz").build(img_set, "out", str(tmp_path))
        with zipfile.ZipFile(out) as zf:
            assert zf.namelist() == expected
    finally:
        import shutil
        shutil.rmtree(img_set.temp_dir, ignore_errors=True)


def test_pdf_encoder_from_images(cbz_file, tmp_path):
    path, expected = cbz_file
    img_set = registry.decoder_for("cbz").decode(str(path))
    try:
        out = registry.encoder_for("pdf").build(img_set, "merged", str(tmp_path))
        with fitz.open(out) as doc:
            assert doc.page_count == len(expected)
    finally:
        import shutil
        shutil.rmtree(img_set.temp_dir, ignore_errors=True)


# --- Graph resolution (PC-4) ------------------------------------------------

def test_graph_imageset_to_document(cbz_file):
    path, expected = cbz_file
    img_set = registry.decoder_for("cbz").decode(str(path))
    try:
        doc = adapt(img_set, Kind.DOCUMENT)
        assert doc.kind is Kind.DOCUMENT
        with fitz.open(doc.path) as d:
            assert d.page_count == len(expected)
    finally:
        import shutil
        shutil.rmtree(img_set.temp_dir, ignore_errors=True)


def test_graph_document_to_imageset(pdf_file):
    from core.intermediates import Document
    path, count = pdf_file
    doc = Document(path=path, page_count=count)
    img_set = adapt(doc, Kind.IMAGE_SET)
    try:
        assert img_set.kind is Kind.IMAGE_SET and len(img_set) == count
    finally:
        import shutil
        shutil.rmtree(img_set.temp_dir, ignore_errors=True)


def test_graph_same_kind_is_noop(cbz_file):
    img_set = registry.decoder_for("cbz").decode(str(cbz_file[0]))
    try:
        assert adapt(img_set, Kind.IMAGE_SET) is img_set
    finally:
        import shutil
        shutil.rmtree(img_set.temp_dir, ignore_errors=True)


def test_graph_no_path_raises():
    from core.intermediates import TextData
    with pytest.raises(NoConversionPath):
        adapt(TextData(text="x"), Kind.ARCHIVE)
