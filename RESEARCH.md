# Fabrication research log

This repository treats physical fabrication as an experiment loop. Geometry
verification establishes what was modeled; it does not establish printer fit.
Record physical outcomes here so failed prints remain useful evidence and later
designs do not silently repeat them.

## Nominal CAD and production compensation

The default research baseline is nominal CAD under ideal production. Functional
geometry—such as intentional running clearance between mating parts—is part of
the design. Printer shrink correction, slicer scaling, extrusion compensation,
elephant-foot correction, and similar process adjustments are not CAD geometry;
record them separately as fabrication variables.

Do not transfer a successful production transform into the source model merely
because it worked for one printer or material. If physical evidence shows that
material behavior requires genuinely different geometry, create an explicit
named parameter or material/process variant, retain the nominal baseline, and
document the evidence and scope. This is a case-specific exception that must be
re-evaluated when the material, machine, process, or use condition changes.

## Evidence rules

- Give each physical trial a stable ID and never rewrite its outcome. Add a new
  trial when geometry, process, material, machine, or evaluation changes.
- Report the modeled dimensions and the fabrication context separately. Use
  `unknown` when a setting was not captured; do not reconstruct it from memory.
- Record slicer transforms and compensation as process variables without
  altering the nominal CAD record.
- Classify outcomes as `pass`, `fail`, `mixed`, or `pending`. A revised design is
  `pending` until a physical specimen is evaluated.
- Describe the observation before proposing a cause. Clearly label causal
  explanations as hypotheses unless a controlled comparison supports them.
- Link the exact source or artifact revision when available. Record measured
  values and the instrument or method; do not substitute nominal CAD values.
- Preserve unsuccessful results. A failure can be superseded, but not converted
  into a pass because a later revision worked.

## Thread-fit trials

All dimensions are millimetres. Clearance is diametric. BOSL2 `$slop` is listed
because this model's internal trapezoidal thread uses `$slop = clearance / 4`.

| Trial | Status | Pair | Nominal thread | Internal clearance | `$slop` | Engagement | Process context | Observation |
| --- | --- | --- | --- | ---: | ---: | --- | --- | --- |
| THR-001 | fail | `leveling-stand-foot` external / `leveling-stand-platform` internal | Tr18×2, 30° trapezoidal, 1 mm modeled depth, right-handed | 0.6 | 0.15 | Designed 10–16 | First physical print; printer, material, layer height, orientation, and post-processing not recorded | User reported the screws were too tight. No insertion torque, achieved engagement, or dimensional measurements were recorded. |
| THR-002 | pending | Same pair | Tr18×2, 30° trapezoidal, 1 mm modeled depth, right-handed | 1.0 | 0.25 | Designed 10–16 | Not yet reported | Current calibration hypothesis. It must not be called successful until a printed pair is tested. |
| THR-003 | fail | ABS external screw / original leveling-stand socket | Nominal Tr18×2 CAD source; external screw transformed to 99% XY in the slicer, retaining Z pitch | 0.6 | 0.15 | Designed 10–16 before slicer scaling | ABS; external screw part scaled to 99% in XY in the slicer and tested in the original platform; printer, other slicer settings, orientation, and post-processing not recorded | User reported that the screw was still too tight. Start depth, achieved engagement, and torque were not recorded. The CAD male remains 18 mm; if the entire external thread received the reported slicer transform, the printed nominal major diameter became 17.82 mm while its 2 mm Z pitch remained unchanged. |
| THR-004 | fail | Slicer-scaled 99%-XY ABS foot / `leveling-stand-female-thread-test` coupon | Nominal Tr18×2 CAD source; external screw transformed to 99% XY in the slicer, retaining Z pitch | 1.0 | 0.25 | Coupon thread length 20 | ABS male at 99% XY by slicer transform and revised female coupon at 100%; printer, other slicer settings, orientation, cleanup, and achieved engagement not recorded | User reported that the pair was still a smidge too tight. This rejects 1.0 mm female clearance for the tested slicer-scaled ABS male configuration. |
| THR-005 | pending | Same slicer-scaled 99%-XY ABS foot / revised `leveling-stand-female-thread-test` coupon | Nominal Tr18×2 CAD source; 99% XY is applied only in the slicer | 1.2 | 0.30 | Coupon thread length 20 | Female coupon changed by +0.2 mm diametric clearance; fabrication not yet reported | Controlled follow-up to THR-004. Neither CAD model contains a 99% scale transform, and the platform remains at 1.0 mm until this coupon is physically evaluated. |
| THR-006 | pass | Slicer-scaled 99%-XY ABS foot / THR-005 female coupon | Nominal Tr18×2 CAD source; external screw transformed to 99% XY only in the slicer | 1.2 | 0.30 | Coupon thread length 20; achieved engagement not recorded | ABS male at 99% XY by slicer transform and 1.2 mm-clearance female coupon at 100%; printer, other slicer settings, orientation, cleanup, and quantitative measurements not recorded | User reported the fit was “about perfect.” This is the first successful qualitative thread-fit result for the project and supports promoting 1.2 mm female clearance to the platform for this fabrication configuration. |
| THR-007 | pending | Three slicer-scaled 99%-XY ABS feet / promoted full platform | Nominal Tr18×2 CAD feet; 99% XY remains slicer-side only | 1.2 | 0.30 | Designed 10–16 | Full platform CAD promoted from the THR-006 coupon result; fabrication not yet reported | Validate all three sockets, 6 mm adjustment travel, upright adjustment, and fit under load. Coupon success supports the clearance but does not prove whole-platform consistency. |
| THR-008 | mixed | `hat-stand-male-thread-test` / `hat-stand-female-thread-test` | Tr24×3, 30° trapezoidal, 1.5 mm modeled depth; male CAD diameter 23.76 (99% of 24), female nominal diameter 24 | 1.2 | 0.30 | Test coupons; functional when fully bottomed out, partial-engagement holding not acceptable | Material, printer, slicer settings, orientation, cleanup, insertion torque, backlash, and achieved engagement not recorded | User reported the fit was very loose but functional when screwed all the way in. It is acceptable for the hat stand because that joint bottoms out, but unsuitable for an application that must hold position before bottoming out. |

