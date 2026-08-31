# OpenSCAD Workbench

[![CI](https://github.com/geraldsummers/openscad-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/geraldsummers/openscad-workbench/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Describe the part you want. Your AI coding agent writes the OpenSCAD model,
checks the resulting geometry, visually inspects it from ten angles, and shows
you the full-resolution results.**

OpenSCAD Workbench is an environment for AI-assisted parametric CAD. Instead of
manually translating every idea into OpenSCAD, you can give a compatible agent
a natural-language request such as:

> Make me a 70 × 30 × 4 mm mounting plate with rounded corners and two M4
> clearance holes, centered 10 mm from either end.

The repository's [`AGENTS.md`](AGENTS.md) gives the agent a concrete modeling
contract, while `scadctl` supplies deterministic export and verification tools.
The agent is expected to clarify missing critical dimensions, create or revise
the SCAD source, correct failed checks, inspect every render, and hand back the
SCAD, STL, 3MF, verification report, and human-facing preview workspace.

```text
your request
    ↓
AI agent → requirements + parametric OpenSCAD source
    ↓
scadctl → STL/3MF export + source assertions + mesh checks
    ↓
AI inspection → ten full-resolution views, including underside isometrics
    ↓
Herdr → one native image tab per angle for your review
```

It is designed for brackets, adapters, enclosures, fixtures, replacement parts,
and other dimensioned single-solid models that can be expressed in OpenSCAD.
It does not pretend that software-only checks prove printability, strength, fit,
or safety: those claims still require slicing, material decisions, measurements,
and physical testing.

## Use it with an AI agent

Clone and bootstrap the workbench, then open the repository in an AI coding
agent that follows `AGENTS.md`. Ask for the model in ordinary language and
include the dimensions, fit relationships, and intended orientation you know.

For example:

```text
Design a wall-mountable holder for a 42 mm diameter cylinder. Make the back
plate 80 × 60 × 5 mm, use four M4 clearance holes on a 60 × 40 mm pattern,
and leave 0.5 mm radial clearance around the cylinder. Verify it and show me
every angle.
```

The expected agent workflow is:

1. Resolve missing dimensions that materially affect the design.
2. Record the request as stable, testable requirements.
3. Write a parametric `model.scad` and source assertions.
4. Run `scadctl verify`, diagnose failures, and iterate until technical checks
   pass.
5. Inspect all ten original 1600×1200 views and record concrete visual evidence.
6. Present each angle in its own aspect-correct native Herdr tab.
7. Hand off editable source, STL, 3MF, previews, and the verification report.

## Quick start

The bootstrap currently supports Linux on x86-64 and installs its pinned
OpenSCAD snapshot, BOSL2 library, and Python environment in user space. It
requires Python 3.13, `curl`, `dpkg-deb`, `tar`, `zsh`, and Xvfb.

```sh
git clone https://github.com/geraldsummers/openscad-workbench.git
cd openscad-workbench
scripts/bootstrap
```

You can also drive the underlying workflow manually:

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

### What “verified” means

The workbench can establish that the exported mesh is manifold, consists of one
connected body, matches declared bounds and sections, rests on Z=0, fits the
configured build envelope, and agrees between STL and 3MF exports. It also binds
an agent's structured visual inspection and the human preview presentation to
the exact artifact digest.

Verification does **not** establish structural strength, tolerances on a real
printer, ergonomics, regulatory compliance, material suitability, support
requirements, or successful fabrication. The agent must label those as physical
or downstream validation instead of presenting them as proven.

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
