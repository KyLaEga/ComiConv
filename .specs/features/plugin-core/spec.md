# Feature: Plugin Core

Critical-path architecture that turns ComiConv from a hardcoded comic converter into a registry-
driven universal converter. Enables cheap addition of Wave 1 formats and deferred attachment of
Wave 2 heavy plugins — without rewriting the core.

Scope: **desktop (Python)** primary; **mobile (Dart)** mirrors the same model (it is already
halfway there via `OutputFormat`/`ComicSource`).

## Requirements

- **PC-1 — Converter registry.** A registry maps `(source_type, output_format_id) → handler`.
  Handlers self-register; the pipeline never branches on file extension by hand.

- **PC-2 — Typed intermediates.** Define a small set of intermediate payload types the pipeline
  passes between stages: `ImageSet`, `Document`, `Archive`, `TextData`, `ByteStream`.
  A source decodes to one intermediate; an output format consumes one intermediate.

- **PC-3 — Signature detection.** Real file type is determined by magic bytes via registry-driven
  detectors, ignoring the file extension. Falls back to extension only when no signature matches.

- **PC-4 — Conversion graph.** Given a source intermediate and a target format, resolve a direct
  handler, else a chained path A→X→B over registered handlers. No path → clear, surfaced error.

- **PC-5 — Capability manifest.** A per-platform manifest declares which `(format, direction)` pairs
  are available (e.g. HEIC write: iOS yes, Android/Windows no). The registry consults it; the UI
  hides/greys unavailable targets instead of failing at runtime.

- **PC-6 — Modular registration.** Codec/format modules register via an entry-point/plugin
  mechanism so a build can include or exclude module groups. Heavy (Wave 2) modules are excludable
  from the base build; excluding one must not break the core or other modules.

- **PC-7 — Unified task profile.** A single "conversion profile" (target format + quality/compression
  + resize + flags) applies across ALL source types, not just images — so batch profiling works for
  archives, documents, text, etc.

- **PC-8 — Backward compatibility.** Existing behavior (CBZ/ZIP/PDF in, CBZ/ZIP/PDF out, loose-image
  merge, natural sort, Zip-Slip-safe extraction, sandbox cleanup, cancel checks) is preserved and
  re-expressed through the registry. No regression in current conversions.

- **PC-9 — Memory & cancellation contract.** Handlers honor the existing streaming/thread-limit and
  `cancel_check` / `isCancelled` contracts, and temp dirs are cleaned on completion AND cancel.

## Out of scope (this feature)
- Implementing the actual Wave 1 format handlers (that is Milestone 1) — here we only provide the
  framework + migrate the existing handlers as the first registry citizens.
- Any Wave 2 heavy module implementation.

## Acceptance
- All current conversions pass through the registry with no behavioral regression (PC-8).
- Adding a hypothetical new format = registering one handler + manifest entry, with **zero** edits
  to pipeline/dispatch code (demonstrated by a trivial sample handler in tests).
- A heavy module can be excluded at build time and the base build still runs (PC-6).
</content>
