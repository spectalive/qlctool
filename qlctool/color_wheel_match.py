"""The wheel position that comes closest to a palette colour, on a fixture
whose colour is a wheel and not three channels.

The four BEAM 230W 7R have no RGB: their colour is a wheel of fifteen named
positions, so a scene that paints the rig red cannot reach them the way it
reaches a PAR. They stayed on whatever the beam colour animation last picked,
which is why the heads never matched the rest of the rig even when everything
else did.

The match is by the position's own name, read from the definition - never by
DMX value, which differs per fixture - and it is deliberately loose: a wheel has
White, Orange and Ice on it, not the palette's eighteen names. Where nothing on
the wheel is near the colour, this returns None and the wheel is left alone
rather than parked on a position that means something else.
"""

from . import roles
from .capability import FixtureCapabilities
from .names.default_names import default_names
from .names.names import Names

# Colour identifier -> wheel position names to try, best first. Names are the
# ones the real definitions use (BEAM 230W 7R and MiN Wash), lowercased on lookup.
WHEEL_NAMES: dict[str, tuple[str, ...]] = {
    "red": ("red", "crimson"),
    "fire_red": ("red", "crimson"),
    "orange": ("orange", "gold"),
    "amber": ("gold", "orange", "calid white"),
    "yellow": ("yellow", "light yellow"),
    "green": ("green",),
    "mint_green": ("green", "chartreuse"),
    "cyan": ("cyan", "ice", "light blue"),
    "light_blue": ("light blue", "ice", "cyan"),
    "sky_blue": ("light blue", "blue"),
    "blue": ("blue",),
    "deep_blue": ("blue",),
    "purple": ("purple", "violet", "uv"),
    "ultraviolet": ("uv", "violet", "purple"),
    "magenta": ("magenta", "pink"),
    "fuchsia": ("pink", "magenta"),
    "pink": ("pink", "light pink"),
    "white": ("white", "light white"),
}


def color_wheel_pairs(
    capabilities: FixtureCapabilities, color_name: str, names: Names | None = None
) -> list[tuple[int, int]]:
    """(offset, value) putting this fixture's colour wheel on that colour.

    `color_name` is a colour identifier or any spelling of one in `names` (the
    show's vocabulary, overrides included; every shipped catalogue by default).
    Empty when the fixture has RGB - three channels are a better way to say a
    colour than a wheel, and a macro channel on a wash overrides them - when it
    has no colour wheel, or when the wheel carries nothing near the colour.
    """
    if any(capabilities.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE)):
        return []
    wheel = capabilities.wheel_for_role(roles.COLOR_MACRO)
    if wheel is None:
        return []

    offset, positions = wheel
    by_name = {(position.name or "").strip().lower(): position for position in positions}
    vocabulary = default_names() if names is None else names
    matches = vocabulary.lookup(color_name, ("colors",))
    identifier = matches[0] if matches else color_name
    for wanted in WHEEL_NAMES.get(identifier, ()):
        position = by_name.get(wanted)
        if position is not None:
            return [(offset, position.middle)]
    return []
