"""Shared test fixtures for ComiConv.

Builds small, deterministic image sets and source containers (loose images,
CBZ/ZIP, PDF) so the golden tests can assert conversion parity without binary
blobs checked into the repo.
"""
import io
import zipfile

import fitz
import pytest
from PIL import Image


def _solid_png(path, color, size=(16, 24)):
    Image.new("RGB", size, color).save(path, format="PNG")


@pytest.fixture
def page_colors():
    # Deliberately out of natural order on disk to exercise sorting.
    return [
        ("page_2.png", (200, 30, 30)),
        ("page_10.png", (30, 200, 30)),
        ("page_1.png", (30, 30, 200)),
    ]


@pytest.fixture
def loose_images(tmp_path, page_colors):
    """A folder of loose PNG pages. Returns (folder, expected_natural_order)."""
    folder = tmp_path / "Loose Comic"
    folder.mkdir()
    for name, color in page_colors:
        _solid_png(folder / name, color)
    expected = ["page_1.png", "page_2.png", "page_10.png"]
    return folder, expected


@pytest.fixture
def cbz_file(tmp_path, page_colors):
    """A .cbz archive of PNG pages. Returns (path, expected_natural_order)."""
    path = tmp_path / "MyComic.cbz"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, color in page_colors:
            buf = io.BytesIO()
            Image.new("RGB", (16, 24), color).save(buf, format="PNG")
            zf.writestr(name, buf.getvalue())
    expected = ["page_1.png", "page_2.png", "page_10.png"]
    return path, expected


@pytest.fixture
def pdf_file(tmp_path, page_colors):
    """A 3-page PDF. Returns (path, page_count)."""
    path = tmp_path / "MyDoc.pdf"
    doc = fitz.open()
    for _name, _color in page_colors:
        doc.new_page(width=120, height=180)
    doc.save(path)
    doc.close()
    return path, len(page_colors)
