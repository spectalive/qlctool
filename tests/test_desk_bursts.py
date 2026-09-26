"""2026-09-13 tablet bench: a lost release must have a master-side deadline."""

from copy import deepcopy

import pytest
from lxml import etree
from rig_root import RIG_ROOT

from qlctool.build_deskmap import build_deskmap
from qlctool.capabilities_of import capabilities_of
from qlctool.checks.rule_context import RuleContext
from qlctool.checks.rule_desk_bursts import check_desk_bursts
from qlctool.checks.rule_held_column import check_held_column
from qlctool.checks.show_graph import build_show_graph, group_fixtures
from qlctool.controllers.tablet_desk_bounded_latches import tablet_desk_bounded_latches
from qlctool.desk_burst_buttons import desk_burst_buttons
from qlctool.desk_burst_identifier import desk_burst_identifier
from qlctool.desk_burst_sources import desk_burst_sources
from qlctool.desk_policy import BURST_MS
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.names.default_names import default_names
from qlctool.names.load_catalogue import load_catalogue
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, iter_local

REPO = RIG_ROOT


@pytest.fixture(scope="module")
def generated():
    workspace = Workspace.load(REPO / "QLC+ Setups/Vibra.qxw")
    library = FixtureLibrary.load()
    build_canonical_show(workspace, library)
    return workspace, library


def test_bursts_preserve_sources_and_validate_without_function_names(generated):
    original, library = generated
    workspace = deepcopy(original)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    sources = desk_burst_sources(workspace.root, default_names())
    buttons = desk_burst_buttons(workspace.root)
    assert sources.keys() == buttons.keys()
    names = default_names()
    assert {desk_burst_identifier(s.caption, names) for s in sources.values()} == BURST_MS.keys()
    for key, candidates in buttons.items():
        button = candidates[0]
        chaser = graph.functions[button.function]
        scene = graph.functions[int(find_local(chaser, "Step").text)]
        assert chaser.get("Name").startswith("Desk · ")
        assert scene.get("Name").endswith("(ráfaga)")
        chaser.set("Name", "renamed chaser")
        scene.set("Name", "renamed scene")
        assert sources[key].action == "Flash"
    assert not check_desk_bursts(graph, workspace.root)
    groups = group_fixtures(workspace.root)
    context = RuleContext(root=workspace.root, graph=graph, groups=groups, entries={}, states=set())
    bounded = tablet_desk_bounded_latches(context)
    assert not check_held_column(graph, groups, workspace.root, bounded)


@pytest.mark.parametrize(
    "fault",
    [
        "loop",
        "backwards",
        "hold",
        "step-fade-in",
        "step-fade-out",
        "common-fade",
        "common-duration",
        "beats",
        "no-step",
        "two-steps",
        "shared-source",
        "changed-values",
        "other-parent",
        "automatic-burst",
        "direct-scene-button",
        "wrong-button",
        "flash-button",
        "duplicate-button",
        "missing-button",
        "dial",
    ],
)
def test_2026_09_13_burst_corruption_fails_closed(generated, fault):
    original, library = generated
    workspace = deepcopy(original)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    source = desk_burst_sources(workspace.root, default_names())["humo-vert"]
    target = desk_burst_buttons(workspace.root)["humo-vert"][0]
    button = next(b for b in iter_local(workspace.root, "Button") if b.get("ID") == str(target.id))
    chaser = graph.functions[target.function]
    step = find_local(chaser, "Step")
    scene_id = int(step.text)
    scene = graph.functions[scene_id]
    if fault == "loop":
        find_local(chaser, "RunOrder").text = "Loop"
    elif fault == "backwards":
        find_local(chaser, "Direction").text = "Backward"
    elif fault == "hold":
        step.set("Hold", "30000")
    elif fault in ("step-fade-in", "step-fade-out"):
        step.set("FadeIn" if fault.endswith("in") else "FadeOut", "1000")
    elif fault == "common-fade":
        find_local(chaser, "Speed").set("FadeOut", "1000")
    elif fault == "common-duration":
        find_local(chaser, "SpeedModes").set("Duration", "Common")
    elif fault == "beats":
        etree.SubElement(chaser, chaser.tag.replace("Function", "Tempo")).text = "Beats"
    elif fault == "no-step":
        chaser.remove(step)
    elif fault == "two-steps":
        chaser.append(deepcopy(step))
    elif fault == "shared-source":
        step.text = str(source.function)
    elif fault == "changed-values":
        find_local(scene, "FixtureVal").text = "0,1"
    elif fault in ("other-parent", "automatic-burst"):
        parent = next(f for f in graph.functions.values() if f.get("Type") == "Collection")
        extra = deepcopy(step)
        extra.text = str(scene_id if fault == "other-parent" else target.function)
        parent.append(extra)
    elif fault == "direct-scene-button":
        extra = deepcopy(button)
        extra.set("ID", "99999")
        extra.set("Caption", "private scene leak")
        find_local(extra, "Function").set("ID", str(scene_id))
        button.getparent().getparent().append(extra)
    elif fault == "wrong-button":
        find_local(button, "Function").set("ID", str(source.function))
    elif fault == "flash-button":
        find_local(button, "Action").text = "Flash"
    elif fault == "duplicate-button":
        extra = deepcopy(button)
        extra.set("ID", "99999")
        button.getparent().append(extra)
    elif fault == "missing-button":
        button.getparent().remove(button)
    elif fault == "dial":
        dial = next(iter_local(workspace.root, "SpeedDial"))
        member = deepcopy(find_local(dial, "Function"))
        member.text = str(target.function)
        dial.append(member)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    assert check_desk_bursts(graph, workspace.root)
    frame = load_catalogue("es")["messages"]["desk_bursts_invalid"].split("{")[0]
    with pytest.raises(ValueError, match=frame):
        build_deskmap(workspace, library, "unsaved.qxw")
    if fault == "loop":
        groups = group_fixtures(workspace.root)
        context = RuleContext(
            root=workspace.root, graph=graph, groups=groups, entries={}, states=set()
        )
        bounded = tablet_desk_bounded_latches(context)
        assert check_held_column(graph, groups, workspace.root, bounded)


def test_burst_map_keeps_source_captions_and_swatches(generated, tmp_path):
    workspace, library = generated
    from qlctool.checks.show_graph import group_fixtures
    from qlctool.desk_policy import split_caption
    from qlctool.desk_swatch import swatches
    from qlctool.leading_glyph import leading_glyph

    path = tmp_path / "show.qxw"
    workspace.save(path)
    deskmap = build_deskmap(workspace, library, path)
    graph = build_show_graph(workspace.root, capabilities_of(workspace.root, library))
    for key, source in desk_burst_sources(workspace.root, default_names()).items():
        control = deskmap["controls"][key]
        glyph, caption = leading_glyph(split_caption(source.caption)[0])
        assert control["caption"] == caption
        assert control["icon"] == glyph
        assert control["swatches"] == swatches(
            graph, group_fixtures(workspace.root), source.function
        )
        assert control["widget"] != source.id
        assert control["function"] != source.function
