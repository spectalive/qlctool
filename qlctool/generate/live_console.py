"""Lay out the console the show is run from: three pages, biggest first.

The person in front of this laptop is not a lighting operator. They are whoever
is nearest when something happens, on a 13" screen, in a dark room, with a party
going on - so the console is built to a fixed 1440x900 and split into three
pages that answer three different questions:

1. **Show** - what state is the room in, and how do I hit it? Seven big buttons
   for the state and six for the hits that ride on top. Nothing else.
2. **Manual** - the layers, for somebody who does know the rig and wants to
   drive it while AUTO runs.
3. **Libreria** - the raw material the show is built from: 90 two-colour mixes,
   90 matrix effects, 20 gobos, 17 beam colours. Nobody hunts through these
   mid-set; they are here to be borrowed, not pressed.

Two rules decide the frames.

**A function and the functions it starts never share a solo frame.** A solo
frame stops every other widget's function as soon as one starts
(VCSoloFrame::slotWidgetFunctionStarting), and a Toggle button reports its
function starting however it was started - so AUTO dies the instant it starts a
wheel that sits in the same solo frame. Masters and anything that drives other
functions live in plain frames; only leaf looks are grouped solo.

**The room is in exactly one state.** That is the same mechanism used
deliberately: AUTO, the four moments, the work light and the blackout share one
solo frame, so starting any of them stops whichever was running. That is what
makes "Ambiente and Fiesta at the same time" - two energy levels stacked on one
rig, which is what turned the room white - impossible to press.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from lxml import etree

from ..argb import argb_from_rgb
from ..palette import PALETTE
from ..vc.appearance import DEFAULT
from ..vc.audio_triggers import build_audio_triggers
from ..vc.button import FLASH, STOP_ALL, TOGGLE, build_button
from ..vc.console_font import console_font
from ..vc.frame import build_frame
from ..vc.label import build_label
from ..vc.matrix_control import build_matrix_control
from ..vc.speed_dial import build_speed_dial
from ..vc.widget_ids import next_widget_id
from ..vc.xy_pad import build_xy_pad
from ..workspace import Workspace
from ..xmlutil import find_local, localname

CANVAS_WIDTH = 1440
CANVAS_HEIGHT = 900
HEADER = 26          # the frame header, where the page arrows live
GAP = 6

# The console is one multipage frame filling the screen. The page arrows are in
# its header; these keys do the same without aiming a mouse in the dark.
PAGE_NEXT_KEY = "PgDown"
PAGE_PREVIOUS_KEY = "PgUp"
PAGE_SHOW, PAGE_MANUAL, PAGE_LIBRARY = 0, 1, 2
PAGES = 3

# The panic button. Backspace because it is big, reachable without looking, and
# bound to nothing else in QLC+ or in this console.
STOP_ALL_KEY = "Backspace"
STOP_ALL_FADE_MS = 1000

OUTER_X, OUTER_Y = 4, 4
OUTER_WIDTH, OUTER_HEIGHT = 1432, 892

LEFT_X, LEFT_WIDTH = 8, 524
MIDDLE_X, MIDDLE_WIDTH = 540, 628
RIGHT_X, RIGHT_WIDTH = 1176, 256

TITLE_FONT = console_font(15)
HUGE_FONT = console_font(28)
BIG_FONT = console_font(15)
HELP_FONT = console_font(11, bold=False)
# A colour bank button is 48px wide and a mix button carries two names: at the
# console's own size the caption is cut off, and a cut-off caption is what the
# blank buttons it replaces were.
SMALL_FONT = console_font(9)
TINY_FONT = console_font(8)

# Keys 1-0 across a colour bank, as the hand-built console has them. Every
# widget sees every key press - on any page, visible or not - so one key lights
# that colour on all three banks.
BANK_KEYS = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")

# A colour bank button is 44px wide: the name has to survive that.
SHORT_COLOR = {
    "UltraVioleta": "UV", "Amarillo": "Amar", "Magenta": "Mage",
    "Blanco": "Blan", "Naranja": "Nara",
}
# ...and a two-colour mix carries two of them, so those go to two letters. One
# letter is what made "R/A" mean both Rojo/Azul and Rojo/Amarillo.
# Two wheel positions carry a sentence for a name and no button is that wide.
LONG_WHEEL_NAME = {
    "Rainbow effect fast to slow": "Arcoiris +",
    "Rainbow effect reverse slow to fast": "Arcoiris -",
}
MIX_CODE = {
    "Rojo": "Ro", "Verde": "Ve", "Azul": "Az", "Amarillo": "Am", "Cyan": "Cy",
    "Magenta": "Ma", "Blanco": "Bl", "Naranja": "Na", "Rosa": "Rs",
    "UltraVioleta": "UV",
}

# The room's state: one at a time, biggest first. Caption, function, and the
# geometry inside the solo frame.
ROOM_STATES: tuple[tuple[str, str, tuple[int, int, int, int], str], ...] = (
    ("AUTO", "AUTO — el show se lleva solo · Q", (8, 26, 690, 190), HUGE_FONT),
    ("Momento Charla", "CHARLA — alguien habla · F1", (704, 26, 352, 92), BIG_FONT),
    ("Momento Tranquilo", "TRANQUILO — bajón · F2", (1062, 26, 352, 92), BIG_FONT),
    ("Momento Fiesta", "FIESTA — marcha normal · F3", (704, 124, 352, 92), BIG_FONT),
    ("Momento Locura", "LOCURA — todo a la vez · F4", (1062, 124, 352, 92), BIG_FONT),
    ("Blanco Total", "BLANCO TOTAL — luz de trabajo · X", (8, 222, 690, 92), BIG_FONT),
    ("Todo Negro", "TODO NEGRO — apaga las luces · º", (704, 222, 710, 92), BIG_FONT),
)

# The hits: they add to whatever state is running instead of replacing it, so
# they live in a plain frame. Six across one row.
HITS: tuple[tuple[str, str], ...] = (
    ("Flash 100%", "FLASH · Espacio"),
    ("Flash 50%", "FLASH SUAVE · -"),
    ("Humo ON", "HUMO YA — mantén pulsado · H"),
    ("Strobo Rapido", "STROBO · F"),
    ("Strobo Medio", "STROBO SUAVE · T"),
    ("Color Beam Animacion", "COLOR BEAM · C"),
)

# What page 1 says about itself, because nobody reads a manual at a venue.
HELP_LINES = (
    (
        "Arriba: en qué estado está la sala. Solo puede haber UNO — pulsar "
        "otro cambia el estado, no se suman. AUTO es el normal: colores, humo "
        "y la noche subiendo y bajando sola."
    ),
    (
        "Los MOMENTOS son para cuando pasa algo: alguien sube a hablar "
        "(CHARLA), la sala baja (TRANQUILO), va bien (FIESTA), el último tema "
        "(LOCURA). Cuando pase el momento, vuelve a pulsar AUTO."
    ),
    (
        "Abajo: los GOLPES. Esos SÍ se suman a lo que esté sonando. FLASH y "
        "HUMO YA funcionan mientras los mantienes pulsados y se apagan al "
        "soltar."
    ),
    (
        "PARAR TODO apaga todas las funciones a la vez: es el botón de cuando "
        "algo se ha quedado encendido y no sabes cuál."
    ),
    (
        "PgDn / PgUp cambian de página: 2 = control manual capa a capa, "
        "3 = librería de colores, mezclas, matrices y gobos. Las teclas "
        "funcionan desde cualquier página."
    ),
)

# The two dials are the only widgets on the console whose effect is invisible
# until something is already running.
DIAL_LINES = (
    "Velocidad de las ruedas de color",
    "y del movimiento de las cabezas.",
    "Solo se nota con la rueda o el",
    "movimiento encendidos.",
)

# Page 3 says what it is for, because a page of 180 buttons otherwise reads as
# something somebody is supposed to be using.
LIBRARY_LINES = (
    "Esta página es el almacén: las mezclas de dos colores, las matrices y",
    "los 42 efectos propios de los paneles. Están aquí para mirarlos y para",
    "construir AUTO con ellos, no para pulsarlos con la sala llena.",
    "· · ·",
    "Las flechas de la cabecera de cada marco cambian de grupo: cada grupo",
    "de luces tiene sus propias mezclas y sus propias matrices.",
    "· · ·",
    "Los 42 efectos de los paneles no los ha visto nadie todavía: el aparato",
    "solo los llama «Effect N». Pulsa, mira, y apunta cuáles valen la pena.",
    "· · ·",
    "Las ruedas por grupo pintan los mismos fixtures que la rueda general.",
    "Encender las dos a la vez suma los dos colores: sale blanco.",
)

# The five spectrum bands, and which look each one presses. Only one is bound:
# a starting point, since the thresholds and the pairing are a decision at the
# venue with the real music playing. Its target is a Toggle button in a plain
# frame - an audio bar calls pressFunction on the way up and again on the way
# down, so a Flash button would latch on and never release, and a target inside
# the room-state solo frame would have the bass line killing AUTO.
AUDIO_BANDS: tuple[tuple[str, str | None], ...] = (
    ("Graves", None),
    ("Medios-graves", None),
    ("Medios", None),
    ("Medios-agudos", "Strobo Rapido"),
    ("Agudos", None),
)


@dataclass(frozen=True)
class GeneratedConsole:
    frame_ids: list[int] = field(default_factory=list)
    button_ids: list[int] = field(default_factory=list)
    widget_ids: list[int] = field(default_factory=list)


class _Ids:
    """Widget IDs, handed out in order from wherever the console left off."""

    def __init__(self, root: etree._Element) -> None:
        self._next = next_widget_id(root)

    def take(self) -> int:
        value = self._next
        self._next += 1
        return value


def generate_live_console(
    workspace: Workspace,
    master: dict[str, int],
    banks: Sequence,
    matrices: Sequence,
    movement,
    gobos,
    beam_colors,
    prisms,
    mover_fixture_ids: Sequence[int],
    builtins,
    keys: dict[str, str],
    flash_functions: Sequence[str] = (),
    matrix_algorithms: Sequence[str] = (),
) -> GeneratedConsole:
    """Build the whole console on the workspace's (emptied) root frame."""
    root_frame = _root_frame(workspace.root)
    names = _function_names(workspace)
    ids = _Ids(workspace.root)
    console = GeneratedConsole()
    flash = set(flash_functions)

    widget_of: dict[int, int] = {}

    def button(parent, function_id, caption, x, y, w, h, page=None, **kwargs):
        widget_id = ids.take()
        element = build_button(
            parent, widget_id, caption, function_id, x=x, y=y, width=w,
            height=h, **kwargs,
        )
        _on_page(element, page)
        console.button_ids.append(widget_id)
        console.widget_ids.append(widget_id)
        if function_id is not None:
            widget_of[function_id] = widget_id
        return element

    def frame(parent, caption, x, y, w, h, page=None, **kwargs):
        widget_id = ids.take()
        element = build_frame(parent, widget_id, caption, x, y, w, h, **kwargs)
        _on_page(element, page)
        console.frame_ids.append(widget_id)
        console.widget_ids.append(widget_id)
        return element

    def label(parent, caption, x, y, w, h, page=None, font=DEFAULT):
        widget_id = ids.take()
        element = build_label(parent, widget_id, caption, x, y, w, h, font=font)
        _on_page(element, page)
        console.widget_ids.append(widget_id)
        return element

    def master_button(parent, name, caption, x, y, w, h, page=None, **kwargs):
        """A button for a master function, with its key and its action."""
        if name not in master:
            return None
        return button(
            parent, master[name], caption, x, y, w, h, page=page,
            key=keys.get(name),
            action=FLASH if name in flash else TOGGLE,
            **kwargs,
        )

    outer = frame(
        root_frame, "", OUTER_X, OUTER_Y, OUTER_WIDTH, OUTER_HEIGHT,
        pages=PAGES, next_page_key=PAGE_NEXT_KEY,
        previous_page_key=PAGE_PREVIOUS_KEY, font=TITLE_FONT,
    )

    _page_show(outer, button, master_button, frame, label)
    _page_manual(
        outer, button, master_button, frame, label, ids, console, names,
        banks, movement, gobos, beam_colors, prisms, mover_fixture_ids,
    )
    _page_library(
        outer, button, frame, label, ids, console, names,
        banks, matrices, builtins, matrix_algorithms,
    )

    # Last, because a band presses a button and needs its widget ID.
    triggers_id = ids.take()
    triggers = build_audio_triggers(
        outer, triggers_id, "Audio (hay que elegir entrada en Configuración)",
        RIGHT_X, 330, RIGHT_WIDTH, 110,
        bars=[
            (name, widget_of.get(master.get(target)) if target else None)
            for name, target in AUDIO_BANDS
        ],
    )
    _on_page(triggers, PAGE_MANUAL)
    console.widget_ids.append(triggers_id)

    _set_canvas(workspace.root)
    return console


