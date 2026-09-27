"""Page 4's live matrix control: the first RGBMatrix, with its algorithm picker.

Moved verbatim out of `page_library` (2026-09-27 split). `ids` is the
console's own id counter, so the widget ids come out in the order they
always did.
"""

from collections.abc import Sequence

from lxml import etree

from ..names.names import Names
from ..vc.build_matrix_control import build_matrix_control
from .console_ids import ConsoleIds
from .console_layout import PAGE_LIBRARY, RIGHT_WIDTH, RIGHT_X
from .generated_console import GeneratedConsole
from .generated_matrices import GeneratedMatrices
from .on_page import on_page


def live_matrix(
    outer: etree._Element,
    ids: ConsoleIds,
    console: GeneratedConsole,
    matrices: Sequence[GeneratedMatrices],
    matrix_algorithms: Sequence[str],
    vocabulary: Names,
) -> None:
    """A rig with no RGBMatrix gets no live control for one."""
    if not (matrices and matrices[0].matrix_ids):
        return
    matrix_widget_id = ids.take()
    control = build_matrix_control(
        outer,
        matrix_widget_id,
        vocabulary.display("live_matrix"),
        RIGHT_X,
        68,
        RIGHT_WIDTH,
        200,
        function_id=matrices[0].matrix_ids[0],
        algorithms=list(matrix_algorithms),
    )
    on_page(control, PAGE_LIBRARY)
    console.widget_ids.append(matrix_widget_id)
