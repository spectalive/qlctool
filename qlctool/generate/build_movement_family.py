"""The JUGAR page's movement family: the speed hooks, then every shape pick."""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from .generated_play_wrappers import GeneratedPlayWrappers
from .hook import hook
from .pick import pick
from .play_page_layout import GAP, HEADER, LEFT, WIDTH


def build_movement_family(
    outer: etree._Element,
    button: Callable[..., object],
    master_button: Callable[..., object],
    frame: Callable[..., etree._Element],
    label: Callable[..., object],
    names: Mapping[int, str],
    ids_by_name: Mapping[str, int],
    wrappers: GeneratedPlayWrappers,
    page: int,
    title_font: str,
    big_font: str,
    small_font: str,
    vocabulary: Names,
) -> None:
    # A rig with nothing that pans and tilts has no hook and no pick here.
    moving = ("soft_movements", "head_movements", "fast_movements", "heads_centre")
    if not wrappers.movement_ids and not any(
        ids_by_name.get(vocabulary.display(h)) is not None for h in moving
    ):
        return
    family = frame(
        outer,
        vocabulary.display("family_heads"),
        LEFT,
        478,
        WIDTH,
        142,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    label(
        family,
        vocabulary.display("cycle_guidance"),
        GAP,
        HEADER,
        WIDTH - 2 * GAP,
        18,
        font=small_font,
    )
    # Fifteen across since 2026-09-22: the shape picks tripled when every
    # figure got its simultaneous and its alternating twin, and this frame has
    # no room to grow - GOBOS starts 148 px below it. Four hooks and twenty-six
    # picks fit exactly two rows at fifteen (`rule_console` measures it).
    columns = 15
    pitch = (WIDTH - 2 * GAP) // columns
    hooks = (
        ("soft_movements", "hook_heads_slow", False),
        ("head_movements", "hook_heads_normal", True),
        ("fast_movements", "hook_heads_fast", False),
        ("heads_centre", "centre_caption", False),
    )
    index = 0
    for function, caption, include_key in hooks:
        hook(
            master_button,
            family,
            ids_by_name,
            vocabulary.display(function),
            vocabulary.display(caption),
            index,
            columns,
            pitch,
            big_font,
            top=46,
            include_key=include_key,
        )
        index += 1
    for function_id in wrappers.movement_ids:
        pick(
            button,
            family,
            names,
            function_id,
            index,
            columns,
            pitch,
            small_font,
            vocabulary,
            top=46,
            mark="↔",
        )
        index += 1
