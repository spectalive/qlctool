"""Page 3 of the live console: direct controls that remain useful beside the play families.

Moved verbatim out of `live_console` (2026-09-27 split). The widget closures
(`button`, `master_button`, `frame`, `label`) and the id counter are the
console's own, so the widget ids come out in the order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.appearance import DEFAULT
from ..vc.bank_pitch import (
    BANK_COLUMN_TOP,
    DIMMER_FRAME_HEIGHT,
    bank_pitch_for,
)
from ..vc.button import FLASH
from ..vc.dial_function import DialFunction
from ..vc.grand_master_slider import build_grand_master_slider
from ..vc.speed_dial import build_speed_dial
from ..vc.xy_pad import build_xy_pad
from .bank_caption import bank_caption
from .bind_pad import bind_pad
from .console_ids import ConsoleIds
from .console_layout import (
    BANK_KEYS,
    DIMMER_CHASES,
    GAP,
    GRAND_MASTER_HEIGHT,
    GRAND_MASTER_LINES,
    GRAND_MASTER_WIDTH,
    HEADER,
    HELP_FONT,
    LEFT_WIDTH,
    LEFT_X,
    MIDDLE_WIDTH,
    MIDDLE_X,
    MOVEMENT_DIAL_LINES,
    OUTER_WIDTH,
    PAGE_CONTROL,
    RIGHT_WIDTH,
    RIGHT_X,
    SMALL_FONT,
    TEMPO_TAP_KEY,
    TINY_FONT,
    TITLE_FONT,
)
from .generated_bank import GeneratedBank
from .generated_console import GeneratedConsole
from .mix_caption import mix_caption
from .on_page import on_page
from .page_control_title import page_control_title
from .swatch import swatch
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

    # The banks are one frame per fixture group, and the number of groups is
    # not a constant: a fifth group (the two MAC WASH, 2026-08-31) pushed this
    # column and everything under it off the bottom of the screen, which the
    # `consola` rule reported and the generator's own "fits on one screen" line
    # had cheerfully denied. So the pitch comes from the room left between the
    # layers above and the dimmer frame below, never from a number typed here.
    # Held, with ForceLTP, since 2026-09-02: RGB mixes HTP, so a latched bank
    # on top of a running state never showed its colour - AUTO on cyan plus
    # key 1 was white on twenty-seven fixtures (cross-audit). A Flash with
    # Override and ForceLTP writes past the HTP compare and the state's own
    # wheel steps, so "the heads are red" is true for as long as the key is
    # down, and the state's colour comes straight back on release. A plain
    # frame: momentary buttons have nothing for a solo frame to stop.
    y = BANK_COLUMN_TOP
    bank_pitch = bank_pitch_for(len(banks))
    for bank in banks:
        element = frame(
            outer,
            vocabulary.render("bank_frame", group=bank.group_name),
            LEFT_X,
            y,
            LEFT_WIDTH,
            bank_pitch - 6,
            page=PAGE_CONTROL,
            font=TITLE_FONT,
        )
        # Keys 1-0 follow the bank's key list - eight solids, then the old
        # blue/red splits on 9 and 0 (restored 2026-08-28). The solids the
        # splits displaced stay in the row, keyless, after them.
        keyed = bank.key_ids[: len(BANK_KEYS)] or bank.scene_ids[: len(BANK_KEYS)]
        keyless = [fid for fid in bank.scene_ids if fid not in keyed]
        pitch = (LEFT_WIDTH - 2 * GAP) // max(len(keyed) + len(keyless), 1)
        for index, function_id in enumerate(keyed + keyless):
            name = names.get(function_id, "")
            split = " / " in name
            button(
                element,
                function_id,
                mix_caption(name, mix_code) if split else bank_caption(name, short_colour),
                x=GAP + index * pitch,
                y=HEADER,
                w=pitch - 3,
                h=44,
                key=BANK_KEYS[index] if index < len(keyed) else None,
                action=FLASH,
                flash_override=True,
                flash_force_ltp=True,
                background=swatch(name, palette),
                foreground=swatch(name, palette, second=True) if split else DEFAULT,
                font=TINY_FONT if split else SMALL_FONT,
            )
        y += bank_pitch

    if has_intensity:
        dimmers = frame(
            outer,
            vocabulary.display("intensity_chases"),
            LEFT_X,
            y,
            LEFT_WIDTH,
            DIMMER_FRAME_HEIGHT,
            page=PAGE_CONTROL,
            font=TITLE_FONT,
        )
        for index, (function, caption) in enumerate(DIMMER_CHASES):
            column, row = index % 3, index // 3
            master_button(
                dimmers,
                vocabulary.display(function),
                vocabulary.display(caption),
                GAP + column * 170,
                HEADER + row * 52,
                166,
                46,
            )

    # Below the audio triggers (they end at y=440): the left column is full,
    # four colour banks deep.
    grand_master_y = 450
    # The bass bar's target has to be a widget (SpectrumBar presses widgets,
    # not functions), so its plain white hit gets a button of its own here,
    # beside the audio triggers that press it.
    master_button(
        outer,
        vocabulary.display("bass_hit"),
        vocabulary.display("bass_button"),
        RIGHT_X + GRAND_MASTER_WIDTH + GAP,
        grand_master_y,
        RIGHT_WIDTH - GRAND_MASTER_WIDTH - GAP,
        60,
        page=PAGE_CONTROL,
    )
    grand_master_id = ids.take()
    grand_master = build_grand_master_slider(
        outer,
        grand_master_id,
        vocabulary.display("grand_master"),
        RIGHT_X,
        grand_master_y,
        GRAND_MASTER_WIDTH,
        GRAND_MASTER_HEIGHT,
    )
    bind_pad(grand_master, pad_bindings, vocabulary.display("grand_master"))
    on_page(grand_master, PAGE_CONTROL)
    console.widget_ids.append(grand_master_id)
    for index, line in enumerate(GRAND_MASTER_LINES):
        label(
            outer,
            vocabulary.display(line),
            RIGHT_X,
            grand_master_y + GRAND_MASTER_HEIGHT + GAP + index * 22,
            RIGHT_WIDTH,
            20,
            page=PAGE_CONTROL,
            font=HELP_FONT,
        )

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

    # Keep the aiming controls directly below the beam wheel. The outer frame
    # is 892px tall, so the pad leaves the same 6px inset at its bottom after
    # taking the space released by moving the wheel up (2026-09-03). A rig
    # with nothing that pans and tilts gets no pad to aim nothing with.
    if mover_fixture_ids:
        label(
            outer,
            vocabulary.display("aim_frame"),
            MIDDLE_X,
            224,
            MIDDLE_WIDTH,
            20,
            page=PAGE_CONTROL,
            font=HELP_FONT,
        )
        pad_id = ids.take()
        pad = build_xy_pad(
            outer,
            pad_id,
            vocabulary.display("xy_pad"),
            MIDDLE_X,
            250,
            MIDDLE_WIDTH,
            636,
            fixture_ids=list(mover_fixture_ids),
        )
        on_page(pad, PAGE_CONTROL)
        console.widget_ids.append(pad_id)

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
