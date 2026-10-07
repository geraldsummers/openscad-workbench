# OpenSCAD Workbench — AI modeling instructions

Turn the user's natural-language part request into an editable, parametric
OpenSCAD model and evidence-backed exports. Clarify critical missing dimensions,
iterate on failed checks, visually inspect every required angle, and leave the
human-facing Herdr review workspace open. A request to “make,” “design,” or
“model” a part includes this complete workflow unless the user narrows the task.

## Modeling contract

- Treat OpenSCAD dimensions as millimetres.
- Model nominal design intent under ideal production by default. CAD dimensions
  may include functional relationships such as required running clearance, but
  must not silently include printer shrink factors, extrusion compensation,
  elephant-foot offsets, or slicer scaling.
- Keep manufacturing compensation in the slicer or fabrication process and
  record it as process context in `RESEARCH.md`; do not bake a reported slicer
  transform back into reusable CAD source.
- Material- or process-specific geometry is an exception, not a default. Use it
  only when the user requests it or physical evidence shows that geometry itself
  must change. Isolate it behind a named parameter or variant, document the
  rationale and applicable material/process, and preserve the nominal model.
- Keep each model in `models/<name>/` with `model.scad`, `model.toml`, and `spec.md`.
- Export exactly one connected solid. Separate physical parts belong in separate model directories.
- Require the solid to touch Z=0 within 0.01 mm and fit within 270 x 270 x 256 mm by extents.
- Use schema-v2 manifests and map every `[requirement-id]` in `spec.md` to a source, mesh, or visual `[[requirements]]` entry in `model.toml`.
- Run `scadctl verify MODEL`, inspect all ten original-resolution PNGs with the agent image-viewing tool, complete the generated inspection template, record it with `scadctl review MODEL --input FILE`, refresh the dedicated human-facing Herdr workspace with `scadctl present MODEL`, and finish with `scadctl status`.
- Presentation uses one persistent `OpenSCAD · <model>` workspace with ten angle tabs followed by Spec, Report, and Source. Populate it off-focus and focus Isometric Front only after every tab reports ready. Do not close the workspace automatically.
- Every angle tab must use Herdr `pane.graphics.set` with its original 1600×1200 PNG. Fit and center it using the reported cell pixel dimensions so its source aspect ratio is preserved. Do not substitute a contact-sheet overview, `timg`, or character-cell rendering; require successful native graphics acknowledgements for all ten tabs.
- Do not claim fabrication quality from geometry checks alone. This workbench does not slice or assess material, nozzle, supports, overhangs, or toolpaths.

## Research contract

- Treat every physical print report as research evidence. Read `RESEARCH.md`
  before changing a previously fabricated model, and update it whenever the user
  reports fit, failure, measurements, ergonomics, or other physical outcomes.
- Preserve trial history with stable IDs. Never erase or relabel an unsuccessful
  trial when revising the design; record the revision as a separate pending trial.
- Separate observations, measurements, and hypotheses. Do not infer printer
  settings, material, tolerances, or causes that were not reported. Mark missing
  context as `unknown` and ask for it only when it is material to the next decision.
- Record nominal thread form, pitch, handedness, modeled depth, internal
  clearance, BOSL2 `$slop`, engagement range, relevant geometry revision, process
  context, and outcome for mating-thread experiments.
- Keep nominal CAD parameters and downstream production transforms in separate
  research fields. A slicer-scaled specimen is evidence about that fabrication
  configuration, not authorization to scale the source model.
- Use `pass`, `fail`, `mixed`, or `pending` consistently. Software verification
  can move a CAD revision to geometrically verified, but only a physical result
  can establish fabricated fit or ergonomics.
- Prefer controlled, single-variable revisions and explicitly note confounders.
  Define the next evaluation and success criteria before calling a hypothesis
  validated. Report negative and mixed results with the same care as successes.
- Keep model `spec.md` exclusions synchronized with the research ledger and link
  research entries when they materially motivate the current parameters.
- When a material-aware CAD exception is necessary, state the evidence, scope,
  baseline nominal geometry, exceptional parameter or variant, and conditions
  under which the exception should be removed or re-evaluated.

## Toolchain inventory

- OpenSCAD 2026.08.30 snapshot, extracted AppImage under `$HOME/.local/opt/openscad/2026.08.30`; reproduce with `scripts/bootstrap`.
- BOSL2 v2.0.752 at commit `5b1f7b2d4344b75265324309e11c3c8e7f5cbb8b` under `$HOME/.local/share/OpenSCAD/libraries/BOSL2`; reproduce with `scripts/bootstrap`.
- Python 3.13 project virtual environment at `.venv`; reproduce with `scripts/bootstrap`.
- Herdr native pane graphics enabled in `$HOME/.config/herdr/config.toml` with `[experimental] kitty_graphics = true`; reload with `herdr server reload-config`.

## Checks

- Use `pytest` for focused verifier tests.
- Run `scripts/check` before handing off changes to the workbench.
