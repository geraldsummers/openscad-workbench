include <BOSL2/std.scad>

opening_diameter = 200;
frame_width = 12;
tunnel_depth = 35;
base_width = 244;
base_depth = 45;
base_thickness = 4;
screw_hole_diameter = 4.5;
screw_spacing = 210;
facet_count = 160;

outer_diameter = opening_diameter + 2 * frame_width;
overall_height = outer_diameter;

assert(opening_diameter > 0 && frame_width >= 10, "The tunnel needs a positive opening and substantial wall");
assert(tunnel_depth > frame_width && base_depth > tunnel_depth, "The tunnel and mounting rail depths must remain distinct");
assert(base_width > outer_diameter, "The mounting rail must project beyond the tunnel");
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
        translate([0, 0, outer_diameter / 2])
            extrude_y(tunnel_depth)
                difference() {
                    circle(d=outer_diameter, $fn=facet_count);
                    circle(d=opening_diameter, $fn=facet_count);
                }
        cuboid([base_width, base_depth, base_thickness], anchor=BOTTOM);
    }
    for (x = [-screw_spacing / 2, screw_spacing / 2])
        translate([x, 0, -0.1])
            cylinder(h=base_thickness + 0.2, d=screw_hole_diameter, $fn=48);
}
