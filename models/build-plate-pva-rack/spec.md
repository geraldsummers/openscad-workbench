# Build-plate PVA rack specification

## Requirements

- [overall-size] The rack is exactly 270 x 270 x 14 mm: mesh-verified by `model.toml`.
- [ground-clearance] The underside of every horizontal frame and grid member begins exactly 10 mm above the table: source-verified by OpenSCAD assertions and a pass marker.
- [open-clearance] A representative grid cell remains empty through the 10 mm space beneath the rack: mesh-verified with a void occupancy probe.
- [triangular-lattice] Three families of 5 mm ribs, separated by 60 degrees and repeated on a 45 mm cadence, form a triangular lattice intended to resist in-plane shear and twisting better than the prior square grid: source-verified by OpenSCAD assertions and a pass marker; comparative fabricated stiffness remains unverified.
- [nine-foot-support] Nine feet form a 3 x 3 layout at the corners, edge centers, and rack center: source-verified by OpenSCAD assertions and a pass marker.
- [reinforced-attachments] Each foot flares from a 28 x 28 mm table contact to a 42 x 42 mm deck attachment beneath a matching full-thickness support node: source-verified by OpenSCAD assertions and a pass marker.
- [center-support] The center foot forms continuous solid support from Z=0 to the grid underside: mesh-verified with a solid occupancy probe.
- [flat-unobstructed-top] All frame and grid top faces end on the same Z=14 plane without lips, tabs, or other raised locating features: source-verified by OpenSCAD assertions and a pass marker.
- [intended-shape] The rack is one connected square perimeter-and-triangular-lattice structure with regular openings, nine broadly attached flared feet, and no unintended panels or raised features: visually verified in all ten standard views.

## Intended use

Place one 270 x 270 mm build plate flat on the coplanar frame and lattice while applying PVA. The triangulated deck distributes ordinary hand pressure, while the flared nine-foot arrangement spreads each attachment into a broad support node and keeps substantial open space beneath the plate.

## Exclusions

Load certification, fabricated stiffness, surface grip, and fit on a physical printer bed require real-world testing. Slicing, material, nozzle, support, overhang, and toolpath assessment are out of scope.
