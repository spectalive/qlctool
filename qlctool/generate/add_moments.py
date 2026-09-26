"""The room states a person takes over with: talk, calm, party, frenzy.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from .first_of import first_of
from .flat_scene import flat_scene
from .moments import Moment, generate_moments
from .show_build import ShowBuild
from .show_collection import show_collection


def add_moments(build: ShowBuild) -> None:
    """The moments, each with its own colour bed and intensity."""
    workspace = build.workspace
    caps = build.caps
    vocabulary = build.vocabulary
    described = build.described
    master = build.master
    builtins = build.builtins
    paneles_charla_id = build.paneles_charla_id
    pixel_layer = build.pixel_layer
    movement = build.movement
    home_id = build.home_id
    beam_colors = build.beam_colors
    gobo_open_id = build.gobo_open_id
    prism_off_id = build.prism_off_id
    intensity = build.intensity
    charla_intensity_ids = build.charla_intensity_ids
    peak_static = build.peak_static
    # The moments: a room state somebody takes over with, each one bringing its
    # own colour bed because the console stops AUTO the instant one starts.
    # These are what a night actually needs a person for - a speaker on stage,
    # a lull, the last track - and they are the reason the energy levels are no
    # longer buttons: pressing two of those at once is what put the room on
    # every colour at once.
    charla_scene_id = flat_scene(
        workspace,
        caps,
        vocabulary.display("talk_light_base"),
        described.tuning.talk_white,
        dimmer_full=False,
        exclude_effect_mode_fixture_ids=builtins.fixture_ids,
    )
    beam_white_id = first_of(beam_colors.scene_ids)
    master[vocabulary.display("talk_light")] = show_collection(
        workspace,
        vocabulary.display("talk_light"),
        [f for f in (charla_scene_id, beam_white_id) if f is not None],
    )
    # Every moment brings its own intensity base beside its colour, because
    # the colour scenes no longer open anything on their own. The talk state
    # also owns the matrix/programmed-fixture base directly: `Intensidad Total`
    # deliberately excludes those fixtures to keep their automatic owner unique.
    moments = generate_moments(
        workspace,
        [
            # Somebody is talking: steady warm light, heads parked, nothing moving,
            # no wheel and no matrix - the one state where change is the enemy.
            Moment(
                vocabulary.display("talk_moment"),
                [
                    home_id,
                    master[vocabulary.display("talk_light")],
                    gobo_open_id,
                    prism_off_id,
                    *charla_intensity_ids,
                    *([paneles_charla_id] if paneles_charla_id is not None else []),
                ],
            ),
            # A lull: the colour bed and the pixels keep breathing at the low
            # intensity base, and the heads rest without freezing - each family on
            # its own slow shapes. Parked dead they read as broken ("molaría un
            # movimiento suave estilo reposo", owner, 2026-08-29); home is only the
            # fallback for a rig whose movers grew neither family.
            Moment(
                vocabulary.display("calm_moment"),
                [
                    master.get(vocabulary.display("colour_wheel")),
                    *pixel_layer,
                    *([movement.slow_id] if movement.slow_id is not None else [home_id]),
                    gobo_open_id,
                    prism_off_id,
                    intensity.ambient_id,
                ],
            ),
            # The party moment carries the prism from 2026-08-30 for the same
            # reason the party level does: the dance takes it in and out, and a
            # room somebody put into FIESTA by hand should get the whole rig.
            Moment(
                vocabulary.display("party_moment"),
                [
                    master.get(vocabulary.display("colour_wheel")),
                    *pixel_layer,
                    master.get(vocabulary.display("head_movements")),
                    master.get(vocabulary.display("gobo_animation")),
                    master.get(vocabulary.display("prism_animation"), prism_off_id),
                    intensity.full_id,
                ],
            ),
            # Everything the rig has, minus the strobe: a strobe belongs to a hit
            # somebody presses and lets go of, not to a state left running. The
            # dimmers belong to the chase, so the intensity base is the dimmerless
            # one, like the peak level's: `Intensidad Total` beside the chase held
            # every dimmer at 255 and HTP made the chase cosmetic - which is why
            # locura opened as a flat white wall ("empieza todo blanco y normal",
            # owner, 2026-08-29).
            Moment(
                vocabulary.display("frenzy_moment"),
                [
                    master.get(vocabulary.display("colour_wheel")),
                    *pixel_layer,
                    master.get(
                        vocabulary.display("fast_movements"),
                        master.get(vocabulary.display("head_movements")),
                    ),
                    master.get(vocabulary.display("gobo_animation")),
                    master.get(vocabulary.display("prism_animation")),
                    master.get(vocabulary.display("dimmer_chase")),
                    peak_static,
                ],
            ),
        ],
        names=vocabulary,
    )
    master.update(moments)
