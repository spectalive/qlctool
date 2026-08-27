"""An AudioTriggers widget that presses nothing, and one that presses a strobe.

Codex audit verification, 2026-08-27 (docs/superpowers/plans/
2026-08-27-qlc-audit-verification.md, claim A1): all three shipped shows carry
an `AudioTriggers` widget with `BarsNumber="5"` and zero `SpectrumBar`
children - the generator lists five bands and binds none of them, so the
widget does nothing even after somebody picks an audio input in
Configuration. A widget with no bar bound to a channel, a function or another
widget is dead by construction, not by a setting left unset on site.

The other half is the one the 2026-08-27 strobe-safety pass already fixed
once, from the other direction: `check_latched_strobe` and
`check_strobe_rate` both walk a function's descendants (`ShowGraph.
descendants`) looking for a strobe's *shape* (`strobe_flash_rate`), never its
name, because a button decides when a strobe fires. An audio bar is not a
button - it calls `pressFunction` on the way up and again on the way down
whenever the signal crosses its threshold, with no finger involved and no
cap on how often a beat repeats it. Reusing that same descendant walk here
means any bar bound to a function - directly, or through a widget that
presses one - that reaches a strobe anywhere under it is a finding, bound or
unbound button notwithstanding.
"""

from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local, localname
from .finding import ERROR, Finding
from .rule_console import WIDGETS
from .show_graph import ShowGraph
from .strobe_shape import strobe_flash_rate

RULE = "disparador de audio vacio"
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
    findings: list[Finding] = []
    for widget in iter_local(console, "AudioTriggers"):
        findings += _check_widget(graph, groups, widget, widgets_by_id)
    return findings


def _check_widget(
    graph: ShowGraph, groups, widget, widgets_by_id: dict
) -> list[Finding]:
    caption = widget.attrib.get("Caption", "") or "AudioTriggers"
    bars = list(iter_local(widget, "SpectrumBar"))
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
        function_id = _bound_function(bar, widgets_by_id)
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


def _bound_function(bar, widgets_by_id: dict) -> int | None:
    """The function a bar would start, resolved through a widget if it targets one."""
    bar_type = bar.attrib.get("Type")
    if bar_type == FUNCTION_BAR:
        function_id = bar.attrib.get("FunctionID")
        return int(function_id) if function_id is not None else None
    if bar_type == WIDGET_BAR:
        target = widgets_by_id.get(bar.attrib.get("WidgetID"))
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