def _page_show(outer, button, master_button, frame, label) -> None:
    """Page 1: the state the room is in, the hits, and the panic button."""
    label(
        outer, "1 · SHOW — pulsa AUTO y ya está. PgDn para el resto.",
        LEFT_X, 30, OUTER_WIDTH - 16, 30, page=PAGE_SHOW, font=TITLE_FONT,
    )

    # Solo on purpose: this is what makes the room one state at a time. Nothing
    # here starts anything else in here, so the solo-frame rule is not broken -
    # a moment starts wheels and chasers, and every one of those lives on
    # another page, in a plain frame.
    room = frame(
        outer, "LA SALA ESTÁ ASÍ — solo una a la vez",
        LEFT_X, 68, OUTER_WIDTH - 16, 322, page=PAGE_SHOW, solo=True,
        font=TITLE_FONT,
    )
    for name, caption, (x, y, w, h), font in ROOM_STATES:
        master_button(room, name, caption, x, y, w, h, font=font)

    hits = frame(
        outer, "GOLPES — se suman a lo que ya está sonando",
        LEFT_X, 400, OUTER_WIDTH - 16, 160, page=PAGE_SHOW, font=TITLE_FONT,
    )
    for index, (name, caption) in enumerate(HITS):
        master_button(
            hits, name, caption,
            GAP + 2 + index * 234, HEADER + 4, 228, 118, font=BIG_FONT,
        )

    panic = frame(
        outer, "SI ALGO VA MAL", LEFT_X, 570, OUTER_WIDTH - 16, 118,
        page=PAGE_SHOW, font=TITLE_FONT,
    )
    # No function of its own: StopAll stops every one that is running, which is
    # the only honest answer to "something is on and nobody knows what started
    # it". A scene would only add one more thing on top of the mess.
    button(
        panic, None, "PARAR TODO · Retroceso", GAP + 2, HEADER + 4, 460, 78,
        action=STOP_ALL, key=STOP_ALL_KEY, stop_all_fade_ms=STOP_ALL_FADE_MS,
        font=BIG_FONT,
    )
    label(
        panic,
        "Para todas las funciones con un fundido de 1 segundo y deja la sala "
        "a oscuras. Después, pulsa AUTO para volver a empezar.",
        476, HEADER + 4, 930, 78, font=HELP_FONT,
    )

    for index, line in enumerate(HELP_LINES):
        label(
            outer, line, LEFT_X, 700 + index * 26, OUTER_WIDTH - 16, 24,
            page=PAGE_SHOW, font=HELP_FONT,
        )


