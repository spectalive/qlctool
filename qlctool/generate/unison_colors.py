"""One colour across the whole rig at once, and the wheel that cycles it.

The per-group banks give each group its own Random wheel, and three Random
wheels running unattended never agree: the heads sit on magenta while the PARs
sit on green, which is not a look, it is three shows in one room. What the owner
asks for is the rig reading as *one* colour on most steps - amber, red, blue
everywhere at the same time - with the two-colour contrast as the exception
rather than the rule, and white on none of them (`wheel_palette`).

So this builds the wheel that AUTO actually runs: a scene per colour over every
colour-capable fixture in the patch, plus a handful of heads-against-the-rest
contrasts for variety. Fixtures are picked by capability, not by group, which is
also why the two CLB2.4 grids - in no fixture group, and therefore in no colour
bank and no matrix - are lit by it at all, and why the four beams, whose colour
is a wheel rather than three channels, are put on the nearest position that
wheel carries instead of being left out.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from .. import roles
from ..capabilities_of import capabilities_of
from ..capability import FixtureCapabilities
from ..complementary_pairs import COMPLEMENTARY_PAIRS
from ..functions.chaser import build_chaser
from ..functions.collection import build_collection
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..names.default_names import default_names
from ..names.names import Names
from ..palette import PALETTE, PRIMARY_COLORS
from ..workspace import Workspace
from .color_scene import color_scene_values
from .wheel_color_values import wheel_color_values

# The wheel's pace. Slower than a per-group wheel on purpose: a whole-room
# colour change every 1,5 s reads as flicker, where one group changing that
# often reads as motion.
WHEEL_HOLD = 2500
WHEEL_FADE = 800

# The moving heads against everything else: (heads, rest). Two is the most a
# rotation may put on the room at once ("colores sutiles, como mucho 2 mezclas
# de colores", owner, 2026-09-22), and which two is the professionals' rule,
# not taste: complementary colours, placed between roles, the warm one leading
# (`complementary_pairs`). No white: it read as the room lit up, on the
# wheel's own clock (`rule_wheel_white`).
CONTRAST_PAIRS: tuple[tuple[str, str], ...] = tuple(
    (pair.lead, pair.bed) for pair in COMPLEMENTARY_PAIRS
)


@dataclass(frozen=True)
class GeneratedUnison:
    scene_ids: list[int] = field(default_factory=list)
    contrast_ids: list[int] = field(default_factory=list)
    wheel_id: int | None = None
    # What the wheel steps for each plain colour: the scene, or the Collection
    # that starts it beside the pixel groups' matrix of the same colour. These
    # are what a hand pick has to start, so the bars follow a picked colour the
    # way they follow a stepped one.
    solid_step_ids: list[int] = field(default_factory=list)


def generate_unison_colors(
    workspace: Workspace,
    library: FixtureLibrary,
    colors: Sequence[str] = PRIMARY_COLORS,
    contrasts: Sequence[tuple[str, str]] = CONTRAST_PAIRS,
    hold: int = WHEEL_HOLD,
    fade: int = WHEEL_FADE,
    exclude_fixture_ids: Sequence[int] = (),
    step_extras: Mapping[str, Sequence[int]] | None = None,
    program_gated_ids: Sequence[int] = (),
    palette: dict[str, tuple[int, int, int]] | None = None,
    wheel_name: str | None = None,
    scene_prefix: str = "Rig",
    names: Names | None = None,
) -> GeneratedUnison:
    """Rig-wide colour scenes and one Random wheel over them.

    `exclude_fixture_ids` keeps the wheel off fixtures a matrix already paints.
    RGB channels mix HTP, so a fixture told red by this wheel and blue by a
    running matrix comes out magenta - and a third source makes it white. One
    fixture, one colour source; the pixel groups belong to their matrix. Their
    colour *wheels* are still set, because a matrix cannot reach one: that is
    what keeps the beams on the same colour as the rest of the rig.

    `step_extras` is what keeps the *matrix-painted* fixtures on the wheel's
    colour: per colour name, extra functions - the pixel groups' matrices of
    that same colour - that the step starts beside the scene, wrapped together
    in a Collection. Two chasers rotating colour never land on the same one;
    one chaser starting both by the step is what "the bars follow the show"
    means in QLC+. A contrast step runs the *rest* colour's extras, because
    that is the colour everything that is not a moving head is on.

    `program_gated_ids` are the self-animating panels: every scene writes
    their RGB (with the rest, on the rest's colour) but never their mode
    channel - whether they are listening belongs to `Ciclo Paneles Mixto`,
    which flips them between their own programmes and manual. One colour
    clock, one mode owner.

    `palette` supplies the values behind the names, so a mode can mean the same
    seventeen colours with less of each: the pastel wheel passes the palette run
    through `pastel` and keeps the names, which is also what lets the beams'
    wheel match - a wheel has red, not pale red. `wheel_name` and
    `scene_prefix` keep the three modes' functions apart in one workspace.

    `names` is the show's vocabulary: the colour names are spelled in it, and
    the folder, the default wheel name and the step names come from it.
    """
    vocabulary = default_names() if names is None else names
    path = vocabulary.display("path_rig_colours")
    wheel_name = vocabulary.display("colour_wheel") if wheel_name is None else wheel_name
    caps = capabilities_of(workspace.root, library)
    values_of = PALETTE if palette is None else palette
    excluded = set(exclude_fixture_ids)
    lit_ids = [c.fixture.fixture_id for c in caps if c.fixture.fixture_id not in excluded]

    extras = step_extras or {}
    scene_ids: list[int] = []
    solid_steps: list[int] = []
    steps: list[int] = []
    for name in colors:
        # Colour only, never intensity: these scenes run all night under every
        # energy level, and a dimmer at 255 here is a dimmer no level can ever
        # bring down - HTP, the highest write wins (2026-08-27). The levels
        # own the dimmers and shutters now.
        values = color_scene_values(caps, values_of[name], fixture_ids=lit_ids, dimmer_full=False)
        values.update(
            color_scene_values(
                caps,
                values_of[name],
                fixture_ids=program_gated_ids,
                dimmer_full=False,
                internal_program_off=False,
            )
        )
        values.update(wheel_color_values(caps, name, dimmer=None, names=vocabulary))
        if not values:
            continue
        step_name = f"{scene_prefix} {name}"
        scene_id = _scene(workspace, step_name, values, path)
        scene_ids.append(scene_id)
        step_id = _step(workspace, step_name, scene_id, extras.get(name), path, vocabulary)
        solid_steps.append(step_id)
        steps.append(step_id)

    head_ids = [
        c.fixture.fixture_id for c in caps if c.has_role(roles.PAN) and c.has_role(roles.TILT)
    ]
    rest_ids = [
        c.fixture.fixture_id
        for c in caps
        if c.fixture.fixture_id not in head_ids and c.fixture.fixture_id not in excluded
    ]

    contrast_ids: list[int] = []
    for heads_color, rest_color in contrasts:
        values = _contrast_values(
            caps, head_ids, rest_ids, heads_color, rest_color, excluded, values_of, vocabulary
        )
        values.update(
            color_scene_values(
                caps,
                values_of[rest_color],
                fixture_ids=program_gated_ids,
                dimmer_full=False,
                internal_program_off=False,
            )
        )
        if len(values) < 2:
            continue
        name = vocabulary.render("contrast", heads=heads_color, rest=rest_color)
        scene_id = _scene(workspace, name, values, path)
        contrast_ids.append(scene_id)
        steps.append(_step(workspace, name, scene_id, extras.get(rest_color), path, vocabulary))

    wheel_id: int | None = None
    if steps:
        wheel_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                wheel_id,
                wheel_name,
                steps,
                fade_in=fade,
                hold=hold,
                fade_out=fade,
                run_order="Random",
                path=path,
            )
        )

    return GeneratedUnison(
        scene_ids=scene_ids,
        contrast_ids=contrast_ids,
        wheel_id=wheel_id,
        solid_step_ids=solid_steps,
    )


def _contrast_values(
    caps: list[FixtureCapabilities],
    head_ids: Sequence[int],
    rest_ids: Sequence[int],
    heads_color: str,
    rest_color: str,
    excluded: set[int],
    values_of: dict[str, tuple[int, int, int]],
    vocabulary: Names,
) -> dict[int, list[tuple[int, int]]]:
    """The movers on one colour, everything else on the other.

    Colour only, like the solid steps: intensity belongs to the levels.
    """
    lit_heads = [fid for fid in head_ids if fid not in excluded]
    values = color_scene_values(
        caps, values_of[heads_color], fixture_ids=lit_heads, dimmer_full=False
    )
    values.update(
        color_scene_values(caps, values_of[rest_color], fixture_ids=rest_ids, dimmer_full=False)
    )
    for color, fixture_ids in ((heads_color, head_ids), (rest_color, rest_ids)):
        values.update(
            wheel_color_values(caps, color, fixture_ids=fixture_ids, dimmer=None, names=vocabulary)
        )
    return values


def _scene(workspace: Workspace, name: str, values, path: str) -> int:
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id


def _step(
    workspace: Workspace,
    name: str,
    scene_id: int,
    extras: Sequence[int] | None,
    path: str,
    vocabulary: Names,
) -> int:
    """What the wheel actually steps: the scene, with its extras beside it."""
    if not extras:
        return scene_id
    function_id = next_function_id(workspace.root)
    step_name = vocabulary.render("with_pixels", name=name)
    workspace.add_function(build_collection(function_id, step_name, [scene_id, *extras], path=path))
    return function_id
