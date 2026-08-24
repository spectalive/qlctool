"""Strip a workspace down to its patch: fixtures, groups and I/O, no content.

The starting point for a fresh show. Everything that describes *the rig* stays -
patched fixtures, fixture groups, channel groups, the input/output map, the
monitor - and everything that describes *a show* goes: functions, and the
Virtual Console widgets that point at them. What comes out loads in QLC+ as an
empty console over the same patch, ready for generated content.
"""

from lxml import etree

from .constants import QLC_NS
from .workspace import Workspace
from .xmlutil import find_local, localname

# Engine children that describe the rig rather than the show.
KEPT_ENGINE_CHILDREN = (
    "InputOutputMap", "Fixture", "FixtureGroup", "ChannelsGroup", "Monitor",
)


def strip_to_skeleton(workspace: Workspace) -> Workspace:
    """Remove every Function and Virtual Console widget, in place.

    Returns the same workspace so it can be chained; the patch is untouched.
    """
    engine = workspace.engine
    for child in list(engine):
        if localname(child) not in KEPT_ENGINE_CHILDREN:
            engine.remove(child)

    console = find_local(workspace.root, "VirtualConsole")
    if console is not None:
        frame = find_local(console, "Frame")
        if frame is not None:
            for child in list(frame):
                if localname(child) != "Appearance":
                    frame.remove(child)
        else:
            # No frame at all: give the console the empty one QLC+ expects.
            console.insert(0, etree.Element(f"{{{QLC_NS}}}Frame", Caption=""))

    return workspace
