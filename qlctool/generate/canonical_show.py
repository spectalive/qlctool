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
from ..internal_program import internal_program, internal_program_off_pairs
from ..library import FixtureLibrary
from ..matrix_algorithms import CURATED_MATRICES
from ..monitor_positions import house_right_fixture_ids
from ..palette import PALETTE, PRIMARY_COLORS
from ..skeleton import strip_to_skeleton
from ..stage_plot import load_stage_plot
from ..strobe_speed import strobe_speed_pairs
from ..workspace import Workspace
from .beam_subsets import generate_beam_subsets
from .beat_tempo import BeatTiming, apply_beat_tempo
from .builtin_effects import generate_builtin_effects
from .color_banks import GeneratedBank, generate_color_banks
from .color_scene import color_scene_values
from .dimmer_chases import generate_dimmer_chases
from .dimmer_sequence import generate_dimmer_sequence
from .dimmerless_intensity import generate_dimmerless_intensity
from .energy_intensity import generate_energy_intensity
from .energy_levels import EnergyLevel, generate_energy_levels
from .flash_color import generate_flash_color
from .home_position import generate_home_position
from .live_console import generate_live_console
from .matrix_effects import GeneratedMatrices, generate_matrix_effects
from .moments import Moment, generate_moments
from .movement_efx import moving_head_ids
from .movement_families import generate_movement_families
from .pixel_base import generate_pixel_base
from .pixel_wheel_matrices import generate_pixel_wheel_matrices
from .smoke_auto import generate_smoke_auto
from .stage_aim import generate_stage_aim
from .stage_layout import generate_stage_layout, unplaced_fixtures
from .stage_plot_layout import apply_stage_plot
from .strobe_effects import generate_strobe_effects
from .unison_colors import CONTRAST_PAIRS, generate_unison_colors
from .vertical_smoke_light import generate_vertical_smoke_light
from .wheel_color_values import wheel_color_values
from .wheel_scenes import generate_wheel_scenes

SHOW_PATH = "Show"
MATRIX_ALGORITHMS: tuple[str | None, ...] = ("Fill", "Even/Odd", "Strobe", "Waves", None)
# What the unattended cycle steps. "Strobe" is generated but left out of it:
# it is a strobe, and this show's own rule is that a strobe is a button
# somebody holds, not one look in a rotation that loops all night. On the bars
# it was a third of the reason the pixels read as "off half the time".
CYCLE_ALGORITHMS: tuple[str | None, ...] = ("Fill", "Even/Odd", "Waves", None)
MATRIX_COLORS = ("Rojo", "Verde", "Azul", "Ambar", "Magenta", "Blanco")

# The light somebody is lit by when they speak: white, warmed off daylight so a
# face does not read as a mortuary, and flat enough that nothing draws the eye.
CHARLA_WHITE = (255, 214, 170)

# How long the night spends at each level, in milliseconds. A wave rather than a
# ramp: the cycle comes down through the middle level instead of jumping from
# peak to quiet. Peak is a burst, not a block - two continuous minutes of fast
# movement and prism stopped reading as a peak at all (Codex review,
# 2026-08-27: 20-45 s); the wave passes through it twice per cycle anyway.
AMBIENT_HOLD = 4 * 60 * 1000
PARTY_HOLD = 8 * 60 * 1000
PEAK_HOLD = 40 * 1000

# Beat-locked timings, in beats, for `newshow --beats`. Two bars of colour, one
# bar of matrix, eight bars of one movement shape: the counts a chase is
# actually written in.
MATRIX_BEATS = BeatTiming(hold=4)
BEAT_TIMINGS: dict[str, BeatTiming] = {
    "Rueda Colores": BeatTiming(hold=8, fade=1),
    "Movimientos Suaves": BeatTiming(hold=64),
    "Movimientos Washes": BeatTiming(hold=32),
    "Movimientos Beams": BeatTiming(hold=32),
    "Rapidos Washes": BeatTiming(hold=16),
    "Rapidos Beams": BeatTiming(hold=16),
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
    "Flash Color": ".",
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
    "Humo Vertical": "N",
    # Live-only looks. The hand-built console has these on V/B/C/Z; C is
    # already Color Beam here, so the sequence moves rather than clashes.
    "Dimmer Chase": "V",
    "Dimmer Chase 2": "B",
    "Dimmer Secuencia": "M",
    "Dimmer PingPong": "Z",
    "Strobo ON": "S",
    "Strobo OFF": "D",
}
# Held, not latched. The smoke burst is one of them on purpose: a pump on a
# Toggle button is how a tank ends up empty when somebody walks away from it.
FLASH_FUNCTIONS = (
    "Flash 100%", "Flash 50%", "Flash Color", "Humo ON", "Golpe Graves",
)

