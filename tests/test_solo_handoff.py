"""The frames that hand a family from AUTO to a pick must hear monitored hooks.

Dated 2026-09-12, found while building the tablet desk: every solo frame of the
generated Vibra show carried ExcludeMonitored=True. A hook that AUTO had started
as a child (the colour wheel under COLOR) sat in Monitoring state, and QLC+
5.2.2's VCButton::notifyFunctionStarting (vcbutton.cpp:258) returns without
stopping a monitoring button when the frame excludes them - so a pick never
took the family, and the room had two colour sources. The same flag let two
haze timers run on one pump, and let a moment start beside an AUTO that the
page-2 duplicate had started.
"""

from pathlib import Path

from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, iter_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"

# The frames whose Toggles a room state can start as children.
HEARING_FRAMES = ("COLOR", "PIXELES", "CABEZAS", "GOBOS", "PRISMA", "LA SALA", "HUMO AMBIENTE")


def _head(caption: str) -> str:
    return caption.split(" — ")[0].strip()


def _excludes(frame) -> str:
    element = find_local(frame, "ExcludeMonitored")
    return element.text if element is not None else "missing"


def test_the_family_and_room_frames_hear_monitored_hooks():
    workspace = Workspace.load(SHOW)
    build_canonical_show(workspace, FixtureLibrary.load())
    frames = list(iter_local(workspace.root, "SoloFrame"))
    assert frames
    hearing = [f for f in frames if _head(f.attrib.get("Caption", "")).startswith(HEARING_FRAMES)]
    deaf = [f for f in frames if f not in hearing]
    assert len(hearing) == 7, [f.attrib.get("Caption") for f in hearing]
    for frame in hearing:
        assert _excludes(frame) == "False", frame.attrib.get("Caption")
    # The library frames keep the exclusion: a chaser stepping through looks
    # that have buttons beside it would otherwise cut itself dead.
    assert deaf, "the library still has solo frames of its own"
    for frame in deaf:
        assert _excludes(frame) == "True", frame.attrib.get("Caption")
