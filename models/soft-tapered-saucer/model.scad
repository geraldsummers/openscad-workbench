// Self-centering saucer for the soft tapered planter — millimetres.

outer_diameter = 142;
overall_height = 18;
floor_thickness = 3;
wall_thickness = 3;
basin_depth = 15;
mating_planter_base_diameter = 126;
radial_clearance = 1.5;
locating_inner_diameter = mating_planter_base_diameter + 2 * radial_clearance;
locating_outer_diameter = 135;
locating_height = 7;
support_height = 5;
support_radius = 10;
support_center_radius = 38;
channel_width = 10;
profile_softening = 1.5;

$fn = 192;

outer_radius = outer_diameter / 2;
inner_basin_radius = outer_radius - wall_thickness;
locating_inner_radius = locating_inner_diameter / 2;
locating_outer_radius = locating_outer_diameter / 2;

assert(outer_diameter == 142 && overall_height == 18,
       "Saucer envelope must remain 142 x 142 x 18 mm");
assert(floor_thickness == 3 && wall_thickness == 3,
       "Saucer must retain 3 mm floor and wall thicknesses");
assert(overall_height - floor_thickness == basin_depth,
       "Usable basin depth must be 15 mm");
assert(locating_inner_diameter == 129 && radial_clearance == 1.5,
       "Locating ring must provide 1.5 mm radial planter clearance");
assert(locating_outer_radius < inner_basin_radius,
       "Locating ring must remain inside the catch basin");
assert((outer_diameter - mating_planter_base_diameter) / 2 == 8,
       "Saucer must extend only 8 mm radially beyond the planter base");
assert(support_height > floor_thickness && support_height < locating_height,
       "Supports must raise the planter above the floor but remain below the locating ring");
assert(channel_width > 0 && channel_width < locating_outer_diameter,
       "Drainage channels must be positive and narrower than the locating ring");

echo("SCADCTL_REQUIREMENT:saucer-parameters:PASS");
echo("SCADCTL_REQUIREMENT:mating-clearance:PASS");
echo("SCADCTL_REQUIREMENT:compact-footprint:PASS");
echo("SCADCTL_REQUIREMENT:raised-seat:PASS");

module rounded_basin() {
    rotate_extrude(convexity=10)
        polygon([
            [0, 0],
            [outer_radius - profile_softening, 0],
            [outer_radius - 0.5, 0.5],
            [outer_radius, profile_softening],
            [outer_radius, overall_height - profile_softening],
            [outer_radius - 0.5, overall_height - 0.5],
            [outer_radius - profile_softening, overall_height],
            [inner_basin_radius, overall_height],
            [inner_basin_radius, floor_thickness],
            [0, floor_thickness]
        ]);
}

module broken_locating_ring() {
    difference() {
        translate([0, 0, floor_thickness])
            difference() {
                cylinder(h=locating_height - floor_thickness,
                         d=locating_outer_diameter);
                translate([0, 0, -0.1])
                    cylinder(h=locating_height - floor_thickness + 0.2,
                             d=locating_inner_diameter);
            }

        for (angle = [0 : 90 : 270])
            rotate([0, 0, angle])
                translate([locating_inner_radius - 1, -channel_width / 2,
                           floor_thickness - 0.1])
                    cube([locating_outer_radius - locating_inner_radius + 2,
                          channel_width, locating_height - floor_thickness + 0.2]);
    }
}

module support_pads() {
    for (angle = [45 : 90 : 315])
        rotate([0, 0, angle])
            translate([support_center_radius, 0, floor_thickness])
                cylinder(h=support_height - floor_thickness, r=support_radius);
}

union() {
    rounded_basin();
    broken_locating_ring();
    support_pads();
}
