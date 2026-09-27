"""What one EFX writes: pan/tilt, dimmer or RGB, depending on the fixture's Mode."""

from lxml import etree

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from ..xmlutil import find_local, findall_local

# EFXFixture::Mode - what an EFX drives on a fixture that participates in it.
EFX_PAN_TILT, EFX_DIMMER, EFX_RGB = 0, 1, 2
EFX_ROLES: dict[int, tuple[str, ...]] = {
    EFX_PAN_TILT: (roles.PAN, roles.PAN_FINE, roles.TILT, roles.TILT_FINE),
    EFX_DIMMER: (roles.DIMMER, roles.DIMMER_FINE),
    EFX_RGB: (roles.RED, roles.GREEN, roles.BLUE),
}


def efx_driven(
    function: etree._Element, capabilities: dict[int, FixtureCapabilities]
) -> dict[int, dict[int, int | None]]:
    driven: dict[int, dict[int, int | None]] = {}
    for element in findall_local(function, "Fixture"):
        identifier = find_local(element, "ID")
        if identifier is None or identifier.text is None:
            continue
        fixture_id = int(identifier.text)
        capability = capabilities.get(fixture_id)
        if capability is None:
            continue
        mode = find_local(element, "Mode")
        wanted = EFX_ROLES.get(
            int(mode.text) if mode is not None and mode.text else EFX_PAN_TILT, ()
        )
        driven.setdefault(fixture_id, {}).update(
            {offset: None for role in wanted for offset in capability.offsets_for_role(role)}
        )
    return driven
