"""Converter registry (spec PC-1).

Three self-registration tables drive the whole pipeline so it never branches on
file extension by hand:

    detectors  signature/extension -> source_type id
    decoders   source_type id      -> Decoder   (produces an Intermediate)
    encoders   format id           -> Encoder   (consumes an Intermediate)

Handlers register via the ``@register_*`` decorators at import time. The module
loader (spec PC-6) decides which handler modules are imported for a given build,
so excluding a module simply means its handlers never register — the core and
other modules are unaffected.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional

from .intermediates import Kind


class Decoder:
    """Turns a source path into one Intermediate.

    Subclasses set ``source_type`` and implement ``decode(source, cancel_check)``.
    """
    source_type: str = ""

    def decode(self, source, cancel_check=None):  # pragma: no cover - interface
        raise NotImplementedError


class Encoder:
    """Builds output from one Intermediate kind.

    Subclasses set ``format_id``, ``extension``, ``accepts`` (a Kind) and
    implement ``build(intermediate, filename, output_dir, profile, cancel_check)``.
    """
    format_id: str = ""
    extension: str = ""
    accepts: Optional[Kind] = None

    def build(self, intermediate, filename, output_dir, profile=None,
              cancel_check=None):  # pragma: no cover - interface
        raise NotImplementedError


class Registry:
    def __init__(self):
        self._detectors: List[Callable] = []
        self._decoders: Dict[str, Decoder] = {}
        self._encoders: Dict[str, Encoder] = {}

    # --- registration -------------------------------------------------------
    def register_detector(self, fn: Callable) -> Callable:
        """A detector is ``fn(head: bytes, ext: str) -> Optional[str]`` returning
        a source_type id when it recognises the input, else None."""
        self._detectors.append(fn)
        return fn

    def register_decoder(self, decoder: Decoder) -> Decoder:
        if not decoder.source_type:
            raise ValueError("Decoder must declare a source_type")
        self._decoders[decoder.source_type] = decoder
        return decoder

    def register_encoder(self, encoder: Encoder) -> Encoder:
        if not encoder.format_id:
            raise ValueError("Encoder must declare a format_id")
        if encoder.accepts is None:
            raise ValueError(f"Encoder {encoder.format_id} must declare 'accepts'")
        self._encoders[encoder.format_id] = encoder
        return encoder

    # --- lookup -------------------------------------------------------------
    def detect(self, head: bytes, ext: str = "") -> Optional[str]:
        for fn in self._detectors:
            result = fn(head, ext)
            if result:
                return result
        return None

    def decoder_for(self, source_type: str) -> Optional[Decoder]:
        return self._decoders.get(source_type)

    def encoder_for(self, format_id: str) -> Optional[Encoder]:
        return self._encoders.get(format_id)

    def encoders(self) -> Dict[str, Encoder]:
        return dict(self._encoders)

    def reset(self):
        """Test helper: clear all registrations."""
        self._detectors.clear()
        self._decoders.clear()
        self._encoders.clear()


# Process-wide default registry plus decorator-style helpers.
registry = Registry()


def detector(fn):
    return registry.register_detector(fn)


def decoder(cls):
    """Class decorator: instantiate and register a Decoder subclass."""
    registry.register_decoder(cls())
    return cls


def encoder(cls):
    """Class decorator: instantiate and register an Encoder subclass."""
    registry.register_encoder(cls())
    return cls
