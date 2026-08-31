# Workspace bridge specification

## Requirements

- [overall-size] Overall dimensions are 80 x 30 x 24 mm: mesh-verified by `model.toml`.
- [parameter-safety] The named dimensions preserve a valid corner radius, narrower tunnel, and continuous crown: source-verified by OpenSCAD assertions and a pass marker.
- [left-right-symmetry] The bridge is symmetric across its left-right center plane: mesh-verified by mirrored-volume comparison.
- [open-tunnel] A clear void passes through the full depth at the center of the bridge: mesh-verified with a void occupancy probe.
- [intended-shape] The result is one upright rounded bridge with two legs, a smooth centered arch, and no unintended features: visually verified in all eight views.

## Exclusions

This is a workspace demonstration object, not a fit-critical functional part. Slicing, material, nozzle, support, overhang, and toolpath assessment are out of scope.
