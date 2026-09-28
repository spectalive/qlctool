"""Where a strobing value sits on its channel's slow-to-fast run."""

from ..capability import Capability

FAST_TO_SLOW_PRESET = "StrobeFastToSlow"


def speed_fraction(strobing: Capability | None, value: int) -> float:
    """Where a strobing value sits on its channel's slow-to-fast run."""
    if strobing is None:
        return value / 255
    span = strobing.maximum - strobing.minimum
    if span == 0:
        return 1.0
    fraction = (value - strobing.minimum) / span
    if strobing.preset == FAST_TO_SLOW_PRESET:
        return 1.0 - fraction
    return fraction
