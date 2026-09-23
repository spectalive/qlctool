"""An sRGB hex colour as the CIE xyY GDTF stores for a wheel slot.

QLC+ writes a wheel colour as `#rrggbb`; GDTF writes chromaticity `x,y` and
luminance `Y` on a 0-100 scale. The conversion is the standard one - sRGB
transfer curve to linear light, the D65 matrix to XYZ, then normalise - and a
black or unparseable value comes back as the D65 white point at zero
luminance rather than a division by zero.
"""

from pygdtf import ColorCIE

from .srgb_linear import srgb_linear

D65 = (0.3127, 0.3290)


def cie_from_hex(text: str) -> ColorCIE:
    """`#rrggbb` (or `rrggbb`) as CIE xyY, luminance in percent."""
    digits = text.strip().lstrip("#")
    if len(digits) != 6:
        return ColorCIE(D65[0], D65[1], 100.0)
    try:
        r, g, b = (int(digits[i : i + 2], 16) / 255 for i in (0, 2, 4))
    except ValueError:
        return ColorCIE(D65[0], D65[1], 100.0)

    rl, gl, bl = (srgb_linear(c) for c in (r, g, b))
    x = 0.4124 * rl + 0.3576 * gl + 0.1805 * bl
    y = 0.2126 * rl + 0.7152 * gl + 0.0722 * bl
    z = 0.0193 * rl + 0.1192 * gl + 0.9505 * bl
    total = x + y + z
    if total <= 0:
        return ColorCIE(D65[0], D65[1], 0.0)
    return ColorCIE(round(x / total, 6), round(y / total, 6), round(y * 100, 4))
