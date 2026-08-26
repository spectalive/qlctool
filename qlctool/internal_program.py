"""The programs a fixture runs by itself, and the channel that switches them on.

Some fixtures are small lighting desks. The HYULIGHTS panels carry forty-two
built-in effects, twelve colour ones and two sound-reactive modes, all of them
reached through one **mode** channel that decides whether the fixture obeys DMX
colour at all or runs its own show. Leave that channel where an untouched
channel sits - zero, "No function" - and the fixture is four RGB cells and
nothing else, which is how this rig used them for years: "estos cacharros
tienen animaciones muy chulas que no estamos aprovechando" (owner, 2026-08-26).

Two things follow, and both are traps.

A fixture running its own program **ignores the red, green and blue** it is
sent. So a colour wheel painting it is painting nothing, and something has to
choose: the rig's colour, or the fixture's own animation.

And the mode channel is sticky. Nothing resets it, so a look that wants direct
colour has to say so - drive the mode back to off - or the panel keeps running
last night's effect through a speech.
"""

from dataclasses import dataclass

from . import roles
from .capability import FixtureCapabilities
from .definition import Capability

# The range name that marks the mode channel's "obey DMX" position.
OFF_NAMES = ("no function", "off", "no funcion")
# The range name that marks the position where the fixture runs its own show.
AUTO_NAMES = ("auto",)


@dataclass(frozen=True)
class InternalProgram:
    """A fixture's self-running effects: how to switch them on and pick one."""

    mode_offset: int
    off_value: int
    auto_value: int
    effect_offset: int
    effects: tuple[Capability, ...]
    speed_offset: int | None

    @property
    def count(self) -> int:
        return len(self.effects)


def internal_program(capabilities: FixtureCapabilities) -> InternalProgram | None:
    """Resolve the fixture's own-program channels, or None when it has none.

    Recognised by shape, never by model: one effect channel whose ranges name a
    mode - one of them "no function", another an automatic one - and a second
    effect channel carrying the list of programs to choose from.
    """
    channels = capabilities.capabilities_for_role(roles.EFFECT)
    if len(channels) < 2:
        return None

    mode = _mode_channel(channels)
    if mode is None:
        return None
    mode_offset, off_range, auto_range = mode

    effects = max(
        (item for item in channels if item[0] != mode_offset),
        key=lambda item: len(item[1]),
    )
    if len(effects[1]) < 2:
        return None

    speed = capabilities.offsets_for_role(roles.SPEED)
    return InternalProgram(
        mode_offset=mode_offset,
        off_value=off_range.middle,
        auto_value=auto_range.middle,
        effect_offset=effects[0],
        effects=effects[1],
        speed_offset=speed[0] if speed else None,
    )


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


def _mode_channel(channels) -> tuple[int, Capability, Capability] | None:
    for offset, ranges in channels:
        off = _named(ranges, OFF_NAMES)
        auto = _named(ranges, AUTO_NAMES)
        if off is not None and auto is not None:
            return offset, off, auto
    return None


def _named(ranges: tuple[Capability, ...], wanted: tuple[str, ...]):
    for capability in ranges:
        name = capability.name.strip().lower()
        if any(name.startswith(word) for word in wanted):
            return capability
    return None