def _page_manual(
    outer, button, master_button, frame, label, ids, console, names,
    banks, movement, gobos, beam_colors, prisms, mover_fixture_ids,
) -> None:
    """Page 2: the layers, for somebody who wants to drive it by hand."""
    label(
        outer, "2 · MANUAL — capas sueltas, se encienden sobre AUTO",
        LEFT_X, 30, OUTER_WIDTH - 16, 30, page=PAGE_MANUAL, font=TITLE_FONT,
    )

    layers = frame(
        outer, "Capas del show", LEFT_X, 68, LEFT_WIDTH, 140,
        page=PAGE_MANUAL, font=TITLE_FONT,
    )
    layer_names = (
        ("Rueda Colores", "Rueda de colores · W"),
        ("Rueda Mezcla", "Rueda de mezclas · E"),
        ("Movimientos Cabezas", "Mover cabezas · A"),
        ("Gobo Animacion", "Gobos girando · G"),
        ("Prisma Animacion", "Prisma · P"),
        ("Humo Auto", "Humo automático · J"),
    )
    for index, (name, caption) in enumerate(layer_names):
        column, row = index % 3, index // 3
        master_button(
            layers, name, caption,
            GAP + column * 172, HEADER + row * 52, 166, 46,
        )

    y = 216
    for bank in banks:
        element = frame(
            outer, f"Colores {bank.group_name} — teclas 1-0",
            LEFT_X, y, LEFT_WIDTH, 122, page=PAGE_MANUAL, solo=True,
            font=TITLE_FONT,
        )
        for index, function_id in enumerate(bank.scene_ids[: len(BANK_KEYS)]):
            name = names.get(function_id, "")
            button(
                element, function_id, _bank_caption(name),
                x=GAP + index * 51, y=HEADER, w=48, h=44,
                key=BANK_KEYS[index],
                background=_swatch(name), font=SMALL_FONT,
            )
        y += 128

    dimmers = frame(
        outer, "Intensidad y strobo de fixture", LEFT_X, y, LEFT_WIDTH, 136,
        page=PAGE_MANUAL, font=TITLE_FONT,
    )
    for index, (name, caption) in enumerate((
        ("Dimmer Chase", "Barrido de intensidad · V"),
        ("Dimmer PingPong", "Pares / impares · Z"),
        ("Strobo ON", "Strobo del fixture · S"),
        ("Strobo OFF", "Parar ese strobo · D"),
    )):
        column, row = index % 2, index // 2
        master_button(
            dimmers, name, caption,
            GAP + column * 258, HEADER + row * 52, 252, 46,
        )

    shapes = frame(
        outer, "Figura que dibujan las cabezas", MIDDLE_X, 68, MIDDLE_WIDTH, 80,
        page=PAGE_MANUAL, solo=True, font=TITLE_FONT,
    )
    for index, function_id in enumerate(movement.efx_ids):
        button(
            shapes, function_id, _after(names.get(function_id, ""), "Movimiento "),
            x=GAP + index * 88, y=HEADER, w=82, h=44,
        )

    # The beams' wheels are a live decision, not library material: somebody
    # picks a gobo while the show runs. They sit beside the movement shapes.
    _wheel_frame(
        outer, button, frame, names, gobos.scene_ids,
        "Gobos — solo los 4 BEAM", "Gobo - ",
        MIDDLE_X, 156, MIDDLE_WIDTH, 150, PAGE_MANUAL, columns=12,
    )
    _wheel_frame(
        outer, button, frame, names, beam_colors.scene_ids,
        "Color de los BEAM — su rueda, no RGB", "Color Beam - ",
        MIDDLE_X, 314, MIDDLE_WIDTH, 150, PAGE_MANUAL, columns=12,
    )
    _wheel_frame(
        outer, button, frame, names, prisms.scene_ids,
        "Prisma — solo los 4 BEAM", "Prisma - ",
        MIDDLE_X, 472, MIDDLE_WIDTH, 92, PAGE_MANUAL, columns=12,
    )

    label(
        outer, "Apunta las 12 cabezas a mano — arrastra dentro del cuadro",
        MIDDLE_X, 574, MIDDLE_WIDTH, 20, page=PAGE_MANUAL, font=HELP_FONT,
    )
    pad_id = ids.take()
    pad = build_xy_pad(
        outer, pad_id, "Cabezas", MIDDLE_X, 598, MIDDLE_WIDTH, 280,
        fixture_ids=list(mover_fixture_ids),
    )
    _on_page(pad, PAGE_MANUAL)
    console.widget_ids.append(pad_id)

    wheel_ids = [b.wheel_id for b in banks if b.wheel_id is not None]
    wheel_ids += [b.mix_wheel_id for b in banks if b.mix_wheel_id is not None]
    for index, (caption, function_ids, time_ms) in enumerate((
        ("Vel. Colores", wheel_ids, 1900),
        (
            "Vel. Movimiento",
            [movement.chaser_id] if movement.chaser_id else [],
            10000,
        ),
    )):
        if not function_ids:
            continue
        dial_id = ids.take()
        dial = build_speed_dial(
            outer, dial_id, caption,
            RIGHT_X + index * 132, 68, 124, 150,
            function_ids=function_ids, time_ms=time_ms,
        )
        _on_page(dial, PAGE_MANUAL)
        console.widget_ids.append(dial_id)

    for index, line in enumerate(DIAL_LINES):
        label(
            outer, line, RIGHT_X, 228 + index * 22, RIGHT_WIDTH, 20,
            page=PAGE_MANUAL, font=HELP_FONT,
        )


