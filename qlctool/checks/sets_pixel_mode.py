"""The look writes the mode channel of a fixture's named internal programme."""

from collections.abc import Mapping

from ..fixture_capabilities import FixtureCapabilities
from .pixel_mode_offset import pixel_mode_offset


def sets_pixel_mode(capability: FixtureCapabilities, written: Mapping[int, int | None]) -> bool:
    mode = pixel_mode_offset(capability)
    return mode is not None and mode in written
