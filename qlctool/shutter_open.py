"""The value that opens a fixture's shutter, when it has one to open.

Raising the dimmer is not enough on a fixture with a mechanical shutter: a
BEAM 230W 7R at DMX 0 on its shutter channel is shut, dimmer at full or not, and
a Chauvet MiN Wash keeps its whole intensity on a shutter-style channel with no
separate dimmer at all. Both sat dark in every generated scene until this
existed - the hand-built show opened them by hand ("Luz ON Cabezas" sends 255 to
the beams' channel 6) and the generators did not.

The value is read out of the definition, never guessed: QLC+ marks the range
with the `ShutterOpen` preset, and a definition too old to carry presets is read
by the range's own name. A fixture with no such range - every LED PAR here,
whose shutter channel is only a strobe - is left alone.
"""

from . import roles
from .capability import FixtureCapabilities
from .definition import Capability
from .shutter_open_value import shutter_open_value

OPEN_PRESET = "ShutterOpen"


def shutter_open_pairs(capabilities: FixtureCapabilities) -> list[tuple[int, int]]:
    """(offset, value) putting every shutter this fixture has into its open range.

    Which value inside that range is `shutter_open_value`'s question: not the
    middle, which is where the beams stayed dark on 2026-08-29.
    """
    return [
        (offset, shutter_open_value(opening))
        for offset, opening in shutter_open_ranges(capabilities)
    ]


def shutter_open_ranges(
    capabilities: FixtureCapabilities,
) -> list[tuple[int, Capability]]:
    """(offset, the range that counts as open) for every shutter it has.

    The range, not just a value, because whether a fixture is open depends on
    where its shutter *is*, not on whether anybody wrote to it. A CLB2.4 head
    labels DMX 0 "no strobe", so an untouched channel is already open; a BEAM
    230W 7R puts open near the top, so an untouched channel is shut. Only the
    range can tell those apart, and getting it wrong is either a fixture
    reported dark that is fine or a fixture dark that nobody warned about.
    """
    found: list[tuple[int, Capability]] = []
    for offset, ranges in capabilities.capabilities_for_role(roles.STROBE):
        opening = _open_range(ranges)
        if opening is not None:
            found.append((offset, opening))
    return found


def _open_range(ranges: tuple[Capability, ...]) -> Capability | None:
    """The last open range on the channel.

    Last, not first, because a shutter channel that has two of them puts one
    just above "closed" at the bottom and one at the very top; the top one is
    the one clear of the closed range, and the one the hand-built show used.
    """
    by_preset = [r for r in ranges if r.preset == OPEN_PRESET]
    if by_preset:
        return by_preset[-1]
    by_name = [r for r in ranges if r.name.strip().lower() == "open"]
    return by_name[-1] if by_name else None