def _page_library(
    outer, button, frame, label, ids, console, names,
    banks, matrices, builtins, matrix_algorithms,
) -> None:
    """Page 3: the material the show is built from, not buttons for a set."""
    label(
        outer,
        "3 · LIBRERÍA — de aquí sale el show. No hace falta tocar nada de esto "
        "durante una fiesta.",
        LEFT_X, 30, OUTER_WIDTH - 16, 30, page=PAGE_LIBRARY, font=TITLE_FONT,
    )

    mixes = frame(
        outer, "Mezclas de dos colores", LEFT_X, 68, LEFT_WIDTH, 230,
        page=PAGE_LIBRARY, solo=True, pages=len(banks) or 1, font=TITLE_FONT,
    )
    for page, bank in enumerate(banks):
        label(
            mixes, f"Grupo: {bank.group_name}", GAP, HEADER, 512, 20,
            page=page, font=HELP_FONT,
        )
        for index, function_id in enumerate(bank.split_ids):
            column, row = index % 10, index // 10
            name = names.get(function_id, "")
            _on_page(
                button(
                    mixes, function_id, _mix_caption(name),
                    x=GAP + column * 51, y=HEADER + 24 + row * 51, w=48, h=45,
                    background=_swatch(name),
                    foreground=_swatch(name, second=True),
                    font=TINY_FONT,
                ),
                page,
            )

    matrix_frame = frame(
        outer, "Matrices — dibujos sobre las barras y los paneles",
        MIDDLE_X, 68, MIDDLE_WIDTH, 300, page=PAGE_LIBRARY, solo=True,
        pages=len(matrices) or 1, font=TITLE_FONT,
    )
    for page, generated in enumerate(matrices):
        group = _before(names.get(_first(generated.matrix_ids), ""), " - ")
        label(
            matrix_frame, f"Grupo: {group}", GAP, HEADER, 400, 20,
            page=page, font=HELP_FONT,
        )
        for index, function_id in enumerate(generated.matrix_ids):
            column, row = index % 6, index // 6
            _on_page(
                button(
                    matrix_frame, function_id,
                    _after(names.get(function_id, ""), " - "),
                    x=GAP + column * 102, y=HEADER + 24 + row * 46, w=96, h=40,
                    font=SMALL_FONT,
                ),
                page,
            )

    # Each group's own colour wheel and its matrix cycle. Both start the looks
    # sitting in the solo frames above, so both live in a plain frame.
    wheel_ids = [b.wheel_id for b in banks if b.wheel_id is not None]
    wheel_ids += [b.mix_wheel_id for b in banks if b.mix_wheel_id is not None]
    cycles = frame(
        outer, "Ruedas y ciclos por grupo — no usar a la vez que la rueda "
        "general: se suman los colores",
        MIDDLE_X, 376, MIDDLE_WIDTH, 190, page=PAGE_LIBRARY, font=TITLE_FONT,
    )
    entries = [(fid, _wheel_caption(names.get(fid, ""))) for fid in wheel_ids]
    entries += [
        (m.chaser_id, _after(names.get(m.chaser_id, ""), "Ciclo "))
        for m in matrices if m.chaser_id is not None
    ]
    # The panels' own cycle belongs here and not among the effects it starts:
    # a chaser sharing a solo frame with its own steps dies as it begins.
    if builtins.chaser_id is not None:
        entries.append((
            builtins.chaser_id, _after(names.get(builtins.chaser_id, ""), "Ciclo "),
        ))
    for index, (function_id, caption) in enumerate(entries):
        column, row = index % 5, index // 5
        button(
            cycles, function_id, caption,
            x=GAP + column * 122, y=HEADER + row * 50, w=116, h=44,
            font=SMALL_FONT,
        )

    if builtins.scene_ids:
        panels = frame(
            outer,
            "Paneles — sus 42 efectos propios, sin ver todavía",
            MIDDLE_X, 580, MIDDLE_WIDTH, 244, page=PAGE_LIBRARY, solo=True,
            font=TITLE_FONT,
        )
        for index, function_id in enumerate(builtins.scene_ids):
            column, row = index % 12, index // 12
            button(
                panels, function_id,
                _after(names.get(function_id, ""), " - "),
                x=GAP + column * 51, y=HEADER + row * 52, w=47, h=46,
                font=TINY_FONT,
            )

    if matrices and matrices[0].matrix_ids:
        matrix_widget_id = ids.take()
        control = build_matrix_control(
            outer, matrix_widget_id, "Matriz en vivo", RIGHT_X, 68,
            RIGHT_WIDTH, 200,
            function_id=matrices[0].matrix_ids[0],
            algorithms=list(matrix_algorithms),
        )
        _on_page(control, PAGE_LIBRARY)
        console.widget_ids.append(matrix_widget_id)

    for index, line in enumerate(LIBRARY_LINES):
        label(
            outer, line, LEFT_X, 310 + index * 26, LEFT_WIDTH, 24,
            page=PAGE_LIBRARY, font=HELP_FONT,
        )


