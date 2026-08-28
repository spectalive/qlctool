"""The light for the vertical smoke, exactly as the hand-built show ran it.

When the vertical smoke fires, the panels put up their own programme so the
column reads against the room. The hand-built console had this on its
"HUMO AUTO" button - misnamed, it never touched a smoke machine - as a chaser
holding the panels' Effect 1 for a minute and then Effect 3 for ten
("como el antiguo", owner, 2026-08-28). Both are full-panel colour cycles;
the values, the order and the holds here are that chaser's, verbatim
(DeluxeEventos2 ID 367: values 2 and 14 on the effect channel, 60 s / 600 s).

It is a latched look on purpose: the smoke moment lasts as long as it lasts,
and somebody presses it off - or a room state replaces it - when it is over.
"""

from collections.abc import Sequence

from ..functions.chaser import build_chaser
from ..ids import next_function_id
from ..workspace import Workspace

NAME = "Humo Vertical"
# The hand-built chaser's own holds: one minute of Effect 1, ten of Effect 3.
FIRST_HOLD_MS = 60000
SECOND_HOLD_MS = 600000
# 1-based programme numbers, as the effect scenes are ordered.
EFFECTS = (1, 3)


def generate_vertical_smoke_light(
    workspace: Workspace,
    effect_scene_ids: Sequence[int],
    path: str = "Efectos Propios",
) -> int | None:
    """The `Humo Vertical` chaser, or None when the panels are not patched."""
    if len(effect_scene_ids) < max(EFFECTS):
        return None
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(
            function_id,
            NAME,
            [effect_scene_ids[number - 1] for number in EFFECTS],
            hold=[FIRST_HOLD_MS, SECOND_HOLD_MS],
            run_order="Loop",
            path=path,
        )
    )
    return function_id
