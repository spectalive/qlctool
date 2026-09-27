"""Whether the range holding a value spins the wheel rather than naming."""

from ..definition import Capability

ROTATION_PRESET_PREFIX = "Rotation"


def is_rotation(positions: tuple[Capability, ...], value: int) -> bool:
    for position in positions:
        if position.minimum <= value <= position.maximum:
            return (position.preset or "").startswith(ROTATION_PRESET_PREFIX)
    return False
