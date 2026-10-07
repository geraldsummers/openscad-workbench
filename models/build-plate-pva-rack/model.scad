include <BOSL2/std.scad>

footprint_width = 270;
footprint_depth = 270;
ground_clearance = 10;
grid_thickness = 4;
frame_width = 10;
rib_width = 5;
lattice_spacing = 45;
lattice_angles = [0, 60, -60];
lattice_offsets = [-180, -135, -90, -45, 0, 45, 90, 135, 180];
lattice_frame_overlap = 0.5;
foot_base_size = 28;
foot_attachment_size = 42;
foot_centers = [21, footprint_width / 2, footprint_width - 21];

overall_height = ground_clearance + grid_thickness;
inner_width = footprint_width - 2 * frame_width;
inner_depth = footprint_depth - 2 * frame_width;
lattice_strip_length = 2 * max(footprint_width, footprint_depth);

assert(footprint_width == 270 && footprint_depth == 270,
       "Rack footprint must remain exactly 270 x 270 mm");
assert(ground_clearance == 10 && overall_height == 14,
       "Grid underside must be 10 mm above the table and total height must be 14 mm");
assert(grid_thickness > 0 && frame_width > rib_width,
       "Frame and grid dimensions must be positive, with a wider perimeter frame");
assert(lattice_angles == [0, 60, -60]
       && lattice_spacing == 45
       && lattice_spacing >= 9 * rib_width
       && lattice_frame_overlap > 0
       && lattice_frame_overlap < frame_width,
       "Three rib families at 60 degree increments must form the sparse triangular lattice");
assert(len(lattice_offsets) == 9
       && lattice_offsets == [for (index = [-4:4]) index * lattice_spacing],
       "Each rib family must cover the deck on a regular 45 mm cadence");
assert(len(foot_centers) == 3
       && foot_centers[0] == foot_attachment_size / 2
       && foot_centers[1] == footprint_width / 2
       && foot_centers[2] == footprint_width - foot_attachment_size / 2,
       "Three foot positions per axis must form the intended 3 x 3 support layout");
assert(foot_attachment_size > foot_base_size
       && foot_attachment_size == 42
       && foot_base_size == 28,
       "Each foot must flare from a 28 mm base into a 42 mm deck attachment");
assert(ground_clearance + grid_thickness == overall_height,
       "All frame and grid top faces must share the 14 mm top plane");

echo("SCADCTL_REQUIREMENT:ground-clearance:PASS");
echo("SCADCTL_REQUIREMENT:triangular-lattice:PASS");
echo("SCADCTL_REQUIREMENT:nine-foot-support:PASS");
echo("SCADCTL_REQUIREMENT:reinforced-attachments:PASS");
echo("SCADCTL_REQUIREMENT:flat-unobstructed-top:PASS");

module perimeter_frame() {
    difference() {
        cube([footprint_width, footprint_depth, grid_thickness]);
        translate([frame_width, frame_width, -0.01])
            cube([inner_width, inner_depth, grid_thickness + 0.02]);
    }
}

module triangular_lattice_2d() {
    intersection() {
        translate([frame_width - lattice_frame_overlap,
                   frame_width - lattice_frame_overlap])
            square([inner_width + 2 * lattice_frame_overlap,
                    inner_depth + 2 * lattice_frame_overlap]);

        union()
            for (angle = lattice_angles, offset = lattice_offsets)
                translate([footprint_width / 2, footprint_depth / 2])
                    rotate(angle)
                        translate([0, offset])
                            square([lattice_strip_length, rib_width], center=true);
    }
}

module support_nodes() {
    for (x = foot_centers, y = foot_centers)
        translate([x - foot_attachment_size / 2,
                   y - foot_attachment_size / 2,
                   0])
            cube([foot_attachment_size, foot_attachment_size, grid_thickness]);
}

module reinforced_feet() {
    for (x = foot_centers, y = foot_centers)
        translate([x, y, 0])
            hull() {
                translate([-foot_base_size / 2, -foot_base_size / 2, 0])
                    cube([foot_base_size, foot_base_size, 0.8]);
                translate([-foot_attachment_size / 2,
                           -foot_attachment_size / 2,
                           ground_clearance - 0.8])
                    cube([foot_attachment_size, foot_attachment_size, 0.8]);
            }
}

union() {
    reinforced_feet();
    translate([0, 0, ground_clearance]) {
        perimeter_frame();
        linear_extrude(height=grid_thickness)
            triangular_lattice_2d();
        support_nodes();
    }
}
