"""The JUGAR page's pixel family: the panel cycle hooks, then every panel pick."""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from .generated_play_wrappers import GeneratedPlayWrappers
from .hook import hook
from .pick import pick
from .play_page_layout import GAP, HEADER, LEFT, WIDTH


def build_pixel_family(
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
    hooks = (vocabulary.display("panel_cycle"), vocabulary.display("talk_panels"))
    if not wrappers.panel_ids and not any(ids_by_name.get(h) is not None for h in hooks):
        return
    family = frame(
        outer,
        vocabulary.display("family_pixels"),
        LEFT,
        376,
        WIDTH,
        96,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    label(
        family,
        vocabulary.display("pixels_guidance"),
        GAP,
        HEADER,
        WIDTH - 2 * GAP,
        18,
        font=small_font,
    )
    columns = 15
    pitch = (WIDTH - 2 * GAP) // columns
    hook(
        master_button,
        family,
        ids_by_name,
        vocabulary.display("panel_cycle"),
        vocabulary.display("hook_panels_auto"),
        0,
        columns,
        pitch,
        big_font,
        top=46,
    )
    hook(
        master_button,
        family,
        ids_by_name,
        vocabulary.display("talk_panels"),
        vocabulary.display("talk_panels"),
        1,
        columns,
        pitch,
        big_font,
        top=46,
    )
    for index, function_id in enumerate(wrappers.panel_ids, start=2):
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
            mark="▦",
        )
