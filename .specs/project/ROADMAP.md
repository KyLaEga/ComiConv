# ComiConv — Roadmap

Priority scale: P0 (now / critical path) → P3 (later). Wave 2 = deferred heavy plugins.

## Milestone 0 — Plugin Core (P0, critical path) — feature `plugin-core`
The architecture that makes universality cheap. Must land before bulk format work.
- Converter registry: `(from_type, to_format) → handler`.
- Pipeline generalized from "comic/pages" to typed intermediates (image-set, document, archive,
  text/data, byte-stream).
- Conversion graph: direct A→B, or chained A→X→B.
- Per-platform capability manifest (e.g. HEIC write = iOS yes / Android no).
- Modular codec registration so heavy modules can be excluded from the base build.
- Signature (magic-byte) validation as a registry-driven detector.

## Milestone 1 — Wave 1 Core formats
Built on top of Milestone 0. Grouped by ROI.

### M1a — Graphics raster (P0)
JPEG, PNG, WEBP, HEIC(read), BMP, GIF(static), TIFF, AVIF.
Asymmetric: HEIC/animated-GIF read ≫ write.

### M1b — Documents-as-images (P0)
PDF ↔ images (incl. **Split PDF → images/CBZ**), CBZ/ZIP, DJVU(read), CBR(read, unrar — read-only, never write).

### M1c — Text & data (P1, high ROI / low weight)
Markdown/HTML/TXT → PDF; Markdown ↔ HTML; CSV ↔ JSON ↔ TSV ↔ YAML.

### M1d — Archives (P1)
ZIP ↔ TAR ↔ 7z; gzip/bzip2/xz; CB7/CBT.

### M1e — Office data extraction, NO layout (P2)
XLSX → CSV; DOCX → text/Markdown. (Explicitly NOT layout rendering.)

## Milestone 2 — Core UX improvements (folded into M1)
Natural sort (P0, exists), resize/downscale (P0), compression presets (P0), dry-run size preview
(P1), EXIF/ICC strip option (P1), session log report (P1), free-space precheck (P1), grayscale (P2).

## Milestone 3 — Wave 2 heavy plugins (deferred, separate modules)
- Office-with-layout → PDF (rendering engine). P3.
- Video/audio (FFmpeg module). P3.
- SVG rasterization. P2/P3.
- On-device AI upscale/OCR. P3.

Each attaches via Milestone 0's registry + modular build; none ships in the base binary.
</content>
