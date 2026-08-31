include <BOSL2/std.scad>
include <BOSL2/threading.scad>

pad_diameter = 40;
pad_height = 6;
pad_sides = 16;
pad_top_chamfer = 1;
thread_diameter = 18;
thread_length = 26;
thread_pitch = 2;
thread_depth = thread_pitch / 2;
joint_overlap = 1;
minimum_engagement = 10;
maximum_engagement = 16;
adjustment_travel = maximum_engagement - minimum_engagement;
mating_platform_radius = 75;
mating_support_radius = 85;
thumbwheel_exposure = mating_support_radius + pad_diameter / 2 - mating_platform_radius;

assert(pad_diameter > thread_diameter,
       "The hand pad must be wider than the threaded shaft");
assert(pad_top_chamfer > 0 && pad_top_chamfer < pad_height / 2,
       "The pad chamfer must fit within the pad height");
assert(joint_overlap > 0 && joint_overlap < pad_height,
       "The threaded shaft must overlap the pad to form one solid");
assert(thread_length - joint_overlap >= maximum_engagement,
       "The protruding shaft must support maximum socket engagement");
assert(adjustment_travel == 6 && minimum_engagement / thread_pitch >= 5,
       "The foot must provide 6 mm travel with at least five engaged pitches");
assert(thumbwheel_exposure == 30,
       "The side-access thumbwheel must project 30 mm beyond the circular platform");
echo("SCADCTL_REQUIREMENT:foot-parameters:PASS");
echo("SCADCTL_REQUIREMENT:upright-access:PASS");

cyl(
    h=pad_height,
    d=pad_diameter,
    chamfer2=pad_top_chamfer,
    $fn=pad_sides,
    anchor=BOTTOM
) {
    attach(TOP, BOTTOM, overlap=joint_overlap)
        trapezoidal_threaded_rod(
            d=thread_diameter,
            l=thread_length,
            pitch=thread_pitch,
            thread_angle=30,
            thread_depth=thread_depth,
            blunt_start=true,
            bevel2=true,
            anchor=BOTTOM,
            $fn=64
        );
}
