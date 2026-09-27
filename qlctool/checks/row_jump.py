"""One step of a row, with the not-rigged fixtures named as such."""

from .joined import Joined
from .stage_position_label import stage_position_label


def row_jump(before: tuple[bool, float], after: tuple[bool, float]) -> Joined:
    """One step of the row, with the not-rigged fixtures named as such."""
    return Joined((stage_position_label(before), stage_position_label(after)), "->")
