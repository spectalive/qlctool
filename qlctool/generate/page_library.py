"""Page 4 of the live console: the material the show is built from, not buttons for a set.

Moved verbatim out of `live_console` (2026-09-27 split). The widget closures
(`button`, `master_button`, `frame`, `label`) and the id counter are the
console's own, so the widget ids come out in the order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from .beam_subsets import GeneratedBeamSubsets
from .console_ids import ConsoleIds
from .console_layout import LEFT_WIDTH, LEFT_X, OUTER_WIDTH, PAGE_LIBRARY, TITLE_FONT
from .cycles import cycles
from .generated_bank import GeneratedBank
from .generated_builtins import GeneratedBuiltins
from .generated_console import GeneratedConsole
from .generated_matrices import GeneratedMatrices
from .library_help import library_help
from .live_matrix import live_matrix
from .matrix_frame import matrix_frame
from .mixes import mixes
from .panels import panels
from .speed_fader import speed_fader
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

    speed_fader(outer, master_button, label, ids, console, builtins, vocabulary)

    live_matrix(outer, ids, console, matrices, matrix_algorithms, vocabulary)

    library_help(
        outer,
        label,
        builtins,
        has_panels,
        any(library_splits),
        any(generated.matrix_ids for generated in matrices),
        vocabulary,
    )