def _wheel_frame(
    outer, button, frame, names, scene_ids, caption, marker, x, y, width,
    height, page, columns,
) -> None:
    """A solo frame of wheel positions - gobos, beam colours, prism."""
    if not scene_ids:
        return
    element = frame(
        outer, caption, x, y, width, height, page=page, solo=True,
        font=TITLE_FONT,
    )
    step = (width - GAP * 2) // columns
    for index, function_id in enumerate(scene_ids):
        column, row = index % columns, index // columns
        caption = _after(names.get(function_id, ""), marker)
        button(
            element, function_id, LONG_WHEEL_NAME.get(caption, caption),
            x=GAP + column * step, y=HEADER + row * 52, w=step - 4, h=46,
            font=TINY_FONT,
        )


def _root_frame(root: etree._Element) -> etree._Element:
    console = find_local(root, "VirtualConsole")
    if console is None:
        raise ValueError("workspace has no <VirtualConsole>")
    frame = find_local(console, "Frame")
    if frame is None:
        raise ValueError("Virtual Console has no root <Frame>")
    return frame


def _function_names(workspace: Workspace) -> dict[int, str]:
    return {
        int(f.attrib["ID"]): f.attrib.get("Name", "")
        for f in workspace.engine
        if localname(f) == "Function" and f.attrib.get("ID")
    }


