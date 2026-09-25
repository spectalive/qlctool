"""Build the JUGAR page: one releasable manual surface per channel family."""

from collections.abc import Mapping, Sequence

from ..argb import argb_from_rgb
from ..names.default_names import default_names
from ..names.names import Names
from ..names.template_affixes import template_affixes
from ..palette import PALETTE
from ..vc.button import FLASH, TOGGLE
from .generated_play_wrappers import GeneratedPlayWrappers as _GeneratedPlayWrappers
from .smc_pad_colors import readable_foreground

# Catalogue identifiers of the frames a consumer (the tablet's map) finds the
# page's parts by.
FAMILY_FRAMES = ("family_colour", "family_pixels", "family_heads", "family_gobos", "family_prism")
_HEADER = 26
_GAP = 6
_LEFT = 8
_WIDTH = 1416
_SMALL_BUTTON_HEIGHT = 44
_HOOK_BACKGROUND = str(argb_from_rgb((20, 105, 82)))
_HOOK_FOREGROUND = str(argb_from_rgb(readable_foreground((20, 105, 82))))

_RESET_NAMES = (
    "auto",
    "talk_moment",
    "calm_moment",
    "party_moment",
    "frenzy_moment",
    "full_white",
    "all_black",
    "flash_full",
    "flash_colour",
    "smoke_on",
    "strobe_fast",
)
# The reset strip's short captions, keyed by function identifier; AUTO keeps
# its own name. Flash, colour flash, haze and strobe reuse the hit captions,
# whose words are the same (ruling B9).
_RESET_CAPTIONS = (
    ("talk_moment", "reset_talk"),
    ("calm_moment", "reset_calm"),
    ("party_moment", "reset_party"),
    ("frenzy_moment", "reset_frenzy"),
    ("full_white", "reset_white"),
    ("all_black", "reset_black"),
    ("flash_full", "hit_flash"),
    ("flash_colour", "hit_flash_colour"),
    ("smoke_on", "haze_word"),
    ("strobe_fast", "hit_strobe"),
)


def build_play_page(
    outer,
    button,
    master_button,
    frame,
    label,
    names: Mapping[int, str],
    master: Mapping[str, int],
    play_wrappers: _GeneratedPlayWrappers,
    colour_flash_ids: Mapping[str, int],
    flash_functions: Sequence[str],
    page: int,
    title_font: str,
    big_font: str,
    small_font: str,
    palette: Mapping[str, tuple[int, int, int]] | None = None,
    vocabulary: Names | None = None,
) -> None:
    """Append page two; only its picks and reset-strip duplicates stay keyless.

    `names` maps function id to function name; the page's own words come from
    `vocabulary`, None meaning `default_names()`.
    """
    vocabulary = default_names() if vocabulary is None else vocabulary
    ids_by_name = {name: function_id for function_id, name in names.items()}
    flashes = set(flash_functions)

    label(
        outer,
        vocabulary.display("page_play"),
        _LEFT,
        30,
        _WIDTH,
        22,
        page=page,
        font=title_font,
    )
    _build_reset_strip(
        outer,
        button,
        frame,
        label,
        master,
        flashes,
        page,
        title_font,
        small_font,
        vocabulary,
    )
    _build_colour_hits(
        outer,
        button,
        frame,
        colour_flash_ids,
        page,
        title_font,
        small_font,
        PALETTE if palette is None else palette,
        vocabulary,
    )
    _build_color_family(
        outer,
        button,
        master_button,
        frame,
        label,
        names,
        ids_by_name,
        play_wrappers,
        page,
        title_font,
        big_font,
        small_font,
        vocabulary,
    )
    _build_pixel_family(
        outer,
        button,
        master_button,
        frame,
        label,
        names,
        ids_by_name,
        play_wrappers,
        page,
        title_font,
        big_font,
        small_font,
        vocabulary,
    )
    _build_movement_family(
        outer,
        button,
        master_button,
        frame,
        label,
        names,
        ids_by_name,
        play_wrappers,
        page,
        title_font,
        big_font,
        small_font,
        vocabulary,
    )
    _build_gobo_family(
        outer,
        button,
        master_button,
        frame,
        label,
        names,
        ids_by_name,
        play_wrappers,
        page,
        title_font,
        big_font,
        small_font,
        vocabulary,
    )
    _build_prism_family(
        outer,
        button,
        master_button,
        frame,
        label,
        names,
        ids_by_name,
        play_wrappers,
        page,
        title_font,
        big_font,
        small_font,
        vocabulary,
    )