# Where the held flashes sit on every shutter's slow-to-fast run. The hand-built
# show's `Flash 100%` strobed the rig near the top of each channel (CromoWash
# 240 of 10-255, Vortex 250, panels 255) and its `Flash 50%` was the *same*
# full white at roughly half the strobe speed (Vortex 220, panels 140, beams
# 120) - not half the brightness. Space without the strobe is the regression
# the owner caught at home on 2026-08-27: "esto no hace estrobo y antes lo
# hacia".
FLASH_STROBE_FAST = 0.85
FLASH_STROBE_SLOW = 0.45


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
    # `wheel_color` is what lights the beams: they have no RGB, so a colour
    # scene alone skipped them entirely and "everything white" left the four
    # 7R dark - not dimmed, never written to.
    master["Blanco Total"] = _flat_scene(
        workspace, caps, "Blanco Total", (255, 255, 255), wheel_color="Blanco"
    )
    master["Todo Negro"] = _blackout(workspace, caps)
    # The flashes are the work light *strobing*: full white plus every shutter
    # driven, fast on Space and at half speed on `-` - which is what "50%"
    # meant on the hand-built console, not half the brightness.
    master["Flash 100%"] = _flat_scene(
        workspace, caps, "Flash 100%", (255, 255, 255), wheel_color="Blanco",
        strobe=FLASH_STROBE_FAST,
    )
    master["Flash 50%"] = _flat_scene(
        workspace, caps, "Flash 50%", (255, 255, 255), wheel_color="Blanco",
        strobe=FLASH_STROBE_SLOW,
    )
    # And the third flash the old console had on `.`: the strobe over whatever
    # colour is already running - dimmer and shutter only, RGB untouched.
    master["Flash Color"] = generate_flash_color(
        workspace, caps, fraction=FLASH_STROBE_FAST
    )
    # The bass bar's hit. It was `Flash 100%` - but that scene now strobes,
    # and a strobe fired by whatever the PA does is a strobe nobody chose. So
    # the bass keeps its own plain white: same look, shutters open, no strobe.
    master["Golpe Graves"] = _flat_scene(
        workspace, caps, "Golpe Graves", (255, 255, 255), wheel_color="Blanco"
    )

    banks = generate_color_banks(workspace, library)

    # The panels' own forty-two programmes. Nobody has watched them yet, so
    # every one is generated and the cycle is slow enough to see them.
    builtins = generate_builtin_effects(workspace, caps, label="Paneles")
    if builtins.chaser_id is not None:
        master["Efectos Paneles"] = builtins.chaser_id
    # The vertical smoke's companion light: the panels on the two colour
    # cycles the hand-built show held up while the column fired.
    vertical_id = generate_vertical_smoke_light(workspace, builtins.scene_ids)
    if vertical_id is not None:
        master["Humo Vertical"] = vertical_id

    matrices: list[GeneratedMatrices] = []
    # Matrices are drawn only where a group is really made of pixels: on a
    # group of single-cell fixtures a matrix is a colour wheel with extra
    # steps. The pixel groups' colour, though, belongs to the rig-wide wheel -
    # their matrices ride inside its steps, one per wheel colour, because two
    # chasers each rotating colour on their own clock never agree: the wheel
    # had the room on cyan while the bars' cycle had them on magenta ("van con
    # los colores a su bola", owner, 2026-08-26). The standalone cycle is still
    # generated for the console; AUTO does not step it.
    pixel_group_ids: list[int] = []
    # Every fixture a running matrix paints. The rig-wide colour wheel is kept
    # off these: RGB mixes HTP, so a bar told red by the wheel and blue by its
    # matrix comes out magenta, and a third source makes it white. One fixture,
    # one colour source.
    matrix_lit_ids: set[int] = set()
    subset = {name: PALETTE[name] for name in matrix_colors}
    for group in fixture_groups(workspace.root):
        # A fixture with forty-two animations of its own does not need a
        # four-cell chase drawn over it, and could not show one anyway: in its
        # automatic mode it ignores the red, green and blue a matrix writes.
        if _all_self_animating(caps, group.fixture_ids):
            continue
        generated = generate_matrix_effects(
            workspace,
            group_id=group.group_id,
            algorithms=algorithms,
            chaser_algorithms=CYCLE_ALGORITHMS,
            palette=subset,
            path=f"Matrices {group.name}",
            curated=[c for c in CURATED_MATRICES if c.group_name == group.name],
        )
        matrices.append(generated)
        if generated.chaser_id is not None and _is_pixel_group(caps, group.fixture_ids):
            pixel_group_ids.append(group.group_id)
            matrix_lit_ids |= set(group.fixture_ids)
    matrix_ids = [fid for m in matrices for fid in m.matrix_ids]

    # A matrix writes RGB and nothing else, so the panels' master dimmer and
    # shutter need somebody. That used to be the rig-wide wheel, until these
    # fixtures were taken off it; without this they are coloured and dark.
    pixel_base_id = generate_pixel_base(workspace, caps, sorted(matrix_lit_ids))
    if pixel_base_id is not None:
        master["Pixeles ON"] = pixel_base_id
    # Everything the pixel groups need beside the wheel: their intensity, and
    # the panels' own programmes. Their colour is not here - the wheel's steps
    # carry it, matrix included. Wherever the wheel goes, this goes.
    pixel_layer = [
        fid for fid in (pixel_base_id, builtins.chaser_id) if fid is not None
    ]

    # The wheel colours the pixel groups too, but through a matrix of its own
    # colour started by each step - never through the scene, whose RGB would
    # mix HTP with the matrix and land on a colour nobody chose.
    step_matrices = generate_pixel_wheel_matrices(
        workspace,
        pixel_group_ids,
        _wheel_colors(),
        CYCLE_ALGORITHMS,
    ) if pixel_group_ids else {}

    # Symmetry comes from reversing one side: with every head going the same way
    # round the room sweeps in parallel, and with house right backwards the
    # pairs open and close together. Movement is generated per optics family -
    # washes wide and slow, beams narrow and shorter - because one geometry
    # over both tuned the show for neither (Codex review, 2026-08-27).
    mirrored = house_right_fixture_ids(workspace.root)
    movement = generate_movement_families(
        workspace, library, mirrored_ids=mirrored
    )
    if movement.cabezas_id is not None:
        master["Movimientos Cabezas"] = movement.cabezas_id
    if movement.rapidos_id is not None:
        master["Movimientos Rapidos"] = movement.rapidos_id
    home_id = generate_home_position(workspace, library)
    if home_id is not None:
        # On the console beside the movement shapes: stillness is a look too.
        master["Cabezas Centro"] = home_id
    # The hand-built show's stage look, aimed by eye on the real rig and
    # carried as measured data: heads on the stage, colour left to the state.
    stage_aim_id = generate_stage_aim(workspace, library)
    if stage_aim_id is not None:
        master["Escenario"] = stage_aim_id

    # Wheel scenes state the wheel and nothing else: their dimmer used to ride
    # along at 255, which a quiet level could never bring down (HTP). The
    # levels own intensity now - see `energy_intensity`.
    gobos = generate_wheel_scenes(
        workspace, library, role=roles.GOBO, label="Gobo", path="Gobos",
        dimmer_full=False,
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
        fixture_ids=beams, hold=6000, path="Color Beam", dimmer_full=False,
    )
    if beam_colors.chaser_id is not None:
        master["Color Beam Animacion"] = beam_colors.chaser_id

    prisms = generate_wheel_scenes(
        workspace, library, role=roles.PRISM, label="Prisma", run_order="Loop",
        hold=8000, path="Prisma", dimmer_full=False,
    )
    beam_subsets = generate_beam_subsets(workspace, library)
    if prisms.chaser_id is not None:
        master["Prisma Animacion"] = prisms.chaser_id

    smoke = generate_smoke_auto(workspace, library)
    master["Humo Auto"] = smoke.chaser_id
    # The burst on its own, for the console: a held button, never a latched one.
    master["Humo ON"] = smoke.on_id

    dimmers = generate_dimmer_chases(workspace, library)
    master["Dimmer Chase"] = dimmers.chase_id
    master["Dimmer Chase 2"] = dimmers.chase2_id
    master["Dimmer PingPong"] = dimmers.pingpong_id

    # The burst chasers step the *plain* white and black - not "Flash 100%",
    # which now carries the hardware strobe: a chaser latching that scene for
    # 125 ms a step would stack a ~17 Hz shutter strobe on top of its own
    # 4 Hz chop.
    strobes = generate_strobe_effects(
        workspace, library,
        full_id=master["Blanco Total"], black_id=master["Todo Negro"],
    )
    master["Strobo Rapido"] = strobes.fast_id
    master["Strobo Medio"] = strobes.medium_id
    if strobes.on_id is not None:
        master["Strobo ON"] = strobes.on_id
        master["Strobo OFF"] = strobes.off_id

    # One wheel over the whole rig, not one per group: three Random wheels
    # never land on the same colour, and the heads and the PARs have to.
    # Off the rig-wide wheel go the fixtures somebody else is colouring: the
    # pixel groups their matrix paints, and the panels running their own
    # programmes, which ignore red, green and blue while they do.
    unison = generate_unison_colors(
        workspace, library,
        exclude_fixture_ids=sorted(matrix_lit_ids | set(builtins.fixture_ids)),
        step_extras=step_matrices,
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
    # Each level carries its own intensity base, and nobody else bids on those
    # dimmers: with the colour scenes stripped of theirs, "Ambiente" really is
    # dimmer than "Fiesta" for the first time. The pixel groups stay out -
    # `Pixeles ON` owns them.
    intensity = generate_energy_intensity(
        workspace, caps,
        exclude_fixture_ids=sorted(matrix_lit_ids | set(builtins.fixture_ids)),
    )
    if intensity.ambient_id is not None:
        master["Intensidad Ambiente"] = intensity.ambient_id
    if intensity.full_id is not None:
        master["Intensidad Total"] = intensity.full_id
        master["Dimmer Secuencia"] = generate_dimmer_sequence(
            workspace,
            breath_id=intensity.full_id,
            program_ids=[
                dimmers.chase_id, dimmers.pingpong_id, dimmers.chase2_id,
            ],
        )
    # Peak hands its dimmers to the chase instead: `Intensidad Total` beside it
    # would hold every one of them at 255, and HTP means the chase's dips could
    # never win - cosmetic forever (TODO.md, 2026-08-27). The fixtures the chase
    # cannot reach - no dimmer role, like the MiN Wash - still need an owner or
    # they go dark the moment the level's old flat scene leaves; this is theirs.
    peak_static = generate_dimmerless_intensity(
        workspace, caps,
        exclude_fixture_ids=sorted(matrix_lit_ids | set(builtins.fixture_ids)),
    )
    if peak_static is not None:
        master["Intensidad Peak"] = peak_static
    energy = generate_energy_levels(
        workspace,
        levels=[
            EnergyLevel(
                "Nivel Ambiente",
                # Alive from the first second - "el auto es eso, como el modo
                # auto de las cabezas en si" (owner, 2026-08-27). The washes
                # breathe through wide slow shapes, the beams hold their fan,
                # and the room sits at the low intensity base. The gobo wheel
                # is parked open: the quiet level is where the pattern comes
                # *out*, and a wheel nothing drives keeps what it was left on.
                [fid for fid in (
                    movement.slow_id, movement.fan_id, gobo_open_id,
                    intensity.ambient_id,
                ) if fid is not None],
                AMBIENT_HOLD,
            ),
            EnergyLevel(
                "Nivel Fiesta",
                [fid for fid in (
                    movement.wash_id, movement.beam_id,
                    master["Gobo Animacion"], intensity.full_id,
                ) if fid is not None],
                PARTY_HOLD,
            ),
            EnergyLevel(
                "Nivel Peak",
                [fid for fid in (
                    movement.fast_wash_id, movement.fast_beam_id,
                    master["Gobo Animacion"],
                    master.get("Prisma Animacion"),
                    master["Dimmer Chase"], peak_static,
                ) if fid is not None],
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
    auto_members = [master["Rueda Colores"], master["Humo Auto"], *pixel_layer]
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
    # Every moment brings its own intensity base beside its colour, because
    # the colour scenes no longer open anything on their own.
    moments = generate_moments(workspace, [
        # Somebody is talking: steady warm light, heads parked, nothing moving,
        # no wheel and no matrix - the one state where change is the enemy.
        Moment("Momento Charla", [
            home_id, master["Luz Charla"], gobo_open_id, beam_white_id,
            intensity.full_id,
        ]),
        # A lull: the colour bed and the pixels keep breathing at the low
        # intensity base, the heads stay where they are.
        Moment("Momento Tranquilo", [
            master["Rueda Colores"], *pixel_layer, home_id, gobo_open_id,
            intensity.ambient_id,
        ]),
        Moment("Momento Fiesta", [
            master["Rueda Colores"], *pixel_layer,
            master["Movimientos Cabezas"], master["Gobo Animacion"],
            intensity.full_id,
        ]),
        # Everything the rig has, minus the strobe: a strobe belongs to a hit
        # somebody presses and lets go of, not to a state left running.
        Moment("Momento Locura", [
            master["Rueda Colores"], *pixel_layer,
            master.get("Movimientos Rapidos", master["Movimientos Cabezas"]),
            master["Gobo Animacion"],
            master.get("Prisma Animacion"),
            master["Dimmer Chase"],
            intensity.full_id,
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
            builtins=builtins,
            keys=KEYS,
            flash_functions=FLASH_FUNCTIONS,
            matrix_algorithms=[a for a in algorithms if a],
            beam_subsets=beam_subsets,
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
        prism_ids=prisms.scene_ids + beam_subsets.prism_scene_ids,
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


def _wheel_colors() -> dict[str, tuple[int, int, int]]:
    """Every colour a wheel step can put the room on, in wheel order.

    The solid steps use the primary palette; a contrast step puts everything
    that is not a moving head - the pixel groups included - on its *rest*
    colour, so those are wheel colours too even when the primaries skip them.
    """
    names = list(PRIMARY_COLORS)
    names += [rest for _, rest in CONTRAST_PAIRS if rest not in names]
    return {name: PALETTE[name] for name in names}


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


def _flat_scene(
    workspace, caps, name, rgb, wheel_color: str | None = None,
    wheel_dimmer: int = 255, strobe: float | None = None,
) -> int:
    """One colour on every colour-capable fixture; smoke machines excluded.

    `wheel_color` names the palette colour to put the wheel-coloured fixtures
    on - the beams, which have no RGB and are otherwise skipped. `strobe`
    additionally drives every strobe channel at that point of its slow-to-fast
    run, overriding the open-shutter values a plain look carries - which is
    what turns the work light into a flash.
    """
    values = color_scene_values(caps, rgb)
    if wheel_color is not None:
        values.update(
            wheel_color_values(caps, wheel_color, dimmer=wheel_dimmer)
        )
    if strobe is not None:
        for capability in caps:
            if capability.is_smoke:
                continue
            strobing = strobe_speed_pairs(capability, strobe)
            if not strobing:
                continue
            fixture_id = capability.fixture.fixture_id
            merged = dict(values.get(fixture_id, []))
            merged.update(strobing)
            values[fixture_id] = sorted(merged.items())
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
        pairs = [(offset, 0) for offset in sorted(offsets)]
        # And out of its own programme: a blackout that leaves a panel
        # animating in the dark is a blackout that ends the moment somebody
        # raises a dimmer.
        pairs += internal_program_off_pairs(capability)
        if pairs:
            values[capability.fixture.fixture_id] = sorted(pairs)
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


def _all_self_animating(caps, fixture_ids) -> bool:
    """True when every colour-capable member runs programmes of its own."""
    wanted = set(fixture_ids)
    members = [c for c in caps if c.fixture.fixture_id in wanted]
    return bool(members) and all(
        internal_program(capability) is not None for capability in members
    )
