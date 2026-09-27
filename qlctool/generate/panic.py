"""Page 1's panic frame: StopAll and Blackout, the two answers to "something is on".

Moved verbatim out of `page_show` (2026-09-27 split). `button` and `frame` are
the console's own widget closures, so the widget ids come out in the order
they always did.
"""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from ..vc.build_button import BLACKOUT, STOP_ALL
from .bind_pad import bind_pad
from .console_layout import (
    BIG_FONT,
    BLACKOUT_KEY,
    GAP,
    HEADER,
    HELP_FONT,
    LEFT_X,
    OUTER_WIDTH,
    PAGE_SHOW,
    STOP_ALL_FADE_MS,
    STOP_ALL_KEY,
    TITLE_FONT,
)


def panic(
    outer: etree._Element,
    button: Callable[..., etree._Element],
    frame: Callable[..., etree._Element],
    label: Callable[..., etree._Element],
    pad_bindings: Mapping[str, int],
    vocabulary: Names,
) -> None:
    """The panic frame: StopAll and Blackout."""
    panic = frame(
        outer,
        vocabulary.display("panic_frame"),
        LEFT_X,
        500,
        OUTER_WIDTH - 16,
        118,
        page=PAGE_SHOW,
        font=TITLE_FONT,
    )
    # Neither drives a function of its own. StopAll stops every one that is
    # running, which is the only honest answer to "something is on and nobody
    # knows what started it". Blackout answers a different question - it forces
    # the outputs themselves to zero, for when the desk is stuck showing light
    # that no running function accounts for. And unlike StopAll, Blackout is a
    # latch, not a one-shot: qmlui's VCButton::Action::Blackout case toggles
    # `inputOutputMap()->toggleBlackout()` on press (qmlui/virtualconsole/
    # vcbutton.cpp:445-450) - the first APAGON forces the room dark regardless
    # of what AUTO or a moment is still doing underneath, and only a second
    # APAGON lifts it back to that. AUTO restarts nothing while blacked out:
    # it has to follow the second APAGON, not replace it - the help label
    # below says so.
    # The panic pair rides the SMC-PAD's transport buttons - on the device's
    # right edge, physically apart from the pads a hand hammers in the dark.
    stop_all = button(
        panic,
        None,
        vocabulary.display("stop_all_button"),
        GAP + 2,
        HEADER + 4,
        460,
        78,
        action=STOP_ALL,
        key=STOP_ALL_KEY,
        stop_all_fade_ms=STOP_ALL_FADE_MS,
        font=BIG_FONT,
    )
    bind_pad(stop_all, pad_bindings, vocabulary.display("stop_all"))
    blackout = button(
        panic,
        None,
        vocabulary.display("blackout_button"),
        474,
        HEADER + 4,
        200,
        78,
        action=BLACKOUT,
        key=BLACKOUT_KEY,
        font=BIG_FONT,
    )
    bind_pad(blackout, pad_bindings, vocabulary.display("blackout"))
    label(
        panic,
        vocabulary.display("panic_help"),
        680,
        HEADER + 4,
        726,
        78,
        font=HELP_FONT,
    )
