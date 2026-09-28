"""(offset, value) pairs that put a fixture back under DMX colour control."""

from .fixture_capabilities import FixtureCapabilities
from .internal_program import internal_program


def internal_program_off_pairs(
    capabilities: FixtureCapabilities,
) -> list[tuple[int, int]]:
    """(offset, value) putting the fixture back under DMX colour control.

    Empty for a fixture with no programs of its own. Every scene that states a
    colour carries these, for the same reason it carries the shutter: a channel
    nobody writes keeps whatever the last look left there.
    """
    program = internal_program(capabilities)
    return [] if program is None else [(program.mode_offset, program.off_value)]
