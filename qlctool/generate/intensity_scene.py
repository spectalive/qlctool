"""One intensity scene: the rig's dimmers at one level, shutters open."""

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from ..fog_off_pairs import fog_off_pairs
from ..functions.build_scene import build_scene
from ..mode_park_pairs import mode_park_pairs
from ..next_function_id import next_function_id
from ..shutter_open_pairs import shutter_open_pairs
from ..stepped_dimmer_offsets import stepped_dimmer_offsets
from ..strobe_off_pairs import strobe_off_pairs
from ..wheel_blade_offsets import wheel_blade_offsets
from ..workspace import Workspace
from ..zoom_wide_pairs import zoom_wide_pairs

# The quiet level's dimmer is not this scene's business, only the full one's:
# a blade dimmer or a lit smoke machine's LED joins this level regardless of
# the level requested (see `generate_energy_intensity`).
FULL_LEVEL = 255


def intensity_scene(
    workspace: Workspace,
    capabilities: list[FixtureCapabilities],
    excluded: set[int],
    name: str,
    level: int,
    path: str,
    outside: set[int],
) -> int | None:
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in capabilities:
        if capability.fixture.fixture_id in excluded:
            continue
        # The pump is owned at zero by whatever is running, on every machine
        # including the fog-only ones: a Flash restores nothing on release, and
        # on a pump that is the tank (`fog_off_pairs`).
        if capability.is_smoke:
            off = fog_off_pairs(capability)
            if off:
                values[capability.fixture.fixture_id] = sorted(set(off))
        # Fog-only machines have no light to own; the lit ones' LED dimmer is
        # intensity like any other - the pump is a different role entirely.
        if capability.is_smoke and not capability.is_lit_smoke:
            continue
        # A blade dimmer has no fraction to give: between the ends it covers
        # part of the lens instead of dimming, and the quiet level held that
        # for four minutes (`stepped_dimmer_offsets`). It joins the level at full and
        # takes its darkness from the shutter, like the MiN Wash does.
        stepped = set(stepped_dimmer_offsets(capability))
        # A lit smoke machine's LED sits behind its own nozzle and does not
        # read below full: "si no pones el canal 2 a 255 no se ven" (owner,
        # 2026-08-29). The quiet level's 110 left four machines invisible.
        full = capability.is_lit_smoke
        # A wheel-coloured head's blade opens with its colour, not here: a
        # level holding it open left the beams lit in the last colour after a
        # released colour pick (`wheel_blade_offsets`, 2026-09-27). A head no
        # colour look reaches keeps it here, since nothing else would open it.
        with_colour: set[int] = set()
        if capability.fixture.fixture_id not in outside:
            with_colour = set(wheel_blade_offsets(capability))
        pairs = [
            (offset, FULL_LEVEL if full or offset in stepped else level)
            for offset in capability.offsets_for_role(roles.DIMMER)
            if offset not in with_colour
        ]
        pairs += shutter_open_pairs(capability)
        pairs += zoom_wide_pairs(capability)
        # A strobe-only channel is LTP and a released Flash restores nothing:
        # the intensity owner writes the strobe off.
        pairs += strobe_off_pairs(capability)
        pairs += fog_off_pairs(capability)
        # A head no colour look reaches is parked by nothing else: its
        # self-running channel is stated here, where it is lit (2026-09-25).
        if capability.fixture.fixture_id in outside:
            pairs += mode_park_pairs(capability)
        if pairs:
            values[capability.fixture.fixture_id] = sorted(set(pairs))
    if not values:
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id
