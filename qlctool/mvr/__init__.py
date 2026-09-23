"""The rig as an MVR package for a GDTF visualiser.

QLC+ keeps the rig in its own terms - `.qxf` definitions, a `<Monitor>` node of
near-corner positions in millimetres, y up and z towards the audience. A
visualiser built on GDTF and MVR (BlenderDMX, Capture) wants a fixture type per
definition with named attributes and geometry, and a scene of fixtures placed by
a matrix, z up and y upstage. Every unit in here does one step of that
translation; `write_mvr` runs them in order.
"""
