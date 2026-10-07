use <../models/drone-playground-carousel-base/model.scad>
use <../models/drone-playground-carousel-rotor/model.scad>
use <../models/drone-playground-carousel-cap/model.scad>
color("slategray") carousel_base();
color("hotpink") translate([0,0,112]) carousel_rotor();
color("gold") translate([0,0,120]) carousel_cap();
