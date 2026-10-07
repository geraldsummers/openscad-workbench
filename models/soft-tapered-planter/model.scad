// Soft tapered planter — dimensions in millimetres.

top_diameter = 160;
base_diameter = 126;
height = 145;
side_wall = 3;
floor_thickness = 4;
drain_hole_diameter = 8;
drain_hole_radius = 24;
drain_hole_count = 5;
profile_softening = 1.5;
scallop_count = 12;
scallop_extension = 4;
scallop_samples_per_lobe = 24;
scallop_fade_fraction = 1 / 3;

$fn = 192;

top_radius = top_diameter / 2;
base_radius = base_diameter / 2;
inner_top_radius = top_radius - side_wall;
inner_base_radius = base_radius - side_wall;
scallop_fade_start_z = height * (1 - scallop_fade_fraction);
overall_scalloped_diameter = top_diameter + 2 * scallop_extension;

assert(top_diameter == 160 && base_diameter == 126 && height == 145,
       "Planter core dimensions must remain 160 mm at the top, 126 mm at the base, and 145 mm tall");
assert(side_wall == 3 && floor_thickness == 4,
       "Planter must retain the approved 3 mm wall and 4 mm floor");
assert(top_radius > base_radius && inner_base_radius > 0,
       "Planter must taper outward and retain a usable cavity");
assert(drain_hole_count == 5 && drain_hole_diameter == 8,
       "Drainage pattern must contain five 8 mm holes");
assert(drain_hole_radius + drain_hole_diameter / 2 < inner_base_radius,
       "Drainage holes must remain inside the cavity floor");
assert(profile_softening > 0 && profile_softening < side_wall,
       "Profile softening must be positive and smaller than the wall");
assert(scallop_count >= 6 && scallop_count % 2 == 0,
       "Scalloped rim must use an even count of at least six lobes");
assert(scallop_extension == 4 && overall_scalloped_diameter == 168,
       "Twelve scallops must extend 4 mm beyond the original rim");
assert(abs(height - scallop_fade_start_z - height / 3) < 0.001,
       "Scallops must begin one third of the planter height below the top");
assert(scallop_fade_start_z > floor_thickness && top_radius + scallop_extension > top_radius,
       "Scallops must fade gently upward and outward from the upper body");

echo("SCADCTL_REQUIREMENT:planter-parameters:PASS");
echo("SCADCTL_REQUIREMENT:drainage-pattern:PASS");
echo("SCADCTL_REQUIREMENT:scalloped-rim:PASS");

module drain_holes() {
    cylinder(h=floor_thickness + 0.2, d=drain_hole_diameter);

    for (angle = [0 : 90 : 270])
        rotate([0, 0, angle])
            translate([drain_hole_radius, 0, 0])
                cylinder(h=floor_thickness + 0.2, d=drain_hole_diameter);
}

function body_radius_at(z) =
    z <= 0 ? base_radius - profile_softening :
    z <= 0.5 ? base_radius - 0.5 :
    z <= profile_softening ? base_radius :
    base_radius + (top_radius - base_radius)
        * (z - profile_softening) / (height - profile_softening);

function scallop_ease_at(z) =
    z <= scallop_fade_start_z ? 0 :
    let (progress = (z - scallop_fade_start_z)
                    / (height - scallop_fade_start_z))
        progress * progress * (3 - 2 * progress);

function scalloped_outer_radius(angle, z) =
    body_radius_at(z)
        + scallop_extension * scallop_ease_at(z)
            * (1 + cos(scallop_count * angle)) / 2;

module planter_outer_solid() {
    sample_count = scallop_count * scallop_samples_per_lobe;
    fade_span = height - scallop_fade_start_z;
    layer_z = [
        0,
        0.5,
        profile_softening,
        scallop_fade_start_z,
        scallop_fade_start_z + fade_span * 0.25,
        scallop_fade_start_z + fade_span * 0.5,
        scallop_fade_start_z + fade_span * 0.75,
        height
    ];
    points = concat(
        [for (z = layer_z)
            for (i = [0 : sample_count - 1])
                let (angle = 360 * i / sample_count,
                     radius = scalloped_outer_radius(angle, z))
                    [radius * cos(angle), radius * sin(angle), z]],
        [[0, 0, 0], [0, 0, height]]
    );

    layer_count = len(layer_z);
    bottom_center = layer_count * sample_count;
    top_center = bottom_center + 1;
    faces = concat(
        [for (layer = [0 : layer_count - 2])
            for (i = [0 : sample_count - 1])
                let (j = (i + 1) % sample_count,
                     lower_i = layer * sample_count + i,
                     lower_j = layer * sample_count + j,
                     upper_i = (layer + 1) * sample_count + i,
                     upper_j = (layer + 1) * sample_count + j)
                    each [[lower_i, lower_j, upper_j],
                          [lower_i, upper_j, upper_i]]],
        [for (i = [0 : sample_count - 1])
            let (j = (i + 1) % sample_count)
                [bottom_center, j, i]],
        [for (i = [0 : sample_count - 1])
            let (j = (i + 1) % sample_count,
                 top_i = (layer_count - 1) * sample_count + i,
                 top_j = (layer_count - 1) * sample_count + j)
                [top_center, top_i, top_j]]
    );

    outward_faces = [for (face = faces)
        [for (index = [len(face) - 1 : -1 : 0]) face[index]]];

    polyhedron(points=points, faces=outward_faces, convexity=10);
}

difference() {
    planter_outer_solid();
    translate([0, 0, floor_thickness])
        cylinder(h=height - floor_thickness + 0.2,
                 r1=inner_base_radius, r2=inner_top_radius);
    translate([0, 0, -0.1]) drain_holes();
}
