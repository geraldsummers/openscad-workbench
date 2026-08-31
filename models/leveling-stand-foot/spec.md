# Adjustable leveling stand foot specification

## Requirements

- [overall-size] The leveling foot is 40 x 40 x 31 mm: mesh-verified by `model.toml`.
- [foot-parameters] The broad sixteen-sided thumbwheel, 18 mm diameter by 2 mm pitch trapezoidal thread, connected 1 mm overlap, and 10–16 mm engagement limits obey their declared constraints: source-verified by OpenSCAD assertions and a pass marker.
- [upright-access] When installed at the 85 mm outrigger radius, the 40 mm thumbwheel projects 30 mm beyond the circular platform for tool-free upright adjustment: source-verified by OpenSCAD assertions and a pass marker.
- [flat-contact] The pad underside contains a broad, solid, flat contact region: mesh-verified with a solid occupancy probe.
- [thread-profile] The shaft has a continuous right-handed 18 mm by 2 mm BOSL2 trapezoidal external thread: visually verified in the four elevation and two isometric views.
- [foot-shape] The part is one leveling foot with a broad flat sixteen-sided side-access thumbwheel, connected shaft, and beveled thread tip: visually verified in all eight views.

## Assembly

Print three identical copies. Thread each foot into one outrigger socket in `leveling-stand-platform`, keeping at least 10 mm engaged. The sixteen-sided 40 mm wheel is both the side-access hand grip and the supporting-surface contact.

## Exclusions

The fixed 0.6 mm diametric mating clearance is encoded in the platform. Actual fit, surface grip, stiffness, and load capacity require physical testing. Slicing, material, nozzle, support, overhang, and toolpath assessment are out of scope.
