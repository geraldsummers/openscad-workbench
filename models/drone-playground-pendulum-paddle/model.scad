paddle_width=40; paddle_height=100; paddle_thickness=8; axle_diameter=6; axle_length=30;
module pendulum_paddle(){ union(){ translate([-paddle_width/2,-paddle_thickness/2,0]) cube([paddle_width,paddle_thickness,paddle_height]); translate([0,0,paddle_height]) rotate([90,0,0]) cylinder(d=axle_diameter,h=axle_length,center=true,$fn=32); translate([0,0,11]) rotate([90,0,0]) cylinder(d=22,h=paddle_thickness+2,center=true,$fn=48); }}
assert(paddle_width==40 && paddle_height==100 && axle_diameter==6); echo("SCADCTL_REQUIREMENT:parameters:PASS"); pendulum_paddle();
