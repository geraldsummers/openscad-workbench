include <BOSL2/std.scad>
include <BOSL2/threading.scad>

coupon_diameter = 30;
coupon_height = 20;
thread_diameter = 18;
thread_pitch = 2;
thread_depth = thread_pitch / 2;
thread_clearance_diametric = 1.2;
mask_epsilon = 0.1;

$slop = thread_clearance_diametric / 4;

assert(coupon_diameter == 30 && coupon_height == 20,
       "Coupon must match one platform outrigger boss");
assert(thread_diameter == 18 && thread_pitch == 2 && thread_depth == 1,
       "Coupon must use the platform Tr18x2 thread form");
assert(thread_clearance_diametric == 1.2 &&
       thread_clearance_diametric == 4 * $slop,
       "Coupon must test 1.2 mm diametric clearance with BOSL2 slop 0.30");
echo("SCADCTL_REQUIREMENT:coupon-parameters:PASS");
echo("SCADCTL_REQUIREMENT:through-thread:PASS");

difference() {
    cyl(h=coupon_height, d=coupon_diameter, anchor=BOTTOM, $fn=96);

    down(mask_epsilon)
        trapezoidal_threaded_rod(
            d=thread_diameter,
            l=coupon_height + 2 * mask_epsilon,
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
