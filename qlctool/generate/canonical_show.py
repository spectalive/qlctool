"""Build the whole show: content, structure, and a console that runs itself.

The shows this rig plays are unattended - the laptop is left alone and has to
keep changing colour, movement and gobos on its own - so the target is not a
console full of buttons for an operator, it is one AUTO function that brings up
everything at once, with the manual buttons there for when somebody does sit
down. The shape is taken from the hand-built show: colour banks per group with
Random wheels, mixed two-colour looks, gobo and prism animations, movement, and
smoke on a timer.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from .. import roles
from ..beat_generator import set_beat_generator
from ..capabilities_of import capabilities_of
from ..fixture_group import fixture_groups
from ..functions.collection import build_collection
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..monitor_positions import house_right_fixture_ids
from ..palette import PALETTE
from ..skeleton import strip_to_skeleton
from ..stage_plot import load_stage_plot
from ..workspace import Workspace
from .beat_tempo import BeatTiming, apply_beat_tempo
from .color_banks import GeneratedBank, generate_color_banks
from .color_scene import color_scene_values
from .dimmer_chases import generate_dimmer_chases
from .energy_levels import EnergyLevel, generate_energy_levels
from .home_position import generate_home_position
from .live_console import generate_live_console
from .matrix_effects import GeneratedMatrices, generate_matrix_effects
from .moments import Moment, generate_moments
from .movement_efx import generate_movement_efx, moving_head_ids
from .smoke_auto import generate_smoke_auto
from .stage_layout import generate_stage_layout, unplaced_fixtures
from .stage_plot_layout import apply_stage_plot
from .strobe_effects import generate_strobe_effects
from .unison_colors import generate_unison_colors
from .wheel_scenes import generate_wheel_scenes

SHOW_PATH = "Show"
MATRIX_ALGORITHMS: tuple[str | None, ...] = ("Fill", "Even/Odd", "Strobe", "Waves", None)
MATRIX_COLORS = ("Rojo", "Verde", "Azul", "Ambar", "Magenta", "Blanco")

# Movement at the peak: the same shapes, twice round in the time of one.
FAST_MOVEMENT_DURATION = 3424

# The light somebody is lit by when they speak: white, warmed off daylight so a
# face does not read as a mortuary, and flat enough that nothing draws the eye.
CHARLA_WHITE = (255, 214, 170)

# How long the night spends at each level, in milliseconds. A wave rather than a
# ramp: the cycle comes down through the middle level instead of jumping from
# peak to quiet.
AMBIENT_HOLD = 4 * 60 * 1000
PARTY_HOLD = 8 * 60 * 1000
PEAK_HOLD = 2 * 60 * 1000

# Beat-locked timings, in beats, for `newshow --beats`. Two bars of colour, one
# bar of matrix, eight bars of one movement shape: the counts a chase is
# actually written in.
MATRIX_BEATS = BeatTiming(hold=4)
BEAT_TIMINGS: dict[str, BeatTiming] = {
    "Rueda Colores": BeatTiming(hold=8, fade=1),
    "Movimientos Cabezas": BeatTiming(hold=32),
    "Movimientos Rapidos": BeatTiming(hold=16),
    "Gobo Animacion": BeatTiming(hold=16),
    "Color Beam Animacion": BeatTiming(hold=16),
    "Prisma Animacion": BeatTiming(hold=32),
    "Dimmer Chase": BeatTiming(hold=4),
    "Dimmer PingPong": BeatTiming(hold=2),
}

# The console the owner works with: one key each. The night-running looks keep
# the letters the hand-built show had, so muscle memory carries over; the
# moments - the states somebody takes the room into by hand - are on F1-F4,
# which is a row of its own and cannot collide with a colour bank on 1-0.
KEYS = {
    # Page 1: the state the room is in, and the hits that ride on top of it.
    "AUTO": "Q",
    "Momento Charla": "F1",
    "Momento Tranquilo": "F2",
    "Momento Fiesta": "F3",
    "Momento Locura": "F4",
    "Blanco Total": "X",
    "Todo Negro": "º",
    "Flash 100%": "Space",
    "Flash 50%": "-",
    "Humo ON": "H",
    "Strobo Rapido": "F",
    "Strobo Medio": "T",
    "Color Beam Animacion": "C",
    # Page 2: the layers, for somebody standing at the laptop.
    "Rueda Colores": "W",
    "Rueda Mezcla": "E",
    "Movimientos Cabezas": "A",
    "Gobo Animacion": "G",
    "Prisma Animacion": "P",
    "Humo Auto": "J",
    # Live-only looks. The hand-built console has these on V/B/C/Z; C is
    # already Color Beam here, so they move rather than clash.
    "Dimmer Chase": "V",
    "Dimmer PingPong": "Z",
    "Strobo ON": "S",
    "Strobo OFF": "D",
}
# Held, not latched. The smoke burst is one of them on purpose: a pump on a
# Toggle button is how a tank ends up empty when somebody walks away from it.
FLASH_FUNCTIONS = ("Flash 100%", "Flash 50%", "Humo ON")


@dataclass(frozen=True)
class CanonicalShow:
    banks: list[GeneratedBank] = field(default_factory=list)
    matrix_ids: list[int] = field(default_factory=list)
    efx_ids: list[int] = field(default_factory=list)
    gobo_ids: list[int] = field(default_factory=list)
    prism_ids: list[int] = field(default_factory=list)
    master_ids: dict[str, int] = field(default_factory=dict)
    button_ids: list[int] = field(default_factory=list)
    function_count: int = 0
    stage_placed: int = 0


def build_canonical_show(
    workspace: Workspace,
    library: FixtureLibrary,
    algorithms: Sequence[str | None] = MATRIX_ALGORITHMS,
    matrix_colors: Sequence[str] = MATRIX_COLORS,
    with_layout: bool = True,
    plot_path: str | None = None,
    beats: bool = False,
) -> CanonicalShow:
    """Strip the workspace to its patch and generate a self-running show on it."""
    strip_to_skeleton(workspace)
    # The patch carries the rig, not where any of it stands: give the 2D and 3D
    # views a plot to draw, or they stack every fixture on one spot. A workspace
    # whose Monitor already places everything was positioned by hand in QLC+ -
    # leave it alone, a generated plot is a starting point, not an improvement
    # on a measured one.
    stage_placed = 0
    if plot_path:
        stage_placed = len(apply_stage_plot(
            workspace, load_stage_plot(plot_path, workspace.root)
        ).rigged)
    elif unplaced_fixtures(workspace):
        stage_placed = generate_stage_layout(workspace, library).placed
    caps = capabilities_of(workspace.root, library)
    master: dict[str, int] = {}

    # Base looks first, so they are the lowest function IDs and read first.
    # One white, not three. "Luces ON", "Todo Blanco" and "Flash 100%" were all
    # full white on the same fixtures, which is why nobody could say what the
    # difference was: there was none. What is left is a latched work light and a
    # held hit, and the names say which is which.
    master["Blanco Total"] = _flat_scene(
        workspace, caps, "Blanco Total", (255, 255, 255)
    )
    master["Todo Negro"] = _blackout(workspace, caps)
    master["Flash 100%"] = _flat_scene(
        workspace, caps, "Flash 100%", (255, 255, 255)
    )
    master["Flash 50%"] = _flat_scene(
        workspace, caps, "Flash 50%", (128, 128, 128)
    )

    banks = generate_color_banks(workspace, library)

    matrices: list[GeneratedMatrices] = []
    # AUTO runs a matrix cycle only where a group is really made of pixels. A
    # matrix paints its group's own colour, so a cycle over the heads and
    # another over the PARs is what put them on different colours all night -
    # and on a group of single-cell fixtures a matrix is a colour wheel with
    # extra steps anyway. The bars and panels keep theirs: they have something
    # to draw with.
    pixel_chasers: list[int] = []
    # Every fixture a running matrix paints. The rig-wide colour wheel is kept
    # off these: RGB mixes HTP, so a bar told red by the wheel and blue by its
    # matrix comes out magenta, and a third source makes it white. One fixture,
    # one colour source.
    matrix_lit_ids: set[int] = set()
    subset = {name: PALETTE[name] for name in matrix_colors}
    for group in fixture_groups(workspace.root):
        generated = generate_matrix_effects(
            workspace,
            group_id=group.group_id,
            algorithms=algorithms,
            palette=subset,
            path=f"Matrices {group.name}",
        )
        matrices.append(generated)
        if generated.chaser_id is not None and _is_pixel_group(caps, group.fixture_ids):
            pixel_chasers.append(generated.chaser_id)
            matrix_lit_ids |= set(group.fixture_ids)
    matrix_ids = [fid for m in matrices for fid in m.matrix_ids]

    # Symmetry comes from reversing one side: with every head going the same way
    # round the room sweeps in parallel, and with house right backwards the
    # pairs open and close together.
    mirrored = house_right_fixture_ids(workspace.root)
    movement = generate_movement_efx(
        workspace, library, path="Movimiento", chaser_hold=10000,
        chaser_run_order="Random", mirrored_ids=mirrored,
    )
    if movement.chaser_id is not None:
        master["Movimientos Cabezas"] = movement.chaser_id
    # The same shapes at twice the speed, for the peak. Movement is a level, not
    # a background: the quiet part of the night has the heads held still and the
    # loud part has them moving fast, and one EFX cannot be both - the speed
    # lives on the EFX, not on the chaser that steps it.
    fast_movement = generate_movement_efx(
        workspace, library, path="Movimiento Rapido", chaser_hold=6000,
        chaser_run_order="Random", duration=FAST_MOVEMENT_DURATION,
        chaser_name="Movimientos Rapidos", label_prefix="Movimiento Rapido",
        mirrored_ids=mirrored,
    )
    if fast_movement.chaser_id is not None:
        master["Movimientos Rapidos"] = fast_movement.chaser_id
    home_id = generate_home_position(workspace, library)

    gobos = generate_wheel_scenes(
        workspace, library, role=roles.GOBO, label="Gobo", path="Gobos"
    )
    if gobos.chaser_id is not None:
        master["Gobo Animacion"] = gobos.chaser_id
    # The beams' own colour wheel: restricted to the fixtures that have gobos,
    # so a MiN Wash's Color Macro channel is not driven with beam positions.
    beams = [
        c.fixture.fixture_id
        for c in capabilities_of(workspace.root, library)
        if c.has_role(roles.GOBO)
    ]
    beam_colors = generate_wheel_scenes(
        workspace, library, role=roles.COLOR_MACRO, label="Color Beam",
        fixture_ids=beams, hold=6000, path="Color Beam",
    )
    if beam_colors.chaser_id is not None:
        master["Color Beam Animacion"] = beam_colors.chaser_id

    prisms = generate_wheel_scenes(
        workspace, library, role=roles.PRISM, label="Prisma", run_order="Loop",
        hold=8000, path="Prisma",
    )
    if prisms.chaser_id is not None:
        master["Prisma Animacion"] = prisms.chaser_id

    smoke = generate_smoke_auto(workspace, library)
    master["Humo Auto"] = smoke.chaser_id
    # The burst on its own, for the console: a held button, never a latched one.
    master["Humo ON"] = smoke.on_id

    dimmers = generate_dimmer_chases(workspace, library)
    master["Dimmer Chase"] = dimmers.chase_id
    master["Dimmer PingPong"] = dimmers.pingpong_id

    # Strobes reuse the base looks rather than duplicating them, so the flash
    # chasers step the same "Flash 100%" and "Todo Negro" the console flashes.
    strobes = generate_strobe_effects(
        workspace, library,
        full_id=master["Flash 100%"], black_id=master["Todo Negro"],
    )
    master["Strobo Rapido"] = strobes.fast_id
    master["Strobo Medio"] = strobes.medium_id
    if strobes.on_id is not None:
        master["Strobo ON"] = strobes.on_id
        master["Strobo OFF"] = strobes.off_id

    # One wheel over the whole rig, not one per group: three Random wheels
    # never land on the same colour, and the heads and the PARs have to.
    unison = generate_unison_colors(
        workspace, library, exclude_fixture_ids=sorted(matrix_lit_ids)
    )
    if unison.wheel_id is not None:
        master["Rueda Colores"] = unison.wheel_id
    master["Rueda Mezcla"] = _collection(
        workspace, "Rueda Mezcla",
        [b.mix_wheel_id for b in banks if b.mix_wheel_id is not None],
    )
    # The night goes somewhere: the colour bed, the pixels and the haze run
    # underneath, and what sits on top is a level that changes every few
    # minutes. Everything a room reads as "peak" - fast movement, prism, the
    # dimmer chase - is held back for the level that is meant to be one.
    #
    # A level carries no colour at all. The matrix cycle moved out of them and
    # into AUTO, because a level that owns the bars' colour hands it back on
    # every step - and because two levels running at once (which the console
    # used to allow) then put two colour sources on one fixture.
    gobo_open_id = _first(gobos.scene_ids)
    energy = generate_energy_levels(
        workspace,
        levels=[
            EnergyLevel(
                "Nivel Ambiente",
                # Heads held still, and the beams on the open position of their
                # gobo wheel: the quiet level is where the pattern comes *out*,
                # and a wheel nothing drives keeps whatever it was left on.
                [fid for fid in (home_id, gobo_open_id) if fid is not None],
                AMBIENT_HOLD,
            ),
            EnergyLevel(
                "Nivel Fiesta",
                [master["Movimientos Cabezas"], master["Gobo Animacion"]],
                PARTY_HOLD,
            ),
            EnergyLevel(
                "Nivel Peak",
                [master.get("Movimientos Rapidos", master["Movimientos Cabezas"]),
                 master["Gobo Animacion"],
                 *( [master["Prisma Animacion"]] if "Prisma Animacion" in master else []),
                 master["Dimmer Chase"]],
                PEAK_HOLD,
            ),
        ],
        order=("Nivel Ambiente", "Nivel Fiesta", "Nivel Peak", "Nivel Fiesta"),
    )
    master.update(energy.level_ids)
    if energy.cycle_id is not None:
        master["Ciclo Energia"] = energy.cycle_id

    # The one thing to press: the colour bed, the pixels, the haze and the
    # energy cycle. Not the beams' colour wheel: it started after the colour
    # wheel and so won the beams' one colour channel, which is what kept them
    # off whatever the rest of the rig was doing. The rig-wide scenes set that
    # wheel themselves now, and `Color Beam Animacion` stays as a button for
    # somebody at the laptop.
    auto_members = [master["Rueda Colores"], master["Humo Auto"], *pixel_chasers]
    if "Ciclo Energia" in master:
        auto_members.append(master["Ciclo Energia"])
    else:
        auto_members += [master["Movimientos Cabezas"], master["Gobo Animacion"]]
    master["AUTO"] = _collection(workspace, "AUTO", auto_members)

    # The moments: a room state somebody takes over with, each one bringing its
    # own colour bed because the console stops AUTO the instant one starts.
    # These are what a night actually needs a person for - a speaker on stage,
    # a lull, the last track - and they are the reason the energy levels are no
    # longer buttons: pressing two of those at once is what put the room on
    # every colour at once.
    master["Luz Charla"] = _flat_scene(
        workspace, caps, "Luz Charla", CHARLA_WHITE
    )
    beam_white_id = _first(beam_colors.scene_ids)
    moments = generate_moments(workspace, [
        # Somebody is talking: steady warm light, heads parked, nothing moving,
        # no wheel and no matrix - the one state where change is the enemy.
        Moment("Momento Charla", [
            home_id, master["Luz Charla"], gobo_open_id, beam_white_id,
        ]),
        # A lull: the colour bed and the pixels keep breathing, the heads stay
        # where they are.
        Moment("Momento Tranquilo", [
            master["Rueda Colores"], *pixel_chasers, home_id, gobo_open_id,
        ]),
        Moment("Momento Fiesta", [
            master["Rueda Colores"], *pixel_chasers,
            master["Movimientos Cabezas"], master["Gobo Animacion"],
        ]),
        # Everything the rig has, minus the strobe: a strobe belongs to a hit
        # somebody presses and lets go of, not to a state left running.
        Moment("Momento Locura", [
            master["Rueda Colores"], *pixel_chasers,
            master.get("Movimientos Rapidos", master["Movimientos Cabezas"]),
            master["Gobo Animacion"],
            master.get("Prisma Animacion"),
            master["Dimmer Chase"],
        ]),
    ])
    master.update(moments)

    if beats:
        # The layers that should feel the music go on the beat; the energy cycle
        # stays on the clock, because it measures the night rather than the song
        # - and because a beat that never arrives would freeze it.
        set_beat_generator(workspace.root, "Audio")
        present = {f.attrib.get("Name") for f in workspace.engine}
        timings = {
            name: timing for name, timing in BEAT_TIMINGS.items() if name in present
        }
        timings.update({
            name: MATRIX_BEATS
            for name in present
            if name and name.startswith("Ciclo Matrices")
        })
        apply_beat_tempo(workspace, timings)

    button_ids: list[int] = []
    if with_layout:
        console = generate_live_console(
            workspace,
            master=master,
            banks=banks,
            matrices=matrices,
            movement=movement,
            gobos=gobos,
            beam_colors=beam_colors,
            prisms=prisms,
            mover_fixture_ids=moving_head_ids(workspace, library),
            keys=KEYS,
            flash_functions=FLASH_FUNCTIONS,
            matrix_algorithms=[a for a in algorithms if a],
        )
        button_ids = console.button_ids

    functions = [
        f for f in workspace.engine if f.tag.endswith("}Function")
    ]
    return CanonicalShow(
        banks=banks,
        matrix_ids=matrix_ids,
        efx_ids=movement.efx_ids,
        gobo_ids=gobos.scene_ids + beam_colors.scene_ids,
        prism_ids=prisms.scene_ids,
        master_ids=master,
        button_ids=button_ids,
        function_count=len(functions),
        stage_placed=stage_placed,
    )


def _first(ids) -> int | None:
    """The first of a generated list, or None when nothing was generated.

    A wheel's first position is its open one in every definition here, which is
    what the quiet level wants: no gobo rather than whatever was left in.
    """
    return ids[0] if ids else None


def _is_pixel_group(caps, fixture_ids) -> bool:
    """True when a member really has pixels: more than one red channel.

    An 8-segment bar has eight of them and a matrix can draw across it; a PAR
    or a wash head has one, and every algorithm on it collapses to a colour.
    """
    wanted = set(fixture_ids)
    return any(
        len(c.offsets_for_role(roles.RED)) > 1
        for c in caps
        if c.fixture.fixture_id in wanted
    )


def _flat_scene(workspace, caps, name, rgb) -> int:
    """One colour on every colour-capable fixture; smoke machines excluded."""
    values = color_scene_values(caps, rgb)
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_scene(function_id, name, values, path=SHOW_PATH)
    )
    return function_id


def _blackout(workspace, caps) -> int:
    """Everything to zero - except the smoke machine, which is never touched."""
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in caps:
        if capability.is_smoke:
            continue
        offsets = [
            offset
            for role in (roles.RED, roles.GREEN, roles.BLUE, roles.WHITE, roles.DIMMER)
            for offset in capability.offsets_for_role(role)
        ]
        if offsets:
            values[capability.fixture.fixture_id] = [(o, 0) for o in sorted(offsets)]
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_scene(function_id, "Todo Negro", values, path=SHOW_PATH)
    )
    return function_id


def _collection(workspace: Workspace, name: str, members: list[int]) -> int:
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_collection(function_id, name, members, path=SHOW_PATH)
    )
    return function_id
