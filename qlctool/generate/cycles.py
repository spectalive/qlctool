"""Page 4's group wheels and cycles frame: each group's own colour wheel and its matrix cycle.

Moved verbatim out of `page_library` (2026-09-27 split). `button` and `frame`
are the console's own widget closures, so the widget ids come out in the
order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from ..names.template_affixes import template_affixes
from .after_marker import after_marker
from .console_layout import (
    GAP,
    HEADER,
    MIDDLE_WIDTH,
    MIDDLE_X,
    PAGE_LIBRARY,
    SMALL_FONT,
    TITLE_FONT,
)
from .generated_bank import GeneratedBank
from .generated_builtins import GeneratedBuiltins
from .generated_matrices import GeneratedMatrices


def cycles(
    outer: etree._Element,
    button: Callable[..., etree._Element],
    frame: Callable[..., etree._Element],
    names: Mapping[int, str],
    banks: Sequence[GeneratedBank],
    matrices: Sequence[GeneratedMatrices],
    builtins: GeneratedBuiltins,
    vocabulary: Names,
) -> None:
    """Each group's own colour wheel and its matrix cycle. Both start the looks
    sitting in the solo frames above, so both live in a plain frame.
    """
    cycles = frame(
        outer,
        vocabulary.display("group_wheels_frame"),
        MIDDLE_X,
        376,
        MIDDLE_WIDTH,
        190,
        page=PAGE_LIBRARY,
        font=TITLE_FONT,
    )
    # The wheel captions are rendered from the bank, not parsed from the
    # wheel's name (ruling B8).
    entries = [
        (b.wheel_id, vocabulary.render("group_colour_wheel_caption", group=b.group_name))
        for b in banks
        if b.wheel_id is not None
    ]
    entries += [
        (b.mix_wheel_id, vocabulary.render("group_mix_wheel_caption", group=b.group_name))
        for b in banks
        if b.mix_wheel_id is not None
    ]
    cycle_marker = template_affixes(vocabulary, "cycle")[0]
    entries += [
        (m.chaser_id, after_marker(names.get(m.chaser_id, ""), cycle_marker))
        for m in matrices
        if m.chaser_id is not None
    ]
    # The panels' own cycle belongs here and not among the effects it starts:
    # a chaser sharing a solo frame with its own steps dies as it begins.
    if builtins.chaser_id is not None:
        entries.append(
            (
                builtins.chaser_id,
                after_marker(names.get(builtins.chaser_id, ""), cycle_marker),
            )
        )
    for index, (function_id, caption) in enumerate(entries):
        column, row = index % 5, index // 5
        button(
            cycles,
            function_id,
            caption,
            x=GAP + column * 122,
            y=HEADER + row * 50,
            w=116,
            h=44,
            font=SMALL_FONT,
        )
