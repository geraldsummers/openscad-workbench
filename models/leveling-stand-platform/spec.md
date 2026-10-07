# Adjustable leveling stand platform specification

## Requirements

- [overall-size] The platform with its fixed outriggers is approximately 177.224 x 175 x 20 mm: mesh-verified by `model.toml`.
- [platform-parameters] Three reinforced arms and 30 mm threaded bosses lie on a 170 mm pitch circle, spaced 120 degrees apart; every arm overlaps both the circular platform and its boss, and the sockets use 1.2 mm diametric thread clearance: source-verified by OpenSCAD assertions and a pass marker.
- [adjustment-range] The operating engagement range remains 10 to 16 mm, producing 6 mm of independent leveling travel: source-verified by OpenSCAD assertions and a pass marker.
- [outrigger-access] With the 40 mm mating wheels installed, the assembly has a 210 mm maximum radial envelope and each wheel projects 30 mm beyond the circular platform: source-verified by OpenSCAD assertions and a pass marker.
- [coplanar-top] The circular platform, all three outrigger arms, and all three boss top faces terminate at the same 20 mm plane around the thread openings: source-verified by OpenSCAD assertions and a pass marker.
- [through-threads] Each threaded socket passes completely through its 20 mm outrigger boss: source-verified by OpenSCAD assertions and a pass marker.
- [open-thread-socket] The forward outrigger boss has a clear threaded entrance from below: mesh-verified with a void occupancy probe.
- [thread-exit] The forward threaded socket exits through the coplanar outrigger top: mesh-verified with a void occupancy probe.
- [solid-flat-top] The central circular platform top remains solid and uninterrupted: mesh-verified with a solid occupancy probe.
- [platform-shape] The part is one circular, completely flat-topped platform with three fixed reinforced outriggers, through-threaded top openings, and no unintended features: visually verified in all ten views.

## Assembly

Print this platform once and `leveling-stand-foot` three times. Thread one foot into each outrigger boss and maintain at least 10 mm of engagement. Each 40 mm wheel extends 30 mm beyond the circular platform, allowing tool-free side adjustment while the stand remains upright. Turning a foot clockwise as viewed from below lowers that corner; counterclockwise raises it. With the revised 18 mm-tall wheels, the nominal top height is 47 to 53 mm.

The platform, arms, and boss top faces provide one coplanar plane when the part is inverted, interrupted only by the three intended through-thread openings. Whether that orientation requires slicer-generated supports remains dependent on the chosen process and is not asserted by this model.

## Exclusions

Physical trial THR-004 in `../../RESEARCH.md` found a 99%-XY slicer-transformed ABS screw slightly too tight with 1.0 mm female clearance. THR-006 found the same screw “about perfect” with a 1.2 mm-clearance coupon, so this platform now promotes that female clearance as pending full-platform trial THR-007. The CAD male remains nominal; 99% XY remains a slicer-side process variable. The intended scale is a centered 1–3 kg light-duty load, while whole-platform thread consistency, surface grip, stiffness, and load capacity require further physical testing. Slicing, material, nozzle, support, overhang, and toolpath assessment are out of scope.
