"""One tile's top-left corner in a family frame's button grid."""

from .play_page_layout import GAP


def grid_position(index: int, columns: int, pitch: int, top: int) -> tuple[int, int]:
    return GAP + (index % columns) * pitch, top + (index // columns) * 46
