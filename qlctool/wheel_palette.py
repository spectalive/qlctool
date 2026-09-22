"""The palette a rotation may step through by itself: everything but white.

"Las luces blancas en las ruedas de colores automáticas no: en teoría es un
color, pero en directo se ve todo iluminado y queda horrible. Luz blanca solo
para blanco total" (owner, 2026-09-22). White is in `PALETTE` because the
hand-built show drives it - for the work light, the flashes, a hand pick - but
a wheel that lands on it by Random rotation is the house lights coming up in
the middle of a song. So every automatic colour clock is built from this
subset, and `rule_wheel_white` sees any that is not.
"""

from .palette import PALETTE

WHITE = "Blanco"

WHEEL_PALETTE: dict[str, tuple[int, int, int]] = {
    name: rgb for name, rgb in PALETTE.items() if name != WHITE
}
