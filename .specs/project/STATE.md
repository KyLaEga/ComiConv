# ComiConv — State (persistent memory)

## Decisions
- **2026-06-26** — Pivot to universal converter; two-wave scope; heavy formats deferred but
  plug-in point designed now. (See PROJECT.md boundary rule.)
- **2026-06-26** — Mobile already has proto-plugin shape (`OutputFormat`, `ComicSource`); adopt and
  generalize it as the cross-repo model. Desktop monolith (`converter.py`
  `OptimizedMediaConverter`) to be refactored toward a registry.
- **2026-06-26** — CBR/RAR and DJVU are **read-only**; never write (unrar licensing).
- **2026-06-26** — HEIC/animated-GIF are **read-first**; write is asymmetric and platform-gated.

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
