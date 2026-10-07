include <BOSL2/std.scad>

opening_width = 220;
opening_height = 110;
frame_width = 12;
frame_depth = 12;
base_width = 256;
base_depth = 32;
base_thickness = 4;
screw_hole_diameter = 4.5;
screw_spacing = 210;

outer_width = opening_width + 2 * frame_width;
overall_height = opening_height + frame_width;

assert(opening_width > 0 && opening_height > 0, "The limbo opening must be positive");
assert(frame_width >= 10 && frame_depth > 0, "The frame dimensions must remain substantial");
assert(base_width > outer_width && base_depth > frame_depth, "The mounting rail must project beyond the uprights");
assert(screw_spacing / 2 + screw_hole_diameter / 2 + 4 < base_width / 2, "Each screw hole needs a safe edge margin");
assert(base_width <= 270 && base_depth <= 270 && overall_height <= 256, "The model must fit the workbench envelope");
echo("SCADCTL_REQUIREMENT:parameters:PASS");

module limbo_profile() {
    union() {
        for (x = [-(opening_width + frame_width) / 2, (opening_width + frame_width) / 2])
            translate([x - frame_width / 2, 0])
                square([frame_width, overall_height]);
        translate([-outer_width / 2, opening_height])
            square([outer_width, frame_width]);
    }
}

module extrude_y(depth) {
    rotate([90, 0, 0])
        linear_extrude(height=depth, center=true, convexity=10)
            children();
}

difference() {
    union() {
        extrude_y(frame_depth) limbo_profile();
        cuboid([base_width, base_depth, base_thickness], anchor=BOTTOM);
    }
    for (x = [-screw_spacing / 2, screw_spacing / 2])
        translate([x, 0, -0.1])
            cylinder(h=base_thickness + 0.2, d=screw_hole_diameter, $fn=48);
}
