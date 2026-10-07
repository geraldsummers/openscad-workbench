outer=244; bar=12; chimney_height=244; base_thickness=4; mount_hole_diameter=4.5;
module dive_chimney(){ difference(){ union(){
 translate([-outer/2,-outer/2,0]) cube([outer,bar,base_thickness]); translate([-outer/2,outer/2-bar,0]) cube([outer,bar,base_thickness]);
 for(x=[-outer/2,outer/2-bar],y=[-outer/2,outer/2-bar]) translate([x,y,0]) cube([bar,bar,chimney_height]);
 for(z=[0,chimney_height-bar]) { translate([-outer/2,-outer/2,z]) cube([outer,bar,bar]); translate([-outer/2,outer/2-bar,z]) cube([outer,bar,bar]); translate([-outer/2,-outer/2,z]) cube([bar,outer,bar]); translate([outer/2-bar,-outer/2,z]) cube([bar,outer,bar]); }
 } for(x=[-outer/2+6,outer/2-6],y=[-outer/2+6,outer/2-6]) translate([x,y,-1]) cylinder(d=mount_hole_diameter,h=18,$fn=24); }}
assert(outer-2*bar>=200 && chimney_height==244); echo("SCADCTL_REQUIREMENT:parameters:PASS"); dive_chimney();
