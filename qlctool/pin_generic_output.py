"""Pin every universe's DMX output to the generic USB binding the rig runs on.

The three shipped shows disagreed about the interface (old-vs-new audit,
2026-08-28): two carried the show Mac's FT232R serial number `A50285BI`, the
split file carried `AB0PEY7F` from another machine - and a workspace opened
with only the *other* interface attached simply outputs nothing. `docs/rig.md`
records the decision: `UID="None"`, so QLC+ binds line 0 of whatever USB-DMX
interface is connected. The stale `UniverseChannels` (still 300 with fixtures
patched through 316) is normalised to the patch's real top channel at the
same time - QLC+ recomputes it at runtime, but a file that says what the rig
does is the point of this repo.
"""

from lxml import etree

from .fixture import patched_fixtures
from .xmlutil import find_local, iter_local

GENERIC_UID = "None"
OUTPUT_PLUGIN = "DMX USB"


def pin_generic_output(root: etree._Element) -> None:
    """Rewrite every <Output> to the generic DMX USB binding, in place."""
    top_channel = max(
        (fixture.address + fixture.channels for fixture in patched_fixtures(root)),
        default=0,
    )
    engine = find_local(root, "Engine")
    io_map = find_local(engine, "InputOutputMap") if engine is not None else None
    if io_map is None:
        return
    for universe in iter_local(io_map, "Universe"):
        output = find_local(universe, "Output")
        if output is None:
            continue
        output.set("Plugin", OUTPUT_PLUGIN)
        output.set("UID", GENERIC_UID)
        output.attrib.pop("Name", None)
        parameters = find_local(output, "PluginParameters")
        if parameters is not None and top_channel:
            parameters.set("UniverseChannels", str(top_channel))
