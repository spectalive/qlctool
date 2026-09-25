"""Per-group colour banks and the wheels that cycle them, as the show has them.

The hand-built show does not drive the whole rig as one colour: the heads, the
LED pars and the bars each have their own bank of colour scenes, and each bank
has a Random-order chaser - a "rueda de colores" - which is what actually runs
when nobody is at the console. This generates that shape: one scene per colour
per group, the two-colour splits, and a wheel for each.
"""

from collections.abc import Mapping, Sequence

from ..argb import RGB
from ..capabilities_of import capabilities_of
from ..fixture_group import fixture_groups
from ..key_split_pairs import KEY_SPLIT_PAIRS
from ..library import FixtureLibrary
from ..names.default_names import default_names
from ..names.names import Names
from ..palette import PALETTE, PRIMARY_COLORS
from ..split_pairs import SPLIT_PAIRS
from ..wheel_palette import WHEEL_PALETTE
from ..workspace import Workspace
from .bank_for_group import bank_for_group
from .generated_bank import GeneratedBank


def generate_color_banks(
    workspace: Workspace,
    library: FixtureLibrary,
    colors: Sequence[str] = PRIMARY_COLORS,
    split_pairs: Sequence[tuple[str, str]] = SPLIT_PAIRS,
    hold: int = 1500,
    fade: int = 400,
    exclude_effect_mode_fixture_ids: Sequence[int] = (),
    palette: Mapping[str, RGB] | None = None,
    wheel_palette: Mapping[str, RGB] | None = None,
    key_split_pairs: Sequence[tuple[str, str]] = KEY_SPLIT_PAIRS,
    names: Names | None = None,
) -> list[GeneratedBank]:
    """One colour bank plus wheels per fixture group that can do colour.

    `names` is the show's vocabulary: the colour names are spelled in it, and
    the banks' folders and wheels are named from it.
    """
    vocabulary = default_names() if names is None else names
    caps = capabilities_of(workspace.root, library)
    banks: list[GeneratedBank] = []
    values_of = PALETTE if palette is None else palette
    wheel_of = WHEEL_PALETTE if wheel_palette is None else wheel_palette

    for group in fixture_groups(workspace.root):
        bank = bank_for_group(
            workspace,
            caps,
            group,
            colors,
            split_pairs,
            hold,
            fade,
            exclude_effect_mode_fixture_ids,
            values_of,
            wheel_of,
            key_split_pairs,
            vocabulary,
        )
        if bank is not None:
            banks.append(bank)
    return banks
