"""Page 4's live fader over the panels' speed channel, beside the effects it paces.

Moved verbatim out of `page_library` (2026-09-27 split). `master_button` and
`label` are the console's own widget closures, and `ids` its id counter, so
the widget ids come out in the order they always did.
"""

from collections.abc import Callable

from lxml import etree

from ..names.names import Names
from ..vc.build_level_slider import build_level_slider
from .console_ids import ConsoleIds
from .console_layout import HELP_FONT, PAGE_LIBRARY, RIGHT_WIDTH, RIGHT_X, SMALL_FONT
from .generated_builtins import GeneratedBuiltins
from .generated_console import GeneratedConsole
from .on_page import on_page


def speed_fader(
    outer: etree._Element,
    master_button: Callable[..., etree._Element | None],
    label: Callable[..., etree._Element],
    ids: ConsoleIds,
    console: GeneratedConsole,
    builtins: GeneratedBuiltins,
    vocabulary: Names,
) -> None:
    """The hand-built console's "Strobo LED Effect Speed", whose slider sat
    at 253 with the show's own sequence stepping 160-255. The channel is in
    the Speed group, so it is LTP, not HTP: the slider monitors the running
    value until somebody moves it, and from then on its Override fader wins
    outright - at zero too, which is the slowest, not "the cycle's" - until
    the red reset X hands the channel back (`VCSlider::writeDMXLevel`;
    cross-audit, 2026-09-02).
    """
    if not builtins.speed_channels:
        return
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
