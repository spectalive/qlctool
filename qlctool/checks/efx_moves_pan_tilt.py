"""An EFX running any of its fixtures in PanTilt mode."""

from lxml import etree

from ..find_local import find_local
from ..iter_local import iter_local

# EFXFixture::Mode - PanTilt, Dimmer, RGB
EFX_PANTILT_MODE = "0"


def efx_moves_pan_tilt(function: etree._Element) -> bool:
    # An EFX names its members `<Fixture>`, not `<EFXFixture>` (efxfixture.cpp).
    for fixture in iter_local(function, "Fixture"):
        mode = find_local(fixture, "Mode")
        if mode is not None and (mode.text or "").strip() == EFX_PANTILT_MODE:
            return True
    return False
