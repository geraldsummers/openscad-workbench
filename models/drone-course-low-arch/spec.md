# Low arch specification

## Requirements

- [overall-size] Overall dimensions are 244 x 32 x 178 mm: mesh-verified by `model.toml`.
- [parameters] The 200 x 150 mm arch opening, frame, rail, and screw margins remain valid: source-verified by OpenSCAD assertions and a pass marker.
- [clear-opening] The lower central flight passage remains unobstructed through the arch: mesh-verified with a void occupancy probe.
- [mounting-holes] Both plain 4.5 mm mounting holes pass completely through the base: mesh-verified with a void occupancy probe.
- [left-right-symmetry] The arch and mounting rail are left-right symmetric: mesh-verified by mirrored-volume comparison.
- [intended-shape] One low semicircular arch joins cleanly to a two-hole mounting rail: visually verified in all ten standard views.

## Use

This is one option in a screw-mounted course for 65-85 mm ducted tiny-whoop drones. Print any subset; print the weave post in multiples to form a slalom.

## Exclusions

Screw selection, baseboard thickness, collision safety, fabricated durability, slicing, material, nozzle, support, overhang, and toolpath assessment are out of scope.
