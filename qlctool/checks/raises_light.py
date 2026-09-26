"""Whether a scene opens a fixture's intensity path itself.

Shared by the flash rules: a dimmer written lit, or a labelled shutter written
into its open range, is a scene that raises light on the fixture. A held colour
bank, a gobo pick or the stage aim state a wheel, a position or an RGB triple
and leave every dimmer and shutter to the state beneath - they raise nothing.
"""

from collections.abc import Mapping

from .. import roles
from ..capability import FixtureCapabilities
from ..shutter_open import shutter_open_ranges
from .show_graph import lit


def raises_light(capability: FixtureCapabilities, written: Mapping[int, int | None]) -> bool:
    """Whether the scene opens this fixture's intensity path itself."""
    if any(lit(written[o]) for o in capability.offsets_for_role(roles.DIMMER) if o in written):
        return True
    for offset, opening in shutter_open_ranges(capability):
        value = written.get(offset)
        if value is not None and opening.minimum <= value <= opening.maximum:
            return True
    return False
