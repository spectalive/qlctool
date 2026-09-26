"""The hand-built prism dance as one chaser."""

from ..functions.chaser import build_chaser
from ..ids import next_function_id
from ..names.names import Names
from ..workspace import Workspace

# The hand-built `Prisma Animacion` (Chaser 373) was a choreography, not a
# toggle: single beams and mirrored pairs taking the prism in turn, all-in as
# the crest, all-out as the rest. Steps are indices into
# `generate_beam_subsets`'s fixed order ("1","2","3","4","1 y 3","2 y 4");
# None means the whole-rig wheel scene (False=out, True=in).
_PRISM_CHOREOGRAPHY: tuple[int | bool, ...] = (3, 5, 0, 1, True, 2, 4, False)


def prism_choreography(
    workspace: Workspace,
    wheel_scene_ids: list[int],
    subset_scene_ids: list[int],
    extra_step_ids: list[int] | None = None,
    *,
    hold: int,
    vocabulary: Names,
) -> int | None:
    """The old eight-step prism dance, or the plain out/in walk as fallback.

    The dance needs the full set of subset scenes (a rig with fewer than four
    prism beams generates fewer) and both wheel positions; anything less falls
    back to walking the wheel scenes the way the generator always did.

    extra_step_ids ride at the end of the dance: the same prism turning at the
    other speeds, which is one channel's worth of variety the room never saw.
    `vocabulary` names the chaser and its folder.
    """
    if len(wheel_scene_ids) < 2:
        return None
    out_id, in_id = wheel_scene_ids[0], wheel_scene_ids[1]
    if len(subset_scene_ids) >= 6:
        steps = [
            (in_id if step is True else out_id if step is False else subset_scene_ids[step])
            for step in _PRISM_CHOREOGRAPHY
        ]
    else:
        steps = list(wheel_scene_ids)
    steps += list(extra_step_ids or [])
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(
            function_id,
            vocabulary.display("prism_animation"),
            steps,
            hold=hold,
            path=vocabulary.display("path_prism"),
        )
    )
    return function_id