def _build_reset_strip(
    outer,
    button,
    frame,
    label,
    master,
    flashes,
    page,
    title_font,
    small_font,
    vocabulary: Names,
) -> None:
    strip = frame(
        outer,
        vocabulary.display("reset_frame"),
        _LEFT,
        56,
        _WIDTH,
        90,
        page=page,
        font=title_font,
    )
    label(
        strip,
        vocabulary.display("reset_guidance"),
        _GAP,
        _HEADER,
        420,
        18,
        font=small_font,
    )
    # A function the show lacks (the haze, on a rig without a machine) takes
    # no place in the strip.
    present = [
        (vocabulary.display(i), master[vocabulary.display(i)])
        for i in _RESET_NAMES
        if master.get(vocabulary.display(i)) is not None
    ]
    pitch = (_WIDTH - 426 - 2 * _GAP) // max(len(present), 1)
    captions = {
        vocabulary.display(function): vocabulary.display(caption)
        for function, caption in _RESET_CAPTIONS
    }
    for index, (name, function_id) in enumerate(present):
        is_flash = name in flashes
        button(
            strip,
            function_id,
            captions.get(name, name),
            426 + _GAP + index * pitch,
            44,
            pitch - 4,
            _SMALL_BUTTON_HEIGHT,
            action=FLASH if is_flash else TOGGLE,
            flash_override=is_flash,
            font=small_font,
        )


def _build_colour_hits(
    outer,
    button,
    frame,
    colour_flash_ids,
    page,
    title_font,
    small_font,
    palette: Mapping[str, tuple[int, int, int]],
    vocabulary: Names,
) -> None:
    hits = frame(
        outer,
        vocabulary.display("colour_hits"),
        _LEFT,
        152,
        _WIDTH,
        70,
        page=page,
        font=title_font,
    )
    pitch = (_WIDTH - 2 * _GAP) // max(len(colour_flash_ids), 1)
    for index, (colour_name, function_id) in enumerate(colour_flash_ids.items()):
        colour = palette[colour_name]
        button(
            hits,
            function_id,
            colour_name.upper(),
            _GAP + index * pitch,
            _HEADER,
            pitch - 4,
            _SMALL_BUTTON_HEIGHT,
            action=FLASH,
            flash_override=True,
            flash_force_ltp=True,
            background=str(argb_from_rgb(colour)),
            foreground=str(argb_from_rgb(readable_foreground(colour))),
            font=small_font,
        )


