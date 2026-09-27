"""The JUGAR page's prism family: the animate/rest hooks, then every prism pick."""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from .generated_play_wrappers import GeneratedPlayWrappers
from .hook import hook
from .pick import pick
from .play_page_layout import GAP, HEADER, LEFT, WIDTH


def build_prism_family(
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
    hooks = (
        ("prism_animation", "hook_prism", True),
        ("prism_rest", "rest_caption", False),
    )
    offered = [ids_by_name.get(vocabulary.display(function)) for function, _, _ in hooks]
    if not wrappers.prism_ids and all(function_id is None for function_id in offered):
        return
    family = frame(
        outer,
        vocabulary.display("family_prism"),
        LEFT,
        784,
        WIDTH,
        100,
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
    columns = 11
    pitch = (WIDTH - 2 * GAP) // columns
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
    for function_id in wrappers.prism_ids:
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
            mark="✧",
        )
        index += 1
