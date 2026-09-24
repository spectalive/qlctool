"""Where the Vibra show sets the channels no capability decides."""

from ..description.fixture_tuning import FixtureTuning

VIBRA_TUNING = FixtureTuning(
    # Where the beams' focus channel sits. Nothing wrote it until 2026-08-30,
    # which means it sat at DMX 0 - one end of the travel - for every gobo
    # this rig has ever projected: seventeen patterns thrown out of focus,
    # which is most of why "se echaba en falta mas variedad" (owner).
    # Mid-travel is a starting point and nothing more; the number that is
    # *right* depends on the throw, so it is one constant, it travels with the
    # gobo scenes, and TODO.md carries the job of reading it off the room.
    beam_focus=127,
    # Slow forward on the 7R prism rotation's 0-127 slow-to-fast run: the
    # inserted prism turns, which is what makes it read as a kaleidoscope and
    # not a smudge.
    prism_spin_slow=25,
    # Where the held flashes sit on every shutter's slow-to-fast run. The
    # hand-built show's `Flash 100%` strobed the rig near the top of each
    # channel (CromoWash 240 of 10-255, Vortex 250, panels 255) and its
    # `Flash 50%` was the *same* full white at roughly half the strobe speed
    # (Vortex 220, panels 140, beams 120) - not half the brightness. Space
    # without the strobe is the regression the owner caught at home on
    # 2026-08-27: "esto no hace estrobo y antes lo hacia". 0.85 was still a
    # stroll next to those numbers - the owner clocked it on the PARs on
    # 2026-08-29, "el flash es entre 246-248, como lo tenemos ahora es muy
    # lento" - and 0.97 is that: 247 on the CLB2.4's 1-255, 248 on the
    # CromoWash's 10-255. Same night for the slow one: "el flash slow para los
    # par es unos 200, no lo que esta ahora" - 0.45 had it at 115, and 0.785
    # is the 200 the owner asked for (CromoWash 202).
    strobe_fast=0.97,
    strobe_slow=0.785,
    # The light somebody is lit by when they speak: white, warmed off
    # daylight so a face does not read as a mortuary, and flat enough that
    # nothing draws the eye.
    talk_white=(255, 214, 170),
)
