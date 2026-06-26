"""T10 — acceptance: a new format plugs in with ZERO core edits (spec PC-1/PC-6).

Importing modules.tar_io is the ONLY thing needed to make 'tar' a usable target;
no pipeline/registry/orchestration file was touched to add it.
"""
import tarfile

import pytest

from core.capabilities import can_write
from core.registry import registry


def test_tar_format_registers_on_import():
    import modules.tar_io  # noqa: F401 — import IS the registration
    assert registry.encoder_for("tar") is not None
    assert can_write("tar", "linux")


def test_tar_encoder_produces_archive(cbz_file, tmp_path):
    import modules.tar_io  # noqa: F401
    from core.loader import load_base_modules
    load_base_modules()

    img_set = registry.decoder_for("cbz").decode(str(cbz_file[0]))
    try:
        out = registry.encoder_for("tar").build(img_set, "out", str(tmp_path))
        assert out.exists() and out.suffix == ".tar"
        with tarfile.open(out) as tf:
            assert tf.getnames() == cbz_file[1]
    finally:
        import shutil
        shutil.rmtree(img_set.temp_dir, ignore_errors=True)
