"""The JUGAR page's colour family: automatic hooks, then every colour pick."""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from .bound_pick import bound_pick
from .generated_play_wrappers import GeneratedPlayWrappers
from .hook import hook
from .pick import pick
from .play_page_layout import GAP, HEADER, LEFT, WIDTH
from .source_name import source_name


def build_color_family(
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
    family = frame(
        outer,
        vocabulary.display("family_colour"),
        LEFT,
        228,
        WIDTH,
        142,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    label(
        family,
        vocabulary.display("colour_guidance"),
        GAP,
        HEADER,
        WIDTH - 2 * GAP,
        18,
        font=small_font,
    )
    columns = 13
    pitch = (WIDTH - 2 * GAP) // columns
    # The three automatic colour modes sit first, in this frame, which is solo:
    # choosing one stops the other two, so the room always has exactly one
    # colour clock ("colores simples, colores completos, colores pastel
    # tenues", owner, 2026-09-22).
    hooks = (
        ("colour_wheel", "hook_colours", True),
        ("simple_wheel", "hook_simple", True),
        ("pastel_wheel", "hook_pastel", True),
        ("multicolour_wheel", "hook_multicolour", True),
        ("mix_wheel", "hook_mix", True),
        ("talk_light", "talk_light", False),
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
    for function_id in wrappers.color_ids:
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
            mark="🎨",
        )
        index += 1
    rainbow_captions = {
        vocabulary.display("rainbow_together"): vocabulary.display("hook_rainbow_together"),
        vocabulary.display("rainbow_steps"): vocabulary.display("hook_rainbow_steps"),
    }
    for function_id in wrappers.rainbow_ids:
        name = source_name(names.get(function_id, ""), vocabulary)
        bound_pick(
            master_button,
            family,
            name,
            function_id,
            index,
            columns,
            pitch,
            small_font,
            vocabulary,
            top=46,
            caption=rainbow_captions[name],
            include_key=True,
        )
        index += 1
