"""Every place a workspace names a function by its id, and what it wrote there.

A function is referred to in more places than the steps of a Chaser. The engine
does it in Collection and Chaser steps (`ChaserStep::saveXML` writes the id as
the step's text), a Sequence's `BoundScene`, a Show track's `SceneID` and each
`ShowFunction` on it. The console does it in a button's, matrix's or slider's
`<Function>` (an `ID` attribute or the text), a speed dial's `<Function>` list,
a cue list's `<Chaser>`, a clock `<Schedule Function>`, a slider's
`<Adjust Function>`, an audio bar's `FunctionID` (on a `Bar`, `VolumeBar` or
`SpectrumBar`, so it is read on any element) and an XY pad preset's `<FuncID>`.
The tags are QLC+'s own (`engine/src/`, `ui/src/virtualconsole/` and
`qmlui/virtualconsole/` in the upstream source).

A Sequence's steps are left out: their text is channel values, not an id.
Nothing is interpreted here - the raw text is handed back, so a step that says
`None` is reported as `None` rather than silently skipped.
"""

from collections.abc import Iterator

from lxml import etree

from ..xmlutil import find_local, localname
from .console_reference import console_reference
from .engine_reference import engine_reference
from .invalid_function_id import INVALID_ID
from .nearest_caption import nearest_caption


def function_references(root: etree._Element) -> Iterator[tuple[str, str]]:
    """(who refers, the raw id it wrote) for every function reference in the file."""
    engine = find_local(root, "Engine")
    for function in engine if engine is not None else ():
        if localname(function) != "Function":
            continue
        holder = function.get("Name", function.get("ID", ""))
        for element in function.iter():
            yield from engine_reference(function, element, holder)
    console = find_local(root, "VirtualConsole")
    for element in console.iter() if console is not None else ():
        raw = console_reference(element)
        if raw is not None and raw != INVALID_ID:
            yield nearest_caption(element), raw
