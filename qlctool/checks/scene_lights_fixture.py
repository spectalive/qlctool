"""Whether a scene lights a fixture through dimmer, RGB or white above zero."""

from collections.abc import Mapping

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from .lit import lit

LIGHTING_ROLES = (roles.DIMMER, roles.RED, roles.GREEN, roles.BLUE, roles.WHITE)


def scene_lights_fixture(
    capability: FixtureCapabilities, written: Mapping[int, int | None]
) -> bool:
    for role in LIGHTING_ROLES:
        for offset in capability.offsets_for_role(role):
            if offset in written and lit(written[offset]):
                return True
    return False
