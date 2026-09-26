"""The show's clock: the beat generator, the tap dial's layers and the beat timings.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from ..beat_generator import set_beat_generator
from .beat_tempo import apply_beat_tempo
from .movement_tempo_functions import movement_tempo_functions
from .show_build import ShowBuild
from .steps_are_scenes import steps_are_scenes
from .tap_dial_functions import tap_dial_functions


def apply_show_tempo(build: ShowBuild) -> None:
    """The beat generator, the dials' functions and, for a beat show, the beat timings."""
    workspace = build.workspace
    vocabulary = build.vocabulary
    described = build.described
    master = build.master
    beats = build.beats
    bpm_tap = build.bpm_tap
    matrices = build.matrices
    # The show runs on the clock and is re-timed by the tap dial, which is the
    # only tempo control QLC+ 5.2.2 offers a keyboard key: its `ControlBPM`
    # tap - the one that would drive the global BPM - is not in that version
    # at all ("Unknown speed dial tag: ControlBPM", read out of the show Mac's
    # own log, 2026-08-29). So the layers that read as the room's tempo go
    # under one dial, each with the multiplier that says how many taps it is
    # worth, and the beat generator stays Internal for the meters and for
    # anything the operator switches to Beats by hand.
    #
    # `bpm_tap` is that future build, ready for the QLC+ that has ControlBPM:
    # the layers go on Beats, the generator is Internal, and page 1's tap sets
    # the BPM they all count against. It is opt-in precisely because 5.2.2
    # would load it and silently do nothing.
    set_beat_generator(
        workspace.root,
        "Audio" if beats else "Internal",
        bpm=0 if beats else described.timing.bpm,
    )
    tempo_functions = tap_dial_functions(
        workspace, master, matrices, described.timing.beat_ms, vocabulary
    )
    movement_functions = movement_tempo_functions(workspace, described.timing.beat_ms, vocabulary)

    if beats or bpm_tap:
        # The PA-driven variant hands the pace to the audio beat instead. Only
        # the layers whose steps are Scenes: a chaser in Beats passes its fade
        # to each step as a raw number, and an EFX subtracts that from its own
        # millisecond duration (`EFX::loopDuration`), which is how a 16 s head
        # sweep became a 6 s one and stopped completing its turns (owner,
        # 2026-08-29). Matrix cycles are the same trap wearing a frame clock.
        present = {f.attrib.get("Name") for f in workspace.engine}
        # The matrix cycles by what they are, not by how their name starts: the
        # chasers `generate_matrix_effects` made, whatever language named them.
        names_by_id = {
            int(f.attrib["ID"]): f.get("Name", "")
            for f in workspace.engine
            if f.tag.endswith("}Function")
        }
        matrix_cycles = {names_by_id[m.chaser_id] for m in matrices if m.chaser_id is not None}
        timings = {
            name: timing
            for name, timing in described.timing.beat_timings.items()
            if name in present and steps_are_scenes(workspace, name)
        }
        timings.update(
            {name: described.timing.matrix_beats for name in present if name in matrix_cycles}
        )
        apply_beat_tempo(workspace, timings)
    build.tempo_functions = tempo_functions
    build.movement_functions = movement_functions
