# High-poly sphere specification

## Requirements

- [overall-diameter] The sphere is 50 mm in diameter, mesh-verified on all axes.
- [positive-diameter] The diameter is positive, source-verified by an OpenSCAD assertion.
- [high-poly] The sphere uses 256 rotational facets for a high-poly surface, source-verified by an OpenSCAD assertion.
- [spherical-form] The model is a complete, smooth sphere with no clipping, holes, or unintended features, visually verified in all ten standard views.

## Assumptions

The unspecified size is set to a convenient 50 mm diameter. The sphere is translated upward so its lowest point touches Z=0.

## Exclusions

Slicing, material, nozzle, supports, overhangs, and toolpaths are out of scope.
