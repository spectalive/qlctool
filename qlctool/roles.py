"""The semantic roles a QLC+ channel can play, and their fixed string values.

A role is what a channel *does* (red, dimmer, pan) independent of the fixture,
so a generator can say "set red to full" and the capability layer resolves it
to the right channel index on each fixture. `role_of` derives one from a
channel's preset, group and name.
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
