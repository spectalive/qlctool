"""The speed dial's multiplier controls, by the factor an OSC address names.

`<prefix>/<id>/x<f>` presses the dial's control for factor `f` of QLC+'s
`VCSpeedDial::SpeedMultiplier` (2 = 1/16x ... 6 = 1x ... 10 = 16x). Those
controls are the dial's input ids 6-9 (1/16x to 1/2x), 4 (reset to 1x) and
10-13 (2x to 16x) in qmlui/virtualconsole/vcspeeddial.h. Factor 0 and 1 have no
button: a dial's multiplier is set, not cleared. The same table is dmxdesk's
`core/qlc_osc_factor_input.c`, so the desk and the show agree on every address.
"""

OSC_DIAL_FACTOR_INPUTS = {2: 6, 3: 7, 4: 8, 5: 9, 6: 4, 7: 10, 8: 11, 9: 12, 10: 13}
