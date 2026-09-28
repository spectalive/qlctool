"""A fixture's self-running effects: how to switch them on and pick one.

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

from .capability import Capability


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
