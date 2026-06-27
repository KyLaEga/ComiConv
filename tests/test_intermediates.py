"""T1 — Intermediate type invariants (spec PC-2)."""
from pathlib import Path

from core.intermediates import (
    Archive,
    ArchiveEntry,
    ByteStream,
    Document,
    ImageSet,
    Kind,
    TextData,
)


def test_imageset_kind_and_path_coercion():
    s = ImageSet(pages=["a/1.png", "a/2.png"], name="A")
    assert s.kind is Kind.IMAGE_SET
    assert all(isinstance(p, Path) for p in s.pages)
    assert len(s) == 2


def test_imageset_preserves_order():
    order = ["page_1.png", "page_2.png", "page_10.png"]
    assert [p.name for p in ImageSet(pages=order).pages] == order


def test_document_kind():
    d = Document(path="x.pdf", page_count=3)
    assert d.kind is Kind.DOCUMENT and d.path == Path("x.pdf") and d.page_count == 3


def test_archive_kind():
    a = Archive(entries=[ArchiveEntry("1.png", Path("/t/1.png"))])
    assert a.kind is Kind.ARCHIVE and a.entries[0].arcname == "1.png"


def test_textdata_kind():
    t = TextData(text="# hi", subtype="markdown")
    assert t.kind is Kind.TEXT_DATA and t.subtype == "markdown"


def test_bytestream_kind():
    b = ByteStream(data=b"\x00\x01")
    assert b.kind is Kind.BYTE_STREAM and b.data == b"\x00\x01"


def test_temp_dir_default_none():
    assert ImageSet(pages=[]).temp_dir is None
