use <../models/drone-playground-canyon-left/model.scad>
use <../models/drone-playground-canyon-right/model.scad>
color("orange") translate([0,-135,0]) canyon_wall_left();
color("deepskyblue") translate([0,135,0]) canyon_wall_right();
