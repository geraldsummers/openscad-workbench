include <BOSL2/std.scad>

opening_width = 200;
opening_height = 150;
frame_width = 12;
frame_depth = 8;
base_width = 244;
base_depth = 32;
base_thickness = 4;
screw_hole_diameter = 4.5;
screw_spacing = 210;
facet_count = 160;

inner_radius = opening_width / 2;
straight_height = opening_height - inner_radius;
spring_height = base_thickness + frame_width + straight_height;
outer_radius = inner_radius + frame_width;
overall_height = spring_height + outer_radius;

assert(opening_width > 0 && opening_height > opening_width / 2, "The arch needs positive straight sides beneath its semicircle");
assert(frame_width >= 10 && frame_depth > 0, "The frame dimensions must remain substantial");
assert(base_width > opening_width + 2 * frame_width && base_depth > frame_depth, "The mounting rail must project beyond the arch");
assert(screw_spacing / 2 + screw_hole_diameter / 2 + 4 < base_width / 2, "Each screw hole needs a safe edge margin");
assert(overall_height <= 256 && base_width <= 270 && base_depth <= 270, "The model must fit the workbench envelope");
echo("SCADCTL_REQUIREMENT:parameters:PASS");

module upper_half_circle(radius, center_z) {
    intersection() {
        translate([0, center_z]) circle(r=radius, $fn=facet_count);
        translate([-radius, center_z]) square([2 * radius, radius + 0.01]);
    }
}

module arch_profile() {
    difference() {
        union() {
            translate([-(inner_radius + frame_width), 0])
                square([2 * (inner_radius + frame_width), spring_height]);
            upper_half_circle(outer_radius, spring_height);
        }
        union() {
            translate([-inner_radius, base_thickness + frame_width])
                square([2 * inner_radius, straight_height + 0.01]);
            upper_half_circle(inner_radius, spring_height);
        }
    }
}

module extrude_y(depth) {
    rotate([90, 0, 0])
        linear_extrude(height=depth, center=true, convexity=10)
            children();
}

difference() {
    union() {
        extrude_y(frame_depth) arch_profile();
        cuboid([base_width, base_depth, base_thickness], anchor=BOTTOM);
    }
    for (x = [-screw_spacing / 2, screw_spacing / 2])
        translate([x, 0, -0.1])
            cylinder(h=base_thickness + 0.2, d=screw_hole_diameter, $fn=48);
}
