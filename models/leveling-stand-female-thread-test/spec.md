# Leveling stand female-thread test coupon specification

## Requirements

- [overall-size] The coupon is 30 mm diameter by 20 mm tall, matching one platform outrigger boss: mesh-verified by `model.toml`.
- [coupon-parameters] The internal thread is the next controlled candidate: Tr18×2, 30° trapezoidal profile, 1 mm modeled depth, 1.2 mm diametric clearance, and BOSL2 `$slop` 0.30: source-verified by OpenSCAD assertions and a pass marker.
- [through-thread] The female thread passes through the full 20 mm coupon height: source-verified by an OpenSCAD assertion and a pass marker.
- [open-bottom] The threaded socket has a clear entrance through the bottom: mesh-verified with a void occupancy probe.
- [open-top] The threaded socket exits through the top: mesh-verified with a void occupancy probe.
- [coupon-shape] The part is one compact cylindrical female-thread coupon with a continuous open socket and no unintended features: visually verified in all ten views.

## Test use

The previous 1.0 mm-clearance coupon failed THR-004 with an ABS foot transformed to 99% XY in the slicer. This revision increased only female CAD diametric clearance by 0.2 mm. Physical trial THR-006 reported the resulting fit as “about perfect,” making it the project's first successful qualitative thread result. The nominal male CAD model and full platform remain unchanged; any 99% male transform belongs only in the slicer.

## Exclusions

This coupon tests fit only. THR-006 physically validates its fit qualitatively for the reported ABS and slicer-scaling configuration, but does not establish platform strength, loaded adjustment, surface grip, whole-assembly behavior, or transferability to other processes. Slicing, material, nozzle, support, overhang, and toolpath assessment are out of scope.
