"""Where the beams' movement is centred, in raw tilt.

Every movement EFX this repo ever generated sat at the QLC+ default - X 127,
Y 127, the raw middle of pan and tilt - because `EFXAxis.offset` defaults there
and no caller had ever overridden it. Mid-travel is not an aim, it is the
absence of one, and on this rig it points the beams at the floor: "está todo el
rato haciendo un circulo pequeño en el suelo" (owner, 2026-08-29, watching the
ambient level).

Which way the room is was measured in the room, and the first attempt got it
backwards. Three numbers fix the 7R's tilt axis:

- **127 is the floor** under the truss, the owner watching the beams circle
  there.
- **88 is the wall behind**: the first aim moved them 39 counts down the scale
  and "ahora los 7R apuntan a la pared" (owner, 2026-08-29). So the wall side
  is *below* 127, and the ceiling reading in `docs/rig.md` - a CromoWash stuck
  at coarse zero pointing up - is the far end of the same side.
- **~196 is where the hand-built show aimed them**, its own `Escenario`
  (tilt 189-204, pan 156-162), which is the other way entirely.

So on a 7R the room opens up as the number *grows*: floor at 127, and the
crowd beyond it toward the show's own aim. The value here sits inside that
stretch, far enough past the floor that no beam figure falls back onto it and
short of the extreme.

The washes needed the same and have their own number, and it runs the other
way, because a raw tilt value is not comparable across models - the hand-built
show aims a 7R at 196 and a CromoWash at 46 for the same job. Their axis is
anchored by the hand-built show too:

- **128 is the back wall.** `Cabezas Reposo` parks every wash there, and it is
  what the owner saw under AUTO: "los washes apuntan para atrás a la pared, que
  no me interesa iluminar" (2026-08-29).
- **~46 is the room.** The hand-built `Escenario` aims CromoWash #1 at tilt 49
  and #2 at 43, pan 161/176 - down off the wall and out.

So the usable band is roughly 40 to 120, and the crowd sits inside it, between
the wall and the stage. That band is also why the wash figures shrank: a shape
55 tall around any centre in that band climbs back onto the wall, and a figure
that was never aimed was free to be as tall as it liked.

These are two numbers, on purpose, because they are two scales. They are first
aims in raw DMX like the fan's, to be nudged in the real room - and which way
is which is written above, per family, because guessing it cost a pass.
"""

# Tilt the beams' movement is built around: out over the crowd, not the floor
# and not the wall behind it.
BEAM_TILT_AIM = 170
# The same for the washes, on their own scale: off the back wall, into the room.
WASH_TILT_AIM = 88
