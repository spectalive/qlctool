"""An EFX modulating red, green and blue - a hue that travels by itself.

Matrices are deliberately out, on the same judgment `rule_wheel_colour`
makes: a matrix paints the *pixels* of a group and can say nothing about a
member that has none, so a two-colour Alternate over Cabezas is a claim
about eight RGB heads and not about the four beams beside them. An EFX in
RGB mode is the opposite - it names its fixtures one by one, and the ones
it leaves out it leaves out silently.
"""

from lxml import etree

from ..xmlutil import find_local, iter_local

# EFXFixture::Mode - PanTilt, Dimmer, RGB
EFX_RGB_MODE = "2"


def efx_animates_colour(function: etree._Element) -> bool:
    if function.attrib.get("Type") != "EFX":
        return False
    # An EFX names its members `<Fixture>`, not `<EFXFixture>` - the class name
    # is EFXFixture but the tag is not (`efxfixture.cpp::saveXML`).
    for fixture in iter_local(function, "Fixture"):
        mode = find_local(fixture, "Mode")
        if mode is not None and (mode.text or "").strip() == EFX_RGB_MODE:
            return True
    return False
