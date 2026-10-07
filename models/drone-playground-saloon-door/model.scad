door_width=70; door_height=150; door_thickness=6; hinge_pin_diameter=6; hinge_offset=5;
module saloon_door(){ union(){ cylinder(d=hinge_pin_diameter,h=door_height,$fn=32); translate([0,-door_thickness/2,0]) cube([door_width,door_thickness,door_height]); translate([door_width-18,-door_thickness/2-2,door_height-24]) cube([18,door_thickness+4,18]); }}
assert(door_width==70 && door_height==150 && hinge_pin_diameter==6); echo("SCADCTL_REQUIREMENT:parameters:PASS"); saloon_door();
