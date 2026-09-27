"""Page 4 of the live console: the material the show is built from, not buttons for a set.

Moved verbatim out of `live_console` (2026-09-27 split). The widget closures
(`button`, `master_button`, `frame`, `label`) and the id counter are the
console's own, so the widget ids come out in the order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.level_slider import build_level_slider
from ..vc.matrix_control import build_matrix_control
from .beam_subsets import GeneratedBeamSubsets
from .builtin_effects import GeneratedBuiltins
from .console_ids import ConsoleIds
from .console_layout import (
    HELP_FONT,
    LEFT_WIDTH,
    LEFT_X,
    LIBRARY_SEPARATOR,
    OUTER_WIDTH,
    PAGE_LIBRARY,
    RIGHT_WIDTH,
    RIGHT_X,
    SMALL_FONT,
    TITLE_FONT,
)
from .cycles import cycles
from .generated_bank import GeneratedBank
from .generated_console import GeneratedConsole
from .generated_matrices import GeneratedMatrices
from .library_help_lines import library_help_lines
from .matrix_frame import matrix_frame
from .mixes import mixes
from .on_page import on_page
from .panels import panels
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

    matrix_frame(outer, button, frame, label, names, matrices, has_bars, has_panels, vocabulary)

    cycles(outer, button, frame, names, banks, matrices, builtins, vocabulary)

    panels(outer, button, frame, names, builtins, has_panels, vocabulary)

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
