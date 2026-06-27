# ComiConv — Project Vision

## What
A **local, on-device, cross-platform batch file converter**. All computation runs strictly on the
target device — no data is sent to remote servers.

Name: **Com-** (from *Comic Converter*, extended to *Comprehensive*) + **Conv** (*Conversion*).

## Strategic pivot (2026-06)
Evolved from a comic-only converter (CBZ/CBR/PDF of images) into a **universal converter**, while
keeping the "lightweight, on-device, private" promise intact.

## Boundary rule (project law)
> Universal by **scenario**, not by every format.
> Add a format only if on-device conversion is **lightweight** AND produces a result
> **you're not ashamed of**.

This is the single criterion that gates every format decision. It is why office-with-layout
rendering and full video/audio transcoding are deliberately **out of the base product**.

## Two-wave scope
- **Wave 1 — Core**: everything convertible on-device with native/light libraries
  (raster graphics, PDF↔images, archives, text/data formats, office *data extraction*).
- **Wave 2 — Heavy plugins** (implemented later, kept OUT of the base binary):
  office-with-layout → PDF (rendering engine), video/audio (FFmpeg), SVG rasterization,
  on-device AI (upscale/OCR).

The heavy formats are deferred by **implementation**, but their **plug-in point is designed now**
(see feature `plugin-core`). Wave 2 must attach without rewriting the core.

## Repos
- **Desktop**: `KyLaEga/ComiConv` — Python 3 / PySide6, PyInstaller. (this repo)
- **Mobile**: Flutter (`../../Convertor`) — Android (iOS later).

Shared design language; separate implementations. Mobile already has a proto-plugin shape
(`OutputFormat.build`, `ComicSource.loadPages`); desktop is currently monolithic.

## Non-goals
- Cloud/remote processing of user data.
- Office documents with preserved layout in the base build.
- Full video/audio transcoding in the base build (FFmpeg size + GPL/patent/store risk).
- On-device AI models in the base build.
</content>
