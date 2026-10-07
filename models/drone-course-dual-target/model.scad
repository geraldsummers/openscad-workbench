include <BOSL2/std.scad>

opening_diameter = 96;
target_spacing = 108;
frame_width = 12;
frame_depth = 12;
target_center_height = 62;
base_width = 244;
base_depth = 32;
base_thickness = 4;
screw_hole_diameter = 4.5;
screw_spacing = 210;
facet_count = 128;

outer_diameter = opening_diameter + 2 * frame_width;
overall_width = target_spacing + outer_diameter;
overall_height = target_center_height + outer_diameter / 2;

assert(target_spacing < outer_diameter, "The two target frames must overlap into one solid");
assert(target_spacing > opening_diameter, "A solid bridge must remain between the openings");
assert(frame_width >= 10 && target_center_height - outer_diameter / 2 < base_thickness, "The frame must overlap the mounting rail");
assert(base_width > overall_width && base_depth > frame_depth, "The mounting rail must project beyond the targets");
assert(screw_spacing / 2 + screw_hole_diameter / 2 + 4 < base_width / 2, "Each screw hole needs a safe edge margin");
assert(base_width <= 270 && base_depth <= 270 && overall_height <= 256, "The model must fit the workbench envelope");
echo("SCADCTL_REQUIREMENT:parameters:PASS");

module extrude_y(depth) {
    rotate([90, 0, 0])
        linear_extrude(height=depth, center=true, convexity=10)
            children();
}

difference() {
    union() {
        extrude_y(frame_depth)
            difference() {
                union()
                    for (x = [-target_spacing / 2, target_spacing / 2])
                        translate([x, target_center_height])
                            circle(d=outer_diameter, $fn=facet_count);
                for (x = [-target_spacing / 2, target_spacing / 2])
                    translate([x, target_center_height])
                        circle(d=opening_diameter, $fn=facet_count);
            }
        cuboid([base_width, base_depth, base_thickness], anchor=BOTTOM);
    }
    for (x = [-screw_spacing / 2, screw_spacing / 2])
        translate([x, 0, -0.1])
            cylinder(h=base_thickness + 0.2, d=screw_hole_diameter, $fn=48);
}
