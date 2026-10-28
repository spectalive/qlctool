"""Two console controls on one OSC address.

QLC+ files an OSC message under a 16-bit hash of its address (`osc_channel`),
so two addresses can land on one channel, and a desk pressing one control
would press both. Vibra's 536 addresses happen not to collide under any prefix
tried on 2026-10-28, when the generator first bound the console to OSC, but
nothing makes that true of the next console: a show that adds one widget can
bring the first collision with it. The rule reads the channels, not the
addresses - the workspace keeps no address - so a hand-made binding that
collides is seen too.
"""

from lxml import etree

from ..osc_input_universe import osc_input_universe
from .finding import ERROR, Finding
from .osc_bindings import osc_bindings

DOUBLE_RULE_ID = "osc_control_bound_twice"


def check_osc_input(root: etree._Element) -> list[Finding]:
    """A finding for each OSC channel more than one control listens on."""
    universe = osc_input_universe(root)
    if universe is None:
        return []
    return [
        Finding(
            rule_id=DOUBLE_RULE_ID,
            severity=ERROR,
            function=controls[0],
            message_id="osc_input_shared_channel",
            fields={"channel": channel, "others": ", ".join(controls[1:])},
        )
        for channel, controls in sorted(osc_bindings(root, universe).items())
        if len(controls) > 1
    ]
