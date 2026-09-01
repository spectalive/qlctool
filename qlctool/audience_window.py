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

from dataclasses import dataclass


@dataclass(frozen=True)
class Window:
    """A rectangle in raw DMX: where a head is pointing at the people."""

    pan_min: int
    pan_max: int
    tilt_min: int
    tilt_max: int

    @property
    def pan_centre(self) -> int:
        return (self.pan_min + self.pan_max) // 2

    @property
    def tilt_centre(self) -> int:
        return (self.tilt_min + self.tilt_max) // 2

    @property
    def pan_span(self) -> int:
        return (self.pan_max - self.pan_min) // 2

    @property
    def tilt_span(self) -> int:
        return (self.tilt_max - self.tilt_min) // 2

    def holds(self, centre: int, span: int, axis: str) -> bool:
        """Whether a figure of this half-size around this centre stays inside."""
        low, high = (
            (self.pan_min, self.pan_max) if axis == "pan" else (self.tilt_min, self.tilt_max)
        )
        return low <= centre - span and centre + span <= high


BEAM_WINDOW = Window(pan_min=62, pan_max=103, tilt_min=207, tilt_max=234)
WASH_WINDOW = Window(pan_min=76, pan_max=108, tilt_min=212, tilt_max=230)
