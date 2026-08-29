"""Where the beams' movement is centred, in raw tilt.

Every movement EFX this repo ever generated sat at the QLC+ default - X 127,
Y 127, the raw middle of pan and tilt - because `EFXAxis.offset` defaults there
and no caller had ever overridden it. Mid-travel is not an aim, it is the
absence of one, and on this rig it points the beams at the floor: "está todo el
rato haciendo un circulo pequeño en el suelo" (owner, 2026-08-29, watching the
ambient level).

Which way is up is measured, not guessed. Three numbers fix the tilt axis:

- **0 is the ceiling.** A CromoWash whose coarse tilt was stuck at zero "parked
  at one end of 270 degrees of tilt and sat pointing at the ceiling"
  (`docs/rig.md`, measured 2026-08-27).
- **127 is the floor**, the owner watching the beams circle there.
- **~196 is the stage**, the hand-built show's own `Escenario` aiming the four
  7R back over the deck - past the floor, coming up the other side.

So tilt *falls* as the beam rises, and the crowd lives between the ceiling and
the floor: below 127, above 0. The value here puts the centre of the figure out
over the audience, high enough that a circle the size of `BEAM`'s never reaches
the floor line.

This is one number, on purpose. It is a first aim in raw DMX like the fan's,
to be nudged in the real room - up is *smaller*.
"""

# Tilt the beams' movement is built around: out over the crowd, not the floor.
BEAM_TILT_AIM = 88
