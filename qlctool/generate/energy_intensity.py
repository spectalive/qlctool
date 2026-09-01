"""The intensity base each energy level stands on - and nothing else owns.

Colour and intensity used to travel together: every colour scene drove every
dimmer to 255, which worked until the show wanted a quiet level. Intensity
mixes HTP - the highest write wins - so "Ambiente with the dimmers low" was
impossible while the colour wheel held them at full all night (Codex review,
2026-08-27). The split is the fix: colour scenes state colour, and each level
carries exactly one of these scenes as its intensity owner. A level change is
then really a brightness change, because nobody else is bidding.

Covered is everything with an intensity *path* the toolkit can open - a dimmer
channel, or a shutter whose open range the definition labels (the MiN Wash has
no dimmer role at all; its light lives behind the shutter channel). Excluded
are the fixtures somebody else owns: smoke, and the pixel groups whose
intensity is `Pixeles ON` - two owners at different values is the exact bug
this exists to end.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from .. import roles
from ..capability import FixtureCapabilities
from ..fog_off import fog_off_pairs
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..shutter_open import shutter_open_pairs
from ..stepped_dimmer import stepped_dimmer_offsets
from ..strobe_off import strobe_off_pairs
from ..workspace import Workspace
from ..zoom_wide import zoom_wide_pairs

PATH = "Niveles"
# The quiet level's dimmer: visibly down from full, nowhere near dark. A first
# guess for the venue, like the level holds themselves. It reaches every dimmer
# that is a fader; the ones that are a blade go to full instead.
AMBIENT_LEVEL = 110
FULL_LEVEL = 255


@dataclass(frozen=True)
class GeneratedIntensity:
    ambient_id: int | None
    full_id: int | None


def generate_energy_intensity(
    workspace: Workspace,
    capabilities: list[FixtureCapabilities],
    exclude_fixture_ids: Sequence[int] = (),
) -> GeneratedIntensity:
    """Two scenes: the rig's dimmers low, and at full - shutters open in both."""
    excluded = set(exclude_fixture_ids)
    ambient = _scene(workspace, capabilities, excluded, "Intensidad Ambiente", AMBIENT_LEVEL)
    full = _scene(workspace, capabilities, excluded, "Intensidad Total", FULL_LEVEL)
    return GeneratedIntensity(ambient_id=ambient, full_id=full)


def _scene(
    workspace: Workspace,
    capabilities: list[FixtureCapabilities],
    excluded: set[int],
    name: str,
    level: int,
) -> int | None:
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in capabilities:
        if capability.fixture.fixture_id in excluded:
            continue
        # The pump is owned at zero by whatever is running, on every machine
        # including the fog-only ones: a Flash restores nothing on release, and
        # on a pump that is the tank (`fog_off`).
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
        # for four minutes (`stepped_dimmer`). It joins the level at full and
        # takes its darkness from the shutter, like the MiN Wash does.
        stepped = set(stepped_dimmer_offsets(capability))
        # A lit smoke machine's LED sits behind its own nozzle and does not
        # read below full: "si no pones el canal 2 a 255 no se ven" (owner,
        # 2026-08-29). The quiet level's 110 left four machines invisible.
        full = capability.is_lit_smoke
        pairs = [
            (offset, FULL_LEVEL if full or offset in stepped else level)
            for offset in capability.offsets_for_role(roles.DIMMER)
        ]
        pairs += shutter_open_pairs(capability)
        pairs += zoom_wide_pairs(capability)
        # A strobe-only channel is LTP and a released Flash restores nothing:
        # the intensity owner writes the strobe off.
        pairs += strobe_off_pairs(capability)
        pairs += fog_off_pairs(capability)
        if pairs:
            values[capability.fixture.fixture_id] = sorted(set(pairs))
    if not values:
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=PATH))
    return function_id
