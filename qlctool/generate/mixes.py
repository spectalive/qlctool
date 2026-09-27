"""Page 4's mixes frame: the two-colour splits a bank's keys do not carry.

Moved verbatim out of `page_library` (2026-09-27 split). `button`, `frame` and
`label` are the console's own widget closures, so the widget ids come out in
the order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..vc.build_button import FLASH
from .console_layout import (
    GAP,
    HEADER,
    HELP_FONT,
    LEFT_WIDTH,
    LEFT_X,
    PAGE_LIBRARY,
    TINY_FONT,
    TITLE_FONT,
)
from .generated_bank import GeneratedBank
from .mix_caption import mix_caption
from .on_page import on_page
from .swatch import swatch


def mixes(
    outer: etree._Element,
    button: Callable[..., etree._Element],
    frame: Callable[..., etree._Element],
    label: Callable[..., etree._Element],
    names: Mapping[int, str],
    banks: Sequence[GeneratedBank],
    library_splits: Sequence[Sequence[int]],
    palette: Mapping[str, tuple[int, int, int]],
    mix_code: Mapping[str, str],
    vocabulary: Names,
) -> None:
    """Held with ForceLTP like the banks (2026-09-02): a two-colour scene on a
    Toggle adds to the running state's colour instead of showing its own.
    The blue/red pair lives on the bank's keys 9/0 (restored 2026-08-28); a
    second button here would always look off. A rig whose banks hold no
    other mix (one beam, 2026-09-26) gets no frame: it would be empty.
    """
    if not any(library_splits):
        return
    mixes = frame(
        outer,
        vocabulary.display("mixes_frame"),
        LEFT_X,
        68,
        LEFT_WIDTH,
        230,
        page=PAGE_LIBRARY,
        pages=len(banks) or 1,
        font=TITLE_FONT,
    )
    for page, bank in enumerate(banks):
        label(
            mixes,
            vocabulary.render("group_label", group=bank.group_name),
            GAP,
            HEADER,
            512,
            20,
            page=page,
            font=HELP_FONT,
        )
        for index, function_id in enumerate(library_splits[page]):
            column, row = index % 10, index // 10
            name = names.get(function_id, "")
            on_page(
                button(
                    mixes,
                    function_id,
                    mix_caption(name, mix_code),
                    x=GAP + column * 51,
                    y=HEADER + 24 + row * 51,
                    w=48,
                    h=45,
                    action=FLASH,
                    flash_override=True,
                    flash_force_ltp=True,
                    background=swatch(name, palette),
                    foreground=swatch(name, palette, second=True),
                    font=TINY_FONT,
                ),
                page,
            )
