include <BOSL2/std.scad>

width = 40;
depth = 30;
height = 12;
corner_radius = 2;

assert(width > 0 && depth > 0 && height > 0, "Dimensions must be positive");
assert(corner_radius >= 0 && corner_radius <= min(width, depth) / 2,
       "Corner radius must fit the footprint");
echo("SCADCTL_REQUIREMENT:corner-radius:PASS");

cuboid([width, depth, height], rounding=corner_radius, edges="Z", anchor=BOTTOM, $fn=48);
