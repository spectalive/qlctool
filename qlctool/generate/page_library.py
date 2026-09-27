"""Page 4 of the live console: the material the show is built from, not buttons for a set.

Moved verbatim out of `live_console` (2026-09-27 split). The widget closures
(`button`, `master_button`, `frame`, `label`) and the id counter are the
console's own, so the widget ids come out in the order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..names.template_affixes import template_affixes
from ..vc.level_slider import build_level_slider
from ..vc.matrix_control import build_matrix_control
from .after_marker import after_marker
from .beam_subsets import GeneratedBeamSubsets
from .before_marker import before_marker
from .builtin_effects import GeneratedBuiltins
from .console_ids import ConsoleIds
from .console_layout import (
    GAP,
    HEADER,
    HELP_FONT,
    LEFT_WIDTH,
    LEFT_X,
    LIBRARY_SEPARATOR,
    MATRIX_BUTTON_HEIGHT,
    MATRIX_COLUMNS,
    MATRIX_ROW_HEIGHT,
    MIDDLE_WIDTH,
    MIDDLE_X,
    OUTER_WIDTH,
    PAGE_LIBRARY,
    RIGHT_WIDTH,
    RIGHT_X,
    SMALL_FONT,
    TINY_FONT,
    TITLE_FONT,
)
from .first_of import first_of
from .generated_bank import GeneratedBank
from .generated_console import GeneratedConsole
from .generated_matrices import GeneratedMatrices
from .library_help_lines import library_help_lines
from .matrices_frame_caption import matrices_frame_caption
from .mixes import mixes
from .on_page import on_page
from .panels_frame_caption import panels_frame_caption
from .wheel_frame import wheel_frame


def page_library(
    outer: etree._Element,
    button: Callable[..., etree._Element],
    master_button: Callable[..., etree._Element | None],
    frame: Callable[..., etree._Element],
    label: Callable[..., etree._Element],
    ids: ConsoleIds,
    console: GeneratedConsole,
    names: Mapping[int, str],
    banks: Sequence[GeneratedBank],
    matrices: Sequence[GeneratedMatrices],
    builtins: GeneratedBuiltins,
    matrix_algorithms: Sequence[str],
    beam_subsets: GeneratedBeamSubsets | None,
    palette: Mapping[str, tuple[int, int, int]],
    vocabulary: Names,
    mix_code: Mapping[str, str],
    has_bars: bool,
    has_panels: bool,
) -> None:
    """Page 4: the material the show is built from, not buttons for a set."""
    label(
        outer,
        vocabulary.display("page_library"),
        LEFT_X,
        30,
        OUTER_WIDTH - 16,
        30,
        page=PAGE_LIBRARY,
        font=TITLE_FONT,
    )

    library_splits = [[fid for fid in bank.split_ids if fid not in bank.key_ids] for bank in banks]
    mixes(outer, button, frame, label, names, banks, library_splits, palette, mix_code, vocabulary)

    wheel_frame(
        outer,
        button,
        frame,
        names,
        vocabulary,
        beam_subsets.multicolor_scene_ids if beam_subsets is not None else [],
        vocabulary.display("multicolour_frame"),
        "MultiColor - ",
        LEFT_X,
        306,
        LEFT_WIDTH,
        92,
        PAGE_LIBRARY,
        columns=8,
    )

    # No matrix to press (a rig of two panels, 2026-09-26): no frame, and no
    # caption promising patterns on them.
    if any(generated.matrix_ids for generated in matrices):
        matrix_frame = frame(
            outer,
            vocabulary.display(matrices_frame_caption(has_bars, has_panels)),
            MIDDLE_X,
            68,
            MIDDLE_WIDTH,
            300,
            page=PAGE_LIBRARY,
            solo=True,
            pages=len(matrices) or 1,
            font=TITLE_FONT,
        )
        for page, generated in enumerate(matrices):
            first = first_of(generated.matrix_ids)
            group = before_marker(names.get(first, "") if first is not None else "", " - ")
            label(
                matrix_frame,
                vocabulary.render("group_label", group=group),
                GAP,
                HEADER,
                400,
                20,
                page=page,
                font=HELP_FONT,
            )
            step = (MIDDLE_WIDTH - GAP * 2) // MATRIX_COLUMNS
            for index, function_id in enumerate(generated.matrix_ids):
                column, row = index % MATRIX_COLUMNS, index // MATRIX_COLUMNS
                on_page(
                    button(
                        matrix_frame,
                        function_id,
                        after_marker(names.get(function_id, ""), " - "),
                        x=GAP + column * step,
                        y=HEADER + 24 + row * MATRIX_ROW_HEIGHT,
                        w=step - 6,
                        h=MATRIX_BUTTON_HEIGHT,
                        font=SMALL_FONT,
                    ),
                    page,
                )

    # Each group's own colour wheel and its matrix cycle. Both start the looks
    # sitting in the solo frames above, so both live in a plain frame.
    cycles = frame(
        outer,
        vocabulary.display("group_wheels_frame"),
        MIDDLE_X,
        376,
        MIDDLE_WIDTH,
        190,
        page=PAGE_LIBRARY,
        font=TITLE_FONT,
    )
    # The wheel captions are rendered from the bank, not parsed from the
    # wheel's name (ruling B8).
    entries = [
        (b.wheel_id, vocabulary.render("group_colour_wheel_caption", group=b.group_name))
        for b in banks
        if b.wheel_id is not None
    ]
    entries += [
        (b.mix_wheel_id, vocabulary.render("group_mix_wheel_caption", group=b.group_name))
        for b in banks
        if b.mix_wheel_id is not None
    ]
    cycle_marker = template_affixes(vocabulary, "cycle")[0]
    entries += [
        (m.chaser_id, after_marker(names.get(m.chaser_id, ""), cycle_marker))
        for m in matrices
        if m.chaser_id is not None
    ]
    # The panels' own cycle belongs here and not among the effects it starts:
    # a chaser sharing a solo frame with its own steps dies as it begins.
    if builtins.chaser_id is not None:
        entries.append(
            (
                builtins.chaser_id,
                after_marker(names.get(builtins.chaser_id, ""), cycle_marker),
            )
        )
    for index, (function_id, caption) in enumerate(entries):
        column, row = index % 5, index // 5
        button(
            cycles,
            function_id,
            caption,
            x=GAP + column * 122,
            y=HEADER + row * 50,
            w=116,
            h=44,
            font=SMALL_FONT,
        )

    if builtins.scene_ids:
        panels = frame(
            outer,
            vocabulary.render(panels_frame_caption(has_panels), count=len(builtins.scene_ids)),
            MIDDLE_X,
            580,
            MIDDLE_WIDTH,
            244,
            page=PAGE_LIBRARY,
            solo=True,
            font=TITLE_FONT,
        )
        for index, function_id in enumerate(builtins.scene_ids):
            column, row = index % 12, index // 12
            button(
                panels,
                function_id,
                after_marker(names.get(function_id, ""), " - "),
                x=GAP + column * 51,
                y=HEADER + row * 52,
                w=47,
                h=46,
                font=TINY_FONT,
            )

    if builtins.speed_channels:
        # The live fader over the panels' speed channel, beside the effects it
        # paces - the hand-built console's "Strobo LED Effect Speed", whose
        # slider sat at 253 with the show's own sequence stepping 160-255.
        # The channel is in the Speed group, so it is LTP, not HTP: the slider
        # monitors the running value until somebody moves it, and from then
        # on its Override fader wins outright - at zero too, which is the
        # slowest, not "the cycle's" - until the red reset X hands the channel
        # back (`VCSlider::writeDMXLevel`; cross-audit, 2026-09-02).
        slider_id = ids.take()
        slider = build_level_slider(
            outer,
            slider_id,
            vocabulary.display("panel_speed"),
            RIGHT_X,
            580,
            90,
            244,
            channels=list(builtins.speed_channels),
        )
        on_page(slider, PAGE_LIBRARY)
        console.widget_ids.append(slider_id)
        label(
            outer,
            vocabulary.display("panel_speed_help"),
            RIGHT_X + 96,
            580,
            RIGHT_WIDTH - 96,
            120,
            page=PAGE_LIBRARY,
            font=HELP_FONT,
        )
        # The old "Strobo LED - Speed Auto", beside the fader it shares the
        # channel with: the pace rides 160-255 on its own until somebody
        # stops it (HTP - the raised fader wins while it is higher).
        master_button(
            outer,
            vocabulary.display("panel_speed_auto"),
            vocabulary.display("panel_speed_auto_button"),
            RIGHT_X + 96,
            704,
            RIGHT_WIDTH - 96,
            60,
            page=PAGE_LIBRARY,
            font=SMALL_FONT,
        )

    if matrices and matrices[0].matrix_ids:
        matrix_widget_id = ids.take()
        control = build_matrix_control(
            outer,
            matrix_widget_id,
            vocabulary.display("live_matrix"),
            RIGHT_X,
            68,
            RIGHT_WIDTH,
            200,
            function_id=matrices[0].matrix_ids[0],
            algorithms=list(matrix_algorithms),
        )
        on_page(control, PAGE_LIBRARY)
        console.widget_ids.append(matrix_widget_id)

    lines = library_help_lines(
        bool(builtins.scene_ids),
        has_panels,
        has_mixes=any(library_splits),
        has_matrices=any(generated.matrix_ids for generated in matrices),
    )
    for index, line in enumerate(lines):
        label(
            outer,
            LIBRARY_SEPARATOR
            if line is None
            else vocabulary.render(line, count=len(builtins.scene_ids)),
            LEFT_X,
            410 + index * 26,
            LEFT_WIDTH,
            24,
            page=PAGE_LIBRARY,
            font=HELP_FONT,
        )
