"""Rename every colour and function a description names, leaving its values alone."""

from collections.abc import Callable
from dataclasses import replace

from ..color_pair import ColorPair
from .show_description import ShowDescription


def rename_description(
    description: ShowDescription,
    colour: Callable[[str], str],
    function: Callable[[str], str],
) -> ShowDescription:
    """The same description with `colour` applied to colour names and `function` to function names.

    Fixture-group names come from the patch and are never renamed.
    """
    colours = description.colours
    renamed_colours = replace(
        colours,
        palette={colour(name): rgb for name, rgb in colours.palette.items()},
        primary=tuple(colour(name) for name in colours.primary),
        simple=tuple(colour(name) for name in colours.simple),
        white=colour(colours.white),
        analogous_pairs=tuple(
            ColorPair(colour(p.lead), colour(p.bed)) for p in colours.analogous_pairs
        ),
        key_split_pairs=tuple((colour(a), colour(b)) for a, b in colours.key_split_pairs),
        complementary_pairs=tuple(
            ColorPair(colour(p.lead), colour(p.bed)) for p in colours.complementary_pairs
        ),
        matrix_colors=tuple(colour(name) for name in colours.matrix_colors),
    )
    matrices = {
        group: tuple(replace(s, colors=tuple(colour(name) for name in s.colors)) for s in scripts)
        for group, scripts in description.matrices.items()
    }
    timing = replace(
        description.timing,
        beat_timings={function(name): t for name, t in description.timing.beat_timings.items()},
    )
    console = replace(
        description.console,
        keys={function(name): key for name, key in description.console.keys.items()},
        flash_functions=tuple(function(name) for name in description.console.flash_functions),
    )
    return replace(
        description, colours=renamed_colours, matrices=matrices, timing=timing, console=console
    )
