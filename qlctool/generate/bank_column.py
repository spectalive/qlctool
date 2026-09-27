"""Page 3's colour bank column: one frame per fixture group, keys 1-0 across each.

Moved verbatim out of `page_control` (2026-09-27 split). `button` and `frame`
are the console's own widget closures, so the widget ids come out in the
order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.bank_pitch_for import BANK_COLUMN_TOP, bank_pitch_for
from ..vc.build_appearance import DEFAULT
from ..vc.build_button import FLASH
from .bank_caption import bank_caption
from .console_layout import (
    BANK_KEYS,
    GAP,
    HEADER,
    LEFT_WIDTH,
    LEFT_X,
    PAGE_CONTROL,
    SMALL_FONT,
    TINY_FONT,
    TITLE_FONT,
)
from .generated_bank import GeneratedBank
from .mix_caption import mix_caption
from .swatch import swatch


def bank_column(
    outer: etree._Element,
    button: Callable[..., etree._Element],
    frame: Callable[..., etree._Element],
    names: Mapping[int, str],
    banks: Sequence[GeneratedBank],
    palette: Mapping[str, tuple[int, int, int]],
    short_colour: Mapping[str, str],
    mix_code: Mapping[str, str],
    vocabulary: Names,
) -> int:
    """The banks are one frame per fixture group, and the number of groups is
    not a constant: a fifth group (the two MAC WASH, 2026-08-31) pushed this
    column and everything under it off the bottom of the screen, which the
    `consola` rule reported and the generator's own "fits on one screen" line
    had cheerfully denied. So the pitch comes from the room left between the
    layers above and the dimmer frame below, never from a number typed here.
    Held, with ForceLTP, since 2026-09-02: RGB mixes HTP, so a latched bank
    on top of a running state never showed its colour - AUTO on cyan plus
    key 1 was white on twenty-seven fixtures (cross-audit). A Flash with
    Override and ForceLTP writes past the HTP compare and the state's own
    wheel steps, so "the heads are red" is true for as long as the key is
    down, and the state's colour comes straight back on release. A plain
    frame: momentary buttons have nothing for a solo frame to stop.

    Returns the y position where the column ends.
    """
    y = BANK_COLUMN_TOP
    bank_pitch = bank_pitch_for(len(banks))
    for bank in banks:
        element = frame(
            outer,
            vocabulary.render("bank_frame", group=bank.group_name),
            LEFT_X,
            y,
            LEFT_WIDTH,
            bank_pitch - 6,
            page=PAGE_CONTROL,
            font=TITLE_FONT,
        )
        # Keys 1-0 follow the bank's key list - eight solids, then the old
        # blue/red splits on 9 and 0 (restored 2026-08-28). The solids the
        # splits displaced stay in the row, keyless, after them.
        keyed = bank.key_ids[: len(BANK_KEYS)] or bank.scene_ids[: len(BANK_KEYS)]
        keyless = [fid for fid in bank.scene_ids if fid not in keyed]
        pitch = (LEFT_WIDTH - 2 * GAP) // max(len(keyed) + len(keyless), 1)
        for index, function_id in enumerate(keyed + keyless):
            name = names.get(function_id, "")
            split = " / " in name
            button(
                element,
                function_id,
                mix_caption(name, mix_code) if split else bank_caption(name, short_colour),
                x=GAP + index * pitch,
                y=HEADER,
                w=pitch - 3,
                h=44,
                key=BANK_KEYS[index] if index < len(keyed) else None,
                action=FLASH,
                flash_override=True,
                flash_force_ltp=True,
                background=swatch(name, palette),
                foreground=swatch(name, palette, second=True) if split else DEFAULT,
                font=TINY_FONT if split else SMALL_FONT,
            )
        y += bank_pitch
    return y
