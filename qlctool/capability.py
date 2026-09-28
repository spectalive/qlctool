"""One labelled DMX range of a fixture definition channel."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Capability:
    """One labelled DMX range of a channel - a gobo, a colour, prism on/off."""

    minimum: int
    maximum: int
    name: str
    # The QLC+ capability preset, "" when the range carries none. This is how a
    # definition states what a range *is* rather than what it is called, which
    # matters for the ranges a generator has to find on its own: which value
    # opens a mechanical shutter, above all.
    preset: str = ""
    # `Res1` and `Res2`, verbatim: the colour a wheel slot shows (`#ff0000`),
    # the image a gobo slot projects (`BEAM-230W-7R/Gobo1.png`), the two ends
    # of a strobe range in hertz. A visualiser needs them; nothing else does.
    resource: str = ""
    resource2: str = ""

    @property
    def middle(self) -> int:
        """A value safely inside the range, which is what a scene should send."""
        return (self.minimum + self.maximum) // 2
