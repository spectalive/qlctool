"""Whether a fixture is a bar: a pixel fixture whose heads lie in a line."""

from . import roles
from .capability import FixtureCapabilities


def is_bar(capabilities: FixtureCapabilities) -> bool:
    """True for more than one head, each a pixel, laid out as one row or one column.

    Read from the definition, never the model: the patched mode's `<Head>`
    blocks (`declared_heads`), a red channel per pixel, and the `<Layout>` of
    the `<Physical>` block, which must be exactly one row or one column holding
    every declared head. Vibra's LED Bar 240/8 (8 heads, 8 x 1) and CLB2.4
    (4 heads, 4 x 1) are bars; the MAC Wash 1915Z's three rings declare no
    layout (1 x 1), so they are not a line, and a single-cell PAR is not either.
    """
    heads = len(capabilities.declared_heads)
    width, height = capabilities.layout
    return (
        heads > 1
        and len(capabilities.offsets_for_role(roles.RED)) > 1
        and min(width, height) == 1
        and width * height == heads
    )
