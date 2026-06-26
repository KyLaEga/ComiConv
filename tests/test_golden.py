"""T0 — Golden-output safety net (spec PC-8).

Pins the *current* behavior of OptimizedMediaConverter so the plugin-core refactor
can prove parity. Asserts structural invariants (page discovery, natural ordering,
archive contents, PDF page counts) rather than fragile byte-for-byte blobs.
"""
import zipfile

import fitz

from converter import ImageGroup, OptimizedMediaConverter


def _names(paths):
    return [p.name for p in paths]


# --- Discovery + natural ordering -------------------------------------------

def test_find_loose_images_groups_and_sorts(loose_images):
    folder, expected_order = loose_images
    conv = OptimizedMediaConverter()
    targets = conv.find_comics([str(p) for p in folder.iterdir()])
    groups = [t for t in targets if isinstance(t, ImageGroup)]
    assert len(groups) == 1
    assert _names(groups[0].images) == expected_order


def test_extract_cbz_natural_order(cbz_file):
    path, expected_order = cbz_file
    conv = OptimizedMediaConverter()
    images, temp = conv.extract_and_prepare(str(path))
    try:
        assert _names(images) == expected_order
    finally:
        conv.cleanup(temp)


def test_extract_pdf_page_count(pdf_file):
    path, page_count = pdf_file
    conv = OptimizedMediaConverter()
    images, temp = conv.extract_and_prepare(str(path))
    try:
        assert len(images) == page_count
        assert all(p.suffix.lower() == ".jpg" for p in images)
    finally:
        conv.cleanup(temp)


# --- Output encoders ---------------------------------------------------------

def test_to_cbz_roundtrip(cbz_file, tmp_path):
    path, expected_order = cbz_file
    conv = OptimizedMediaConverter()
    images, temp = conv.extract_and_prepare(str(path))
    try:
        out = conv.to_cbz(images, "out", str(tmp_path))
        assert out.exists() and out.suffix == ".cbz"
        with zipfile.ZipFile(out) as zf:
            assert zf.namelist() == expected_order
    finally:
        conv.cleanup(temp)


def test_to_pdf_from_images(cbz_file, tmp_path):
    path, expected_order = cbz_file
    conv = OptimizedMediaConverter()
    images, temp = conv.extract_and_prepare(str(path))
    try:
        out = conv.to_pdf(images, "merged", str(tmp_path))
        assert out.exists() and out.suffix == ".pdf"
        with fitz.open(out) as doc:
            assert doc.page_count == len(expected_order)
    finally:
        conv.cleanup(temp)


def test_unique_path_collision(tmp_path):
    conv = OptimizedMediaConverter()
    (tmp_path / "out.cbz").write_bytes(b"x")
    p = conv._unique_path(tmp_path / "out.cbz")
    assert p.name == "out (2).cbz"
