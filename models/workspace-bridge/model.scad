include <BOSL2/std.scad>

width = 80;
depth = 30;
height = 24;
corner_radius = 4;
tunnel_width = 20;
tunnel_radius = tunnel_width / 2;
tunnel_spring_height = 10;
tunnel_depth = depth + 2;

assert(width > 0 && depth > 0 && height > 0, "Dimensions must be positive");
assert(corner_radius >= 0 && corner_radius <= min(width, depth) / 2,
       "Corner radius must fit the footprint");
assert(tunnel_width > 0 && tunnel_width < width,
       "Tunnel must be narrower than the bridge");
assert(tunnel_spring_height + tunnel_radius < height,
       "Tunnel must leave a continuous crown");
echo("SCADCTL_REQUIREMENT:parameter-safety:PASS");

difference() {
    linear_extrude(height=height)
        offset(r=corner_radius, $fn=48)
            square([width - 2 * corner_radius, depth - 2 * corner_radius], center=true);

    rotate([90, 0, 0])
        linear_extrude(height=tunnel_depth, center=true)
            polygon(concat(
                [[-tunnel_radius, -1], [tunnel_radius, -1]],
                [for (angle = [0:2:180])
                    [tunnel_radius * cos(angle),
                     tunnel_spring_height + tunnel_radius * sin(angle)]]
            ));
}
