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

The washes were guessed at twice as well - the back wall at 128 and the
hand-built `Escenario` at tilt 43-49 were the only anchors, and neither is the
crowd. They have a measured window of their own now, read off MAC WASH 1915Z
#1: pan 76-108, tilt 212-230. Same treatment, same arithmetic, its own numbers.
"""

from ..audience_window import BEAM_WINDOW, WASH_WINDOW

# The centre of the measured window, and the half-size of a figure drawn around
# it. Both come off `audience_window` so the check and the generator cannot
# drift apart - a figure sized here is a figure the rule will pass.
BEAM_PAN_AIM = BEAM_WINDOW.pan_centre
BEAM_PAN_SPAN = BEAM_WINDOW.pan_span
BEAM_TILT_AIM = BEAM_WINDOW.tilt_centre
BEAM_TILT_SPAN = BEAM_WINDOW.tilt_span
# The same for the washes, off their own window.
WASH_PAN_AIM = WASH_WINDOW.pan_centre
WASH_PAN_SPAN = WASH_WINDOW.pan_span
WASH_TILT_AIM = WASH_WINDOW.tilt_centre
WASH_TILT_SPAN = WASH_WINDOW.tilt_span
