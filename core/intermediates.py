"""Typed intermediate payloads passed between pipeline stages (spec PC-2).

A decoder turns a source into exactly one Intermediate; an encoder consumes
exactly one Intermediate. Adapters convert one Intermediate kind into another
(these are the edges of the conversion graph, see core.graph).

The kinds mirror the scenarios the converter actually serves:
    ImageSet    ordered pages (the comic/merge case, today's core)
    Document    a paged document such as PDF
    Archive     a tree of named entries (zip/cbz/tar/7z)
    TextData    text or structured rows/markup (md/html/csv/json/yaml)
    ByteStream  opaque passthrough when no richer model is needed

Each carries an optional ``temp_dir`` so the pipeline can clean up extracted
files on completion AND cancellation, preserving today's sandbox contract
(spec PC-9).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Kind(Enum):
    IMAGE_SET = "image_set"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    TEXT_DATA = "text_data"
    BYTE_STREAM = "byte_stream"


@dataclass
class Intermediate:
    """Base payload. ``temp_dir`` is owned by the pipeline, not the producer."""
    kind: Kind = field(init=False)
    temp_dir: Optional[Path] = None


@dataclass
class ImageSet(Intermediate):
    """Ordered image pages on disk. ``pages`` is already in final (natural) order.

    ``base_dir`` mirrors today's archive re-creation: when set, output encoders
    preserve the relative tree of each page beneath it.
    """
    pages: list = field(default_factory=list)
    name: str = "Images"
    base_dir: Optional[Path] = None

    def __post_init__(self):
        self.kind = Kind.IMAGE_SET
        self.pages = [Path(p) for p in self.pages]

    def __len__(self):
        return len(self.pages)


@dataclass
class Document(Intermediate):
    """A paged document file (e.g. PDF) referenced on disk."""
    path: Path = None
    page_count: int = 0
    name: str = "Document"

    def __post_init__(self):
        self.kind = Kind.DOCUMENT
        if self.path is not None:
            self.path = Path(self.path)


@dataclass
class ArchiveEntry:
    arcname: str
    path: Path


@dataclass
class Archive(Intermediate):
    """A tree of named entries destined for / extracted from a container."""
    entries: list = field(default_factory=list)
    name: str = "Archive"

    def __post_init__(self):
        self.kind = Kind.ARCHIVE


@dataclass
class TextData(Intermediate):
    """Text or structured data. ``rows`` is set for tabular formats (csv/json),
    otherwise ``text`` holds raw text/markup. ``subtype`` disambiguates
    (e.g. 'markdown', 'html', 'csv', 'json', 'yaml')."""
    text: str = ""
    rows: Optional[list] = None
    subtype: str = "text"
    name: str = "Text"

    def __post_init__(self):
        self.kind = Kind.TEXT_DATA


@dataclass
class ByteStream(Intermediate):
    """Opaque bytes passthrough."""
    data: bytes = b""
    name: str = "Bytes"

    def __post_init__(self):
        self.kind = Kind.BYTE_STREAM
