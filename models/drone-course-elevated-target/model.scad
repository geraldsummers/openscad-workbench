include <BOSL2/std.scad>

opening_diameter = 160;
target_center_height = 145;
frame_width = 12;
frame_depth = 8;
support_width = 12;
support_base_spacing = 150;
support_top_spacing = 112;
base_width = 220;
base_depth = 32;
base_thickness = 4;
screw_hole_diameter = 4.5;
screw_spacing = 180;
facet_count = 144;

outer_diameter = opening_diameter + 2 * frame_width;
overall_height = target_center_height + outer_diameter / 2;

assert(opening_diameter > 0 && frame_width >= 10, "The target needs a positive opening and substantial frame");
assert(target_center_height > outer_diameter / 2, "The target must be elevated above the mounting rail");
assert(support_base_spacing > support_top_spacing && support_width > 0, "The supports must splay toward the base");
assert(screw_spacing / 2 + screw_hole_diameter / 2 + 4 < base_width / 2, "Each screw hole needs a safe edge margin");
assert(base_width <= 270 && base_depth <= 270 && overall_height <= 256, "The model must fit the workbench envelope");
echo("SCADCTL_REQUIREMENT:parameters:PASS");

module strut_2d(base_x, top_x) {
    hull() {
        translate([base_x, base_thickness + support_width / 2 - 2]) circle(d=support_width, $fn=48);
        translate([top_x, target_center_height - opening_diameter / 2 + 3]) circle(d=support_width, $fn=48);
    }
}

module target_profile() {
    difference() {
        union() {
            translate([0, target_center_height])
                difference() {
                    circle(d=outer_diameter, $fn=facet_count);
                    circle(d=opening_diameter, $fn=facet_count);
                }
            strut_2d(-support_base_spacing / 2, -support_top_spacing / 2);
            strut_2d(support_base_spacing / 2, support_top_spacing / 2);
        }
        translate([0, target_center_height]) circle(d=opening_diameter, $fn=facet_count);
    }
}

module extrude_y(depth) {
    rotate([90, 0, 0])
        linear_extrude(height=depth, center=true, convexity=10)
            children();
}

difference() {
    union() {
        extrude_y(frame_depth) target_profile();
        cuboid([base_width, base_depth, base_thickness], anchor=BOTTOM);
    }
    for (x = [-screw_spacing / 2, screw_spacing / 2])
        translate([x, 0, -0.1])
            cylinder(h=base_thickness + 0.2, d=screw_hole_diameter, $fn=48);
}
