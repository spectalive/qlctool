"""Resolve a QLC+ channel's semantic role.

Roles are derived from the channel's QLC+ Preset first (precise), then its
Group and name as a fallback.
"""

from . import roles

# The words a pump channel's name carries. "haze" also reads "hazer": a hazer's
# pump is a pump (2026-09-25, review of `rotulo que promete lo que no hay`).
_PUMP_WORDS = ("fog", "smoke", "humo", "haze")

_INTENSITY_PRESETS = {
    "IntensityRed": roles.RED,
    "IntensityGreen": roles.GREEN,
    "IntensityBlue": roles.BLUE,
    "IntensityWhite": roles.WHITE,
    "IntensityAmber": roles.AMBER,
    "IntensityUV": roles.UV,
    "IntensityCyan": roles.CYAN,
    "IntensityMagenta": roles.MAGENTA,
    "IntensityYellow": roles.YELLOW,
    "IntensityDimmer": roles.DIMMER,
    "IntensityMasterDimmer": roles.DIMMER,
    "IntensityDimmerFine": roles.DIMMER_FINE,
    "IntensityMasterDimmerFine": roles.DIMMER_FINE,
}


def role_of(preset: str | None, group: str | None, name: str | None) -> str | None:
    """Resolve a channel's role, or None when it is not one the toolkit drives."""
    p = preset or ""

    if p in _INTENSITY_PRESETS:
        return _INTENSITY_PRESETS[p]
    if p.startswith("PositionPan"):
        return roles.PAN_FINE if "Fine" in p else roles.PAN
    if p.startswith("PositionTilt"):
        return roles.TILT_FINE if "Fine" in p else roles.TILT
    if p.startswith("ShutterStrobe") or p == "ShutterOpen":
        return roles.STROBE
    if p == "ColorMacro":
        return roles.COLOR_MACRO
    if p.startswith(("GoboMacro", "GoboWheel")):
        return roles.GOBO
    if p.startswith("PrismEffect"):
        return roles.PRISM
    if p.startswith("BeamZoom") and "Fine" not in p:
        return roles.ZOOM
    if p.startswith("BeamFocus"):
        return roles.FOCUS

    # Fallback: no usable preset, read the group and the human name.
    g = (group or "").lower()
    n = (name or "").lower()
    if g == "beam" and "zoom" in n:
        return roles.ZOOM
    if g == "beam" and "focus" in n:
        return roles.FOCUS
    if g == "gobo":
        return roles.GOBO
    if g == "prism":
        return roles.PRISM
    if g == "speed" and "prism" in n:
        return roles.PRISM_ROTATION
    if g == "effect" and ("jitter" in n or "shake" in n):
        return roles.GOBO_SHAKE
    if g == "effect" and any(word in n for word in _PUMP_WORDS):
        return roles.SMOKE
    if g == "effect":
        return roles.EFFECT
    if g == "speed":
        return roles.SPEED
    if g == "colour" or ("macro" in n and "color" in n) or "colour" in n:
        return roles.COLOR_MACRO
    if g == "shutter" or "strob" in n:
        return roles.STROBE
    # A pump lives in the Intensity group so QLC+ resets it every cycle (see
    # the LED Spray Fog definition), and it is still a pump: a generator that
    # says "dimmer" must never reach it.
    if g == "intensity" and any(word in n for word in _PUMP_WORDS):
        return roles.SMOKE
    if g == "intensity" and ("dimmer" in n or "master" in n):
        return roles.DIMMER
    return None
