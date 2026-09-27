"""What generate_color_palette built: the palette's scenes and its cycle chaser."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedPalette:
    scene_ids: list[int]
    chaser_id: int | None
