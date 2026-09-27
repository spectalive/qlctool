"""Page 1's tempo dial: the room's tempo, tapped where the operator is looking.

Moved verbatim out of `page_show` (2026-09-27 split). `label` is the
console's own widget closure, and `ids` its id counter, so the widget ids
come out in the order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.dial_function import DialFunction
from ..vc.speed_dial import build_speed_dial
from .bind_pad import bind_pad
from .console_ids import ConsoleIds
from .console_layout import HELP_FONT, PAGE_SHOW, RIGHT_WIDTH, RIGHT_X, TEMPO_TAP_KEY
from .generated_console import GeneratedConsole
from .on_page import on_page
from .tempo_close_line import tempo_close_line
from .tempo_help_line import tempo_help_line


def tempo_dial(
    outer: etree._Element,
    label: Callable[..., etree._Element],
    ids: ConsoleIds,
    console: GeneratedConsole,
    master: Mapping[str, int],
    tempo_functions: Sequence[DialFunction],
    bpm_tap: bool,
    tempo_beat_ms: int,
    pad_bindings: Mapping[str, int],
    vocabulary: Names,
) -> None:
    """The tempo dial, where the operator is looking, with the hand-built
    console's tap key. Each layer carries its own multiplier - see
    `beat_multiplier` - so one tap re-times all of them and none of them
    loses its proportion to the rest.
    """
    if not tempo_functions and not bpm_tap:
        return
    dial_id = ids.take()
    dial = build_speed_dial(
        outer,
        dial_id,
        vocabulary.display("tempo_dial"),
        RIGHT_X,
        700,
        RIGHT_WIDTH,
        120,
        functions=tempo_functions,
        time_ms=tempo_beat_ms,
        tap_key=TEMPO_TAP_KEY,
        control_bpm=bpm_tap,
    )
    bind_pad(dial, pad_bindings, vocabulary.display("tempo_dial"))
    on_page(dial, PAGE_SHOW)
    console.widget_ids.append(dial_id)
    # The middle line names the gobo and prism animations only when the show
    # built them: they are what the dial would re-time.
    tempo_lines = (
        "tempo_1",
        tempo_help_line(
            master.get(vocabulary.display("gobo_animation")) is not None,
            master.get(vocabulary.display("prism_animation")) is not None,
            master.get(vocabulary.display("dimmer_chase")) is not None,
        ),
        tempo_close_line(master.get(vocabulary.display("head_movements")) is not None),
    )
    for index, line in enumerate(tempo_lines):
        label(
            outer,
            vocabulary.display(line),
            RIGHT_X,
            824 + index * 20,
            RIGHT_WIDTH,
            20,
            page=PAGE_SHOW,
            font=HELP_FONT,
        )
