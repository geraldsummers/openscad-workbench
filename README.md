# OpenSCAD Workbench

[![CI](https://github.com/geraldsummers/openscad-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/geraldsummers/openscad-workbench/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

OpenSCAD Workbench is a deterministic CLI and agent workflow for creating,
exporting, inspecting, and validating parametric single-solid OpenSCAD models.
It combines source assertions, mesh analysis, ten-angle rendering, structured
visual review, and native full-resolution presentation in Herdr.

## Quick start

The bootstrap currently supports Linux on x86-64 and installs its pinned
OpenSCAD snapshot, BOSL2 library, and Python environment in user space. It
requires Python 3.13, `curl`, `dpkg-deb`, `tar`, `zsh`, and Xvfb.

```sh
git clone https://github.com/geraldsummers/openscad-workbench.git
cd openscad-workbench
scripts/bootstrap
```

Then create and validate a model:

```sh
scadctl new bracket
scadctl verify bracket
# Inspect and complete build/inspection-template.json, saving it as inspection.json.
scadctl review bracket --input inspection.json
scadctl present bracket
scadctl status bracket
```

## Verification workflow

`verify` writes STL, 3MF, ten 1600×1200 rendered views, a 3200×1920 contact sheet made from 800×600 overview thumbnails, a digest-bound inspection template, and machine-readable and Markdown reports under the model's ignored `build/` directory. Schema-v2 manifests map every requirement to source, mesh, or visual evidence. After the agent inspects all views and submits the completed structured inspection, `present` creates or refreshes one dedicated `OpenSCAD · <model>` Herdr workspace. Each angle gets its original full-resolution PNG in a native image tab—top and underside front/rear isometrics plus Front, Rear, Left, Right, Top, and Bottom—followed by Spec, Report, and Source. Native placement uses the outer terminal's pixel cell dimensions to preserve the PNG aspect ratio and center it without stretching. No terminal block pixels are used. Native presentation requires `[experimental] kitty_graphics = true` and a graphics-capable Herdr attachment. Isometric Front is focused by default; use `--no-focus` to preserve focus.

`status` passes only when the technical checks, agent visual review, and Herdr presentation all refer to the current artifact digest. The presentation is for human review and does not require an explicit approval response.

The technical gate checks export consistency, topology, geometry, image integrity, declared dimensions, source assertions, symmetry, occupancy probes, and sections. It does not slice models or reason about materials, nozzles, supports, or toolpaths.

## Project layout

- `src/scadctl/` contains the CLI and verification pipeline.
- `models/` contains example model sources, manifests, specifications, and
  completed visual inspections.
- `scripts/bootstrap` installs the pinned user-space toolchain.
- `scripts/check` runs tests, shell checks, compilation, and environment checks.

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidance and
[SECURITY.md](SECURITY.md) for private vulnerability reporting.

## License

Released under the [MIT License](LICENSE).
