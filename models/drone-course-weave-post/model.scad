include <BOSL2/std.scad>

post_height = 220;
post_diameter = 18;
foot_width = 70;
foot_depth = 32;
foot_thickness = 4;
reinforcement_height = 18;
reinforcement_diameter = 34;
screw_hole_diameter = 4.5;
screw_spacing = 50;
facet_count = 96;

assert(post_height > reinforcement_height && reinforcement_diameter > post_diameter, "The post must rise above its flared reinforcement");
assert(foot_width > screw_spacing + screw_hole_diameter + 8 && foot_depth > reinforcement_diameter / 2, "The foot must retain safe screw margins");
assert(foot_thickness > 0 && post_diameter >= 16, "The post and foot dimensions must remain positive");
assert(foot_width <= 270 && foot_depth <= 270 && post_height <= 256, "The model must fit the workbench envelope");
echo("SCADCTL_REQUIREMENT:parameters:PASS");

difference() {
    union() {
        cuboid([foot_width, foot_depth, foot_thickness], rounding=4, edges="Z", anchor=BOTTOM);
        cylinder(h=post_height, d=post_diameter, $fn=facet_count);
        cylinder(h=reinforcement_height, d1=reinforcement_diameter, d2=post_diameter, $fn=facet_count);
    }
    for (x = [-screw_spacing / 2, screw_spacing / 2])
        translate([x, 0, -0.1])
            cylinder(h=foot_thickness + 0.2, d=screw_hole_diameter, $fn=48);
}
