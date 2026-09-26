"""One fixture group's colour bank: a scene per colour, the splits, and their wheels."""

from collections.abc import Mapping, Sequence

from ..argb import RGB
from ..capability import FixtureCapabilities
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
from .without_wheel_blades import without_wheel_blades


def bank_for_group(
    workspace: Workspace,
    caps: list[FixtureCapabilities],
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
    extra_fixture_ids: Sequence[int] = (),
) -> GeneratedBank | None:
    """The bank's scenes, splits and wheels; None when the group mixes no colour.

    `extra_fixture_ids` are colour fixtures in no group (ruling D9,
    2026-09-26): they join the solids and the splits the keys press - the
    bank's key scenes - after the group's own members, and never become
    cells of its grid.
    """
    path = vocabulary.render("path_group_colours", group=group.name)
    # The splits are worked out first, so the solids know whether the keys
    # end on splits (9 and 0) and which solids are keyed; they are still added
    # after the solids, which keeps every function ID where it was.
    split_values: list[tuple[tuple[str, str], dict[int, list[tuple[int, int]]]]] = []
    for first, second in split_pairs:
        keyed = (first, second) in key_split_pairs
        split = split_color_scene_values(
            caps,
            values_of[first],
            values_of[second],
            fixture_ids=[*group.fixture_ids, *extra_fixture_ids] if keyed else group.fixture_ids,
            color_names=(first, second),
            dimmer_full=False,
            exclude_effect_mode_fixture_ids=exclude_effect_mode_fixture_ids,
            names=vocabulary,
        )
        # A single fixture cannot show a split; the extras do not make one.
        if len(split.keys() & set(group.fixture_ids)) < 2:
            break
        split_values.append(((first, second), without_wheel_blades(caps, split)))
    built = {pair for pair, _ in split_values}
    keyed_solids = len(colors)
    if all(pair in built for pair in key_split_pairs):
        keyed_solids -= len(key_split_pairs)

    scene_ids: list[int] = []
    # The bank keeps white - key 8 is a hand pick, and a hand may ask for it -
    # but the group's wheel never steps it (`wheel_palette`, 2026-09-22).
    wheel_scene_ids: list[int] = []
    for index, name in enumerate(colors):
        extras = extra_fixture_ids if index < keyed_solids else ()
        # Colour only, no intensity: a bank is a held takeover (a Flash with
        # ForceLTP on the console) of the colour the state is showing, and the
        # state keeps owning the dimmers - a bank that opened them was one
        # more HTP bid and one more thing a released hand left behind.
        values = color_scene_values(
            caps,
            values_of[name],
            fixture_ids=[*group.fixture_ids, *extras],
            dimmer_full=False,
            exclude_effect_mode_fixture_ids=exclude_effect_mode_fixture_ids,
        )
        # A group holding a BEAM 230W 7R holds a fixture with no red channel at
        # all. Colouring the group and skipping it is how the beams sat on last
        # night's colour while everything around them changed.
        values.update(
            without_wheel_blades(
                caps,
                wheel_color_values(
                    caps, name, fixture_ids=group.fixture_ids, dimmer=None, names=vocabulary
                ),
            )
        )
        if not values.keys() & set(group.fixture_ids):
            return None  # no colour-capable fixture in this group
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_scene(function_id, f"{name} {group.name}", values, path=path))
        scene_ids.append(function_id)
        if name in wheel_of:
            wheel_scene_ids.append(function_id)

    split_ids: list[int] = []
    split_of: dict[tuple[str, str], int] = {}
    for (first, second), split in split_values:
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_scene(
                function_id,
                f"{first} / {second} {group.name}",
                split,
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
