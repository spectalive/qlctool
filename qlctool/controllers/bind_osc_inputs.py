"""Bind every console control to its OSC address, beside whatever already drives it.

The address rule is dmxdesk's (`core/qlc_osc_item_json.c`): a widget is
`<prefix>/<id>` on its primary control, and a speed dial adds
`<prefix>/<id>/x<f>` for each multiplier it has a button for. QLC+ keeps a list
of sources per control (`VCWidget::addInputSource`), so the pad's MIDI binding
and the OSC one both stay live.
"""

from lxml import etree

from ..find_local import find_local
from ..localname import localname
from ..vc.build_input_source import build_input_source
from .osc_bound_widgets import OSC_BOUND_WIDGETS
from .osc_channel import osc_channel
from .osc_dial_factor_inputs import OSC_DIAL_FACTOR_INPUTS


def bind_osc_inputs(root: etree._Element, prefix: str, universe: int) -> int:
    """Add the OSC `<Input>`s on `universe` to every control widget; return how many were added."""
    console = find_local(root, "VirtualConsole")
    if console is None:
        return 0
    added = 0
    for widget in console.iter():
        kind = localname(widget)
        if kind not in OSC_BOUND_WIDGETS or widget.get("ID") is None:
            continue
        address = f"{prefix}/{widget.get('ID')}"
        build_input_source(widget, osc_channel(address), universe)
        added += 1
        if kind != "SpeedDial":
            continue
        for factor, source_id in OSC_DIAL_FACTOR_INPUTS.items():
            build_input_source(widget, osc_channel(f"{address}/x{factor}"), universe, source_id)
            added += 1
    return added
