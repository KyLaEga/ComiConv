# Tasks: Plugin Core

Legend: `[P]` = parallelizable. Each task lists Done-when + Tests + Gate.
Desktop (Python) is the primary track; mobile (Dart) mirror tasks are marked `[M]`.

---

## T0 — Golden-output safety net  (PC-8)
- **What**: Capture current desktop conversion outputs (CBZ/ZIP/PDF in → CBZ/ZIP/PDF out, loose-image
  merge) as fixtures, with a test asserting byte/structure parity.
- **Where**: `tests/test_golden.py`, `tests/fixtures/`.
- **Reuses**: existing `OptimizedMediaConverter`.
- **Done when**: tests pass against current code and will catch regressions during refactor.
- **Tests**: golden comparison (page count, names, natural order, archive entries).
- **Gate**: `pytest` green.

## T1 — Intermediate types  (PC-2)
- **What**: Define `ImageSet`, `Document`, `Archive`, `TextData`, `ByteStream` payload classes.
- **Where**: `core/intermediates.py`.
- **Depends on**: T0.
- **Done when**: types model what `extract_and_prepare` returns today (ordered pages + temp dir).
- **Tests**: unit construction + ordering invariants.
- **Gate**: `pytest` green.

## T2 — Registry  (PC-1)
- **What**: `detectors`, `decoders`, `encoders` tables + register decorators + lookup API.
- **Where**: `core/registry.py`.
- **Depends on**: T1.
- **Done when**: handlers can self-register; lookups by source_type/format_id work.
- **Tests**: register + resolve unit tests; duplicate-registration handling.
- **Gate**: `pytest` green.

## T3 — Signature detection  (PC-3)
- **What**: Magic-byte detectors for current types (zip/cbz, pdf, jpg/png/webp/gif/bmp/tiff),
  registry-driven; extension fallback last.
- **Where**: `core/detect.py` + detectors registered for existing formats.
- **Depends on**: T2.
- **Done when**: a mislabeled file (e.g. .jpg that is really PNG) is detected correctly.
- **Tests**: detection table incl. wrong-extension cases.
- **Gate**: `pytest` green.

## T4 — Migrate existing decoders  (PC-8, PC-9)
- **What**: Re-express `extract_and_prepare` branches as registered decoders: ZIP/CBZ (Zip-Slip-safe),
  PDF→pixmap, dir, loose-image group. Preserve cancel_check + temp dir + cleanup contract.
- **Where**: `modules/images/`, `modules/pdf/`, `modules/archive/`.
- **Depends on**: T2, T3. `[P]` per decoder after the package skeleton exists.
- **Done when**: T0 golden tests still pass via the new decoders.
- **Tests**: T0 golden + per-decoder unit (cancel + cleanup).
- **Gate**: `pytest` green, golden parity.

## T5 — Migrate existing encoders + adapters  (PC-4, PC-8)
- **What**: `to_cbz/to_zip` → archive encoder; `to_pdf` → document encoder; register adapters
  `ImageSet→Document` (images→PDF) and `Document→ImageSet` (PDF render) as graph edges.
- **Where**: `modules/archive/`, `modules/pdf/`, `core/graph.py`.
- **Depends on**: T4.
- **Done when**: graph resolves image→pdf and pdf→images via edges; golden parity holds.
- **Tests**: graph resolution unit + golden.
- **Gate**: `pytest` green.

## T6 — Conversion profile  (PC-7)
- **What**: `ConversionProfile` (format, quality, resize, flags) threaded into every encoder.
- **Where**: `core/profile.py`; encoders accept it.
- **Depends on**: T5.
- **Done when**: a single profile object drives all encoders; defaults reproduce current output.
- **Tests**: profile defaults = current behavior; one non-default (resize) changes output.
- **Gate**: `pytest` green.

## T7 — Capability manifest  (PC-5)
- **What**: Declarative manifest `{format_id: {read, write, platforms}}`, resolved per platform;
  registry refuses gated targets.
- **Where**: `core/capabilities.py`, `core/capabilities.toml` (or py dict).
- **Depends on**: T2.  `[P]` with T6.
- **Done when**: gated write target is hidden from available formats on a platform that lacks it.
- **Tests**: manifest resolution per simulated platform.
- **Gate**: `pytest` green.

## T8 — Module loader  (PC-6)
- **What**: Entry-point group `comiconv.modules` (fallback explicit list); base build registers
  light modules only; a heavy module can be excluded without breaking core.
- **Where**: `core/loader.py`, `pyproject`/`ComiConv.spec` wiring.
- **Depends on**: T4, T5.
- **Done when**: removing a module package leaves base build runnable; sample heavy stub excludable.
- **Tests**: load-with / load-without module; exclusion smoke test.
- **Gate**: `pytest` green + app launches.

## T9 — Wire pipeline + UI to registry  (PC-1, PC-5)
- **What**: `main.py` flow calls registry/graph instead of direct methods; UI format list reads the
  manifest. Remove dead hardcoded branches.
- **Where**: `main.py`, `converter.py` (slimmed to orchestration).
- **Depends on**: T5, T6, T7, T8.
- **Done when**: full app runs end-to-end via registry; golden parity; no dead code.
- **Tests**: golden + manual run (`/run`).
- **Gate**: `pytest` green, app verified.

## T10 — Sample new-format proof  (Acceptance)
- **What**: Register a trivial new format handler (e.g. TIFF write or a no-op) touching ONLY a new
  module file + manifest entry — zero edits to pipeline/dispatch.
- **Where**: `modules/sample/`.
- **Depends on**: T9.
- **Done when**: new target appears and works with no core edits (proves PC-1/PC-6 acceptance).
- **Tests**: end-to-end convert into the sample format.
- **Gate**: `pytest` green.

---

## Mobile mirror (Dart) — after desktop validates the model
- **T-M1 [M]**: Generalize `OutputFormat`/`ComicSource` to `Encoder`/`Decoder` + Intermediate kinds.
- **T-M2 [M]**: Registry + static module registrars; heavy modules behind build flag.
- **T-M3 [M]**: Capability manifest shared concept; gate UI in `home_screen.dart`.
- Keep concept names identical to desktop (see design.md mapping).

## Suggested execution order
T0 → T1 → T2 → T3 → (T4 ∥ ) → T5 → (T6 ∥ T7) → T8 → T9 → T10 → mobile mirror.
</content>
