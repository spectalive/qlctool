"""Round G review, 2026-09-26: the shortcut `pick_darkens` takes for light-neutral picks.

A pick that writes no colour, dimmer or strobe channel (a movement figure, a
gobo, a prism) is answered from the room state and the hooks its frame stops,
once per frame and state, and the answer is reused for the frame's other
picks (7204f34). Nothing tested the reuse with a dark answer: each pick
beside a dark state must still get its own finding.
"""

from rig_root import RIG_ROOT

import qlctool.checks.rule_pick_darkens as rule_pick_darkens
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.console_states import room_states
from qlctool.checks.family_frame_picks import family_frame_picks
from qlctool.checks.pick_leaves_light_alone import pick_leaves_light_alone
from qlctool.checks.show_graph import build_show_graph, group_fixtures
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, iter_local

VIBRA_SPLIT = RIG_ROOT / "QLC+ Setups" / "Vibra-split.qxw"


def test_2026_09_26_every_light_neutral_pick_beside_a_dark_state_is_named(monkeypatch):
    root = Workspace.load(VIBRA_SPLIT).root
    graph = build_show_graph(root, capabilities_of(root, FixtureLibrary.load()))
    groups = group_fixtures(root)
    states = room_states(root, graph, groups)
    frames = list(iter_local(find_local(root, "VirtualConsole"), "SoloFrame"))
    neutral = {
        pick_id: stopped
        for frame in frames
        for pick_id, stopped in family_frame_picks(graph, groups, states, frame)
        if pick_leaves_light_alone(graph, groups, pick_id)
    }
    assert len(neutral) > 20, "Vibra-split's heads, gobo and prism frames hold these"

    # The state alone is dark; a pick asked about with it is not.
    asked: list[tuple[int, ...]] = []

    def dark_state(graph, groups, roots, stopped, **_):
        asked.append(roots)
        return {"Dark Fixture"} if len(roots) == 1 else set()

    monkeypatch.setattr(rule_pick_darkens, "instant_dark_fixtures", dark_state)
    findings = rule_pick_darkens.check_pick_darkens(graph, groups, root, states)

    named = {(f.function, f.fields["pick"]) for f in findings}
    for pick_id in neutral:
        for state_id in states:
            assert (graph.name(state_id), graph.name(pick_id)) in named
    # Asked once per state and stopped set, not once per pick.
    alone = [roots for roots in asked if len(roots) == 1]
    assert len(alone) == len(states) * len(set(neutral.values()))
    assert all(
        f.fixtures == ("Dark Fixture",)
        for f in findings
        if f.fields["pick"] in {graph.name(p) for p in neutral}
    )
