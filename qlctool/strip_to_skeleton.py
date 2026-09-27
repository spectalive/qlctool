"""Strip a workspace down to its patch: fixtures, groups and I/O, no content.

The starting point for a fresh show. Everything that describes *the rig* stays -
patched fixtures, fixture groups, channel groups, the input/output map, the
monitor - and everything that describes *a show* goes: functions, and the
Virtual Console widgets that point at them. What comes out loads in QLC+ as an
empty console over the same patch, ready for generated content.

The root frame's caption is the show's, not the input's: it is written from the
catalogue in the show's language (`root_frame`), so an English show built from
a Spanish-saved file does not open on "Página 1" (owner's delegated decision,
2026-09-25).
"""

from lxml import etree

from .constants import QLC_NS
from .names.default_names import default_names
from .names.names import Names
from .workspace import Workspace
from .xmlutil import find_local, localname

# Engine children that describe the rig rather than the show.
KEPT_ENGINE_CHILDREN = (
    "InputOutputMap",
    "Fixture",
    "FixtureGroup",
    "ChannelsGroup",
    "Monitor",
)


def strip_to_skeleton(workspace: Workspace, names: Names | None = None) -> Workspace:
    """Remove every Function and Virtual Console widget, in place.

    Returns the same workspace so it can be chained; the patch is untouched.
    `names` is the show's vocabulary, which captions the root frame.
    """
    vocabulary = default_names() if names is None else names
    caption = vocabulary.display("root_frame")
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
            frame.set("Caption", caption)
        else:
            # No frame at all: give the console the empty one QLC+ expects.
            console.insert(0, etree.Element(f"{{{QLC_NS}}}Frame", Caption=caption))

    return workspace
