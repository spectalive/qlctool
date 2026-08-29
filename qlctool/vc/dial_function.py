"""One function under a speed dial, and how much of the dial's time it takes.

The dial holds one time - one tap - and each function states its own multiple
of it, separately for the duration and for the fade. Both matter together on a
crossfading chaser: QLC+ gives the fade to whatever the chaser starts, and an
EFX subtracts it from its own duration to get the figure it draws
(`EFX::loopDuration`). Scale the duration and leave the fade at a fixed number
of milliseconds and the figure stops being a proportion of the step - which is
how a 16 s head sweep once became a 6 s one.
"""

from dataclasses import dataclass

from .speed_dial import MULTIPLIER_NONE


@dataclass(frozen=True)
class DialFunction:
    """A function id and its QLC+ speed multipliers - see `MULTIPLIERS`."""

    function_id: int
    duration: int
    fade: int = MULTIPLIER_NONE
