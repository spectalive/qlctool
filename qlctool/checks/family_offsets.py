"""The offsets of one fixture that belong to some of the console's families."""

from collections.abc import Collection

from ..capability import FixtureCapabilities
from .families import FAMILIES
from .pixel_mode_offset import pixel_mode_offset

PIXEL_MODE = "pixel-mode"


def family_offsets(capability: FixtureCapabilities, families: Collection[str]) -> frozenset[int]:
    """Offsets whose role is in one of `families`, plus a panel's mode channel for pixel-mode."""
    wanted = {role for family in families for role in FAMILIES.get(family, ())}
    found = {offset for offset, role in enumerate(capability.roles_by_offset) if role in wanted}
    mode = pixel_mode_offset(capability) if PIXEL_MODE in families else None
    if mode is not None:
        found.add(mode)
    return frozenset(found)
