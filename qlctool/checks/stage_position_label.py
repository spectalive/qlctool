"""One row position, in millimetres, or the not-rigged phrase for a spare."""

from .phrase import Phrase


def stage_position_label(key: tuple[bool, float]) -> Phrase | str:
    return Phrase("grid_order_not_rigged") if key[0] else f"{key[1]:.0f} mm"