def _on_page(widget: etree._Element, page: int | None) -> None:
    """Which page of a multipage frame this widget belongs to; 0 is implicit."""
    if page:
        widget.set("Page", str(page))


def _first(ids):
    return ids[0] if ids else None


def _swatch(name: str, second: bool = False) -> str:
    """The ARGB of the palette colour a scene is named after, or Default."""
    parts = [p.strip() for p in name.split(" / ")]
    text = parts[1] if second and len(parts) > 1 else parts[0]
    for color_name in sorted(PALETTE, key=len, reverse=True):
        if text == color_name or text.startswith(f"{color_name} "):
            return str(argb_from_rgb(PALETTE[color_name]))
    return DEFAULT


def _bank_caption(name: str) -> str:
    """"Rojo BarrasLed" is a red button in the bars' bank: it says "Rojo"."""
    first = name.split(" ")[0] if name else ""
    return SHORT_COLOR.get(first, first)


def _wheel_caption(name: str) -> str:
    """"Rueda Colores BarrasLed" is wider than its button; drop the "Rueda"."""
    return _after(name, "Rueda ")


def _mix_caption(name: str) -> str:
    """"Rojo / Azul PAR" reads as "Ro/Az" on a 44px button.

    Two letters, not one: Azul and Amarillo both start with an A, so a
    one-letter code gave six pairs of buttons the same label.
    """
    parts = [p.strip() for p in name.split(" / ")]
    if len(parts) < 2:
        return ""
    first = parts[0].split(" ")[0]
    second = parts[1].split(" ")[0]
    return f"{MIX_CODE.get(first, first[:2])}/{MIX_CODE.get(second, second[:2])}"


def _after(name: str, marker: str) -> str:
    _, separator, tail = name.partition(marker)
    return tail if separator else name


def _before(name: str, marker: str) -> str:
    head, separator, _ = name.partition(marker)
    return head if separator else name


def _set_canvas(root: etree._Element) -> None:
    console = find_local(root, "VirtualConsole")
    properties = find_local(console, "Properties")
    if properties is None:
        return
    size = find_local(properties, "Size")
    if size is None:
        return
    size.set("Width", str(CANVAS_WIDTH))
    size.set("Height", str(CANVAS_HEIGHT))
