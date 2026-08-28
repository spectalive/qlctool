"""Map a QLC+ channel to a semantic role the generators reason about.

A role is what a channel *does* (red, dimmer, pan) independent of the fixture,
so a generator can say "set red to full" and the capability layer resolves it to
the right channel index on each fixture. Roles are derived from the channel's
QLC+ Preset first (precise), then its Group and name as a fallback.
"""

RED = "red"
GREEN = "green"
BLUE = "blue"
WHITE = "white"
AMBER = "amber"
UV = "uv"
CYAN = "cyan"
MAGENTA = "magenta"
YELLOW = "yellow"
DIMMER = "dimmer"
DIMMER_FINE = "dimmer_fine"
PAN = "pan"
PAN_FINE = "pan_fine"
TILT = "tilt"
TILT_FINE = "tilt_fine"
STROBE = "strobe"
COLOR_MACRO = "color_macro"
GOBO = "gobo"
PRISM = "prism"
# The prism's own spin and the gobo's shake: LTP channels that stay where the
# last look left them, so the scenes that own the wheel own these too. Their
# generic Speed/Effect groups would match unrelated channels, hence the
# dedicated roles.
PRISM_ROTATION = "prism_rotation"
GOBO_SHAKE = "gobo_shake"
EFFECT = "effect"
SPEED = "speed"

_INTENSITY_PRESETS = {
    "IntensityRed": RED,
    "IntensityGreen": GREEN,
    "IntensityBlue": BLUE,
    "IntensityWhite": WHITE,
    "IntensityAmber": AMBER,
    "IntensityUV": UV,
    "IntensityCyan": CYAN,
    "IntensityMagenta": MAGENTA,
    "IntensityYellow": YELLOW,
    "IntensityDimmer": DIMMER,
    "IntensityMasterDimmer": DIMMER,
    "IntensityDimmerFine": DIMMER_FINE,
    "IntensityMasterDimmerFine": DIMMER_FINE,
}


def role_of(preset: str | None, group: str | None, name: str | None) -> str | None:
    """Resolve a channel's role, or None when it is not one the toolkit drives."""
    p = preset or ""

    if p in _INTENSITY_PRESETS:
        return _INTENSITY_PRESETS[p]
    if p.startswith("PositionPan"):
        return PAN_FINE if "Fine" in p else PAN
    if p.startswith("PositionTilt"):
        return TILT_FINE if "Fine" in p else TILT
    if p.startswith("ShutterStrobe") or p == "ShutterOpen":
        return STROBE
    if p == "ColorMacro":
        return COLOR_MACRO
    if p.startswith(("GoboMacro", "GoboWheel")):
        return GOBO
    if p.startswith("PrismEffect"):
        return PRISM

    # Fallback: no usable preset, read the group and the human name.
    g = (group or "").lower()
    n = (name or "").lower()
    if g == "gobo":
        return GOBO
    if g == "prism":
        return PRISM
    if g == "speed" and "prism" in n:
        return PRISM_ROTATION
    if g == "effect" and ("jitter" in n or "shake" in n):
        return GOBO_SHAKE
    if g == "effect":
        return EFFECT
    if g == "speed":
        return SPEED
    if g == "colour" or "macro" in n and "color" in n or "colour" in n:
        return COLOR_MACRO
    if g == "shutter" or "strob" in n:
        return STROBE
    if g == "intensity" and ("dimmer" in n or "master" in n):
        return DIMMER
    return None
