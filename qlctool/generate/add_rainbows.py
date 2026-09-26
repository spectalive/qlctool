"""The two whole-rig rainbows, each with the beams' own rainbow spin.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from .rainbow_efx import generate_rainbow_efx
from .show_build import ShowBuild
from .show_collection import show_collection


def add_rainbows(build: ShowBuild) -> None:
    """The rainbows the hand-built console kept on keys of their own."""
    workspace = build.workspace
    library = build.library
    vocabulary = build.vocabulary
    master = build.master
    beam_spin_id = build.beam_spin_id
    # The two whole-rig rainbows the hand-built console kept on keys of their
    # own: console layers, like the group wheels - somebody starts them over
    # (instead of) the wheel, and stops them. AUTO never does.
    rainbows = generate_rainbow_efx(workspace, library, names=vocabulary)
    rainbow_ids: list[int] = []
    for name, function_id in (
        (vocabulary.display("rainbow_together"), rainbows.simultaneo_id),
        (vocabulary.display("rainbow_steps"), rainbows.pasos_id),
    ):
        if function_id is None:
            continue
        # An EFX in RGB mode reaches no wheel, so the rainbow is the EFX plus
        # the beams' own rainbow spin: one button, the whole rig sweeping.
        master[name] = (
            show_collection(workspace, name, [function_id, beam_spin_id])
            if beam_spin_id is not None
            else function_id
        )
        rainbow_ids.append(master[name])
    build.rainbow_ids = rainbow_ids
