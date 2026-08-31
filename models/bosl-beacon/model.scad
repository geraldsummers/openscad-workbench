include <BOSL2/std.scad>

base_diameter = 52;
base_height = 7;
base_chamfer = 1;
tower_height = 28;
tower_bottom_diameter = 30;
tower_top_diameter = 12;
tower_rounding = 1.5;
cap_diameter = 16;
joint_overlap = 1;

assert(base_diameter > tower_bottom_diameter && tower_bottom_diameter > tower_top_diameter,
       "The beacon must taper upward from its base");
assert(base_chamfer > 0 && base_chamfer < base_height / 2,
       "The base chamfer must fit within the base height");
assert(joint_overlap > 0 && joint_overlap < min(base_height, tower_height, cap_diameter),
       "Attachment overlap must be positive and smaller than every joined feature");
assert(tower_rounding > 0 && tower_rounding < tower_top_diameter / 2,
       "Tower rounding must fit its narrow end");
echo("SCADCTL_REQUIREMENT:bosl-parameters:PASS");

// BOSL2 attachments express the stack: each child is anchored to its
// parent's TOP and inset by `joint_overlap` to guarantee one connected solid.
cyl(h=base_height, d=base_diameter, chamfer=base_chamfer, anchor=BOTTOM, $fn=96) {
    attach(TOP, BOTTOM, overlap=joint_overlap)
        cyl(
            h=tower_height,
            d1=tower_bottom_diameter,
            d2=tower_top_diameter,
            rounding1=tower_rounding,
            rounding2=tower_rounding,
            $fn=96
        ) {
            attach(TOP, BOTTOM, overlap=joint_overlap)
                sphere(d=cap_diameter, $fn=96);
        }
}
