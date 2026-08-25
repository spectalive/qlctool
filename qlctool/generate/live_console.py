"""Lay out the console the show is actually run from: one screen, no scrolling.

A console for this rig is not an index of every function. It is the surface
somebody stands at during a party on a 13" laptop, so it is built to a fixed
1440x900 and divided into the zones the hand-built show uses: the master looks
and the wheels top left, the colour banks under them on keys 1-0, the beams'
gobos and colour wheel in the middle, movement, and the pan/tilt pad, speed
dials and audio triggers down the right. Everything that would not fit - the
two-colour mixes, the matrix effects - goes into a multipage frame instead of
pushing the canvas taller than the screen.

One rule decides the frames: **a function and the functions it starts never
share a solo frame.** A solo frame stops every other widget's function as soon
as one starts (VCSoloFrame::slotWidgetFunctionStarting), and a Toggle button
reports its function starting however it was started - so AUTO, whose whole job
is to start the wheels, dies the instant it starts them if its button sits in
the same solo frame as theirs. Masters and anything that drives other functions
live in plain frames; only leaf looks are grouped solo.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from lxml import etree

from ..argb import argb_from_rgb
from ..palette import PALETTE
from ..vc.appearance import DEFAULT
from ..vc.audio_triggers import build_audio_triggers
from ..vc.button import build_button
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

LEFT_X, LEFT_WIDTH = 8, 524
MIDDLE_X, MIDDLE_WIDTH = 540, 628
RIGHT_X, RIGHT_WIDTH = 1176, 256

# Keys 1-0 across a colour bank, as the hand-built console has them. Every
# widget sees every key press, so one key lights that colour on all three banks.
BANK_KEYS = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")

# The five spectrum bands, and which look each one presses. Only two are bound:
# a starting point, since the thresholds and the pairing are a decision at the
# venue with the real music playing. Both targets are Toggle buttons - an audio
# bar calls pressFunction on the way up and again on the way down, so a Flash
# button would latch on and never release.
AUDIO_BANDS: tuple[tuple[str, str | None], ...] = (
    ("Graves", "Todo Blanco"),
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
    keys: dict[str, str],
    flash_functions: Sequence[str] = (),
    matrix_algorithms: Sequence[str] = (),
) -> GeneratedConsole:
    """Build the whole console on the workspace's (emptied) root frame."""
    root_frame = _root_frame(workspace.root)
    names = _function_names(workspace)
    ids = _Ids(workspace.root)
    console = GeneratedConsole()

    widget_of: dict[int, int] = {}

    def button(parent, function_id, caption, x, y, w, h, **kwargs):
        widget_id = ids.take()
        element = build_button(
            parent, widget_id, caption, function_id, x=x, y=y, width=w,
            height=h, **kwargs,
        )
        console.button_ids.append(widget_id)
        console.widget_ids.append(widget_id)
        widget_of[function_id] = widget_id
        return element

    def frame(caption, x, y, w, h, **kwargs):
        widget_id = ids.take()
        element = build_frame(root_frame, widget_id, caption, x, y, w, h, **kwargs)
        console.frame_ids.append(widget_id)
        console.widget_ids.append(widget_id)
        return element

    # --- left column: master, effects, colour banks, mixes ------------------
    # Ten buttons on five columns rather than eight on four: the energy cycle
    # and its three levels belong beside AUTO, and the frame keeps its height.
    show_names = [
        "AUTO", "Ciclo Energia", "Nivel Ambiente", "Nivel Fiesta", "Nivel Peak",
        "Rueda Colores", "Rueda Mezcla", "Luces ON", "Todo Blanco", "Todo Negro",
    ]
    _button_grid(
        frame("Show", LEFT_X, 8, LEFT_WIDTH, 130),
        [(master[n], n) for n in show_names if n in master],
        button, columns=5, width=97, height=44, keys=keys,
        flash={n for n in flash_functions}, names=names,
    )

    effect_names = [
        "Movimientos Cabezas", "Gobo Animacion", "Color Beam Animacion",
        "Prisma Animacion", "Humo Auto", "Flash 100%", "Flash 50%",
    ]
    _button_grid(
        frame("Efectos", LEFT_X, 144, LEFT_WIDTH, 130),
        [(master[n], n) for n in effect_names if n in master],
        button, columns=4, width=122, height=44, keys=keys,
        flash={n for n in flash_functions}, names=names,
    )

    y = 280
    for bank in banks:
        element = frame(
            f"Colores {bank.group_name}", LEFT_X, y, LEFT_WIDTH, 122, solo=True
        )
        for index, function_id in enumerate(bank.scene_ids[: len(BANK_KEYS)]):
            button(
                element, function_id, "",
                x=GAP + index * 50, y=HEADER, w=44, h=44,
                key=BANK_KEYS[index],
                background=_swatch(names.get(function_id, "")),
            )
        y += 128

    mixes = frame(
        "Mezclas", LEFT_X, y, LEFT_WIDTH, 180, solo=True, pages=len(banks) or 1
    )
    for page, bank in enumerate(banks):
        for index, function_id in enumerate(bank.split_ids):
            column, row = index % 10, index // 10
            _on_page(
                button(
                    mixes, function_id, _mix_caption(names.get(function_id, "")),
                    x=GAP + column * 50, y=HEADER + row * 50, w=44, h=44,
                    background=_swatch(names.get(function_id, "")),
                    foreground=_swatch(names.get(function_id, ""), second=True),
                ),
                page,
            )

    # --- middle column: movement, gobos, beam colours, prism, matrices ------
    _button_grid(
        frame("Movimiento", MIDDLE_X, 8, MIDDLE_WIDTH, 80, solo=True),
        [(fid, _after(names.get(fid, ""), "Movimiento ")) for fid in movement.efx_ids],
        button, columns=7, width=82, height=44, names=names,
    )
    _button_grid(
        frame("Gobos", MIDDLE_X, 94, MIDDLE_WIDTH, 146, solo=True),
        [(fid, _after(names.get(fid, ""), "Gobo - ")) for fid in gobos.scene_ids],
        button, columns=10, width=52, height=52, names=names,
    )
    _button_grid(
        frame("Color Beam", MIDDLE_X, 246, MIDDLE_WIDTH, 146, solo=True),
        [
            (fid, _after(names.get(fid, ""), "Color Beam - "))
            for fid in beam_colors.scene_ids
        ],
        button, columns=10, width=52, height=52, names=names,
    )
    _button_grid(
        frame("Prisma", MIDDLE_X, 398, MIDDLE_WIDTH, 80, solo=True),
        [(fid, _after(names.get(fid, ""), "Prisma - ")) for fid in prisms.scene_ids],
        button, columns=5, width=120, height=44, names=names,
    )

    matrix_frame = frame(
        "Matrices", MIDDLE_X, 484, MIDDLE_WIDTH, 260, solo=True,
        pages=len(matrices) or 1,
    )
    for page, generated in enumerate(matrices):
        for index, function_id in enumerate(generated.matrix_ids):
            column, row = index % 6, index // 6
            _on_page(
                button(
                    matrix_frame, function_id,
                    _after(names.get(function_id, ""), " - "),
                    x=GAP + column * 102, y=HEADER + row * 46, w=96, h=40,
                ),
                page,
            )

    # Each group's own colour wheel and its matrix cycle. Both start the looks
    # sitting in the solo frames above, so both live in a plain frame.
    wheel_ids = [b.wheel_id for b in banks if b.wheel_id is not None]
    wheel_ids += [b.mix_wheel_id for b in banks if b.mix_wheel_id is not None]
    _button_grid(
        frame("Ruedas y Ciclos", MIDDLE_X, 750, MIDDLE_WIDTH, 130),
        [(fid, _wheel_caption(names.get(fid, ""))) for fid in wheel_ids]
        + [
            (m.chaser_id, _after(names.get(m.chaser_id, ""), "Ciclo "))
            for m in matrices if m.chaser_id is not None
        ],
        button, columns=5, width=116, height=44, names=names,
    )

    # --- right column: pad, speed dials, dimmers, strobes, audio ----------
    label_id = ids.take()
    build_label(root_frame, label_id, "Cabezas", RIGHT_X, 8, RIGHT_WIDTH, 20)
    console.widget_ids.append(label_id)

    pad_id = ids.take()
    build_xy_pad(
        root_frame, pad_id, "Cabezas", RIGHT_X, 32, RIGHT_WIDTH, 230,
        fixture_ids=list(mover_fixture_ids),
    )
    console.widget_ids.append(pad_id)

    for index, (caption, function_ids, time_ms) in enumerate(
        (
            ("Vel. Colores", wheel_ids, 1900),
            (
                "Vel. Movimiento",
                [movement.chaser_id] if movement.chaser_id else [],
                10000,
            ),
        )
    ):
        if not function_ids:
            continue
        dial_id = ids.take()
        build_speed_dial(
            root_frame, dial_id, caption,
            RIGHT_X + index * 132, 270, 124, 150,
            function_ids=function_ids, time_ms=time_ms,
        )
        console.widget_ids.append(dial_id)

    # Solo within each: two things driving the same dimmers, or a shutter told
    # to strobe and to reopen at once, cancel each other out. Neither frame
    # holds a function that starts another one in it, so solo is safe here.
    _button_grid(
        frame("Dimmers", RIGHT_X, 428, RIGHT_WIDTH, 74, solo=True),
        [
            (master[n], n)
            for n in ("Dimmer Chase", "Dimmer PingPong") if n in master
        ],
        button, columns=2, width=118, height=44, keys=keys, names=names,
    )
    _button_grid(
        frame("Strobos", RIGHT_X, 508, RIGHT_WIDTH, 124, solo=True),
        [
            (master[n], _after(n, "Strobo ") or n)
            for n in ("Strobo ON", "Strobo OFF", "Strobo Rapido", "Strobo Medio")
            if n in master
        ],
        button, columns=2, width=118, height=44, keys=keys, names=names,
    )

    # One live handle on the matrices: the 90 generated ones are fixed, this
    # swaps the algorithm of a running matrix without stopping it.
    if matrices and matrices[0].matrix_ids:
        matrix_widget_id = ids.take()
        build_matrix_control(
            root_frame, matrix_widget_id, "Matriz", RIGHT_X, 638,
            RIGHT_WIDTH, 146,
            function_id=matrices[0].matrix_ids[0],
            algorithms=list(matrix_algorithms),
        )
        console.widget_ids.append(matrix_widget_id)

    # Last, because a band presses a button and needs its widget ID. Both
    # targets are Toggle: an audio bar calls pressFunction on the way up and
    # again on the way down, which a Flash button would never release.
    triggers_id = ids.take()
    build_audio_triggers(
        root_frame, triggers_id, "Audio", RIGHT_X, 790, RIGHT_WIDTH, 100,
        bars=[
            (name, widget_of.get(master.get(target)) if target else None)
            for name, target in AUDIO_BANDS
        ],
    )
    console.widget_ids.append(triggers_id)

    _set_canvas(workspace.root)
    return console


