"""One colour across the whole rig at once, and the wheel that cycles it.

The per-group banks give each group its own Random wheel, and three Random
wheels running unattended never agree: the heads sit on magenta while the PARs
sit on green, which is not a look, it is three shows in one room. What the owner
asks for is the rig reading as *one* colour on most steps - white, amber, red
everywhere at the same time - with the two-colour contrast as the exception
rather than the rule.

So this builds the wheel that AUTO actually runs: a scene per colour over every
colour-capable fixture in the patch, plus a handful of heads-against-the-rest
contrasts for variety. Fixtures are picked by capability, not by group, which is
also why the two CLB2.4 grids - in no fixture group, and therefore in no colour
bank and no matrix - are lit by it at all, and why the four beams, whose colour
is a wheel rather than three channels, are put on the nearest position that
wheel carries instead of being left out.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from .. import roles
from ..capabilities_of import capabilities_of
from ..capability import FixtureCapabilities
from ..functions.chaser import build_chaser
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..palette import PALETTE, PRIMARY_COLORS
from ..workspace import Workspace
from .color_scene import color_scene_values
from .wheel_color_values import wheel_color_values

PATH = "Colores Rig"

# The moving heads against everything else. Two colours the room can tell apart
# at a glance, which a neighbouring pair of the palette cannot.
CONTRAST_PAIRS: tuple[tuple[str, str], ...] = (
    ("Rojo", "Azul"),
    ("Azul", "Ambar"),
    ("Magenta", "Cyan"),
    ("Amarillo", "UltraVioleta"),
    ("Blanco", "Rojo"),
)


@dataclass(frozen=True)
class GeneratedUnison:
    scene_ids: list[int] = field(default_factory=list)
    contrast_ids: list[int] = field(default_factory=list)
    wheel_id: int | None = None


def generate_unison_colors(
    workspace: Workspace,
    library: FixtureLibrary,
    colors: Sequence[str] = PRIMARY_COLORS,
    contrasts: Sequence[tuple[str, str]] = CONTRAST_PAIRS,
    hold: int = 2500,
    fade: int = 800,
    exclude_fixture_ids: Sequence[int] = (),
) -> GeneratedUnison:
    """Rig-wide colour scenes and one Random wheel over them.

    Slower than a per-group wheel on purpose: a whole-room colour change every
    1,5 s reads as flicker, where one group changing that often reads as motion.

    `exclude_fixture_ids` keeps the wheel off fixtures a matrix already paints.
    RGB channels mix HTP, so a fixture told red by this wheel and blue by a
    running matrix comes out magenta - and a third source makes it white. One
    fixture, one colour source; the pixel groups belong to their matrix. Their
    colour *wheels* are still set, because a matrix cannot reach one: that is
    what keeps the beams on the same colour as the rest of the rig.
    """
    caps = capabilities_of(workspace.root, library)
    excluded = set(exclude_fixture_ids)
    lit_ids = [
        c.fixture.fixture_id
        for c in caps
        if c.fixture.fixture_id not in excluded
    ]

    scene_ids: list[int] = []
    for name in colors:
        values = color_scene_values(caps, PALETTE[name], fixture_ids=lit_ids)
        values.update(wheel_color_values(caps, name))
        if not values:
            continue
        scene_ids.append(_scene(workspace, f"Rig {name}", values))

    head_ids = [
        c.fixture.fixture_id
        for c in caps
        if c.has_role(roles.PAN) and c.has_role(roles.TILT)
    ]
    rest_ids = [
        c.fixture.fixture_id
        for c in caps
        if c.fixture.fixture_id not in head_ids and c.fixture.fixture_id not in excluded
    ]

    contrast_ids: list[int] = []
    for heads_color, rest_color in contrasts:
        values = _contrast_values(
            caps, head_ids, rest_ids, heads_color, rest_color, excluded
        )
        if len(values) < 2:
            continue
        contrast_ids.append(
            _scene(
                workspace,
                f"Cabezas {heads_color} / Resto {rest_color}",
                values,
            )
        )

    steps = scene_ids + contrast_ids
    wheel_id: int | None = None
    if steps:
        wheel_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                wheel_id,
                "Rueda Colores",
                steps,
                fade_in=fade,
                hold=hold,
                fade_out=fade,
                run_order="Random",
                path=PATH,
            )
        )

    return GeneratedUnison(
        scene_ids=scene_ids, contrast_ids=contrast_ids, wheel_id=wheel_id
    )


def _contrast_values(
    caps: list[FixtureCapabilities],
    head_ids: Sequence[int],
    rest_ids: Sequence[int],
    heads_color: str,
    rest_color: str,
    excluded: set[int],
) -> dict[int, list[tuple[int, int]]]:
    """The movers on one colour, everything else on the other."""
    lit_heads = [fid for fid in head_ids if fid not in excluded]
    values = color_scene_values(caps, PALETTE[heads_color], fixture_ids=lit_heads)
    values.update(color_scene_values(caps, PALETTE[rest_color], fixture_ids=rest_ids))
    values.update(wheel_color_values(caps, heads_color, fixture_ids=head_ids))
    values.update(wheel_color_values(caps, rest_color, fixture_ids=rest_ids))
    return values


def _scene(workspace: Workspace, name: str, values) -> int:
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=PATH))
    return function_id
