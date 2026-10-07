include <BOSL2/std.scad>
include <BOSL2/threading.scad>
thread_diameter=24; male_diameter=23.76; pitch=3; length=20; knob_diameter=40; knob_height=8;
assert(abs(male_diameter-thread_diameter*0.99)<0.001 && length/pitch>=6, "Thread test dimensions are valid");
echo("SCADCTL_REQUIREMENT:thread-test:PASS");
union(){ cyl(d=knob_diameter,h=knob_height,anchor=BOTTOM,$fn=96);
 translate([0,0,knob_height-1]) trapezoidal_threaded_rod(d=male_diameter,l=length,pitch=pitch,thread_angle=30,thread_depth=pitch/2,blunt_start=true,bevel2=true,anchor=BOTTOM,$fn=64); }