def _button_grid(
    parent, entries, button, columns, width, height, names,
    keys: dict[str, str] | None = None, flash: set[str] | None = None,
) -> None:
    for index, (function_id, caption) in enumerate(entries):
        column, row = index % columns, index // columns
        name = names.get(function_id, "")
        button(
            parent, function_id, caption,
            x=GAP + column * (width + GAP),
            y=HEADER + row * (height + GAP),
            w=width, h=height,
            key=(keys or {}).get(name),
            action="Flash" if name in (flash or set()) else "Toggle",
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


def _on_page(widget: etree._Element, page: int) -> None:
    """Which page of a multipage frame this widget belongs to; 0 is implicit."""
    if page:
        widget.set("Page", str(page))


def _swatch(name: str, second: bool = False) -> str:
    """The ARGB of the palette colour a scene is named after, or Default."""
    parts = [p.strip() for p in name.split(" / ")]
    text = parts[1] if second and len(parts) > 1 else parts[0]
    for color_name in sorted(PALETTE, key=len, reverse=True):
        if text == color_name or text.startswith(f"{color_name} "):
            return str(argb_from_rgb(PALETTE[color_name]))
    return DEFAULT


def _wheel_caption(name: str) -> str:
    """"Rueda Colores BarrasLed" is wider than its button; drop the "Rueda"."""
    return _after(name, "Rueda ")


def _mix_caption(name: str) -> str:
    """"Rojo / Azul PAR" reads as "R/A" on a 44px button."""
    parts = [p.strip() for p in name.split(" / ")]
    if len(parts) < 2:
        return ""
    return f"{parts[0][:1]}/{parts[1][:1]}"


def _after(name: str, marker: str) -> str:
    _, separator, tail = name.partition(marker)
    return tail if separator else name


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
