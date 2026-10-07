use <../models/drone-playground-seesaw-base/model.scad>
use <../models/drone-playground-seesaw-deck/model.scad>
color("slategray") seesaw_base();
color("orange") translate([0,0,84]) rotate([0,8,0]) translate([0,0,-3]) seesaw_deck();
