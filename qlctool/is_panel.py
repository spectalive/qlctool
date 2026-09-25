"""Whether a fixture is a panel: a flat fixture that runs a programme of its own."""

from . import roles
from .capability import FixtureCapabilities
from .has_panel_face import has_panel_face
from .internal_program import internal_program


def is_panel(capabilities: FixtureCapabilities) -> bool:
    """True for a fixture with an internal programme whose heads form one cell or a grid.

    Read from the definition, never the model: the programme is
    `internal_program` (a mode channel with "no function" and "auto" ranges and
    a channel listing the effects); the heads are the patched mode's `<Head>`
    blocks and the `<Layout>` must hold them all, either as one cell or as a
    grid more than one wide and more than one high - a line of heads is a bar.
    A fixture that pans or tilts is a moving head, and a smoke machine is left
    out as `generate_builtin_effects` leaves it out. Vibra's WX-60WPS panels
    declare one head, layout 1 x 1, and a Function / Effect Modes pair.

    One cell is also every PAR with a programme of its own, so a one-cell
    fixture must have a panel's body as well (`has_panel_face`): 26 one-cell
    modes of the upstream library, every PAR among them, were panels before
    (review of 4b50144, 2026-09-25).
    """
    if capabilities.is_smoke or internal_program(capabilities) is None:
        return False
    if capabilities.has_role(roles.PAN) or capabilities.has_role(roles.TILT):
        return False
    heads = max(1, len(capabilities.declared_heads))
    width, height = capabilities.layout
    if width * height != heads:
        return False
    if heads == 1:
        return has_panel_face(capabilities.dimensions)
    return min(width, height) > 1
