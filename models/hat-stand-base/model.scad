include <BOSL2/std.scad>
include <BOSL2/threading.scad>

plate_diameter = 110;
foot_height = 14;
plate_edge_round = 3;
column_diameter = 30;
post_height = 185;
post_overlap = 4;
thread_diameter = 24;
male_thread_scale = 0.99;
male_thread_diameter = thread_diameter * male_thread_scale;
thread_pitch = 3;
thread_length = 32;
thread_depth = thread_pitch / 2;
thread_start = post_height - 5;

assert(plate_diameter > column_diameter && column_diameter > thread_diameter, "The circular plate must be wider than the column and thread");
assert(male_thread_scale == 0.99 && abs(male_thread_diameter - 23.76) < 0.001, "The male thread uses the requested 99% XY-equivalent diameter");
assert(post_height > thread_length && thread_depth > 0, "The post must accommodate the male thread");
assert(thread_pitch > 0 && thread_length / thread_pitch >= 8, "The joint needs at least eight thread pitches");
assert(post_overlap > 0 && post_overlap < foot_height, "The post-foot overlap must connect the solid");
echo("SCADCTL_REQUIREMENT:base-parameters:PASS");
echo("SCADCTL_REQUIREMENT:male-thread:PASS");

union() {
    regular_prism(n=128, d=plate_diameter, h=foot_height, rounding=plate_edge_round, anchor=BOTTOM);
    translate([0, 0, foot_height - post_overlap])
        cyl(d=column_diameter, h=post_height - foot_height + post_overlap, anchor=BOTTOM, $fn=96);
    translate([0, 0, thread_start])
        trapezoidal_threaded_rod(d=male_thread_diameter, l=thread_length, pitch=thread_pitch,
            thread_angle=30, thread_depth=thread_depth, blunt_start=true, bevel2=true,
            anchor=BOTTOM, $fn=64);
}
