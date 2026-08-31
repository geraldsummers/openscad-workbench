# BOSL2 beacon specification

## Requirements

- [overall-size] Overall dimensions are 52 x 52 x 49 mm: mesh-verified by `model.toml`.
- [bosl-parameters] BOSL2 `cyl()` and `sphere()` dimensions preserve the intended taper, valid rounding and chamfer, and overlapping attachment joints: source-verified by OpenSCAD assertions and a pass marker.
- [radial-symmetry] The beacon is symmetric across its horizontal center planes: mesh-verified by mirrored-volume comparison.
- [intended-shape] The result is one upright beacon with a chamfered base, smooth tapered tower, spherical cap, and clean connected joints: visually verified in all eight views.

## Exclusions

This is a BOSL2 workspace demonstration object, not a fit-critical functional part. Slicing, material, nozzle, support, overhang, and toolpath assessment are out of scope.
