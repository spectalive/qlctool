"""The gobo, beam colour and prism wheels, their animations and rests.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from .. import roles
from ..capabilities_of import capabilities_of
from .beam_subsets import generate_beam_subsets
from .dealt_gobo_scenes import generate_dealt_gobo_scenes
from .gobo_shake import generate_gobo_shake
from .prism_choreography import prism_choreography
from .prism_spins import generate_prism_spins
from .rest_scene import generate_rest_scene
from .rig_has_role import rig_has_role
from .show_build import ShowBuild
from .wheel_scenes import GeneratedWheel, generate_wheel_scenes


def add_wheel_looks(build: ShowBuild) -> None:
    """Gobos, the beams' own colour wheel, the prism and their rest scenes."""
    workspace = build.workspace
    library = build.library
    caps = build.caps
    vocabulary = build.vocabulary
    described = build.described
    master = build.master
    # Wheel scenes state the wheel and nothing else: their dimmer used to ride
    # along at 255, which a quiet level could never bring down (HTP). The
    # levels own intensity now - see `energy_intensity`.
    # The shake bursts ride inside the gobo wheel's own rotation - a shake is
    # a step, never a concurrent layer - and every plain gobo scene parks the
    # jitter channel at zero, so the burst always has somebody to end it.
    shake = generate_gobo_shake(
        workspace,
        library,
        companions=((roles.FOCUS, described.tuning.beam_focus),),
    )
    # Four heads, four different patterns, turning over together: the wheel's
    # own walk shows one shape at a time, and a room with four beams in it
    # should not look like one beam repeated (owner, 2026-08-30).
    dealt = generate_dealt_gobo_scenes(
        workspace,
        library,
        companions=((roles.GOBO_SHAKE, 0), (roles.FOCUS, described.tuning.beam_focus)),
        names=vocabulary,
    )
    gobos = (
        generate_wheel_scenes(
            workspace,
            library,
            role=roles.GOBO,
            label="Gobo",
            path="Gobos",
            dimmer_full=False,
            companions=(
                (roles.GOBO_SHAKE, 0, 0),
                (roles.FOCUS, described.tuning.beam_focus, described.tuning.beam_focus),
            ),
            extra_step_ids=shake.scene_ids + dealt,
            names=vocabulary,
        )
        if rig_has_role(caps, roles.GOBO)
        else GeneratedWheel([], None)
    )
    if gobos.chaser_id is not None:
        master[vocabulary.display("gobo_animation")] = gobos.chaser_id
    # The beams' own colour wheel: restricted to the fixtures that have gobos,
    # so a MiN Wash's Color Macro channel is not driven with beam positions -
    # and to those that also have a wheel, since a gobo spot that mixes no
    # colour has none to walk (2026-09-25, Plan C final review: `newshow`
    # stopped at "no fixture in this workspace has a color_macro channel").
    beams = [
        c.fixture.fixture_id
        for c in capabilities_of(workspace.root, library)
        if c.has_role(roles.GOBO) and c.has_role(roles.COLOR_MACRO)
    ]
    beam_colors = (
        generate_wheel_scenes(
            workspace,
            library,
            role=roles.COLOR_MACRO,
            label="Color Beam",
            fixture_ids=beams,
            hold=6000,
            path="Color Beam",
            dimmer_full=False,
            # No chaser of its own since 2026-09-22. A button that walked the
            # beams through their wheel looked like an on/off and behaved like
            # a colour pick ("el boton color beam parece un on of pero
            # realmente cambia como la rueda", owner), and the beams already
            # take the rig's colour from the rig-wide scenes. The wheel's
            # positions stay, as picks on CONTROL.
            make_chaser=False,
            names=vocabulary,
        )
        if beams
        else GeneratedWheel([], None)
    )

    # The prism spins while it is in: its rotation channel is LTP like the
    # wheel, so every prism scene owns it - slow forward when the prism is
    # inserted, stopped on the "None" position. Without this the channel kept
    # whatever the last look left, and a parked prism does not kaleidoscope.
    prisms = (
        generate_wheel_scenes(
            workspace,
            library,
            role=roles.PRISM,
            label=vocabulary.display("prism_label"),
            run_order="Loop",
            hold=8000,
            path=vocabulary.display("path_prism"),
            dimmer_full=False,
            make_chaser=False,
            companions=((roles.PRISM_ROTATION, described.tuning.prism_spin_slow, 0),),
            names=vocabulary,
        )
        if rig_has_role(caps, roles.PRISM)
        else GeneratedWheel([], None)
    )
    # And the same prism turning fast, and turning the other way: one rotation
    # channel, three looks, none of which the show used before 2026-08-30.
    spins = generate_prism_spins(workspace, library, names=vocabulary)
    beam_subsets = generate_beam_subsets(workspace, library, names=vocabulary)
    prism_animation_id = prism_choreography(
        workspace,
        prisms.scene_ids,
        beam_subsets.prism_scene_ids,
        extra_step_ids=spins.scene_ids,
        hold=described.timing.prism_step_ms,
        vocabulary=vocabulary,
    )
    if prism_animation_id is not None:
        master[vocabulary.display("prism_animation")] = prism_animation_id

    gobo_rest_id = (
        generate_rest_scene(workspace, gobos.scene_ids[0], vocabulary.display("gobo_rest"), "Gobos")
        if gobos.scene_ids
        else None
    )
    prism_rest_id = (
        generate_rest_scene(
            workspace,
            prisms.scene_ids[0],
            vocabulary.display("prism_rest"),
            vocabulary.display("path_prism"),
        )
        if prisms.scene_ids
        else None
    )
    build.shake = shake
    build.dealt = dealt
    build.gobos = gobos
    build.beam_colors = beam_colors
    build.prisms = prisms
    build.spins = spins
    build.beam_subsets = beam_subsets
    build.gobo_rest_id = gobo_rest_id
    build.prism_rest_id = prism_rest_id
