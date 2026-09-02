"""The static base a chase-driven level stands on: what the chase cannot own.

`Dimmer Chase` only takes fixtures whose dimmer is a fader - the same walk
`generate_dimmer_chases` makes to build its member list. A fixture with no
dimmer role, like the Chauvet MiN Wash, has no channel the chase could ever
touch: its light lives behind a shutter range instead (`shutter_open_pairs`).
A fixture whose dimmer is a mechanical blade, like the BEAM 230W 7R, is left
out on purpose (`stepped_dimmer`) and gets its one usable value, full, here. So a level that
hands its dimmer fixtures to the chase and drops its old flat intensity scene
would leave that fixture with no owner at all in that level - not shadowed,
just dark, the moment nothing keeps writing its shutter open.

The strobe-only channels are the same gap on a different channel: the levels
that run `Intensidad Ambiente`/`Total` write them off through those scenes,
but a chase level dropped both - so a flash released during the peak left the
Vortex and the panels strobing until the next level's intensity base cleared
it (the same LTP latch `rule_strobe_restore` was written for, one level down).

Shutters are opened on *every* fixture, dimmable or not: a shutter is not a
dimmer value, so opening it fights nothing the chase writes - and skipping it
on the dimmable ones is how `Momento Locura` coloured four beams whose shutter
nothing had opened, and left the washes' strobe channel with no owner for a
released flash to come home to (2026-08-29). Inside the energy cycle the
previous level's `Intensidad Total` happened to leave those channels right -
LTP - which is exactly the kind of luck a self-contained moment does not get.
"""

from collections.abc import Sequence

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


def generate_dimmerless_intensity(
    workspace: Workspace,
    capabilities: Sequence[FixtureCapabilities],
    exclude_fixture_ids: Sequence[int] = (),
    name: str = "Intensidad Peak",
) -> int | None:
    """The chase level's static base. None when no fixture needs one."""
    excluded = set(exclude_fixture_ids)
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in capabilities:
        if capability.fixture.fixture_id in excluded:
            continue
        if capability.is_smoke:
            # The pump, and only to hold it shut: this level runs under the
            # smoke flashes like every other, and a released flash needs
            # something writing zero to come home to (`fog_off`).
            off = fog_off_pairs(capability)
            if off:
                values[capability.fixture.fixture_id] = sorted(set(off))
            if not capability.is_lit_smoke:
                continue
        pairs: list[tuple[int, int]] = []
        if capability.is_lit_smoke:
            # A fog machine with LEDs is a floor PAR the chase never reaches:
            # nothing else lights it in a chase level, so this base does - or
            # the four columns went dark for every peak (cross-audit,
            # 2026-09-02; the montage note of 2026-08-29 wants them "subir y
            # bajar con los niveles").
            pairs += [(offset, 255) for offset in capability.offsets_for_role(roles.DIMMER)]
        # A blade dimmer is out of the chase (`stepped_dimmer`), so this level
        # is the only thing that can own it - at full, the one value it has.
        pairs += [(offset, 255) for offset in stepped_dimmer_offsets(capability)]
        pairs += shutter_open_pairs(capability)
        pairs += zoom_wide_pairs(capability)
        pairs += strobe_off_pairs(capability)
        if pairs:
            fixture_id = capability.fixture.fixture_id
            values[fixture_id] = sorted(set(pairs) | set(values.get(fixture_id, [])))
    if not values:
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=PATH))
    return function_id
