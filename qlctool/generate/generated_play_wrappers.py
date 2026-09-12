"""Generated wrapper IDs grouped by their JUGAR family."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedPlayWrappers:
    """Wrapper IDs grouped by the play page family that owns their buttons."""

    color_ids: list[int] = field(default_factory=list)
    rainbow_ids: list[int] = field(default_factory=list)
    panel_ids: list[int] = field(default_factory=list)
    movement_ids: list[int] = field(default_factory=list)
    gobo_ids: list[int] = field(default_factory=list)
    prism_ids: list[int] = field(default_factory=list)
