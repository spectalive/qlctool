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
# The beam's own edge. A 7R projects a gobo, and a projection nobody focuses is
# a smudge: the channel sits at DMX 0 - one end of its travel - for as long as
# nothing writes it, which is how this rig ran its seventeen gobos for years.
FOCUS = "focus"
# The beam's own width. A wash with a zoom channel and nobody writing it sits at
# whatever DMX 0 means on that model - and nobody knows until a chart says - so the
# looks that light it have to state it, the way they state the shutter.
ZOOM = "zoom"
SPEED = "speed"
# The fog pump of a machine that also carries lights. A plain smoke machine
# types its pump as a master dimmer and that is fine - it has no other
# intensity for the role to collide with. A vertical fog machine with LEDs has
# both: the pump and the light's master dimmer are different channels, and a
# generator that says "dimmer" must never reach the pump.
SMOKE = "smoke"

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
    if p.startswith("BeamZoom") and "Fine" not in p:
        return ZOOM
    if p.startswith("BeamFocus"):
        return FOCUS

    # Fallback: no usable preset, read the group and the human name.
    g = (group or "").lower()
    n = (name or "").lower()
    if g == "beam" and "zoom" in n:
        return ZOOM
    if g == "beam" and "focus" in n:
        return FOCUS
    if g == "gobo":
        return GOBO
    if g == "prism":
        return PRISM
    if g == "speed" and "prism" in n:
        return PRISM_ROTATION
    if g == "effect" and ("jitter" in n or "shake" in n):
        return GOBO_SHAKE
    if g == "effect" and ("fog" in n or "smoke" in n or "humo" in n):
        return SMOKE
    if g == "effect":
        return EFFECT
    if g == "speed":
        return SPEED
    if g == "colour" or ("macro" in n and "color" in n) or "colour" in n:
        return COLOR_MACRO
    if g == "shutter" or "strob" in n:
        return STROBE
    # A pump lives in the Intensity group so QLC+ resets it every cycle (see
    # the LED Spray Fog definition), and it is still a pump: a generator that
    # says "dimmer" must never reach it.
    if g == "intensity" and ("fog" in n or "smoke" in n or "humo" in n):
        return SMOKE
    if g == "intensity" and ("dimmer" in n or "master" in n):
        return DIMMER
    return None
