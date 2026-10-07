pad_size=80; pad_heights=[50,90,130]; pad_thickness=6; mount_hole_diameter=4.5;
module landing_staircase(){ difference(){ union(){ translate([-40,-120,0]) cube([80,240,4]); for(i=[0:2]) { y=-80+i*80; translate([-11,y-11,0]) cube([22,22,pad_heights[i]]); translate([-40,y-40,pad_heights[i]]) cube([pad_size,pad_size,pad_thickness]); translate([-22,y-22,pad_heights[i]+pad_thickness]) cube([44,44,1]); } } for(y=[-106,106]) translate([0,y,-1]) cylinder(d=mount_hole_diameter,h=7,$fn=24); }}
assert(pad_size==80 && pad_heights[2]==130); echo("SCADCTL_REQUIREMENT:parameters:PASS"); landing_staircase();
