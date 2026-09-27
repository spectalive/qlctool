"""Pad numbers row by row from the top, the order a person sees them."""

from .smc_pad_device import PADS

PADS_PER_ROW = 4


def pads_top_down() -> list[int]:
    rows = PADS // PADS_PER_ROW
    return [
        pad
        for row in range(rows - 1, -1, -1)
        for pad in range(row * PADS_PER_ROW + 1, (row + 1) * PADS_PER_ROW + 1)
    ]
