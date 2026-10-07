// Visual assembly demo. Manufacturing meshes remain in their separate model directories.

saucer_seat_height = 5;
demo_cutaway = false;

module assembled_planter_and_saucer() {
    color("lightsteelblue")
        import("../models/soft-tapered-saucer/build/model.stl", convexity=10);

    color("burlywood")
        translate([0, 0, saucer_seat_height])
            import("../models/soft-tapered-planter/build/model.stl", convexity=10);
}

if (demo_cutaway)
    intersection() {
        assembled_planter_and_saucer();
        translate([-100, 0, 0]) cube([200, 100, 200]);
    }
else
    assembled_planter_and_saucer();