def _build_color_family(
    outer,
    button,
    master_button,
    frame,
    label,
    names,
    ids_by_name,
    wrappers,
    page,
    title_font,
    big_font,
    small_font,
    vocabulary: Names,
) -> None:
    family = frame(
        outer,
        vocabulary.display("family_colour"),
        _LEFT,
        228,
        _WIDTH,
        142,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    label(
        family,
        vocabulary.display("colour_guidance"),
        _GAP,
        _HEADER,
        _WIDTH - 2 * _GAP,
        18,
        font=small_font,
    )
    columns = 13
    pitch = (_WIDTH - 2 * _GAP) // columns
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
        _hook(
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
        _pick(
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
        name = _source_name(names.get(function_id, ""), vocabulary)
        _bound_pick(
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


def _build_pixel_family(
    outer,
    button,
    master_button,
    frame,
    label,
    names,
    ids_by_name,
    wrappers,
    page,
    title_font,
    big_font,
    small_font,
    vocabulary: Names,
) -> None:
    hooks = (vocabulary.display("panel_cycle"), vocabulary.display("talk_panels"))
    if not wrappers.panel_ids and not any(ids_by_name.get(h) is not None for h in hooks):
        return
    family = frame(
        outer,
        vocabulary.display("family_pixels"),
        _LEFT,
        376,
        _WIDTH,
        96,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    label(
        family,
        vocabulary.display("pixels_guidance"),
        _GAP,
        _HEADER,
        _WIDTH - 2 * _GAP,
        18,
        font=small_font,
    )
    columns = 15
    pitch = (_WIDTH - 2 * _GAP) // columns
    _hook(
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
    _hook(
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
        _pick(
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


def _build_movement_family(
    outer,
    button,
    master_button,
    frame,
    label,
    names,
    ids_by_name,
    wrappers,
    page,
    title_font,
    big_font,
    small_font,
    vocabulary: Names,
) -> None:
    family = frame(
        outer,
        vocabulary.display("family_heads"),
        _LEFT,
        478,
        _WIDTH,
        142,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    label(
        family,
        vocabulary.display("cycle_guidance"),
        _GAP,
        _HEADER,
        _WIDTH - 2 * _GAP,
        18,
        font=small_font,
    )
    # Fifteen across since 2026-09-22: the shape picks tripled when every
    # figure got its simultaneous and its alternating twin, and this frame has
    # no room to grow - GOBOS starts 148 px below it. Four hooks and twenty-six
    # picks fit exactly two rows at fifteen (`rule_console` measures it).
    columns = 15
    pitch = (_WIDTH - 2 * _GAP) // columns
    hooks = (
        ("soft_movements", "hook_heads_slow", False),
        ("head_movements", "hook_heads_normal", True),
        ("fast_movements", "hook_heads_fast", False),
        ("heads_centre", "centre_caption", False),
    )
    index = 0
    for function, caption, include_key in hooks:
        _hook(
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
        _pick(
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


def _build_gobo_family(
    outer,
    button,
    master_button,
    frame,
    label,
    names,
    ids_by_name,
    wrappers,
    page,
    title_font,
    big_font,
    small_font,
    vocabulary: Names,
) -> None:
    hooks = (vocabulary.display("gobo_animation"), vocabulary.display("gobo_rest"))
    if not wrappers.gobo_ids and not any(ids_by_name.get(h) is not None for h in hooks):
        return
    family = frame(
        outer,
        vocabulary.display("family_gobos"),
        _LEFT,
        626,
        _WIDTH,
        152,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    _hook(
        master_button,
        family,
        ids_by_name,
        vocabulary.display("gobo_animation"),
        vocabulary.display("hook_gobos"),
        0,
        7,
        190,
        big_font,
        top=_HEADER,
        include_key=True,
    )
    _hook(
        master_button,
        family,
        ids_by_name,
        vocabulary.display("gobo_rest"),
        vocabulary.display("rest_caption"),
        1,
        7,
        190,
        big_font,
        top=_HEADER,
    )
    label(
        family,
        vocabulary.display("cycle_guidance"),
        392,
        _HEADER,
        _WIDTH - 398,
        44,
        font=small_font,
    )
    if not wrappers.gobo_ids:
        return
    picks = frame(
        family,
        vocabulary.display("gobo_pages"),
        _GAP,
        74,
        _WIDTH - 2 * _GAP,
        72,
        pages=2,
        font=small_font,
    )
    columns = 14
    pitch = (_WIDTH - 4 * _GAP) // columns
    per_page = 14
    for index, function_id in enumerate(wrappers.gobo_ids):
        button(
            picks,
            function_id,
            f"❋ {_pick_caption(names.get(function_id, ''), vocabulary)}",
            _GAP + (index % per_page) * pitch,
            _HEADER,
            pitch - 4,
            _SMALL_BUTTON_HEIGHT,
            page=index // per_page,
            font=small_font,
        )


def _build_prism_family(
    outer,
    button,
    master_button,
    frame,
    label,
    names,
    ids_by_name,
    wrappers,
    page,
    title_font,
    big_font,
    small_font,
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
        _LEFT,
        784,
        _WIDTH,
        100,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    label(
        family,
        vocabulary.display("cycle_guidance"),
        _GAP,
        _HEADER,
        _WIDTH - 2 * _GAP,
        18,
        font=small_font,
    )
    columns = 11
    pitch = (_WIDTH - 2 * _GAP) // columns
    index = 0
    for function, caption, include_key in hooks:
        _hook(
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
        _pick(
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


def _hook(
    master_button,
    parent,
    ids_by_name,
    name,
    caption,
    index,
    columns,
    pitch,
    font,
    top,
    include_key=False,
) -> None:
    x, y = _grid_position(index, columns, pitch, top)
    master_button(
        parent,
        name,
        caption,
        x,
        y,
        pitch - 4,
        _SMALL_BUTTON_HEIGHT,
        function_id=ids_by_name.get(name),
        include_key=include_key,
        background=_HOOK_BACKGROUND,
        foreground=_HOOK_FOREGROUND,
        font=font,
    )


def _bound_pick(
    master_button,
    parent,
    name,
    function_id,
    index,
    columns,
    pitch,
    font,
    vocabulary,
    top,
    caption=None,
    include_key=False,
) -> None:
    x, y = _grid_position(index, columns, pitch, top)
    master_button(
        parent,
        name,
        _pick_caption(name, vocabulary) if caption is None else caption,
        x,
        y,
        pitch - 4,
        _SMALL_BUTTON_HEIGHT,
        function_id=function_id,
        include_key=include_key,
        font=font,
    )


def _pick(
    button, parent, names, function_id, index, columns, pitch, font, vocabulary, top, mark=""
) -> None:
    """One manual pick. `mark` is the family's glyph, so a full page of picks
    still says which family each tile belongs to (owner, 2026-09-22).
    """
    x, y = _grid_position(index, columns, pitch, top)
    caption = _pick_caption(names.get(function_id, ""), vocabulary)
    button(
        parent,
        function_id,
        f"{mark} {caption}" if mark else caption,
        x,
        y,
        pitch - 4,
        _SMALL_BUTTON_HEIGHT,
        font=font,
    )


def _grid_position(index: int, columns: int, pitch: int, top: int) -> tuple[int, int]:
    return _GAP + (index % columns) * pitch, top + (index // columns) * 46


def _source_name(name: str, vocabulary: Names) -> str:
    return name.removeprefix(vocabulary.display("pick_prefix"))


def _pick_caption(name: str, vocabulary: Names) -> str:
    """The pick's function name without the markers its family's template adds (B8)."""
    caption = _source_name(name, vocabulary)
    prefixes = (
        template_affixes(vocabulary, "movement_shape")[0],
        vocabulary.display("panels_label") + " - ",
        "Gobo - ",
        vocabulary.display("prism_label") + " - ",
    )
    for prefix in prefixes:
        caption = caption.removeprefix(prefix)
    return caption.removesuffix(template_affixes(vocabulary, "with_pixels")[1])
