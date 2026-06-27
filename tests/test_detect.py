"""T3 — Signature detection, incl. wrong-extension cases (spec PC-3)."""
import io
import zipfile

from PIL import Image

from core.detect import detect_path


def test_png_detected(tmp_path):
    p = tmp_path / "a.png"
    Image.new("RGB", (4, 4), (1, 2, 3)).save(p, "PNG")
    assert detect_path(p) == "image"


def test_pdf_detected(tmp_path):
    p = tmp_path / "a.pdf"
    p.write_bytes(b"%PDF-1.4\n%...")
    assert detect_path(p) == "pdf"


def test_zip_vs_cbz_by_extension(tmp_path):
    for name, expected in (("a.zip", "zip"), ("a.cbz", "cbz")):
        p = tmp_path / name
        with zipfile.ZipFile(p, "w") as zf:
            zf.writestr("x.txt", "hi")
        assert detect_path(p) == expected


def test_wrong_extension_uses_signature(tmp_path):
    # A real PNG masquerading as .jpg must be detected as an image by signature.
    p = tmp_path / "lying.jpg"
    Image.new("RGB", (4, 4), (9, 9, 9)).save(p, "PNG")
    assert detect_path(p) == "image"


def test_truncated_falls_back_to_extension(tmp_path):
    p = tmp_path / "empty.pdf"
    p.write_bytes(b"")  # no signature
    assert detect_path(p) == "pdf"


def test_unknown_returns_none(tmp_path):
    p = tmp_path / "mystery.xyz"
    p.write_bytes(b"\x00\x01\x02random")
    assert detect_path(p) is None
