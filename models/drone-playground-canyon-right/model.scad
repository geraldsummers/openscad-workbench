wall_length=240; wall_depth=70; wall_height=120; wall_thickness=10; base_thickness=4; mount_hole_diameter=4.5;
module canyon_wall_right() { difference() { union() {
 translate([-wall_length/2,-wall_depth/2,0]) cube([wall_length,wall_depth,base_thickness]);
 for(i=[0:3]) { x1=-wall_length/2+i*wall_length/4; x2=-wall_length/2+(i+1)*wall_length/4; y1=-(i%2==0?-18:18); y2=-((i+1)%2==0?-18:18);
  hull(){ translate([x1,y1,base_thickness]) cylinder(d=wall_thickness,h=wall_height-base_thickness,$fn=32); translate([x2,y2,base_thickness]) cylinder(d=wall_thickness,h=wall_height-base_thickness,$fn=32); }}
 for(x=[-90,90]) translate([x,0,base_thickness]) cylinder(d=18,h=14,$fn=32);
 } for(x=[-90,90]) translate([x,0,-1]) cylinder(d=mount_hole_diameter,h=20,$fn=24); }}
assert(wall_length==240 && wall_depth==70 && wall_height==120); echo("SCADCTL_REQUIREMENT:parameters:PASS"); canyon_wall_right();
