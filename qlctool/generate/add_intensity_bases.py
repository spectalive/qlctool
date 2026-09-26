"""The work light's parking and the intensity each level and moment runs on.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from .dimmer_sequence import generate_dimmer_sequence
from .dimmerless_intensity import generate_dimmerless_intensity
from .energy_intensity import generate_energy_intensity
from .first_of import first_of
from .park_work_light import park_work_light
from .show_build import ShowBuild
from .show_chaser import show_chaser


def add_intensity_bases(build: ShowBuild) -> None:
    """Each level's intensity base, the peak's dimmerless owner and the dimmer programmes."""
    workspace = build.workspace
    caps = build.caps
    vocabulary = build.vocabulary
    described = build.described
    master = build.master
    builtins = build.builtins
    matrix_lit_ids = build.matrix_lit_ids
    charla_pixel_intensity_id = build.charla_pixel_intensity_id
    home_id = build.home_id
    gobos = build.gobos
    prisms = build.prisms
    gobo_rest_id = build.gobo_rest_id
    prism_rest_id = build.prism_rest_id
    dimmers = build.dimmers
    colours = build.described.colours
    # The night goes somewhere: the colour bed, the pixels and the haze run
    # underneath, and what sits on top is a level that changes every few
    # minutes. Everything a room reads as "peak" - fast movement, prism, the
    # dimmer chase - is held back for the level that is meant to be one.
    #
    # A level carries no colour at all. The matrix cycle moved out of them and
    # into AUTO, because a level that owns the bars' colour hands it back on
    # every step - and because two levels running at once (which the console
    # used to allow) then put two colour sources on one fixture.
    gobo_open_id = gobo_rest_id or first_of(gobos.scene_ids)
    # The prism parked out, spin stopped: every level and moment that does not
    # run `Prisma Animacion` holds this, or the last peak's prism stays in the
    # beam for the whole of the next quiet hour - the same LTP latch as the
    # gobo, on the channel one wheel over.
    prism_off_id = prism_rest_id or first_of(prisms.scene_ids)
    # The work light is a room state and inherits nothing: heads home, gobo
    # open, prism out are folded into the scene itself, or `Todo Negro` ->
    # `Blanco Total` after a party level is four white gobos through a spinning
    # prism (cross-audit, 2026-09-02). `Momento Charla` carries the same three
    # as members; the work light stays one scene because a state in the solo
    # frame must not be started by anything else.
    park_work_light(
        workspace, master[vocabulary.display("full_white")], [home_id, gobo_open_id, prism_off_id]
    )
    # Each level carries its own intensity base, and nobody else bids on those
    # dimmers: with the colour scenes stripped of theirs, "Ambiente" really is
    # dimmer than "Fiesta" for the first time. The pixel groups stay out -
    # `Pixeles ON` owns them.
    intensity = generate_energy_intensity(
        workspace,
        caps,
        exclude_fixture_ids=sorted(matrix_lit_ids | set(builtins.fixture_ids)),
        names=vocabulary,
        look_colours=tuple(colours.palette),
    )
    charla_intensity_ids = [intensity.full_id]
    if charla_pixel_intensity_id is not None:
        charla_intensity_ids.append(charla_pixel_intensity_id)
    if intensity.ambient_id is not None:
        master[vocabulary.display("ambient_intensity")] = intensity.ambient_id
    if intensity.full_id is not None:
        master[vocabulary.display("full_intensity")] = intensity.full_id
    if intensity.full_id is not None and dimmers is not None:
        master[vocabulary.display("dimmer_sequence")] = generate_dimmer_sequence(
            workspace,
            breath_id=intensity.full_id,
            program_ids=[
                dimmers.chase_id,
                dimmers.pingpong_id,
                dimmers.chase2_id,
            ],
            names=vocabulary,
        )
    # Peak hands its dimmers to the chase instead: `Intensidad Total` beside it
    # would hold every one of them at 255, and HTP means the chase's dips could
    # never win - cosmetic forever (TODO.md, 2026-08-27). The fixtures the chase
    # cannot reach - no dimmer role, like the MiN Wash - still need an owner or
    # they go dark the moment the level's old flat scene leaves; this is theirs.
    peak_static = generate_dimmerless_intensity(
        workspace,
        caps,
        exclude_fixture_ids=sorted(matrix_lit_ids | set(builtins.fixture_ids)),
        names=vocabulary,
        look_colours=tuple(colours.palette),
    )
    if peak_static is not None:
        master[vocabulary.display("peak_intensity")] = peak_static
    # The dynamic level's intensity: the running chase and the odd/even
    # ping-pong taking turns in one chaser - steps are alternatives, so the
    # dimmers always have exactly one owner.
    dimmer_programs_id = None
    if dimmers is not None:
        dimmer_programs_id = show_chaser(
            workspace,
            vocabulary.display("dimmer_programmes"),
            [dimmers.chase2_id, dimmers.pingpong_id],
            holds=[described.timing.dynamic_chase_ms, described.timing.dynamic_pingpong_ms],
            path="Dimmers",
        )
        master[vocabulary.display("dimmer_programmes")] = dimmer_programs_id
    build.gobo_open_id = gobo_open_id
    build.prism_off_id = prism_off_id
    build.intensity = intensity
    build.charla_intensity_ids = charla_intensity_ids
    build.peak_static = peak_static
    build.dimmer_programs_id = dimmer_programs_id
