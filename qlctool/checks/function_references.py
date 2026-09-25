"""Every place a workspace names a function by its id, and what it wrote there.

A function is referred to in more places than the steps of a Chaser. The engine
does it in Collection and Chaser steps (`ChaserStep::saveXML` writes the id as
the step's text), a Sequence's `BoundScene`, a Show track's `SceneID` and each
`ShowFunction` on it. The console does it in a button's, matrix's or slider's
`<Function>` (an `ID` attribute or the text), a speed dial's `<Function>` list,
a cue list's `<Chaser>`, a clock `<Schedule Function>`, an audio bar's
`FunctionID` and an XY pad preset's `<FuncID>`. The tags are QLC+'s own
(`engine/src/`, `ui/src/virtualconsole/` in the upstream source).

A Sequence's steps are left out: their text is channel values, not an id.
Nothing is interpreted here - the raw text is handed back, so a step that says
`None` is reported as `None` rather than silently skipped.
"""

from collections.abc import Iterator

from lxml import etree

from ..xmlutil import find_local, localname

# The engine's "no function" (`Function::invalidId()`): a blackout button, an
# unbound slider or a track without a scene. It refers to nothing on purpose.
INVALID_ID = "4294967295"

STEP_TYPES = ("Chaser", "Collection")
# Console tags whose text is a function id.
CONSOLE_TEXT_TAGS = ("Chaser", "FuncID")
# Console tags whose attribute is a function id.
CONSOLE_ATTRIBUTES = {"Schedule": "Function", "SpectrumBar": "FunctionID"}


def function_references(root: etree._Element) -> Iterator[tuple[str, str]]:
    """(who refers, the raw id it wrote) for every function reference in the file."""
    engine = find_local(root, "Engine")
    for function in engine if engine is not None else ():
        if localname(function) != "Function":
            continue
        holder = function.get("Name", function.get("ID", ""))
        for element in function.iter():
            yield from _engine_reference(function, element, holder)
    console = find_local(root, "VirtualConsole")
    for element in console.iter() if console is not None else ():
        raw = _console_reference(element)
        if raw is not None and raw != INVALID_ID:
            yield _caption(element), raw


def _engine_reference(
    function: etree._Element, element: etree._Element, holder: str
) -> Iterator[tuple[str, str]]:
    tag = localname(element)
    if element is function:
        if function.get("Type") == "Sequence" and "BoundScene" in function.attrib:
            yield holder, function.get("BoundScene", "")
    elif tag == "Step" and function.get("Type") in STEP_TYPES:
        yield holder, (element.text or "").strip()
    elif tag == "ShowFunction":
        yield holder, element.get("ID", "")
    elif tag == "Track" and element.get("SceneID", INVALID_ID) != INVALID_ID:
        yield holder, element.get("SceneID", "")


def _console_reference(element: etree._Element) -> str | None:
    tag = localname(element)
    if tag == "Function":
        return element.get("ID", (element.text or "").strip())
    if tag in CONSOLE_TEXT_TAGS:
        return (element.text or "").strip()
    attribute = CONSOLE_ATTRIBUTES.get(tag)
    if attribute is not None and attribute in element.attrib:
        return element.get(attribute)
    return None


def _caption(element: etree._Element) -> str:
    """The nearest widget with a caption: what somebody would look for on the console."""
    for ancestor in element.iterancestors():
        if ancestor.get("Caption"):
            return ancestor.get("Caption", "")
    return localname(element)
