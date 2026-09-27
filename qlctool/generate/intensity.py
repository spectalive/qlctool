"""Page 3's intensity chases and the fixture strobe, three across two rows.

Moved verbatim out of `page_control` (2026-09-27 split). `master_button` and
`frame` are the console's own widget closures, so the widget ids come out in
the order they always did.
"""

from collections.abc import Callable

from lxml import etree

from ..names.names import Names
from ..vc.bank_pitch_for import DIMMER_FRAME_HEIGHT
from .console_layout import DIMMER_CHASES, GAP, HEADER, LEFT_WIDTH, LEFT_X, PAGE_CONTROL, TITLE_FONT


def intensity(
    outer: etree._Element,
    master_button: Callable[..., etree._Element | None],
    frame: Callable[..., etree._Element],
    has_intensity: bool,
    y: int,
    vocabulary: Names,
) -> None:
    """A rig with no fader dimmer and no fixture strobe has nothing for this
    frame to hold (2026-09-26, round G), so it is not drawn empty.
    """
    if not has_intensity:
        return
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
