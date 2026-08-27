"""An AudioTriggers widget that does nothing, or presses something it should not.

Codex audit verification, 2026-08-27 (docs/superpowers/plans/
2026-08-27-qlc-audit-verification.md, claim A1): all three shipped shows carry
an `AudioTriggers` widget with `BarsNumber="5"` and zero `SpectrumBar`
children - the generator lists five bands and binds none of them, so the
widget does nothing even after somebody picks an audio input in
Configuration. A widget none of whose bars is actually bound - no channel, no
function, no widget - is dead by construction, not by a setting left unset on
site.

The other two findings are about a bar that *is* bound, and share one cause:
an audio bar is not a button. It calls `pressFunction`/`releaseFunction` (a
`VCWidgetBar`) or starts/stops a function directly (a `FunctionBar`) on its
own schedule, whenever the signal crosses a threshold, with no finger
involved and no cap on how often a beat repeats it.

- A strobe behind that is a strobe nobody chose to press. This half is the one
  the 2026-08-27 strobe-safety pass already fixed once, from the other
  direction: `check_latched_strobe` and `check_strobe_rate` both walk a
  function's descendants (`ShowGraph.descendants`) looking for a strobe's
  *shape* (`strobe_flash_rate`), never its name. Reusing that same walk here
  means any bar bound to a function - directly, or through a widget that
  starts one - that reaches a strobe anywhere under it is a finding.
- A `VCWidgetBar` that presses a button living in a `SoloFrame` alongside
  other buttons is worse than a latched Toggle: a bar's threshold crossing
  calls `VCButton::requestStateChange` on its target exactly like a finger
  would (`qmlui/virtualconsole/vcaudiotriggers.cpp:506`,
  `checkWidgetFunctionality`), and that ends up at `VCSoloFrame::
  slotFunctionStarting` (`qmlui/virtualconsole/vcbutton.cpp:428-451`), which
  stops every *other* widget's function in the frame the instant one starts,
  and nothing restores whichever was running when the bar's own button
  releases. A human choosing to press a room-state button and lose whatever
  was running is the frame doing its job; a bass line doing the same thing,
  unattended, is a malfunction - the room can go dark for the rest of the
  night.
"""

from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local, localname
from .finding import ERROR, Finding
from .rule_console import WIDGETS
from .show_graph import ShowGraph
from .strobe_shape import strobe_flash_rate

RULE = "disparador de audio vacio"
DMX_BAR = "1"
FUNCTION_BAR = "2"
WIDGET_BAR = "3"


def check_audio_triggers(graph: ShowGraph, groups, root) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    # Restricted to widget tags: a Button's own <Function ID="..."> child
    # carries an ID too, and it is not the widget the bar's WidgetID means.
    widgets_by_id = {
        widget.attrib["ID"]: widget
        for widget in console.iter()
        if localname(widget) in WIDGETS and "ID" in widget.attrib
    }
    solo_frames = _solo_frame_membership(console)
    findings: list[Finding] = []
    for widget in iter_local(console, "AudioTriggers"):
        findings += _check_widget(graph, groups, widget, widgets_by_id, solo_frames)
    return findings


def _check_widget(
    graph: ShowGraph, groups, widget, widgets_by_id: dict, solo_frames: dict
) -> list[Finding]:
    caption = widget.attrib.get("Caption", "") or "AudioTriggers"
    bars = [
        bar for bar in iter_local(widget, "SpectrumBar")
        if _is_bound(bar, widgets_by_id)
    ]
    if not bars:
        return [Finding(
            rule=RULE,
            severity=ERROR,
            function=caption,
            message=(
                "no tiene ninguna banda enlazada a canal, funcion o widget: "
                "no hace nada"
            ),
        )]
    findings: list[Finding] = []
    for bar in bars:
        target = _target_widget(bar, widgets_by_id)
        if target is not None:
            solo_frame = solo_frames.get(target.attrib.get("ID"))
            if solo_frame is not None and _solo_frame_conflict(target, solo_frame):
                findings.append(Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=target.attrib.get("Caption", "") or caption,
                    message=(
                        f"la banda «{bar.attrib.get('Name', '')}» de «{caption}» "
                        f"presiona «{target.attrib.get('Caption', '')}», que "
                        f"comparte un marco solo con otras funciones: la "
                        f"musica para lo que estuviera sonando y nada lo "
                        f"recupera"
                    ),
                ))
        function_id = _bound_function(bar, target)
        if function_id is None:
            continue
        reached = _strobe_reached(graph, groups, function_id)
        if reached is None:
            continue
        findings.append(Finding(
            rule=RULE,
            severity=ERROR,
            function=graph.name(reached),
            message=(
                f"la banda «{bar.attrib.get('Name', '')}» de «{caption}» "
                f"lo arranca: la musica lo dispara sola, sin que nadie "
                f"decida cuando"
            ),
        ))
    return findings


