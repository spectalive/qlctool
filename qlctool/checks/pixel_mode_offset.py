"""The channel that switches a pixel panel between its own programme and the desk.

Not any Effect channel: every colour look parks a stray self-running channel
at zero (`mode_park_pairs`), and on an RGB par with one "auto show" channel
that made every colour scene a pixel-mode owner (round G review, 2026-09-26:
the CLB2.4 in its 2 and 7 channel modes). Only the mode channel of a panel's
named internal programme is the pixel-mode family.
"""

from ..capability import FixtureCapabilities
from ..internal_program import internal_program
from .is_pixel_fixture import is_pixel_fixture


def pixel_mode_offset(capability: FixtureCapabilities) -> int | None:
    """The panel's programme mode offset; None for anything that is not a pixel panel."""
    program = internal_program(capability) if is_pixel_fixture(capability) else None
    return None if program is None else program.mode_offset
