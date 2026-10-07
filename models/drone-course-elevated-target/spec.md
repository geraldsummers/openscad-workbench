# Elevated target specification

## Requirements

- [overall-size] Overall dimensions are 220 x 32 x 237 mm: mesh-verified by `model.toml`.
- [parameters] The 160 mm elevated opening, splayed supports, rail, and screw margins remain valid: source-verified by OpenSCAD assertions and a pass marker.
- [clear-opening] The 160 mm circular flight target remains unobstructed through the frame: mesh-verified with a void occupancy probe.
- [mounting-holes] Both plain 4.5 mm mounting holes pass completely through the base: mesh-verified with a void occupancy probe.
- [left-right-symmetry] The elevated target and splayed supports are left-right symmetric: mesh-verified by mirrored-volume comparison.
- [intended-shape] One elevated round target is supported by two clean splayed legs on a mounting rail: visually verified in all ten standard views.

## Use

This is one option in a screw-mounted course for 65-85 mm ducted tiny-whoop drones. Print any subset; print the weave post in multiples to form a slalom.

## Exclusions

Screw selection, baseboard thickness, collision safety, fabricated durability, slicing, material, nozzle, support, overhang, and toolpath assessment are out of scope.
