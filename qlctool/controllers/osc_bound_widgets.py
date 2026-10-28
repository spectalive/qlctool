"""The console widgets an OSC surface drives."""

# What dmxdesk's converter offers as a control: a button presses, a slider sets
# a level, a speed dial sets a time and a multiplier. Frames, cue lists and XY
# pads have no OSC control on the desk, so they get no address here either.
OSC_BOUND_WIDGETS = ("Button", "Slider", "SpeedDial")
