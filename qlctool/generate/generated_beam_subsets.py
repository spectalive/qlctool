"""What generate_beam_subsets built: the prism and multicolor accent scenes."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedBeamSubsets:
    prism_scene_ids: list[int] = field(default_factory=list)
    multicolor_scene_ids: list[int] = field(default_factory=list)
