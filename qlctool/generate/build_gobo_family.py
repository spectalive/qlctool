"""The JUGAR page's gobo family: the animate/rest hooks, then a paged pick strip."""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from .generated_play_wrappers import GeneratedPlayWrappers
from .hook import hook
from .pick_caption import pick_caption
from .play_page_layout import GAP, HEADER, LEFT, SMALL_BUTTON_HEIGHT, WIDTH


def build_gobo_family(
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
    hooks = (vocabulary.display("gobo_animation"), vocabulary.display("gobo_rest"))
    if not wrappers.gobo_ids and not any(ids_by_name.get(h) is not None for h in hooks):
        return
    family = frame(
        outer,
        vocabulary.display("family_gobos"),
        LEFT,
        626,
        WIDTH,
        152,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    hook(
        master_button,
        family,
        ids_by_name,
        vocabulary.display("gobo_animation"),
        vocabulary.display("hook_gobos"),
        0,
        7,
        190,
        big_font,
        top=HEADER,
        include_key=True,
    )
    hook(
        master_button,
        family,
        ids_by_name,
        vocabulary.display("gobo_rest"),
        vocabulary.display("rest_caption"),
        1,
        7,
        190,
        big_font,
        top=HEADER,
    )
    label(
        family,
        vocabulary.display("cycle_guidance"),
        392,
        HEADER,
        WIDTH - 398,
        44,
        font=small_font,
    )
    if not wrappers.gobo_ids:
        return
    picks = frame(
        family,
        vocabulary.display("gobo_pages"),
        GAP,
        74,
        WIDTH - 2 * GAP,
        72,
        pages=2,
        font=small_font,
    )
    columns = 14
    pitch = (WIDTH - 4 * GAP) // columns
    per_page = 14
    for index, function_id in enumerate(wrappers.gobo_ids):
        button(
            picks,
            function_id,
            f"❋ {pick_caption(names.get(function_id, ''), vocabulary)}",
            GAP + (index % per_page) * pitch,
            HEADER,
            pitch - 4,
            SMALL_BUTTON_HEIGHT,
            page=index // per_page,
            font=small_font,
        )
