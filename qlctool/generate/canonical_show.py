"""What `build_canonical_show` hands back: the ids the CLI and the tests read."""

from dataclasses import dataclass, field

from .generated_bank import GeneratedBank
from .generated_play_wrappers import GeneratedPlayWrappers


@dataclass(frozen=True)
class CanonicalShow:
    """The generated show's parts, by function id, and how many functions it has."""

    banks: list[GeneratedBank] = field(default_factory=list)
    matrix_ids: list[int] = field(default_factory=list)
    efx_ids: list[int] = field(default_factory=list)
    gobo_ids: list[int] = field(default_factory=list)
    prism_ids: list[int] = field(default_factory=list)
    play_wrappers: GeneratedPlayWrappers = field(default_factory=GeneratedPlayWrappers)
    colour_flash_ids: dict[str, int] = field(default_factory=dict)
    master_ids: dict[str, int] = field(default_factory=dict)
    button_ids: list[int] = field(default_factory=list)
    function_count: int = 0
    stage_placed: int = 0
