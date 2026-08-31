# OpenSCAD workbench

## Modeling contract

- Treat OpenSCAD dimensions as millimetres.
- Keep each model in `models/<name>/` with `model.scad`, `model.toml`, and `spec.md`.
- Export exactly one connected solid. Separate physical parts belong in separate model directories.
- Require the solid to touch Z=0 within 0.01 mm and fit within 270 x 270 x 256 mm by extents.
- Use schema-v2 manifests and map every `[requirement-id]` in `spec.md` to a source, mesh, or visual `[[requirements]]` entry in `model.toml`.
- Run `scadctl verify MODEL`, inspect all ten original-resolution PNGs with the agent image-viewing tool, complete the generated inspection template, record it with `scadctl review MODEL --input FILE`, refresh the dedicated human-facing Herdr workspace with `scadctl present MODEL`, and finish with `scadctl status`.
- Presentation uses one persistent `OpenSCAD · <model>` workspace with ten angle tabs followed by Spec, Report, and Source. Populate it off-focus and focus Isometric Front only after every tab reports ready. Do not close the workspace automatically.
- Every angle tab must use Herdr `pane.graphics.set` with its original 1600×1200 PNG. Fit and center it using the reported cell pixel dimensions so its source aspect ratio is preserved. Do not substitute a contact-sheet overview, `timg`, or character-cell rendering; require successful native graphics acknowledgements for all ten tabs.
- Do not claim fabrication quality from geometry checks alone. This workbench does not slice or assess material, nozzle, supports, overhangs, or toolpaths.

## Toolchain inventory

- OpenSCAD 2026.08.30 snapshot, extracted AppImage under `$HOME/.local/opt/openscad/2026.08.30`; reproduce with `scripts/bootstrap`.
- BOSL2 v2.0.752 at commit `5b1f7b2d4344b75265324309e11c3c8e7f5cbb8b` under `$HOME/.local/share/OpenSCAD/libraries/BOSL2`; reproduce with `scripts/bootstrap`.
- Python 3.13 project virtual environment at `.venv`; reproduce with `scripts/bootstrap`.
- Herdr native pane graphics enabled in `$HOME/.config/herdr/config.toml` with `[experimental] kitty_graphics = true`; reload with `herdr server reload-config`.

## Checks

- Use `pytest` for focused verifier tests.
- Run `scripts/check` before handing off changes to the workbench.
