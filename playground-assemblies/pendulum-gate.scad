use <../models/drone-playground-pendulum-gantry/model.scad>
use <../models/drone-playground-pendulum-paddle/model.scad>
color("dodgerblue") pendulum_gantry();
color("orange") translate([0,0,104]) pendulum_paddle();
