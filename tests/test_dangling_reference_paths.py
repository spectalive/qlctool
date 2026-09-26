"""Every path `function_references` reads, broken one at a time (2026-09-26).

Task 2a's review (2026-09-25) found `rule_dangling_reference` tested only on a
Collection step, a button's `<Function>` and a slider's `<Adjust Function>`.
The other paths - a clock's `<Schedule Function>`, an XY pad preset's
`<FuncID>`, a cue list's `<Chaser>`, an audio bar's `FunctionID` (added after
the review of round D1), a Show's `ShowFunction` and `Track SceneID`, a
Sequence's `BoundScene` - would have gone unreported if their branch broke, and no shipped workspace carries any of them to notice. Each
case writes the element, in QLC+'s own tags (`engine/src/`,
`ui/src/virtualconsole/`), with an id nothing carries.
"""

from collections.abc import Callable
from pathlib import Path

import pytest
from lxml import etree

from qlctool.checks.invalid_function_id import INVALID_ID
from qlctool.checks.rule_dangling_reference import check_dangling_references
from qlctool.checks.show_graph import build_show_graph
from qlctool.constants import QLC_NS
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local

CLUB = Path(__file__).resolve().parents[1] / "examples" / "small-club" / "club.qxw"
NOBODY = "987654"


def _tag(name: str) -> str:
    return f"{{{QLC_NS}}}{name}"


def _function(root: etree._Element, kind: str, name: str) -> etree._Element:
    engine = find_local(root, "Engine")
    return etree.SubElement(engine, _tag("Function"), ID="98765", Type=kind, Name=name)


def _widget(root: etree._Element, tag: str, caption: str) -> etree._Element:
    frame = find_local(find_local(root, "VirtualConsole"), "Frame")
    return etree.SubElement(frame, _tag(tag), Caption=caption, ID="98765")


def _clock(root: etree._Element) -> str:
    clock = _widget(root, "Clock", "broken clock")
    etree.SubElement(clock, _tag("Schedule"), Function=NOBODY, Time="12:00:00")
    return "broken clock"


def _xy_pad(root: etree._Element) -> str:
    pad = _widget(root, "XYPad", "broken pad")
    preset = etree.SubElement(pad, _tag("Preset"), ID="0", Type="EFX", Name="figure")
    etree.SubElement(preset, _tag("FuncID")).text = NOBODY
    return "broken pad"


def _cue_list(root: etree._Element) -> str:
    cues = _widget(root, "CueList", "broken cues")
    etree.SubElement(cues, _tag("Chaser")).text = NOBODY
    return "broken cues"


def _audio_bar(root: etree._Element) -> str:
    # `AudioBar::saveXML`: a function bar (Type 2) writes FunctionID on its own tag.
    triggers = _widget(root, "AudioTriggers", "broken bars")
    etree.SubElement(triggers, _tag("SpectrumBar"), Name="bar", Type="2", Index="0").set(
        "FunctionID", NOBODY
    )
    return "broken bars"


def _show_function(root: etree._Element) -> str:
    show = _function(root, "Show", "broken show")
    track = etree.SubElement(show, _tag("Track"), ID="0", Name="track", SceneID=INVALID_ID)
    etree.SubElement(track, _tag("ShowFunction"), ID=NOBODY, StartTime="0", Duration="1000")
    return "broken show"


def _track_scene(root: etree._Element) -> str:
    show = _function(root, "Show", "broken track")
    etree.SubElement(show, _tag("Track"), ID="0", Name="track", SceneID=NOBODY)
    return "broken track"


def _bound_scene(root: etree._Element) -> str:
    _function(root, "Sequence", "broken sequence").set("BoundScene", NOBODY)
    return "broken sequence"


@pytest.mark.parametrize(
    "breaks",
    [_clock, _xy_pad, _cue_list, _audio_bar, _show_function, _track_scene, _bound_scene],
    ids=lambda f: f.__name__.strip("_"),
)
def test_a_reference_nothing_carries_is_reported(breaks: Callable[[etree._Element], str]):
    root = Workspace.load(CLUB).root
    assert not check_dangling_references(build_show_graph(root, []), root)
    holder = breaks(root)
    findings = check_dangling_references(build_show_graph(root, []), root)
    assert [f.function for f in findings] == [holder]
    assert findings[0].fields["function"] == NOBODY
