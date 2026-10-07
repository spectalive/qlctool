"""The corner-to-corner pan and tilt inside which a 7R is on the audience.

Measured on the desk, head by head, by the owner on 2026-08-29, after two
guesses at which way to move the beams had put them on the floor and then on
the wall behind: "eso son los rangos del publico, todo lo fuera de eso (cabeza
1) ya apunta a fuera". The reading is BEAM 230W 7R #1, DMX 219.

It is a *window*, not a centre, and that is what makes it useful: a figure is
right when the whole figure fits inside it, which is a thing a check can ask.
The hand-built show's own `Escenario` sits just below it at tilt 189-204 - the
stage rather than the crowd - and the two bands touching is what says these
numbers describe the real room.

The washes were measured the same way, on MAC WASH 1915Z #1 (DMX 345): pan 76
to 108, tilt 212 to 230. A raw value is not comparable across models, so the
two windows are separate numbers - but they describe the same room, and they
land in the same place, which is the best evidence either of them is right.

Only head #1 of each family has been read. The others sit at their own places
on the truss and their windows will be shifted in pan; until somebody reads
them the family shares one window, which is why the figures are drawn inside it
rather than filling it.
"""

from .audience_window import AudienceWindow

BEAM_WINDOW = AudienceWindow(pan_min=62, pan_max=103, tilt_min=207, tilt_max=234)
WASH_WINDOW = AudienceWindow(pan_min=76, pan_max=108, tilt_min=212, tilt_max=230)
