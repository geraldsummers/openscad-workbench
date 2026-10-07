base_length=140; base_depth=80; pivot_height=82; axle_bore=6.6; mount_hole_diameter=4.5;
module saddle(y){ difference(){ translate([-14,y-8,4]) cube([28,16,pivot_height]); translate([0,y,pivot_height+4]) rotate([90,0,0]) cylinder(d=axle_bore,h=20,center=true,$fn=32); translate([-axle_bore/2,y-11,pivot_height+4]) cube([axle_bore,22,15]); }}
module seesaw_base(){ difference(){ union(){ translate([-base_length/2,-base_depth/2,0]) cube([base_length,base_depth,4]); saddle(-30); saddle(30); for(x=[-62,62]) translate([x,-base_depth/2,4]) cube([10,base_depth,20]); } for(x=[-52,52],y=[-27,27]) translate([x,y,-1]) cylinder(d=mount_hole_diameter,h=7,$fn=24); }}
assert(axle_bore==6.6 && pivot_height==82); echo("SCADCTL_REQUIREMENT:parameters:PASS"); seesaw_base();
