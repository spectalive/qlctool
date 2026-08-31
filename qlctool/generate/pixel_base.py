"""Open the intensity of the fixtures a matrix paints, because a matrix cannot.

An RGBMatrix writes red, green and blue onto each head of its group and nothing
else. On a bar that is all there is - the LED Bar 240/8 is twenty-four channels
of pure RGB - but a HYULIGHTS panel keeps a master dimmer on its first channel
and a shutter on its fifth, and a matrix never touches either. Something else
has to hold them open.

Until the rig-wide colour wheel was taken off these fixtures, it did: every one
of its steps drove `dimmer_full`, so the panels were lit by the wheel and
coloured by the matrix without anyone noticing the split. Excluding them from
the wheel - the fix for two colour sources on one fixture - removed the only
thing opening them, and they went dark except under a flat scene like
`Flash 100%`. Hence this: intensity for the pixel groups, and no colour at all.
"""

from collections.abc import Sequence

from .. import roles
from ..capability import FixtureCapabilities
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..internal_program import internal_program_off_pairs
from ..mode_park import mode_park_pairs
from ..shutter_open import shutter_open_pairs
from ..strobe_off import strobe_off_pairs
from ..workspace import Workspace
from ..zoom_wide import zoom_wide_pairs

NAME = "Pixeles ON"
PATH = "Show"


def generate_pixel_base(
    workspace: Workspace,
    capabilities: list[FixtureCapabilities],
    fixture_ids: Sequence[int],
    name: str = NAME,
    path: str = PATH,
) -> int | None:
    """A Scene opening dimmer and shutter on the matrix-lit fixtures.

    Only fixtures a matrix can really colour - the ones with RGB - and only
    those that have something to open: a bar with neither dimmer nor shutter
    needs nothing and is left out rather than written as an empty FixtureVal.
    Returns None when no fixture in the group needs opening.
    """
    wanted = set(fixture_ids)
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in capabilities:
        if capability.fixture.fixture_id not in wanted or capability.is_smoke:
            continue
        if not any(
            capability.has_role(role)
            for role in (roles.RED, roles.GREEN, roles.BLUE)
        ):
            continue
        pairs = [(o, 255) for o in capability.offsets_for_role(roles.DIMMER)]
        pairs += shutter_open_pairs(capability)
        # A strobe-only channel is LTP and a released Flash restores nothing:
        # the scene that owns the light writes the strobe off.
        pairs += strobe_off_pairs(capability)
        # A wash head in a matrix group is still a head: nothing else writes
        # its zoom, and an unwritten zoom is 0 - the narrowest beam it has.
        pairs += zoom_wide_pairs(capability)
        # And nothing else holds its mode channel either. This scene is what
        # lights a matrix-painted fixture, so it is the one that has to say
        # "listen to DMX" - otherwise the head is free to run its own programme
        # under a matrix that thinks it is painting it. That is what the two
        # MAC WASH did on the night of 2026-08-29, "cambios de colores muy
        # rapidos", and what put them in a group in the first place.
        pairs += internal_program_off_pairs(capability)
        # And the ones whose self-running channel has no names to match
        # on - the MAC WASH's blanket `Function Mode` is exactly that.
        pairs += mode_park_pairs(capability)
        if pairs:
            values[capability.fixture.fixture_id] = pairs

    if not values:
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id
