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

from lxml import etree

from ..find_local import find_local
from ..iter_local import iter_local
from ..xmlutil import localname
from .console_widget_tags import WIDGETS
from .finding import ERROR, Finding
from .show_graph import ShowGraph
from .solo_frame_conflict import solo_frame_conflict
from .solo_frame_membership import solo_frame_membership
from .spectrum_bar_bound_function import spectrum_bar_bound_function
from .spectrum_bar_is_bound import spectrum_bar_is_bound
from .spectrum_bar_target_widget import spectrum_bar_target_widget
from .strobe_reached_from import strobe_reached_from

RULE_ID = "empty_audio_trigger"


def check_audio_triggers(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], root: etree._Element
) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    # Restricted to widget tags: a Button's own <Function ID="..."> child
    # carries an ID too, and it is not the widget the bar's WidgetID means.
    widgets_by_id = {
        str(widget.attrib["ID"]): widget
        for widget in console.iter()
        if localname(widget) in WIDGETS and "ID" in widget.attrib
    }
    solo_frames = solo_frame_membership(console)
    findings: list[Finding] = []
    for widget in iter_local(console, "AudioTriggers"):
        caption = widget.attrib.get("Caption", "") or "AudioTriggers"
        bars = [
            bar
            for bar in iter_local(widget, "SpectrumBar")
            if spectrum_bar_is_bound(bar, widgets_by_id)
        ]
        if not bars:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=caption,
                    message_id="audio_trigger_unbound",
                )
            )
            continue
        for bar in bars:
            target = spectrum_bar_target_widget(bar, widgets_by_id)
            if target is not None:
                target_id = target.attrib.get("ID")
                solo_frame = solo_frames.get(target_id) if target_id is not None else None
                if solo_frame is not None and solo_frame_conflict(target, solo_frame):
                    findings.append(
                        Finding(
                            rule_id=RULE_ID,
                            severity=ERROR,
                            function=target.attrib.get("Caption", "") or caption,
                            message_id="audio_trigger_presses_solo",
                            fields={
                                "band": bar.attrib.get("Name", ""),
                                "caption": caption,
                                "target": target.attrib.get("Caption", ""),
                            },
                        )
                    )
            function_id = spectrum_bar_bound_function(bar, target)
            if function_id is None:
                continue
            reached = strobe_reached_from(graph, groups, function_id)
            if reached is None:
                continue
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(reached),
                    message_id="audio_trigger_starts_function",
                    fields={"band": bar.attrib.get("Name", ""), "caption": caption},
                )
            )
    return findings
