"""Prove one cue has a fixed clock and exclusive ownership of its scene.

Each error is a `[findings]` entry and its fields (ruling B10, round 2), so
the finding reads in the workspace's language.
"""

from lxml import etree

from ..desk_widgets import DeskWidget
from ..generate.live_console import PAGE_CONTROL
from ..xmlutil import find_local, findall_local, iter_local
from .phrase import Phrase
from .show_graph import ShowGraph


def desk_burst_errors(
    graph: ShowGraph,
    root: etree._Element,
    source: DeskWidget,
    button: DeskWidget,
    duration: int,
) -> list[Phrase]:
    errors: list[Phrase] = []
    if button.action != "Toggle" or button.page != PAGE_CONTROL or button.solo is not None:
        errors.append(Phrase("desk_burst_needs_toggle"))
    if button.function is None:
        return errors + [Phrase("desk_burst_not_a_chaser")]
    chaser = graph.functions.get(button.function)
    if chaser is None or graph.kind(button.function) != "Chaser":
        return errors + [Phrase("desk_burst_not_a_chaser")]
    for tag, expected in (("RunOrder", "SingleShot"), ("Direction", "Forward")):
        element = find_local(chaser, tag)
        if element is None or element.text != expected:
            errors.append(Phrase("desk_burst_chaser_setting", {"tag": tag, "expected": expected}))
    modes = find_local(chaser, "SpeedModes")
    if modes is None or dict(modes.attrib.items()) != {
        "FadeIn": "Common",
        "FadeOut": "Common",
        "Duration": "PerStep",
    }:
        errors.append(Phrase("desk_burst_speed_modes"))
    speed = find_local(chaser, "Speed")
    if speed is None or speed.get("FadeIn") != "0" or speed.get("FadeOut") != "0":
        errors.append(Phrase("desk_burst_zero_fades"))
    tempo = find_local(chaser, "Tempo")
    if tempo is not None and tempo.text != "Time":
        errors.append(Phrase("desk_burst_time_clock"))
    steps = findall_local(chaser, "Step")
    if len(steps) != 1:
        return errors + [Phrase("desk_burst_one_step")]
    step = steps[0]
    if duration <= 0 or any(
        step.get(k) != v
        for k, v in {
            "Number": "0",
            "Hold": str(duration),
            "FadeIn": "0",
            "FadeOut": "0",
        }.items()
    ):
        errors.append(Phrase("desk_burst_step_timing", {"duration": duration}))
    try:
        scene_id = int(step.text or "")
    except ValueError:
        return errors + [Phrase("desk_burst_step_no_scene")]
    scene = graph.functions.get(scene_id)
    original = graph.functions.get(source.function) if source.function is not None else None
    if (
        scene is None
        or original is None
        or source.function is None
        or graph.kind(scene_id) != "Scene"
        or graph.kind(source.function) != "Scene"
    ):
        return errors + [Phrase("desk_burst_scenes")]
    scene_values = sorted((v.get("ID"), v.text) for v in findall_local(scene, "FixtureVal"))
    original_values = sorted((v.get("ID"), v.text) for v in findall_local(original, "FixtureVal"))
    if scene_id == source.function or scene_values != original_values:
        errors.append(Phrase("desk_burst_private_copy"))
    parents = {fid for fid, members in graph.members.items() if scene_id in members}
    if parents != {button.function}:
        errors.append(Phrase("desk_burst_shared_scene"))
    if any(button.function in members for members in graph.members.values()):
        errors.append(Phrase("desk_burst_auto_start"))
    console = find_local(root, "VirtualConsole")
    references = list(iter_local(console, "Function")) if console is not None else []
    # Sliders, cue lists and speed dials also carry Function references.
    # A second writer or clock must not hide outside the button-only map.
    targets = [f.get("ID", (f.text or "").strip()) for f in references]
    if str(scene_id) in targets:
        errors.append(Phrase("desk_burst_widget_scene"))
    if targets.count(str(button.function)) != 1:
        errors.append(Phrase("desk_burst_one_button"))
    return errors
