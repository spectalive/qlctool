"""The vertical smoke columns a patch has: the smoke machines that carry their own light.

One answer for the two generators that serve the column, so they cannot drift:
the held burst that fires and lights it (`vertical_smoke_burst`), and the
panels' companion light that plays while it fires (`vertical_smoke_light`).
A column is a smoke machine with a red channel (`is_lit_smoke`); a fog-only
machine is not one, however it is mounted.
"""

from collections.abc import Iterable

from .capability import FixtureCapabilities


def vertical_smoke_columns(
    capabilities: Iterable[FixtureCapabilities],
) -> list[FixtureCapabilities]:
    """The patched smoke machines with a red channel, in patch order."""
    return [c for c in capabilities if c.is_lit_smoke]
