"""The whole palette, taken towards white: the third automatic colour mode.

"Colores pastel tenues" (owner, 2026-09-22). Same eighteen names and the same
hues as `PALETTE`, each blended towards white by `pastel`, so the wheel of the
pastel mode reads as the same show with the volume down rather than as a
different set of colours.
"""

from .palette import PALETTE
from .pastel import pastel

PASTEL_PALETTE: dict[str, tuple[int, int, int]] = {
    name: pastel(rgb) for name, rgb in PALETTE.items()
}
