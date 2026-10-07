include <BOSL2/std.scad>

opening_width = 200;
opening_height = 200;
inner_corner_radius = 10;
frame_width = 12;
frame_depth = 8;
base_width = 244;
base_depth = 32;
base_thickness = 4;
screw_hole_diameter = 4.5;
screw_spacing = 210;

outer_width = opening_width + 2 * frame_width;
outer_height = opening_height + 2 * frame_width;
outer_corner_radius = inner_corner_radius + frame_width;

assert(opening_width > 0 && opening_height > 0, "The gate opening must be positive");
assert(inner_corner_radius > 0 && inner_corner_radius < min(opening_width, opening_height) / 2, "The inner corner radius must fit");
assert(frame_width >= 10 && frame_depth > 0, "The frame dimensions must remain substantial");
assert(base_width > outer_width && base_depth > frame_depth, "The mounting rail must project beyond the frame");
assert(screw_spacing / 2 + screw_hole_diameter / 2 + 4 < base_width / 2, "Each screw hole needs a safe edge margin");
assert(base_width <= 270 && base_depth <= 270 && outer_height <= 256, "The model must fit the workbench envelope");
echo("SCADCTL_REQUIREMENT:parameters:PASS");

module extrude_y(depth) {
    rotate([90, 0, 0])
        linear_extrude(height=depth, center=true, convexity=10)
            children();
}

difference() {
    union() {
        translate([0, 0, outer_height / 2])
            extrude_y(frame_depth)
                difference() {
                    rect([outer_width, outer_height], rounding=outer_corner_radius);
                    rect([opening_width, opening_height], rounding=inner_corner_radius);
                }
        cuboid([base_width, base_depth, base_thickness], anchor=BOTTOM);
    }
    for (x = [-screw_spacing / 2, screw_spacing / 2])
        translate([x, 0, -0.1])
            cylinder(h=base_thickness + 0.2, d=screw_hole_diameter, $fn=48);
}
