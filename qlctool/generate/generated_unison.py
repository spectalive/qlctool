"""What generate_unison_colors built: the rig-wide colour scenes and wheel."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedUnison:
    scene_ids: list[int] = field(default_factory=list)
    contrast_ids: list[int] = field(default_factory=list)
    wheel_id: int | None = None
    # What the wheel steps for each plain colour: the scene, or the Collection
    # that starts it beside the pixel groups' matrix of the same colour. These
    # are what a hand pick has to start, so the bars follow a picked colour the
    # way they follow a stepped one.
    solid_step_ids: list[int] = field(default_factory=list)
