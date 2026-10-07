arm_radius=100; arm_width=14; rotor_thickness=8; hub_diameter=30; axle_bore=6.6;
module carousel_rotor(){ difference(){ linear_extrude(height=rotor_thickness) union(){ circle(d=hub_diameter,$fn=48); for(a=[0,120,240]) rotate(a) hull(){ circle(d=arm_width,$fn=24); translate([arm_radius,0]) circle(d=arm_width,$fn=24); } } translate([0,0,-1]) cylinder(d=axle_bore,h=rotor_thickness+2,$fn=32); }}
assert(arm_radius==100 && axle_bore==6.6); echo("SCADCTL_REQUIREMENT:parameters:PASS"); carousel_rotor();
