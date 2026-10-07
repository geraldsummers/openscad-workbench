cap_diameter=22; cap_height=12; socket_diameter=6.6; socket_depth=9;
module carousel_cap(){ difference(){ cylinder(d1=cap_diameter,d2=18,h=cap_height,$fn=48); translate([0,0,-0.01]) cylinder(d=socket_diameter,h=socket_depth,$fn=32); }}
assert(socket_diameter==6.6 && socket_depth<cap_height); echo("SCADCTL_REQUIREMENT:parameters:PASS"); carousel_cap();
