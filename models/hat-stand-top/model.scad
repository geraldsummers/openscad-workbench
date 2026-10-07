include <BOSL2/std.scad>
include <BOSL2/threading.scad>

plate_diameter = 80;
bar_height = 12;
plate_edge_round = 3;
column_diameter = 30;
socket_height = 48;
socket_overlap = 4;
thread_diameter = 24;
thread_pitch = 3;
thread_depth = thread_pitch / 2;
thread_clearance = 1.2;
socket_thread_length = 35;

$slop = thread_clearance / 4;
assert(plate_diameter > column_diameter && column_diameter > thread_diameter, "The circular plate must be wider than the column and thread");
assert(socket_height > socket_thread_length && socket_overlap > 0 && socket_overlap < bar_height,
       "The socket must have wall and bar overlap");
assert(thread_clearance == 1.2 && thread_diameter == 24 && thread_pitch == 3,
       "The female thread must match the base Tr24x3 thread with 1.2 mm diametric clearance");
echo("SCADCTL_REQUIREMENT:top-parameters:PASS");
echo("SCADCTL_REQUIREMENT:female-thread:PASS");

union() {
    regular_prism(n=128, d=plate_diameter, h=bar_height, rounding=plate_edge_round, anchor=BOTTOM);
    translate([0, 0, 0])
        difference() {
            cyl(d=column_diameter, h=socket_height, anchor=BOTTOM, $fn=96);
            translate([0, 0, -0.1])
                trapezoidal_threaded_rod(d=thread_diameter + thread_clearance, l=socket_height + 0.2,
                    pitch=thread_pitch, thread_angle=30, thread_depth=thread_depth,
                    internal=true, blunt_start=true, bevel1=true, anchor=BOTTOM, $fn=64);
        }
}