THR-006 is the first successful thread-fit result, with a qualitative “about
perfect” assessment rather than measured torque or backlash. THR-001 establishes only
that its complete, partly unknown manufacturing configuration was too tight; it
does not isolate clearance as the sole cause. THR-002 changes clearance while
holding the nominal modeled thread form constant, but uncontrolled print
conditions may still affect comparison. THR-003 establishes that a reported 1%
XY reduction of the ABS external screw was insufficient in the original 0.6 mm
clearance socket. It does not test or resolve the revised 1.0 mm-clearance
platform in THR-002. XY-only scaling also changes external thread diameters and
radial profile depth without changing the Z pitch, making it a different
geometry rather than a clean test of the platform clearance alone.
THR-004 directly tests the revised 1.0 mm female socket with the reported 99%-XY
ABS male and also fails, although less severely by the qualitative report. A
100% male is not separately tested; expecting it to be at least as tight is an
inference from its larger nominal XY dimensions, not a physical result.
THR-006 shows that increasing only the female CAD clearance from 1.0 to 1.2 mm,
while retaining the same slicer-side 99%-XY male transform, changed the reported
result from slightly too tight to about perfect. This controlled comparison
supports the clearance change for the tested ABS workflow, while unrecorded
process settings limit broader generalization.

THR-008 shows that the Tr18×2 clearance result does not transfer directly to
the larger Tr24×3 hat-stand thread when the 99% male reduction and 1.2 mm female
clearance are both used. The tested pair is retained for the hat stand because
its intended joint is fully tightened against a stop. It must not be reused for
adjustable or partial-engagement joints without a tighter follow-up test.

## Prior ABS fit context

The user reports successful fits on other ABS parts when the male part was
scaled to 99% in XY and the female part remained at 100%. The geometries,
nominal clearances, dimensions, printer settings, and evaluation criteria for
those parts are not yet recorded, so this is useful process context rather than
a successful thread trial. THR-003 and THR-004 show that the same scaling
strategy was not sufficient for this Tr18×2 pair at either 0.6 or 1.0 mm female
clearance. This suggests the earlier ABS rule of thumb does not transfer
automatically to coarse printed threads; it does not by itself identify whether
crest/root interference, profile error, or another process effect caused the
binding.

## Ergonomic observations from THR-001 build

The first build also showed that the 40 mm diameter, 6 mm-tall, 16-sided wheel
had too many sides and insufficient grip height. The current revision uses a
40 mm diameter, 18 mm-tall, eight-sided wheel. This is pending physical
evaluation and is not evidence of improved ergonomics yet.

## Planter and saucer trials

| Trial | Status | Pair | Nominal geometry | Process context | Observation |
| --- | --- | --- | --- | --- | --- |
| PLN-001 | fail | `soft-tapered-planter` / `soft-tapered-saucer` | 126 mm planter base; 176 mm saucer outside diameter; 129 mm locating opening | Fabrication and measurement method not reported | User reported that the saucer left too much space around the outside of the planter base. |
| PLN-002 | pending | Same pair | 126 mm planter base; 142 mm saucer outside diameter; 129 mm locating opening; 8 mm radial saucer extension beyond the planter base | Not yet fabricated | Compact-footprint revision prompted by PLN-001. Retains the existing 1.5 mm radial locating clearance. |

## Next physical evaluation

THR-006 validates the 1.2 mm-clearance coupon (`$slop` 0.30) as an about-perfect
qualitative fit with the 99%-XY slicer-transformed ABS male. THR-007 promotes
that clearance into the full platform while leaving all CAD male geometry
nominal; neither CAD model applies the 99% scaling. When the platform is
printed, record the printer, material,
nozzle, layer height, wall settings, part orientation, and any cleanup.
Test all three feet against all three sockets if practical. Record whether each
pair starts by hand, reaches at least 10 mm engagement, traverses the intended
6 mm adjustment range, and can be adjusted from above/side while loaded. Useful
quantitative additions are printed major diameters, socket minor diameters,
insertion torque, backlash, and load during adjustment, together with the
measurement method.

Append each physical result as a new trial and keep all existing rows unchanged.
If the result varies between pairs, classify it as `mixed` and report the full
distribution rather than only the best specimen.
