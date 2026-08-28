"""Per-group colour banks and the wheels that cycle them, as the show has them.

The hand-built show does not drive the whole rig as one colour: the heads, the
LED pars and the bars each have their own bank of colour scenes, and each bank
has a Random-order chaser - a "rueda de colores" - which is what actually runs
when nobody is at the console. This generates that shape: one scene per colour
per group, the two-colour splits, and a wheel for each.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from ..capabilities_of import capabilities_of
from ..fixture_group import DefinedFixtureGroup, fixture_groups
from ..functions.chaser import build_chaser
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..palette import PALETTE, PRIMARY_COLORS
from ..workspace import Workspace
from .color_scene import color_scene_values
from .split_color_scene import split_color_scene_values
from .wheel_color_values import wheel_color_values

# Enough pairs to keep a mix wheel interesting without hundreds of scenes.
SPLIT_COLORS: tuple[str, ...] = (
    "Rojo", "Azul", "Verde", "Amarillo", "Magenta", "Blanco",
)

# The hand-built console's keys 9 and 0 were not solid colours: on every bank
# they were the alternating two-colour looks, blue/red on 9 and red/blue on 0.
# The generator put Naranja and Rosa there instead - muscle-memory regression,
# old-vs-new audit 2026-08-28. These pairs go back on those keys; the two
# solids stay in the bank, keyless.
KEY_SPLIT_PAIRS: tuple[tuple[str, str], ...] = (("Azul", "Rojo"), ("Rojo", "Azul"))


@dataclass(frozen=True)
class GeneratedBank:
    group_name: str
    scene_ids: list[int] = field(default_factory=list)
    split_ids: list[int] = field(default_factory=list)
    wheel_id: int | None = None
    mix_wheel_id: int | None = None
    # What the console binds to keys 1-0: eight solids, then the old blue/red
    # and red/blue splits on 9 and 0. Falls back to plain solids when a group
    # cannot show a split.
    key_ids: list[int] = field(default_factory=list)


def generate_color_banks(
    workspace: Workspace,
    library: FixtureLibrary,
    colors: Sequence[str] = PRIMARY_COLORS,
    split_colors: Sequence[str] = SPLIT_COLORS,
    hold: int = 1500,
    fade: int = 400,
) -> list[GeneratedBank]:
    """One colour bank plus wheels per fixture group that can do colour."""
    caps = capabilities_of(workspace.root, library)
    banks: list[GeneratedBank] = []

    for group in fixture_groups(workspace.root):
        bank = _bank_for_group(
            workspace, caps, group, colors, split_colors, hold, fade
        )
        if bank is not None:
            banks.append(bank)
    return banks


def _bank_for_group(
    workspace: Workspace,
    caps,
    group: DefinedFixtureGroup,
    colors: Sequence[str],
    split_colors: Sequence[str],
    hold: int,
    fade: int,
) -> GeneratedBank | None:
    path = f"Colores {group.name}"
    scene_ids: list[int] = []
    for name in colors:
        values = color_scene_values(
            caps, PALETTE[name], fixture_ids=group.fixture_ids
        )
        # A group holding a BEAM 230W 7R holds a fixture with no red channel at
        # all. Colouring the group and skipping it is how the beams sat on last
        # night's colour while everything around them changed.
        values.update(
            wheel_color_values(caps, name, fixture_ids=group.fixture_ids)
        )
        if not values:
            return None  # no colour-capable fixture in this group
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_scene(function_id, f"{name} {group.name}", values, path=path)
        )
        scene_ids.append(function_id)

    split_ids: list[int] = []
    split_of: dict[tuple[str, str], int] = {}
    for first in split_colors:
        for second in split_colors:
            if first == second:
                continue
            values = split_color_scene_values(
                caps, PALETTE[first], PALETTE[second],
                fixture_ids=group.fixture_ids,
                color_names=(first, second),
            )
            if len(values) < 2:
                break  # a single fixture cannot show a split
            function_id = next_function_id(workspace.root)
            workspace.add_function(
                build_scene(
                    function_id,
                    f"{first} / {second} {group.name}",
                    values,
                    path=path,
                )
            )
            split_ids.append(function_id)
            split_of[(first, second)] = function_id

    # Keys 1-8 stay the first solids; 9 and 0 are the old blue/red pair. A
    # group whose splits never built (single fixture) keeps plain solids.
    key_splits = [split_of[pair] for pair in KEY_SPLIT_PAIRS if pair in split_of]
    if len(key_splits) == len(KEY_SPLIT_PAIRS):
        key_ids = scene_ids[: len(colors) - len(KEY_SPLIT_PAIRS)] + key_splits
    else:
        key_ids = list(scene_ids)

    wheel_id = _wheel(
        workspace, f"Rueda Colores {group.name}", scene_ids, hold, fade, path
    )
    mix_wheel_id = _wheel(
        workspace, f"Rueda Mezcla {group.name}", split_ids, hold, fade, path
    )
    return GeneratedBank(
        group_name=group.name,
        scene_ids=scene_ids,
        split_ids=split_ids,
        wheel_id=wheel_id,
        mix_wheel_id=mix_wheel_id,
        key_ids=key_ids,
    )


def _wheel(
    workspace: Workspace,
    name: str,
    scene_ids: list[int],
    hold: int,
    fade: int,
    path: str,
) -> int | None:
    """A Random-order chaser: unattended, a fixed order reads as a loop."""
    if not scene_ids:
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(
            function_id,
            name,
            scene_ids,
            fade_in=fade,
            hold=hold,
            fade_out=fade,
            run_order="Random",
            path=path,
        )
    )
    return function_id
