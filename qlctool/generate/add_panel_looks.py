"""The panels' built-in programmes, the colour banks and the panels' cycles.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from ..description.split_pairs_of import split_pairs_of
from .builtin_effects import generate_builtin_effects
from .generate_color_banks import generate_color_banks
from .panel_manual import generate_panel_manual
from .panel_speed_auto import generate_panel_speed_auto
from .show_build import ShowBuild
from .show_chaser import show_chaser
from .vertical_smoke_light import generate_vertical_smoke_light


def add_panel_looks(build: ShowBuild) -> None:
    """The panels' programmes and cycles, and every group's colour bank."""
    workspace = build.workspace
    library = build.library
    caps = build.caps
    vocabulary = build.vocabulary
    described = build.described
    wheel = build.wheel
    master = build.master
    colours = build.described.colours
    # The panels' own forty-two programmes. Nobody has watched them yet, so
    # every one is generated and the cycle is slow enough to see them.
    builtins = generate_builtin_effects(
        workspace, caps, label=vocabulary.display("panels_label"), names=vocabulary
    )
    banks = generate_color_banks(
        workspace,
        library,
        exclude_effect_mode_fixture_ids=builtins.fixture_ids,
        colors=colours.primary,
        split_pairs=split_pairs_of(colours),
        palette=colours.palette,
        wheel_palette=wheel,
        key_split_pairs=colours.key_split_pairs,
        names=vocabulary,
    )
    if builtins.chaser_id is not None:
        master[vocabulary.display("panel_effects")] = builtins.chaser_id
    # The two phases in one chaser: steps are alternatives, so the mode
    # channel always has exactly one owner, and Loop - never Random - because
    # the alternation is the point.
    panel_manual_id = generate_panel_manual(workspace, caps, builtins.fixture_ids, names=vocabulary)
    panel_cycle_id = builtins.chaser_id
    if builtins.chaser_id is not None and panel_manual_id is not None:
        panel_cycle_id = show_chaser(
            workspace,
            vocabulary.display("panel_cycle"),
            [builtins.chaser_id, panel_manual_id],
            holds=[described.timing.panel_effects_ms, described.timing.panel_manual_ms],
            path=vocabulary.display("path_builtin_effects"),
        )
        master[vocabulary.display("panel_cycle")] = panel_cycle_id
    # The vertical smoke's companion light: the panels on the two colour
    # cycles the hand-built show held up while the column fired.
    vertical_id = generate_vertical_smoke_light(
        workspace, builtins.scene_ids, caps, names=vocabulary
    )
    if vertical_id is not None:
        master[vocabulary.display("vertical_smoke")] = vertical_id
    # The old "Strobo LED - Speed Auto": the panels' pace riding up and down
    # on its own, beside the manual fader (HTP - whichever is higher wins).
    speed_auto_id = generate_panel_speed_auto(workspace, builtins.speed_channels, names=vocabulary)
    if speed_auto_id is not None:
        master[vocabulary.display("panel_speed_auto")] = speed_auto_id
    build.builtins = builtins
    build.banks = banks
    build.panel_manual_id = panel_manual_id
    build.panel_cycle_id = panel_cycle_id
