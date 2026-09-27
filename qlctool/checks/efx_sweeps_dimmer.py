"""An EFX running any of its fixtures in Dimmer mode."""

from lxml import etree

from ..find_local import find_local
from ..iter_local import iter_local

EFX_DIMMER_MODE = "1"  # EFXFixture::Mode - PanTilt, Dimmer, RGB


def efx_sweeps_dimmer(function: etree._Element) -> bool:
    for fixture in iter_local(function, "Fixture"):
        mode = find_local(fixture, "Mode")
        if mode is not None and (mode.text or "").strip() == EFX_DIMMER_MODE:
            return True
    return False
