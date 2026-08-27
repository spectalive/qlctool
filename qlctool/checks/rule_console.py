"""The console's own traps, which a workspace can load cleanly and still have.

Four of them have already cost a show. A **solo frame** stops every other
widget's function the moment one starts, so a master sharing one with its own
members dies the instant it starts them - that is what killed AUTO. A **key**
reaches every widget on every page, so two buttons on one letter fire both. A
widget past the edge of a 1440x900 canvas is a button nobody can press, because
the show laptop cannot scroll to it. And a widget past the edge of its own
*parent frame* - inside the canvas, so `_off_canvas` never sees it - is a
button drawn clipped or spilling onto whatever sits below or beside that frame:
the librería's Matrices frame grew to 34 buttons on a 6-column layout sized
for 30 (Task 5's curated scripts), and its sixth row rendered into the "Ruedas
y ciclos" frame underneath it (2026-08-27).
"""

from lxml import etree

from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, localname
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "consola"
WIDGETS = {
    "Frame", "SoloFrame", "Button", "Label", "Slider", "XYPad", "SpeedDial",
    "AudioTriggers", "Matrix", "Clock",
}


def check_console(graph: ShowGraph, root: etree._Element, canvas: tuple[int, int]) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    frame = find_local(console, "Frame")
    if frame is None:
        return []

    findings: list[Finding] = []
    findings += _solo_frames(graph, frame)
    findings += _keys(frame)
    findings += _off_canvas(frame, canvas)
    findings += _double_buttons(graph, frame)
    findings += _parent_bounds(frame)
    return findings


def _walk(widget: etree._Element, x: int = 0, y: int = 0):
    for child in widget:
        if localname(child) not in WIDGETS:
            continue
        state = find_local(child, "WindowState")
        if state is None:
            continue
        left = x + int(state.attrib["X"])
        top = y + int(state.attrib["Y"])
        yield child, left, top
        yield from _walk(child, left, top)


def _function_of(button: etree._Element) -> int | None:
    function = find_local(button, "Function")
    if function is None:
        return None
    function_id = int(function.attrib.get("ID", NO_FUNCTION))
    return None if function_id == NO_FUNCTION else function_id


def _solo_frames(graph: ShowGraph, frame: etree._Element) -> list[Finding]:
    findings: list[Finding] = []
    for widget, _, _ in _walk(frame):
        if localname(widget) != "SoloFrame":
            continue
        inside = {
            function_id
            for child in widget
            if localname(child) == "Button"
            and (function_id := _function_of(child)) is not None
        }
        for function_id in sorted(inside):
            clash = (graph.descendants(function_id) - {function_id}) & inside
            if clash:
                findings.append(Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message=(
                        f"comparte el marco solo «{widget.attrib.get('Caption', '')}» "
                        f"con {', '.join(graph.name(c) for c in sorted(clash))}, "
                        f"que es lo que arranca: el marco lo apagara nada mas pulsarlo"
                    ),
                ))
    return findings


def _keys(frame: etree._Element) -> list[Finding]:
    by_key: dict[str, list[str]] = {}
    for widget, _, _ in _walk(frame):
        if localname(widget) != "Button":
            continue
        key = find_local(widget, "Key")
        if key is not None and key.text:
            by_key.setdefault(key.text, []).append(widget.attrib.get("Caption", ""))
    findings = []
    for key, captions in sorted(by_key.items()):
        # 1-0 are on every colour bank on purpose: one key, one colour, three
        # groups. Anything else sharing a key fires two different looks.
        if key in "1234567890" or len(captions) == 1:
            continue
        findings.append(Finding(
            rule=RULE,
            severity=ERROR,
            function=", ".join(captions),
            message=f"comparten la tecla «{key}»: pulsarla dispara todos",
        ))
    return findings


def _off_canvas(frame: etree._Element, canvas: tuple[int, int]) -> list[Finding]:
    width, height = canvas
    findings = []
    for widget, left, top in _walk(frame):
        state = find_local(widget, "WindowState")
        right = left + int(state.attrib["Width"])
        bottom = top + int(state.attrib["Height"])
        if right > width or bottom > height:
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=widget.attrib.get("Caption", "") or localname(widget),
                message=(
                    f"se sale de la pantalla ({right}x{bottom} sobre "
                    f"{width}x{height}): nadie puede pulsarlo"
                ),
            ))
    return findings


def _widgets(parent: etree._Element):
    """Every widget under `parent`, at any depth - each visited exactly once,
    so a containment check below can look at a widget's own direct children
    without walking the tree itself."""
    for child in parent:
        if localname(child) not in WIDGETS:
            continue
        yield child
        yield from _widgets(child)


def _parent_bounds(frame: etree._Element) -> list[Finding]:
    """A widget must fit inside its own parent frame - not just the canvas.

    `_off_canvas` only ever compares a widget's absolute position against the
    outer 1440x900 screen: a widget nested two frames deep can sit well
    inside that and still spill past the box of the frame meant to hold it,
    drawn clipped or over whatever sits below or beside that frame.

    Local coordinates, deliberately: a widget's <WindowState> X/Y is already
    relative to its own parent's top-left, and a multipage frame puts every
    page's widgets at those same local coordinates on purpose - two pages'
    buttons landing on top of each other there is normal, not a bug. Checking
    only against the immediate parent's own Width/Height, never against a
    sibling widget, is what keeps paging from reading as a collision.
    """
    findings: list[Finding] = []
    for widget in _widgets(frame):
        state = find_local(widget, "WindowState")
        if state is None:
            continue
        width, height = int(state.attrib["Width"]), int(state.attrib["Height"])
        for child in widget:
            if localname(child) not in WIDGETS:
                continue
            child_state = find_local(child, "WindowState")
            if child_state is None:
                continue
            right = int(child_state.attrib["X"]) + int(child_state.attrib["Width"])
            bottom = int(child_state.attrib["Y"]) + int(child_state.attrib["Height"])
            if right > width or bottom > height:
                findings.append(Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=child.attrib.get("Caption", "") or localname(child),
                    message=(
                        f"se sale de su propio marco «{widget.attrib.get('Caption', '')}» "
                        f"({right}x{bottom} sobre {width}x{height} del marco): "
                        f"queda cortado o invade lo que hay al lado"
                    ),
                ))
    return findings


def _double_buttons(graph: ShowGraph, frame: etree._Element) -> list[Finding]:
    seen: dict[int, str] = {}
    findings = []
    for widget, _, _ in _walk(frame):
        if localname(widget) != "Button":
            continue
        function_id = _function_of(widget)
        if function_id is None:
            continue
        caption = widget.attrib.get("Caption", "")
        if function_id in seen:
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(function_id),
                message=(
                    f"tiene dos botones («{seen[function_id]}» y «{caption}»): "
                    f"uno de los dos siempre parecera apagado"
                ),
            ))
        else:
            seen[function_id] = caption
    return findings
