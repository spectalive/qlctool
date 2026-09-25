"""The two whole-rig rainbow EFX the hand-built console kept on its own keys.

`Arcoiris Simultáneo` and `Arcoiris Pasos` were relative Circle EFX in RGB
mode: instead of sweeping pan and tilt, the path modulates every RGB head's
colour, so the whole rig breathes through a rainbow - together on one, phased
around the room on the other. The generated show dropped them (old-vs-new
audit, 2026-08-28: all 32 new EFX were absolute pan/tilt); this rebuilds both
with the old geometry - Circle, widths 123/24 and 127/10, duration 13696 ms,
axes X(127, 2, 90) / Y(127, 3, 0) - over every RGB head in the patch.

The panels stay out the way they stay off the colour wheel: a self-animating
fixture ignores the red, green and blue an EFX writes while its programme
runs, and its colour already has an owner.
"""

from dataclasses import dataclass

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.efx import EFXAxis, EFXFixture, build_efx
from ..ids import next_function_id
from ..internal_program import internal_program
from ..library import FixtureLibrary
from ..names.default_names import default_names
from ..names.names import Names
from ..workspace import Workspace
from .movement_efx import spread_offsets

MODE_RGB = 2  # EFXFixture::Mode - PanTilt, Dimmer, RGB

# The hand-built EFX 25/26, verbatim: shared duration and axes, each variant's
# own width/height, named by catalogue identifier.
DURATION_MS = 13696
X_AXIS = EFXAxis(offset=127, frequency=2, phase=90)
Y_AXIS = EFXAxis(offset=127, frequency=3, phase=0)
SIMULTANEO = ("rainbow_together", 123, 24)
PASOS = ("rainbow_steps", 127, 10)


@dataclass(frozen=True)
class GeneratedRainbows:
    simultaneo_id: int | None = None
    pasos_id: int | None = None


def generate_rainbow_efx(
    workspace: Workspace,
    library: FixtureLibrary,
    path: str | None = None,
    names: Names | None = None,
) -> GeneratedRainbows:
    """Both rainbows over every RGB head; empty result when nothing has RGB.

    `names` is the show's vocabulary; `path` defaults to its rig-colours folder.
    """
    vocabulary = default_names() if names is None else names
    path = vocabulary.display("path_rig_colours") if path is None else path
    heads: list[tuple[int, int]] = []  # (fixture id, head index)
    for caps in capabilities_of(workspace.root, library):
        if caps.is_smoke or internal_program(caps) is not None:
            continue
        head_count = len(caps.offsets_for_role(roles.RED))
        heads += [(caps.fixture.fixture_id, head) for head in range(head_count)]
    if not heads:
        return GeneratedRainbows()

    def _rainbow(name: str, width: int, height: int, offsets) -> int:
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_efx(
                function_id,
                name,
                [
                    EFXFixture(
                        fixture_id=fixture_id,
                        head=head,
                        mode=MODE_RGB,
                        start_offset=offset,
                    )
                    for (fixture_id, head), offset in zip(heads, offsets)
                ],
                algorithm="Circle",
                x_axis=X_AXIS,
                y_axis=Y_AXIS,
                width=width,
                height=height,
                is_relative=1,
                duration=DURATION_MS,
                path=path,
            )
        )
        return function_id

    identifier, width, height = SIMULTANEO
    simultaneo_id = _rainbow(vocabulary.display(identifier), width, height, [0] * len(heads))
    identifier, width, height = PASOS
    offsets = spread_offsets(len(heads))
    pasos_id = _rainbow(vocabulary.display(identifier), width, height, offsets)
    return GeneratedRainbows(simultaneo_id=simultaneo_id, pasos_id=pasos_id)
