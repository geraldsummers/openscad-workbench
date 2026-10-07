# Weave post specification

## Requirements

- [overall-size] Overall dimensions are 70 x 34 x 220 mm: mesh-verified by `model.toml`.
- [parameters] The 220 mm post, flared reinforcement, foot, and screw margins remain valid: source-verified by OpenSCAD assertions and a pass marker.
- [mounting-holes] Both plain 4.5 mm mounting holes pass completely through the base: mesh-verified with a void occupancy probe.
- [left-right-symmetry] The post and mounting foot are left-right symmetric: mesh-verified by mirrored-volume comparison.
- [intended-shape] One slender weave post rises from a reinforced, rounded two-hole mounting foot: visually verified in all ten standard views.

## Use

This is one option in a screw-mounted course for 65-85 mm ducted tiny-whoop drones. Print any subset; print the weave post in multiples to form a slalom.

## Exclusions

Screw selection, baseboard thickness, collision safety, fabricated durability, slicing, material, nozzle, support, overhang, and toolpath assessment are out of scope.
