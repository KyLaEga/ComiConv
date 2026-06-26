# ComiConv — State (persistent memory)

## Decisions
- **2026-06-26** — Pivot to universal converter; two-wave scope; heavy formats deferred but
  plug-in point designed now. (See PROJECT.md boundary rule.)
- **2026-06-26** — Mobile already has proto-plugin shape (`OutputFormat`, `ComicSource`); adopt and
  generalize it as the cross-repo model. Desktop monolith (`converter.py`
  `OptimizedMediaConverter`) to be refactored toward a registry.
- **2026-06-26** — CBR/RAR and DJVU are **read-only**; never write (unrar licensing).
- **2026-06-26** — HEIC/animated-GIF are **read-first**; write is asymmetric and platform-gated.

## Progress — feature/plugin-core branch
- T0 done: golden tests (`tests/`), + fixed macOS Zip-Slip false-positive in `converter.py`.
- T1 done: `core/intermediates.py`.
- T2 done: `core/registry.py`.
- T3 done: `core/detect.py` (magic bytes + extension fallback).
- T4 done: `modules/{archive_io,pdf_io,image_io}.py` decoders, golden parity.
- T5 done: encoders + `core/graph.py` adapter graph (PDF<->images edges).
- T8 seeded: `core/loader.py` base-module loading.
- T6 done: `core/profile.py`. T7 done: `core/capabilities.py`.
- T9 done: `converter.py` rewritten as an orchestration shim over the registry;
  UI (`main.py`) untouched, golden parity holds, end-to-end smoke passes.
- T10 done: `modules/tar_io.py` proves a new format plugs in with ZERO core edits.
- 44 tests pass. REMAINING: wire UI format list to capability manifest (deferred, low value
  now — 3 static formats all writable everywhere); T8 build-exclusion smoke test; mobile mirror.

## Blockers
- (none yet)

## Lessons
- Desktop converter currently hardcodes `valid_extensions` and per-format methods
  (`to_cbz/to_zip/to_pdf`) — this is the main thing the registry refactor replaces.

## Todos / deferred ideas
- Decide office-extraction depth (XLSX→CSV confirmed; DOCX→Markdown vs plain text — open).
- Decide animation handling without FFmpeg (GIF↔APNG↔animated-WEBP) — open.
- AVIF encoder perf on mobile — validate before promising write support.

## Preferences
- (none recorded yet)
</content>
