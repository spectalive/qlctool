"""The live console's audio triggers: five spectrum bands, one bound to the bass hit.

Moved verbatim out of `generate_live_console` (2026-09-27 split). `ids` is
the console's own id counter, so the widget ids come out in the order they
always did.
"""

from collections.abc import Mapping

from lxml import etree

from ..names.names import Names
from ..vc.build_audio_triggers import build_audio_triggers
from .console_ids import ConsoleIds
from .console_layout import AUDIO_BANDS, PAGE_CONTROL, RIGHT_WIDTH, RIGHT_X
from .generated_console import GeneratedConsole
from .on_page import on_page


def audio_triggers_row(
    outer: etree._Element,
    ids: ConsoleIds,
    console: GeneratedConsole,
    master: Mapping[str, int],
    widget_of: Mapping[int, int],
    vocabulary: Names,
) -> None:
    """Last, because a band presses a button and needs its widget ID."""
    bars: list[tuple[str, int | None]] = []
    for band, target in AUDIO_BANDS:
        pressed = master.get(vocabulary.display(target)) if target else None
        bars.append(
            (vocabulary.display(band), widget_of.get(pressed) if pressed is not None else None)
        )
    triggers_id = ids.take()
    triggers = build_audio_triggers(
        outer,
        triggers_id,
        vocabulary.display("audio_triggers"),
        RIGHT_X,
        330,
        RIGHT_WIDTH,
        110,
        bars=bars,
    )
    on_page(triggers, PAGE_CONTROL)
    console.widget_ids.append(triggers_id)
