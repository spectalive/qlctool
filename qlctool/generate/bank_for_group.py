"""One fixture group's colour bank: a scene per colour, the splits, and their wheels."""

from collections.abc import Mapping, Sequence

from ..argb import RGB
from ..fixture_group import DefinedFixtureGroup
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..names.names import Names
from ..workspace import Workspace
from .bank_wheel import bank_wheel
from .color_scene import color_scene_values
from .generated_bank import GeneratedBank
from .split_color_scene import split_color_scene_values
from .wheel_color_values import wheel_color_values


def bank_for_group(
    workspace: Workspace,
    caps,
    group: DefinedFixtureGroup,
    colors: Sequence[str],
    split_pairs: Sequence[tuple[str, str]],
    hold: int,
    fade: int,
    exclude_effect_mode_fixture_ids: Sequence[int],
    values_of: Mapping[str, RGB],
    wheel_of: Mapping[str, RGB],
    key_split_pairs: Sequence[tuple[str, str]],
    vocabulary: Names,
) -> GeneratedBank | None:
    path = vocabulary.render("path_group_colours", group=group.name)
    scene_ids: list[int] = []
    # The bank keeps white - key 8 is a hand pick, and a hand may ask for it -
    # but the group's wheel never steps it (`wheel_palette`, 2026-09-22).
    wheel_scene_ids: list[int] = []
    for name in colors:
        # Colour only, no intensity: a bank is a held takeover (a Flash with
        # ForceLTP on the console) of the colour the state is showing, and the
        # state keeps owning the dimmers - a bank that opened them was one
        # more HTP bid and one more thing a released hand left behind.
        values = color_scene_values(
            caps,
            values_of[name],
            fixture_ids=group.fixture_ids,
            dimmer_full=False,
            exclude_effect_mode_fixture_ids=exclude_effect_mode_fixture_ids,
        )
        # A group holding a BEAM 230W 7R holds a fixture with no red channel at
        # all. Colouring the group and skipping it is how the beams sat on last
        # night's colour while everything around them changed.
        values.update(
            wheel_color_values(
                caps, name, fixture_ids=group.fixture_ids, dimmer=None, names=vocabulary
            )
        )
        if not values:
            return None  # no colour-capable fixture in this group
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_scene(function_id, f"{name} {group.name}", values, path=path))
        scene_ids.append(function_id)
        if name in wheel_of:
            wheel_scene_ids.append(function_id)

    split_ids: list[int] = []
    split_of: dict[tuple[str, str], int] = {}
    for first, second in split_pairs:
        values = split_color_scene_values(
            caps,
            values_of[first],
            values_of[second],
            fixture_ids=group.fixture_ids,
            color_names=(first, second),
            dimmer_full=False,
            exclude_effect_mode_fixture_ids=exclude_effect_mode_fixture_ids,
            names=vocabulary,
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
    key_splits = [split_of[pair] for pair in key_split_pairs if pair in split_of]
    if len(key_splits) == len(key_split_pairs):
        key_ids = scene_ids[: len(colors) - len(key_split_pairs)] + key_splits
    else:
        key_ids = list(scene_ids)

    wheel_name = vocabulary.render("group_colour_wheel", group=group.name)
    mix_name = vocabulary.render("group_mix_wheel", group=group.name)
    wheel_id = bank_wheel(workspace, wheel_name, wheel_scene_ids, hold, fade, path)
    mix_wheel_id = bank_wheel(workspace, mix_name, split_ids, hold, fade, path)
    return GeneratedBank(
        group_name=group.name,
        scene_ids=scene_ids,
        split_ids=split_ids,
        wheel_id=wheel_id,
        mix_wheel_id=mix_wheel_id,
        key_ids=key_ids,
    )
