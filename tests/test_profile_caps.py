"""T6/T7 — ConversionProfile + capability manifest (spec PC-5/PC-7)."""
import pytest

from core.capabilities import (
    Capability,
    available_write_formats,
    can_write,
    register_capability,
)
from core.profile import ConversionProfile


# --- Profile ---------------------------------------------------------------

def test_default_profile_is_default():
    assert ConversionProfile(target_format="pdf").is_default()


def test_profile_flags_accessors():
    p = ConversionProfile(target_format="webp", flags={"strip_exif": True})
    assert p.strip_exif and not p.grayscale and not p.is_default()


def test_profile_validates_quality():
    with pytest.raises(ValueError):
        ConversionProfile(quality=0)
    with pytest.raises(ValueError):
        ConversionProfile(quality=101)


def test_profile_validates_max_side():
    with pytest.raises(ValueError):
        ConversionProfile(max_side=0)
    assert ConversionProfile(max_side=2000).max_side == 2000


# --- Capabilities ----------------------------------------------------------

def test_base_formats_writable_everywhere():
    for fid in ("zip", "cbz", "pdf"):
        assert can_write(fid, "linux")
        assert can_write(fid, "win32")
        assert can_write(fid, "darwin")


def test_platform_gated_write():
    register_capability(Capability(
        "heic_test", read=True, write=True,
        write_platforms=frozenset({"darwin", "ios"})))
    assert can_write("heic_test", "darwin")
    assert not can_write("heic_test", "win32")


def test_available_write_formats_filters_by_platform():
    register_capability(Capability(
        "ios_only", read=True, write=True,
        write_platforms=frozenset({"ios"})))
    assert "ios_only" not in available_write_formats("linux")
    assert "ios_only" in available_write_formats("ios")
    assert "pdf" in available_write_formats("linux")


def test_unknown_format_not_writable():
    assert not can_write("does_not_exist", "linux")
