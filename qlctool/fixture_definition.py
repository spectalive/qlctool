"""Everything a QLC+ fixture definition (.qxf) says about one model."""

from dataclasses import dataclass, field

from .channel import Channel
from .definition import Capability
from .dimensions import Dimensions
from .optics import Optics


@dataclass(frozen=True)
class FixtureDefinition:
    manufacturer: str
    model: str
    # <Type>: Moving Head, Color Changer, Smoke, ... - a smoke machine must
    # never be swept up in a "all dimmers to full" scene.
    fixture_type: str
    # channel name -> Channel
    channels: dict[str, Channel]
    # mode name -> ordered list of channel names
    modes: dict[str, list[str]]
    # mode name -> each declared <Head>'s channel offsets. Empty when the mode
    # declares none, which is not the same as "one head": QLC+ then builds a
    # single head holding every channel, and a head keeps only the *last*
    # channel of each colour it finds (`QLCFixtureHead::cacheChannels`). A
    # fixture with three RGB rings and no heads therefore offers a matrix one
    # ring, silently.
    heads: dict[str, tuple[tuple[int, ...], ...]] = field(default_factory=dict)
    dimensions: Dimensions | None = None
    optics: Optics | None = None

    def mode_heads(self, mode: str) -> tuple[tuple[int, ...], ...]:
        """The channel offsets of each <Head> the mode declares."""
        return self.heads.get(mode, ())

    def mode_roles(self, mode: str) -> list[str | None]:
        """Roles in channel order for a mode, index-aligned with DMX offset."""
        return [self.channels[c].role for c in self.modes[mode]]

    def mode_capabilities(self, mode: str) -> list[tuple[Capability, ...]]:
        """Each offset's labelled ranges, index-aligned with mode_roles."""
        return [self.channels[c].capabilities for c in self.modes[mode]]

    def mode_groups(self, mode: str) -> list[str]:
        """Each offset's QLC+ channel group, index-aligned with mode_roles."""
        return [self.channels[c].group for c in self.modes[mode]]
