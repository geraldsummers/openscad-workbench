include <BOSL2/std.scad>
include <BOSL2/threading.scad>

head_diameter = 32;
head_height = 8;
head_chamfer = 1;
thread_diameter = 18;
thread_length = 30;
thread_pitch = 3;
joint_overlap = 1;

assert(head_diameter > thread_diameter,
       "The hex head must be wider than the threaded shaft");
assert(head_chamfer > 0 && head_chamfer < head_height / 2,
       "The head chamfer must fit within the head height");
assert(thread_pitch > 0 && thread_length / thread_pitch >= 6,
       "The shaft must contain at least six full thread pitches");
assert(joint_overlap > 0 && joint_overlap < min(head_height, thread_pitch),
       "The head-to-shaft overlap must create a connected joint");
echo("SCADCTL_REQUIREMENT:thread-parameters:PASS");

// The threaded shaft is attached to the hex head through BOSL2's anchor system.
// A 1 mm overlap ensures the exported result is one connected solid.
cyl(
    h=head_height,
    d=head_diameter,
    chamfer=head_chamfer,
    $fn=6,
    anchor=BOTTOM
) {
    attach(TOP, BOTTOM, overlap=joint_overlap)
        threaded_rod(
            d=thread_diameter,
            l=thread_length,
            pitch=thread_pitch,
            blunt_start=true,
            bevel2=true,
            anchor=BOTTOM,
            $fn=64
        );
}
