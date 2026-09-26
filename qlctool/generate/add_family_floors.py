"""The floors under AUTO and the moments: what a released pick falls back to.

A pick in a family frame stops the frame's hook, and releasing it starts
nothing: QLC+'s solo frame has no restore (`vcsoloframe.cpp`). The gobo, the
gobo shake, the prism and the heads' position are LTP, so they kept whatever
the pick last wrote - Gobo Shake went on shaking under FIESTA, a released
movement left the heads where it stopped (en-sala DMX audit, 2026-09-26;
`rule_pick_release_orphans`).

A floor is a copy of the family's rest scene (gobo open, prism out, heads
centred), started first by every room state, bound to no button. While a hook
or a pick runs it is overridden, since a later fader wins an LTP channel; the
moment they stop, its still-running fader writes the channel again. Measured
in QLC+ 5 on 2026-09-27: gobo and aim returned after Gobo Shake and Circulo
were released, and the hooks won again when pressed (ruling D8). It writes no
intensity, so it never lights anything by itself (`static_floors`).

Added after the console, so every function the console binds keeps its id.
"""

from ..xmlutil import findall_local
from .prepend_collection_steps import prepend_collection_steps
from .rest_scene import generate_rest_scene
from .show_build import ShowBuild

# The room states a family frame's hook runs under.
STATES = ("auto", "talk_moment", "calm_moment", "party_moment", "frenzy_moment")


def add_family_floors(build: ShowBuild) -> None:
    """Copy each family's rest scene as a floor and start it first in every state."""
    workspace = build.workspace
    vocabulary = build.vocabulary
    sources = (
        (build.home_id, "heads_floor"),
        (build.gobo_open_id, "gobo_floor"),
        (build.prism_off_id, "prism_floor"),
    )
    paths = {f.get("ID"): f.get("Path", "") for f in findall_local(workspace.engine, "Function")}
    floors = [
        generate_rest_scene(workspace, source, vocabulary.display(name), paths[str(source)])
        for source, name in sources
        if source is not None
    ]
    if not floors:
        return
    for state in STATES:
        state_id = build.master.get(vocabulary.display(state))
        if state_id is not None:
            prepend_collection_steps(workspace, state_id, floors)
