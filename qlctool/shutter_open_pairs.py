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

from .fixture_capabilities import FixtureCapabilities
from .shutter_open_ranges import shutter_open_ranges
from .shutter_open_value import shutter_open_value


def shutter_open_pairs(capabilities: FixtureCapabilities) -> list[tuple[int, int]]:
    """(offset, value) putting every shutter this fixture has into its open range.

    Which value inside that range is `shutter_open_value`'s question: not the
    middle, which is where the beams stayed dark on 2026-08-29.
    """
    return [
        (offset, shutter_open_value(opening))
        for offset, opening in shutter_open_ranges(capabilities)
    ]
