base_size=90; post_height=110; post_diameter=20; spindle_diameter=6; mount_hole_diameter=4.5;
module carousel_base(){ difference(){ union(){ translate([-base_size/2,-base_size/2,0]) cube([base_size,base_size,4]); cylinder(d1=54,d2=post_diameter,h=post_height,$fn=48); translate([0,0,post_height]) cylinder(d=spindle_diameter,h=14,$fn=32); } for(x=[-34,34],y=[-34,34]) translate([x,y,-1]) cylinder(d=mount_hole_diameter,h=7,$fn=24); }}
assert(post_height==110 && spindle_diameter==6); echo("SCADCTL_REQUIREMENT:parameters:PASS"); carousel_base();
