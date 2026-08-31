include <BOSL2/std.scad>
include <BOSL2/threading.scad>

platform_diameter = 150;
plate_thickness = 8;
plate_bottom = 12;
platform_top = plate_bottom + plate_thickness;
boss_height = platform_top;
boss_diameter = 30;
boss_radius = 85;
boss_count = 3;
arm_width = 24;
arm_bottom = 8;
arm_height = platform_top - arm_bottom;
arm_length = 50;
arm_center_radius = 65;
thread_diameter = 18;
thread_pitch = 2;
thread_depth = thread_pitch / 2;
socket_thread_length = boss_height;
thread_clearance_diametric = 0.6;
adjustment_travel = 6;
minimum_engagement = 10;
maximum_engagement = 16;
mask_epsilon = 0.1;
mating_thumbwheel_diameter = 40;
platform_radius = platform_diameter / 2;
assembly_radius = boss_radius + mating_thumbwheel_diameter / 2;
thumbwheel_exposure = assembly_radius - platform_radius;

$slop = thread_clearance_diametric / 4;

assert(platform_diameter == 150 && plate_thickness == 8,
       "Platform envelope must remain 150 mm by 8 mm");
assert(boss_count == 3 && 360 / boss_count == 120,
       "Exactly three supports must be spaced 120 degrees apart");
assert(boss_radius - boss_diameter / 2 < platform_radius,
       "Each outrigger boss must overlap the circular platform footprint");
assert(arm_center_radius - arm_length / 2 < platform_radius &&
       arm_center_radius + arm_length / 2 > boss_radius - boss_diameter / 2,
       "Each arm must overlap both the platform and its outer boss");
assert(boss_height == platform_top && arm_bottom + arm_height == platform_top,
       "Platform, outrigger arms, and bosses must share one coplanar top face");
assert(maximum_engagement - minimum_engagement == adjustment_travel,
       "Operating engagement must provide exactly 6 mm of leveling travel");
assert(socket_thread_length == boss_height,
       "Each threaded socket must pass completely through its outrigger boss");
assert(thread_clearance_diametric == 4 * $slop,
       "BOSL2 internal-thread slop must produce 0.6 mm diametric clearance");
assert(assembly_radius * 2 == 210 && thumbwheel_exposure == 30,
       "Outrigger wheels must form a 210 mm radial envelope and project 30 mm beyond the platform");
echo("SCADCTL_REQUIREMENT:platform-parameters:PASS");
echo("SCADCTL_REQUIREMENT:adjustment-range:PASS");
echo("SCADCTL_REQUIREMENT:outrigger-access:PASS");
echo("SCADCTL_REQUIREMENT:coplanar-top:PASS");
echo("SCADCTL_REQUIREMENT:through-threads:PASS");

module support_positions() {
    for (angle = [90, 210, 330])
        zrot(angle)
            right(boss_radius)
                children();
}

difference() {
    union() {
        up(plate_bottom)
            cyl(h=plate_thickness, d=platform_diameter, anchor=BOTTOM, $fn=128);

        support_positions()
            cyl(h=boss_height, d=boss_diameter, anchor=BOTTOM, $fn=96);

        for (angle = [90, 210, 330])
            zrot(angle)
                translate([arm_center_radius, 0, boss_height - arm_height])
                    cuboid([arm_length, arm_width, arm_height], anchor=BOTTOM);
    }

    support_positions()
        down(mask_epsilon)
            trapezoidal_threaded_rod(
                d=thread_diameter,
                l=socket_thread_length + 2 * mask_epsilon,
                pitch=thread_pitch,
                thread_angle=30,
                thread_depth=thread_depth,
                internal=true,
                blunt_start=true,
                bevel1=true,
                anchor=BOTTOM,
                $fn=64
            );
}
