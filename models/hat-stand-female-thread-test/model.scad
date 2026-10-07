include <BOSL2/std.scad>
include <BOSL2/threading.scad>
thread_diameter=24; pitch=3; length=20; clearance=1.2; coupon_diameter=40; coupon_height=24;
$slop=clearance/4;
assert(clearance==1.2 && length/pitch>=6, "Thread test dimensions are valid");
echo("SCADCTL_REQUIREMENT:thread-test:PASS");
difference(){ cyl(d=coupon_diameter,h=coupon_height,anchor=BOTTOM,$fn=96);
 translate([0,0,-0.1]) trapezoidal_threaded_rod(d=thread_diameter+clearance,l=length+0.2,pitch=pitch,thread_angle=30,thread_depth=pitch/2,internal=true,blunt_start=true,bevel1=true,anchor=BOTTOM,$fn=64); }
