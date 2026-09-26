"""The floors under AUTO and the moments: what a released pick falls back to.

A pick in a family frame stops the frame's hook, and releasing it starts
nothing: QLC+'s solo frame has no restore (`vcsoloframe.cpp`). The gobo, the
gobo shake, the prism, the heads' position and the panels' programme mode are
LTP, so they kept whatever the pick last wrote - Gobo Shake went on shaking
under FIESTA, a released movement left the heads where it stopped (en-sala
DMX audit, 2026-09-26; `rule_pick_release_orphans`).

A floor is a copy of the family's rest scene (heads centred, gobo open, prism
out, panels on the desk's colour), started first by every room state that
plays the family, bound to no button. While a hook or a pick runs it is
overridden, since a later fader wins an LTP channel; the moment they stop,
its still-running fader writes the channel again. Measured in QLC+ 5 on
2026-09-27: gobo and aim returned after Gobo Shake and Circulo were released,
and the hooks won again when pressed (ruling D8). It writes no intensity, so
it never lights anything by itself (`static_floors`).

Added after the console, so every function the console binds keeps its id.
"""

from ..checks.show_graph import build_show_graph, group_fixtures
from ..xmlutil import findall_local
from .prepend_collection_steps import prepend_collection_steps
from .rest_scene import generate_rest_scene
from .show_build import ShowBuild
from .written_channels import written_channels

# The room states a family frame's hook runs under.
STATES = ("auto", "talk_moment", "calm_moment", "party_moment", "frenzy_moment")


def add_family_floors(build: ShowBuild) -> None:
    """Copy each family's rest scene as a floor and start it first in the states that play it."""
    workspace = build.workspace
    vocabulary = build.vocabulary
    sources = [
        (source, name)
        for source, name in (
            (build.home_id, "heads_floor"),
            (build.gobo_open_id, "gobo_floor"),
            (build.prism_off_id, "prism_floor"),
            (build.paneles_charla_id, "pixel_floor"),
        )
        if source is not None
    ]
    states = [
        state_id
        for state in STATES
        if (state_id := build.master.get(vocabulary.display(state))) is not None
    ]
    graph = build_show_graph(workspace.root, build.caps)
    groups = group_fixtures(workspace.root)
    written = {f: written_channels(graph, groups, f) for f in [*states, *(s for s, _ in sources)]}
    paths = {f.get("ID"): f.get("Path", "") for f in findall_local(workspace.engine, "Function")}
    floors_of: dict[int, list[int]] = {state_id: [] for state_id in states}
    for source, name in sources:
        # Only under a state that plays the family itself: a floor under a
        # state that starts none of the frame's hooks would win the channels
        # over a pick left latched across the switch (2026-09-27 review, M-3).
        playing = [state_id for state_id in states if written[state_id] & written[source]]
        if not playing:
            continue
        floor = generate_rest_scene(workspace, source, vocabulary.display(name), paths[str(source)])
        for state_id in playing:
            floors_of[state_id].append(floor)
    for state_id, floors in floors_of.items():
        if floors:
            prepend_collection_steps(workspace, state_id, floors)
