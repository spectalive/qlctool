"""Page 3's aiming pad, directly below the beam wheel.

Moved verbatim out of `page_control` (2026-09-27 split). `label` is the
console's own widget closure, and `ids` its id counter, so the widget ids
come out in the order they always did.
"""

from collections.abc import Callable, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.build_xy_pad import build_xy_pad
from .console_ids import ConsoleIds
from .console_layout import HELP_FONT, MIDDLE_WIDTH, MIDDLE_X, PAGE_CONTROL
from .generated_console import GeneratedConsole
from .on_page import on_page


def aim_pad(
    outer: etree._Element,
    label: Callable[..., etree._Element],
    ids: ConsoleIds,
    console: GeneratedConsole,
    mover_fixture_ids: Sequence[int],
    vocabulary: Names,
) -> None:
    """The outer frame is 892px tall, so the pad leaves the same 6px inset at
    its bottom after taking the space released by moving the wheel up
    (2026-09-03). A rig with nothing that pans and tilts gets no pad to aim
    nothing with.
    """
    if not mover_fixture_ids:
        return
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