def _is_bound(bar, widgets_by_id: dict) -> bool:
    """Whether this bar actually targets a channel, a function or a widget."""
    bar_type = bar.attrib.get("Type")
    if bar_type == FUNCTION_BAR:
        return bar.attrib.get("FunctionID") is not None
    if bar_type == WIDGET_BAR:
        widget_id = bar.attrib.get("WidgetID")
        # A WidgetID with no matching widget is a dangling reference, not a
        # binding: QLC+'s own `checkWidgetFunctionality` looks the widget up
        # by ID and does nothing when that lookup fails, so a bar left
        # pointing at a deleted or never-created widget presses nothing -
        # the same as no WidgetID at all.
        return widget_id is not None and widget_id in widgets_by_id
    if bar_type == DMX_BAR:
        channels = find_local(bar, "DMXChannels")
        return channels is not None and bool((channels.text or "").strip())
    return False


def _target_widget(bar, widgets_by_id: dict):
    """The widget a VCWidgetBar presses, or None for any other bar type."""
    if bar.attrib.get("Type") != WIDGET_BAR:
        return None
    return widgets_by_id.get(bar.attrib.get("WidgetID"))


def _bound_function(bar, target) -> int | None:
    """The function a bar would start, resolved through its widget if it has one."""
    bar_type = bar.attrib.get("Type")
    if bar_type == FUNCTION_BAR:
        function_id = bar.attrib.get("FunctionID")
        return int(function_id) if function_id is not None else None
    if bar_type == WIDGET_BAR:
        if target is None:
            return None
        function = find_local(target, "Function")
        if function is None:
            return None
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        return None if function_id == NO_FUNCTION else function_id
    return None


def _strobe_reached(graph: ShowGraph, groups, function_id: int) -> int | None:
    """The first descendant with a strobe's shape, or None if none has one."""
    for reached in sorted(graph.descendants(function_id)):
        if strobe_flash_rate(graph, groups, reached) is not None:
            return reached
    return None


def _solo_frame_membership(console) -> dict:
    """Button widget ID -> the SoloFrame it sits directly inside, if any."""
    membership: dict = {}

    def walk(node, solo_ancestor) -> None:
        for child in node:
            name = localname(child)
            if name not in WIDGETS:
                continue
            if name == "Button" and solo_ancestor is not None and "ID" in child.attrib:
                membership[child.attrib["ID"]] = solo_ancestor
            if name in ("Frame", "SoloFrame"):
                walk(child, child if name == "SoloFrame" else solo_ancestor)

    walk(console, None)
    return membership


def _solo_frame_conflict(target, solo_frame) -> bool:
    """Whether another button in the frame would lose its function to this one.

    Only scans `solo_frame`'s direct Button children, unlike
    `_solo_frame_membership` above, which follows a SoloFrame's nested plain
    Frames too - an asymmetry that is fine today because every SoloFrame this
    generator ships holds Buttons directly, never a Button nested inside a
    plain Frame of its own; a shipped SoloFrame that grows one would need this
    walked the same way.
    """
    for button in solo_frame:
        if localname(button) != "Button" or button is target:
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id != NO_FUNCTION:
            return True
    return False
