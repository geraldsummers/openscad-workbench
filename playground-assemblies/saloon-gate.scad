use <../models/drone-playground-saloon-frame/model.scad>
use <../models/drone-playground-saloon-door/model.scad>
color("saddlebrown") saloon_frame();
color("goldenrod") translate([-106,0,25]) rotate([0,0,8]) saloon_door();
color("goldenrod") mirror([1,0,0]) translate([-106,0,25]) rotate([0,0,8]) saloon_door();
