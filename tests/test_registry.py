"""T2 — Registry registration + lookup (spec PC-1)."""
import pytest

from core.intermediates import ImageSet, Kind
from core.registry import Decoder, Encoder, Registry


def test_register_and_lookup_decoder():
    r = Registry()

    class Dummy(Decoder):
        source_type = "dummy"

        def decode(self, source, cancel_check=None):
            return ImageSet(pages=[])

    r.register_decoder(Dummy())
    assert isinstance(r.decoder_for("dummy"), Dummy)
    assert r.decoder_for("missing") is None


def test_register_and_lookup_encoder():
    r = Registry()

    class Out(Encoder):
        format_id = "x"
        extension = "x"
        accepts = Kind.IMAGE_SET

        def build(self, *a, **k):
            return None

    r.register_encoder(Out())
    assert r.encoder_for("x").extension == "x"
    assert "x" in r.encoders()


def test_decoder_requires_source_type():
    r = Registry()
    with pytest.raises(ValueError):
        r.register_decoder(Decoder())


def test_encoder_requires_format_and_accepts():
    r = Registry()

    class NoAccepts(Encoder):
        format_id = "y"
        extension = "y"

    with pytest.raises(ValueError):
        r.register_encoder(NoAccepts())


def test_detector_first_match_wins():
    r = Registry()
    r.register_detector(lambda head, ext: "png" if head[:1] == b"\x89" else None)
    r.register_detector(lambda head, ext: "always")
    assert r.detect(b"\x89PNG", ".bin") == "png"
    assert r.detect(b"xxxx", ".bin") == "always"


def test_reset_clears():
    r = Registry()
    r.register_detector(lambda h, e: "z")
    r.reset()
    assert r.detect(b"x") is None
