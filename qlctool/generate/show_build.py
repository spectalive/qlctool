"""Everything `build_canonical_show` carries from one stage of the show to the next.

The show used to be built by one function of a thousand lines whose locals
were this state. Each stage now lives in its own module (`add_*`) and reads
and writes it here, in the order the functions must be created: the function
ids are handed out in creation order, so the stages run in the order the one
function ran its lines, and the Vibra workspaces stay byte for byte what they
were (2026-09-26, round G).

A field is set by the stage that makes it; reading it before is an
AttributeError, never a silent default.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from ..argb import RGB
from ..capability import FixtureCapabilities
from ..controllers.midi_pad_profile import MidiPadProfile
from ..description.show_description import ShowDescription
from ..library import FixtureLibrary
from ..names.names import Names
from ..vc.dial_function import DialFunction
from ..workspace import Workspace
from .beam_subsets import GeneratedBeamSubsets
from .builtin_effects import GeneratedBuiltins
from .dimmer_chases import GeneratedDimmers
from .energy_intensity import GeneratedIntensity
from .generated_bank import GeneratedBank
from .generated_matrices import GeneratedMatrices
from .generated_play_wrappers import GeneratedPlayWrappers
from .gobo_shake import GeneratedGoboShake
from .movement_families import GeneratedFamilies
from .prism_spins import GeneratedPrismSpins
from .unison_colors import GeneratedUnison
from .wheel_scenes import GeneratedWheel


@dataclass
class ShowBuild:
    """The show under construction and every generated part a later stage needs."""

    workspace: Workspace
    library: FixtureLibrary
    vocabulary: Names
    described: ShowDescription
    wheel: dict[str, RGB]
    pastels: dict[str, RGB]
    contrasts: tuple[tuple[str, str], ...]
    beats: bool
    pad: MidiPadProfile | None
    stage_placed: int
    caps: list[FixtureCapabilities]
    master: dict[str, int] = field(default_factory=dict)

    # Set by `build_canonical_show` straight from its arguments.
    bpm_tap: bool = field(init=False)
    algorithms: Sequence[str | None] = field(init=False)
    matrix_colors: Sequence[str] | None = field(init=False)
    colour_flash_ids: dict[str, int] = field(init=False)
    builtins: GeneratedBuiltins = field(init=False)
    banks: list[GeneratedBank] = field(init=False)
    panel_manual_id: int | None = field(init=False)
    panel_cycle_id: int | None = field(init=False)
    beam_spin_id: int | None = field(init=False)
    matrices: list[GeneratedMatrices] = field(init=False)
    matrix_lit_ids: set[int] = field(init=False)
    matrix_ids: list[int] = field(init=False)
    charla_pixel_intensity_id: int | None = field(init=False)
    paneles_charla_id: int | None = field(init=False)
    pixel_layer: list[int] = field(init=False)
    step_matrices: dict[str, list[int]] = field(init=False)
    pastel_step_matrices: dict[str, list[int]] = field(init=False)
    movement: GeneratedFamilies = field(init=False)
    home_id: int | None = field(init=False)
    stage_aim_id: int | None = field(init=False)
    shake: GeneratedGoboShake = field(init=False)
    dealt: list[int] = field(init=False)
    gobos: GeneratedWheel = field(init=False)
    beam_colors: GeneratedWheel = field(init=False)
    prisms: GeneratedWheel = field(init=False)
    spins: GeneratedPrismSpins = field(init=False)
    beam_subsets: GeneratedBeamSubsets = field(init=False)
    gobo_rest_id: int | None = field(init=False)
    prism_rest_id: int | None = field(init=False)
    dimmers: GeneratedDimmers | None = field(init=False)
    unison: GeneratedUnison = field(init=False)
    rainbow_ids: list[int] = field(init=False)
    gobo_open_id: int | None = field(init=False)
    prism_off_id: int | None = field(init=False)
    intensity: GeneratedIntensity = field(init=False)
    charla_intensity_ids: list[int | None] = field(init=False)
    peak_static: int | None = field(init=False)
    dimmer_programs_id: int | None = field(init=False)
    play_wrappers: GeneratedPlayWrappers = field(init=False)
    tempo_functions: list[DialFunction] = field(init=False)
    movement_functions: list[DialFunction] = field(init=False)
