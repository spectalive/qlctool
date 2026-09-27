"""Page 3's GrandMaster: the workspace's own master fader, and the bass hit beside it.

Moved verbatim out of `page_control` (2026-09-27 split). `master_button` and
`label` are the console's own widget closures, and `ids` its id counter, so
the widget ids come out in the order they always did.
"""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from ..vc.build_grand_master_slider import build_grand_master_slider
from .bind_pad import bind_pad
from .console_ids import ConsoleIds
from .console_layout import (
    GAP,
    GRAND_MASTER_HEIGHT,
    GRAND_MASTER_LINES,
    GRAND_MASTER_WIDTH,
    HELP_FONT,
    PAGE_CONTROL,
    RIGHT_WIDTH,
    RIGHT_X,
)
from .generated_console import GeneratedConsole
from .on_page import on_page


def grand_master(
    outer: etree._Element,
    master_button: Callable[..., etree._Element | None],
    label: Callable[..., etree._Element],
    ids: ConsoleIds,
    console: GeneratedConsole,
    pad_bindings: Mapping[str, int],
    vocabulary: Names,
) -> None:
    """Below the audio triggers (they end at y=440): the left column is full,
    four colour banks deep.
    """
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
