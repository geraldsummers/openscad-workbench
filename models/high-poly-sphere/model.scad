diameter = 50;       // mm
facet_count = 256;   // high-resolution tessellation

assert(diameter > 0, "Sphere diameter must be positive");
echo("SCADCTL_REQUIREMENT:positive-diameter:PASS");

assert(facet_count >= 192 && facet_count % 4 == 0,
       "High-poly facet count must be at least 192 and divisible by four");
echo("SCADCTL_REQUIREMENT:high-poly:PASS");

// Raise the sphere by its radius so the single solid rests on Z=0.
translate([0, 0, diameter / 2])
    sphere(d=diameter, $fn=facet_count);
