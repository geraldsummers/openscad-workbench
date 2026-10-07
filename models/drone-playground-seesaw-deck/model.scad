deck_length=180; deck_depth=100; deck_thickness=6; axle_diameter=6; axle_length=78;
module seesaw_deck(){ union(){ translate([-deck_length/2,-deck_depth/2,3]) cube([deck_length,deck_depth,deck_thickness]); translate([0,0,3]) rotate([90,0,0]) cylinder(d=axle_diameter,h=axle_length,center=true,$fn=32); for(x=[-76,76]) translate([x,-deck_depth/2,9]) cube([8,deck_depth,8]); }}
assert(deck_length==180 && axle_diameter==6); echo("SCADCTL_REQUIREMENT:parameters:PASS"); seesaw_deck();
