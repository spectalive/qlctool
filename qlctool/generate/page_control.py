"""Page 3 of the live console: direct controls that remain useful beside the play families.

Moved verbatim out of `live_console` (2026-09-27 split). The widget closures
(`button`, `master_button`, `frame`, `label`) and the id counter are the
console's own, so the widget ids come out in the order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.dial_function import DialFunction
from ..vc.speed_dial import build_speed_dial
from .aim_pad import aim_pad
from .bank_column import bank_column
from .bind_pad import bind_pad
from .console_ids import ConsoleIds
from .console_layout import (
    DIMMER_CHASES,
    HELP_FONT,
    LEFT_X,
    MIDDLE_WIDTH,
    MIDDLE_X,
    MOVEMENT_DIAL_LINES,
    OUTER_WIDTH,
    PAGE_CONTROL,
    RIGHT_WIDTH,
    RIGHT_X,
    TEMPO_TAP_KEY,
    TITLE_FONT,
)
from .generated_bank import GeneratedBank
from .generated_console import GeneratedConsole
from .grand_master import grand_master
from .intensity import intensity
from .on_page import on_page
from .page_control_title import page_control_title
from .wheel_frame import wheel_frame
from .wheel_scenes import GeneratedWheel


def page_control(
    outer: etree._Element,
    button: Callable[..., etree._Element],
    master_button: Callable[..., etree._Element | None],
    frame: Callable[..., etree._Element],
    label: Callable[..., etree._Element],
    ids: ConsoleIds,
    console: GeneratedConsole,
    names: Mapping[int, str],
    banks: Sequence[GeneratedBank],
    beam_colors: GeneratedWheel,
    master: Mapping[str, int],
    mover_fixture_ids: Sequence[int],
    movement_functions: Sequence[DialFunction],
    tempo_beat_ms: int,
    palette: Mapping[str, tuple[int, int, int]],
    pad_bindings: Mapping[str, int],
    vocabulary: Names,
    short_colour: Mapping[str, str],
    mix_code: Mapping[str, str],
    has_smoke_machine: bool,
) -> None:
    """Page 3: direct controls that remain useful beside the play families."""
    # Page 3's one haze control is the vertical column's light, and its beam
    # wheel frame is built only from beam colour scenes; without either the
    # page title does not promise it. The column's light is built from the
    # panels alone, so haze is promised only where a smoke machine is patched
    # too (2026-09-25: "y humo" on a rig with panels and no smoke machine).
    has_haze_light = (
        has_smoke_machine and master.get(vocabulary.display("vertical_smoke")) is not None
    )
    # A rig with no fader dimmer and no fixture strobe has nothing for the
    # intensity frame to hold (2026-09-26, round G), so it is not drawn empty
    # and the title does not name it.
    has_intensity = any(master.get(vocabulary.display(f)) is not None for f, _ in DIMMER_CHASES)
    label(
        outer,
        vocabulary.display(
            page_control_title(
                has_haze_light,
                bool(beam_colors.scene_ids),
                has_heads=bool(mover_fixture_ids),
                has_intensity=has_intensity,
            )
        ),
        LEFT_X,
        30,
        OUTER_WIDTH - 16,
        30,
        page=PAGE_CONTROL,
        font=TITLE_FONT,
    )

    y = bank_column(outer, button, frame, names, banks, palette, short_colour, mix_code, vocabulary)

    intensity(outer, master_button, frame, has_intensity, y, vocabulary)

    grand_master(outer, master_button, label, ids, console, pad_bindings, vocabulary)

    # The vertical smoke's light: latched on purpose - the column lasts as
    # long as it lasts, and somebody presses it off when it is over.
    # Its help explains that button, so it goes where the button goes.
    if has_haze_light:
        master_button(
            outer,
            vocabulary.display("vertical_smoke"),
            vocabulary.display("vertical_smoke_light"),
            RIGHT_X,
            716,
            RIGHT_WIDTH,
            60,
            page=PAGE_CONTROL,
        )
        label(
            outer,
            vocabulary.display("vertical_smoke_help"),
            RIGHT_X,
            782,
            RIGHT_WIDTH,
            60,
            page=PAGE_CONTROL,
            font=HELP_FONT,
        )

    # The beams' own colour wheel remains held here. A latched colour-wheel
    # pick on JUGAR would stop the rig wheel and leave every RGB fixture dark.
    wheel_frame(
        outer,
        button,
        frame,
        names,
        vocabulary,
        beam_colors.scene_ids,
        vocabulary.display("beam_wheel_frame"),
        "Color Beam - ",
        MIDDLE_X,
        68,
        MIDDLE_WIDTH,
        150,
        PAGE_CONTROL,
        columns=12,
    )

    aim_pad(outer, label, ids, console, mover_fixture_ids, vocabulary)

    # The movement dial stays with the direct controls and on the same tap key
    # as page 1's tempo. It re-times each rotation AND the EFX
    # under it, chaser fade included, so the figure stays the same fraction
    # of its step whatever the room is doing.
    if movement_functions:
        dial_id = ids.take()
        dial = build_speed_dial(
            outer,
            dial_id,
            vocabulary.display("movement_speed"),
            RIGHT_X,
            68,
            124,
            150,
            functions=movement_functions,
            time_ms=tempo_beat_ms,
            tap_key=TEMPO_TAP_KEY,
        )
        bind_pad(dial, pad_bindings, vocabulary.display("movement_speed"))
        on_page(dial, PAGE_CONTROL)
        console.widget_ids.append(dial_id)
        for index, line in enumerate(MOVEMENT_DIAL_LINES):
            label(
                outer,
                vocabulary.display(line),
                RIGHT_X,
                228 + index * 22,
                RIGHT_WIDTH,
                20,
                page=PAGE_CONTROL,
                font=HELP_FONT,
            )
