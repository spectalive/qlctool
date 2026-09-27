"""Page 4's matrices frame: the recovered RGBMatrix algorithm families, one group per page.

Moved verbatim out of `page_library` (2026-09-27 split). `button` and `frame`
are the console's own widget closures, so the widget ids come out in the
order they always did.
"""

from collections.abc import Callable, Mapping, Sequence

from lxml import etree

from ..names.names import Names
from .after_marker import after_marker
from .before_marker import before_marker
from .console_layout import (
    GAP,
    HEADER,
    HELP_FONT,
    MATRIX_BUTTON_HEIGHT,
    MATRIX_COLUMNS,
    MATRIX_ROW_HEIGHT,
    MIDDLE_WIDTH,
    MIDDLE_X,
    PAGE_LIBRARY,
    SMALL_FONT,
    TITLE_FONT,
)
from .first_of import first_of
from .generated_matrices import GeneratedMatrices
from .matrices_frame_caption import matrices_frame_caption
from .on_page import on_page


def matrix_frame(
    outer: etree._Element,
    button: Callable[..., etree._Element],
    frame: Callable[..., etree._Element],
    label: Callable[..., etree._Element],
    names: Mapping[int, str],
    matrices: Sequence[GeneratedMatrices],
    has_bars: bool,
    has_panels: bool,
    vocabulary: Names,
) -> None:
    """No matrix to press (a rig of two panels, 2026-09-26): no frame, and no
    caption promising patterns on them.
    """
    if not any(generated.matrix_ids for generated in matrices):
        return
    matrix_frame = frame(
        outer,
        vocabulary.display(matrices_frame_caption(has_bars, has_panels)),
        MIDDLE_X,
        68,
        MIDDLE_WIDTH,
        300,
        page=PAGE_LIBRARY,
        solo=True,
        pages=len(matrices) or 1,
        font=TITLE_FONT,
    )
    for page, generated in enumerate(matrices):
        first = first_of(generated.matrix_ids)
        group = before_marker(names.get(first, "") if first is not None else "", " - ")
        label(
            matrix_frame,
            vocabulary.render("group_label", group=group),
            GAP,
            HEADER,
            400,
            20,
            page=page,
            font=HELP_FONT,
        )
        step = (MIDDLE_WIDTH - GAP * 2) // MATRIX_COLUMNS
        for index, function_id in enumerate(generated.matrix_ids):
            column, row = index % MATRIX_COLUMNS, index // MATRIX_COLUMNS
            on_page(
                button(
                    matrix_frame,
                    function_id,
                    after_marker(names.get(function_id, ""), " - "),
                    x=GAP + column * step,
                    y=HEADER + 24 + row * MATRIX_ROW_HEIGHT,
                    w=step - 6,
                    h=MATRIX_BUTTON_HEIGHT,
                    font=SMALL_FONT,
                ),
                page,
            )
