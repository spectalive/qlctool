"""The vertical fog machines' column: the fog, and the light inside it.

These machines have DMX priority: with the controller plugged in, their own
timer, remote and colour program are dead, so a show that only drives the pump
gets a column nobody lit - the LED stays dark all night (found against the
scanned manual, 2026-08-29). One scene owns everything the column is: the fog,
the LED dimmer at full - "si no pones el canal 2 a 255 no se ven" (owner) - the
colour, and zeros on the strobe and auto-cycle channels so nothing latches.

The colour is **not** this scene's to state. It forced full white for exactly
one night and the owner watched the result: "salia humo bien pero la luz solo
salia la blanca, no hacia las transiciones de colores" (2026-08-30). Of course
it did - the scene is flashed with `Override`, which is the top fader priority
in QLC+ (`Universe::Flashing`), so its white beat the colour wheel every time
the button went down. The column is a floor PAR that happens to fog: the rig's
colour wheel owns its red, green and blue like everything else, and this scene
raises the pump and the LED master so whatever colour the room is in shows up
inside the fog.

Held on a Flash button, never latched: "pulso el canal de humo o humo vertical,
debe activar el humo (valor 255), al soltar la tecla debe volver a cero al
momento" (owner, 2026-08-29). That is exactly what a Flash does *provided the
pump channel is in the Intensity group* - QLC+ resets those every cycle and
leaves every other group holding its last value
(`Universe::processFaders` -> `zeroIntensityChannels`). It was not, and the
machine fogged until the workspace was reloaded; the definition says Intensity
now, and the release costs one DMX frame.
"""

from .. import roles
from ..capabilities_of import capabilities_of
from ..fog_offsets import fog_offsets
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace

NAME = "Humo Vertical YA"


def generate_vertical_smoke_burst(
    workspace: Workspace,
    library: FixtureLibrary,
    path: str = "Humo",
) -> int | None:
    """The held column scene, or None when the rig has no lit smoke machine.

    Pump and LED master only: the colour comes from whatever the room is
    running, which is the whole point of a lit column.
    """
    machines = [
        c for c in capabilities_of(workspace.root, library) if c.is_smoke and c.has_role(roles.RED)
    ]
    if not machines:
        return None
    values: dict[int, list[tuple[int, int]]] = {}
    for caps in machines:
        pairs = [(offset, 255) for offset in fog_offsets(caps)]
        pairs += [(offset, 255) for offset in caps.offsets_for_role(roles.DIMMER)]
        # Parked, explicitly: the strobe and the auto colour cycle are LTP and
        # keep whatever a stray value left on them.
        for role in (roles.STROBE, roles.EFFECT):
            pairs += [(offset, 0) for offset in caps.offsets_for_role(role)]
        values[caps.fixture.fixture_id] = sorted(pairs)
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, NAME, values, path=path))
    return function_id
