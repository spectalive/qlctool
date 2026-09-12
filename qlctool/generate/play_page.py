"""Build the JUGAR page: one releasable manual surface per channel family."""

from collections.abc import Mapping, Sequence

from ..argb import argb_from_rgb
from ..palette import PALETTE
from ..vc.button import FLASH, TOGGLE
from .generated_play_wrappers import GeneratedPlayWrappers as _GeneratedPlayWrappers
from .smc_pad_colors import readable_foreground

_HEADER = 26
_GAP = 6
_LEFT = 8
_WIDTH = 1416
_SMALL_BUTTON_HEIGHT = 44
_HOOK_BACKGROUND = str(argb_from_rgb((20, 105, 82)))
_HOOK_FOREGROUND = str(argb_from_rgb(readable_foreground((20, 105, 82))))

_RESET_NAMES = (
    "AUTO",
    "Momento Charla",
    "Momento Tranquilo",
    "Momento Fiesta",
    "Momento Locura",
    "Blanco Total",
    "Todo Negro",
    "Flash 100%",
    "Flash Color",
    "Humo ON",
    "Strobo Rapido",
)
_COLOR_GUIDANCE = (
    "Pick fijo; repetirlo lo para y deja la familia quieta. AUTO colores o "
    "Q/F1-F4 devuelve la rueda; pararla corta su fundido de 800 ms."
)
_CYCLE_GUIDANCE = (
    "Bajo AUTO, el ciclo de energia lo recupera en su siguiente paso "
    "(8 min como mucho); para jugar largo pon antes un Momento."
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
) -> None:
    """Append page two; only its picks and reset-strip duplicates stay keyless."""
    ids_by_name = {name: function_id for function_id, name in names.items()}
    flashes = set(flash_functions)

    label(
        outer,
        "2 · JUGAR — toma una familia; AUTO dentro de ella la devuelve.",
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
    )
    _build_colour_hits(
        outer,
        button,
        frame,
        colour_flash_ids,
        page,
        title_font,
        small_font,
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
) -> None:
    strip = frame(
        outer,
        "VOLVER AL SHOW",
        _LEFT,
        56,
        _WIDTH,
        90,
        page=page,
        font=title_font,
    )
    label(
        strip,
        "Volver del todo: AUTO dos veces si ya esta verde, o Backspace y Q.",
        _GAP,
        _HEADER,
        420,
        18,
        font=small_font,
    )
    pitch = (_WIDTH - 426 - 2 * _GAP) // len(_RESET_NAMES)
    for index, name in enumerate(_RESET_NAMES):
        function_id = master.get(name)
        if function_id is None:
            continue
        is_flash = name in flashes
        button(
            strip,
            function_id,
            _reset_caption(name),
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
) -> None:
    hits = frame(
        outer,
        "GOLPES DE COLOR — mantén pulsado",
        _LEFT,
        152,
        _WIDTH,
        70,
        page=page,
        font=title_font,
    )
    pitch = (_WIDTH - 2 * _GAP) // max(len(colour_flash_ids), 1)
    for index, (colour_name, function_id) in enumerate(colour_flash_ids.items()):
        colour = PALETTE[colour_name]
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
) -> None:
    family = frame(
        outer,
        "COLOR",
        _LEFT,
        228,
        _WIDTH,
        142,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    label(family, _COLOR_GUIDANCE, _GAP, _HEADER, _WIDTH - 2 * _GAP, 18, font=small_font)
    columns = 13
    pitch = (_WIDTH - 2 * _GAP) // columns
    hooks = (
        ("Rueda Colores", "AUTO colores · W", True),
        ("Rueda Mezcla", "Mezcla · E", True),
        ("Luz Charla", "Luz Charla", False),
    )
    index = 0
    for name, caption, include_key in hooks:
        _hook(
            master_button,
            family,
            ids_by_name,
            name,
            caption,
            index,
            columns,
            pitch,
            big_font,
            top=46,
            include_key=include_key,
        )
        index += 1
    for function_id in wrappers.color_ids:
        _pick(button, family, names, function_id, index, columns, pitch, small_font, top=46)
        index += 1
    for function_id in wrappers.rainbow_ids:
        name = _source_name(names.get(function_id, ""))
        _bound_pick(
            master_button,
            family,
            name,
            function_id,
            index,
            columns,
            pitch,
            small_font,
            top=46,
            caption={
                "Arcoiris Simultaneo": "Arcoiris junto · '",
                "Arcoiris Pasos": "Arcoiris fases · ¡",
            }[name],
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
) -> None:
    family = frame(
        outer,
        "PIXELES",
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
        "Pulsa un efecto y se queda. AUTO paneles devuelve su ciclo.",
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
        "Ciclo Paneles Mixto",
        "AUTO paneles",
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
        "Paneles Charla",
        "Paneles Charla",
        1,
        columns,
        pitch,
        big_font,
        top=46,
    )
    for index, function_id in enumerate(wrappers.panel_ids, start=2):
        _pick(button, family, names, function_id, index, columns, pitch, small_font, top=46)


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
) -> None:
    family = frame(
        outer,
        "CABEZAS",
        _LEFT,
        478,
        _WIDTH,
        142,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    label(family, _CYCLE_GUIDANCE, _GAP, _HEADER, _WIDTH - 2 * _GAP, 18, font=small_font)
    columns = 8
    pitch = (_WIDTH - 2 * _GAP) // columns
    hooks = (
        ("Movimientos Suaves", "AUTO lento", False),
        ("Movimientos Cabezas", "AUTO normal · A", True),
        ("Movimientos Rapidos", "AUTO rapido", False),
        ("Cabezas Centro", "Centro", False),
    )
    index = 0
    for name, caption, include_key in hooks:
        _hook(
            master_button,
            family,
            ids_by_name,
            name,
            caption,
            index,
            columns,
            pitch,
            big_font,
            top=46,
            include_key=include_key,
        )
        index += 1
    for function_id in wrappers.movement_ids:
        _pick(button, family, names, function_id, index, columns, pitch, small_font, top=46)
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
) -> None:
    family = frame(
        outer,
        "GOBOS",
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
        "Gobo Animacion",
        "AUTO gobos · G",
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
        "Gobo Reposo",
        "Reposo",
        1,
        7,
        190,
        big_font,
        top=_HEADER,
    )
    label(family, _CYCLE_GUIDANCE, 392, _HEADER, _WIDTH - 398, 44, font=small_font)
    picks = frame(
        family,
        "Gobos para elegir — 2 paginas",
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
            _pick_caption(names.get(function_id, "")),
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
) -> None:
    family = frame(
        outer,
        "PRISMA",
        _LEFT,
        784,
        _WIDTH,
        100,
        page=page,
        solo=True,
        exclude_monitored=False,
        font=title_font,
    )
    label(family, _CYCLE_GUIDANCE, _GAP, _HEADER, _WIDTH - 2 * _GAP, 18, font=small_font)
    columns = 11
    pitch = (_WIDTH - 2 * _GAP) // columns
    hooks = (
        ("Prisma Animacion", "AUTO prisma · P", True),
        ("Prisma Reposo", "Reposo", False),
    )
    index = 0
    for name, caption, include_key in hooks:
        _hook(
            master_button,
            family,
            ids_by_name,
            name,
            caption,
            index,
            columns,
            pitch,
            big_font,
            top=46,
            include_key=include_key,
        )
        index += 1
    for function_id in wrappers.prism_ids:
        _pick(button, family, names, function_id, index, columns, pitch, small_font, top=46)
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
    top,
    caption=None,
    include_key=False,
) -> None:
    x, y = _grid_position(index, columns, pitch, top)
    master_button(
        parent,
        name,
        _pick_caption(name) if caption is None else caption,
        x,
        y,
        pitch - 4,
        _SMALL_BUTTON_HEIGHT,
        function_id=function_id,
        include_key=include_key,
        font=font,
    )


