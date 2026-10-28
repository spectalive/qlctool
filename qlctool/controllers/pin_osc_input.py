"""Give the show a universe that listens to an OSC surface.

A QLC+ universe has one input patch, and in a show with a MIDI pad universe 0's
is the pad's, so the OSC surface gets a universe of its own: the next id after
the last one, with no output. QLC+'s OSC plugin listens on port 7700 plus that
universe's index (plugins/osc/osccontroller.cpp), so the second universe of a
show is port 7701.

The line is named `127.0.0.1`. The plugin offers one line per network
interface, named by its address, and `InputOutputMap::setInputPatch` matches a
saved patch by UID, then by name, then by line number - the OSC plugin has no
UIDs, so the name decides. The loopback address is the one line every machine
has, and the plugin's input socket binds every interface whichever line it is
opened on, so a desk on the venue's Wi-Fi still reaches it.

Feedback is left out on purpose. Where QLC+ should send it is the desk's
address, which is the night's DHCP lease, not the show's business: it is set
in the Inputs/Outputs tab like the pad's port is (`pin_midi_input`).
"""

from lxml import etree

from ..constants import QLC_NS
from ..find_local import find_local
from ..iter_local import iter_local
from ..osc_input_universe import osc_input_universe
from ..osc_plugin import OSC_PLUGIN

LINE_NAME = "127.0.0.1"
FALLBACK_LINE = "0"


def pin_osc_input(root: etree._Element) -> int | None:
    """The id of the show's OSC input universe, added after the last universe if missing.

    None when the workspace has no `<InputOutputMap>` to add it to.
    """
    existing = osc_input_universe(root)
    if existing is not None:
        return existing
    engine = find_local(root, "Engine")
    io_map = find_local(engine, "InputOutputMap") if engine is not None else None
    if io_map is None:
        return None
    universes = list(iter_local(io_map, "Universe"))
    ident = max((int(u.get("ID", "0")) for u in universes), default=-1) + 1
    universe = etree.Element(f"{{{QLC_NS}}}Universe", Name=f"Universe {ident + 1}", ID=str(ident))
    etree.SubElement(
        universe,
        f"{{{QLC_NS}}}Input",
        Plugin=OSC_PLUGIN,
        Name=LINE_NAME,
        UID="",
        Line=FALLBACK_LINE,
    )
    if universes:
        universes[-1].addnext(universe)
    else:
        io_map.append(universe)
    return ident
