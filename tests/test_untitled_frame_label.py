"""2026-09-26, review of B10 round 2: an uncaptioned empty frame is named in the show's words.

Round 2 printed the engine tag, `Frame 12` / `SoloFrame 13`, even on a Spanish
show, which had always read `marco 12`. The label is a catalogue phrase now.
"""

import pytest
from lxml import etree

from qlctool.checks.rule_empty_frame import check_empty_frames
from qlctool.names.load_catalogue import load_catalogue


def _console(language: str) -> etree._Element:
    title = load_catalogue(language)["frames"]["room_states"] if language == "en" else "Sala"
    return etree.fromstring(
        "<Workspace><VirtualConsole><Frame>"
        f'<SoloFrame ID="1" Caption="{title}"/>'
        '<Frame ID="12"/><SoloFrame ID="13"/>'
        "</Frame></VirtualConsole></Workspace>"
    )


@pytest.mark.parametrize(
    ("language", "frame", "solo"),
    [("es", "marco 12", "marco solo 13"), ("en", "frame 12", "solo frame 13")],
)
def test_2026_09_26_an_untitled_frame_is_named_in_the_show_language(language, frame, solo):
    named = [finding.function for finding in check_empty_frames(_console(language))]
    assert frame in named
    assert solo in named
    assert not [name for name in named if name.startswith(("Frame ", "SoloFrame "))]
