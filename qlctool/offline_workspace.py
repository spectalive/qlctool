"""A workspace copy that asks QLC+ to open none of the rig's connections.

What the file itself tells QLC+ to open when it loads is removed or turned
off: every universe's `<Input>`, `<Output>` and `<Feedback>` patch (the DMX
interface, Art-Net, the MIDI pad and its LED bridge), an audio beat
generator (the microphone: `BeatType="Audio"` becomes `Internal`), and an
auto-starting network server (`AutoStart="False"`; a web server there would
bind QLC+'s port). QLC+ 5 has no flag to load a workspace without them
(`qmlui/main.cpp`, `engine/src/inputoutputmap.cpp`). The root's
`CurrentWindow` is also forced to `"VC"` (`force_vc_window`), whatever the
file says, so the QML build always opens on the one view whose load logs an
end-of-load marker.

This governs the file only. QLC+ also opens the default I/O patches kept in
its own settings before it loads any workspace (`InputOutputMap::loadDefaults`),
which a copy cannot reach: validation refuses to launch while those exist
(`saved_io_patches`). Used by validation and by the suite's live QLC+
(2026-09-26, reviews of round D6).
"""

from pathlib import Path

from lxml import etree

from .force_vc_window import force_vc_window
from .iter_local import iter_local
from .localname import localname

IO_PATCHES = ("Input", "Output", "Feedback")


def offline_workspace(source: Path, target: Path) -> Path:
    """Write `source` to `target` with its I/O patches, audio beat and server autostart off.

    The copy is also forced onto the Virtual Console view (`force_vc_window`),
    since the QML build's end-of-load marker only ever logs there.
    """
    tree = etree.parse(str(source))
    force_vc_window(tree.getroot())
    for io_map in list(iter_local(tree.getroot(), "InputOutputMap")):
        for child in io_map:
            name = localname(child)
            if name == "Universe":
                for patch in [e for e in child if localname(e) in IO_PATCHES]:
                    child.remove(patch)
            elif name == "BeatGenerator" and child.get("BeatType") == "Audio":
                child.set("BeatType", "Internal")
            elif name == "NetworkServer":
                child.set("AutoStart", "False")
    tree.write(str(target), xml_declaration=True, encoding="UTF-8")
    return target