def _pick(button, parent, names, function_id, index, columns, pitch, font, top) -> None:
    x, y = _grid_position(index, columns, pitch, top)
    button(
        parent,
        function_id,
        _pick_caption(names.get(function_id, "")),
        x,
        y,
        pitch - 4,
        _SMALL_BUTTON_HEIGHT,
        font=font,
    )


def _grid_position(index: int, columns: int, pitch: int, top: int) -> tuple[int, int]:
    return _GAP + (index % columns) * pitch, top + (index // columns) * 46


def _source_name(name: str) -> str:
    return name.removeprefix("Jugar · ")


def _pick_caption(name: str) -> str:
    caption = _source_name(name)
    for prefix in ("Movimiento ", "Paneles - ", "Gobo - ", "Prisma - "):
        caption = caption.removeprefix(prefix)
    return caption.removesuffix(" + Pixeles")


def _reset_caption(name: str) -> str:
    return {
        "Momento Charla": "CHARLA",
        "Momento Tranquilo": "TRANQUILO",
        "Momento Fiesta": "FIESTA",
        "Momento Locura": "LOCURA",
        "Blanco Total": "BLANCO",
        "Todo Negro": "NEGRO",
        "Flash 100%": "FLASH",
        "Flash Color": "FLASH COLOR",
        "Humo ON": "HUMO",
        "Strobo Rapido": "STROBO",
    }.get(name, name)
