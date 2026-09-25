"""Whether a fixture's body is a panel's: a flat face clearly wider than it is tall."""

from .definition import Dimensions


def has_panel_face(dimensions: Dimensions | None) -> bool:
    """True for a `<Dimensions>` half again as wide as tall, and shallower than tall.

    A PAR is a can: its face is round, so its drawn width is never half again
    its height (the yoke makes it taller, not wider), and a PAR 64 is deeper
    than it is tall. Vibra's WX-60WPS panel is 250 wide, 130 high and 70 deep.
    Of the 32 upstream QLC+ library modes with one cell and a programme of their
    own (2026-09-25), this keeps two light bars (Eurolite KLS-180-6, beamZ
    PartyBar2) and leaves out every PAR, among them the LED PAR 64 AT3
    (274 x 268 x 433) and the SlimPAR T6 (84 x 226 x 181). A definition with no
    dimensions cannot tell a panel from a PAR, so it is not called a panel.
    """
    if dimensions is None:
        return False
    return dimensions.width >= 1.5 * dimensions.height and dimensions.depth < dimensions.height
