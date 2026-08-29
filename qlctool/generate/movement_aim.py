"""The window a beam figure has to stay inside, measured in the room.

Every movement EFX this repo ever generated sat at the QLC+ default - X 127,
Y 127, the raw middle of pan and tilt - because `EFXAxis.offset` defaults there
and no caller had ever overridden it. Mid-travel is not an aim, it is the
absence of one: it put the beams on the floor ("está todo el rato haciendo un
circulo pequeño en el suelo"), and two guesses at which way to move them landed
on the wall behind instead ("ahora los 7R apuntan a la pared"). Both guesses
were about *direction*, which is not a thing to guess.

So the owner measured it on the desk, head by head, and sent the corners. On
BEAM 230W 7R #1 (DMX 219) the audience is:

    pan  62 .. 103      tilt  207 .. 234

"Eso son los rangos del publico, todo lo fuera de eso ya apunta a fuera"
(2026-08-29). It is a window, not a centre, and that is the useful shape: a
figure is right when the whole figure fits inside it. The hand-built show's own
`Escenario` sits just under it at tilt 189-204, which is the stage rather than
the crowd - the two bands touching is what says these numbers are real.

The beams' figures are therefore sized by the window, not by taste. A 2-degree
needle that leaves it is not a bigger look, it is a beam in the car park.

The washes have their own scale - a raw tilt value is not comparable across
models - anchored by the hand-built show and by what the owner saw:

- **128 is the back wall.** `Cabezas Reposo` parks every wash there: "los
  washes apuntan para atrás a la pared, que no me interesa iluminar".
- **~46 is the room.** `Escenario` aims CromoWash #1 at tilt 49 and #2 at 43.

Their window has not been measured head by head, so their figures are still
sized by feel, kept inside 40-120.
"""

from ..audience_window import BEAM_WINDOW

# The centre of the measured window, and the half-size of a figure drawn around
# it. Both come off `audience_window` so the check and the generator cannot
# drift apart - a figure sized here is a figure the rule will pass.
BEAM_PAN_AIM = BEAM_WINDOW.pan_centre
BEAM_PAN_SPAN = BEAM_WINDOW.pan_span
BEAM_TILT_AIM = BEAM_WINDOW.tilt_centre
BEAM_TILT_SPAN = BEAM_WINDOW.tilt_span
# The washes, on their own scale: off the back wall, down into the room.
WASH_TILT_AIM = 88
