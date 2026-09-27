"""A tap that flattens every programme to one length.

2026-08-29, the owner on the speed dials: "eso no funciona bien, nunca ha
funcionado bien ... se vuelven todos los programas locos". A tap dial writes
`dial time x multiplier` into each function it lists
(`VCSpeedDial::applyFunctionsTime`), so the multiplier is where a layer states
how long it is in taps. Give every layer the same multiplier and one tap makes
the colour wheel, the prism and the dimmer pulse exactly as long as each
other - the show collapses to one length, which is what "locos" looked like.

The rule reads the wiring: a dial that can be tapped and gives one multiplier
to everything under it is flattening the show. Two functions may honestly share
a multiplier; a whole console cannot - unless every layer under the dial
already runs the same length, in which case one multiplier keeps them as they
are and nothing collapses. A lone fixture's dial lists its four colour wheels
and nothing else, all stepping at the one beat (2026-09-27); the generator
derives each multiplier from that length and cannot honestly write another.

The second half is the tap that does nothing at all. A dial with a tap key and
no functions under it re-times nothing on this QLC+: the `ControlBPM` tap that
would drive the global BPM instead is not in 5.2.2 - it says so when it loads
one ("Unknown speed dial tag: ControlBPM", read out of the show Mac's own log
the same night) - so a bound tap key needs functions to write into.
"""

from lxml import etree

from ..find_local import find_local
from ..findall_local import findall_local
from ..iter_local import iter_local
from .dial_controls_bpm import dial_controls_bpm
from .dial_durations import dial_durations
from .finding import ERROR, Finding
from .has_tap_binding import has_tap_binding

RULE_ID = "tap_dial"
EMPTY_RULE_ID = "tap_dial_empty"

# Below this many functions, one shared multiplier is a coincidence rather
# than a flattened console.
FLATTENING_FROM = 3


def check_tap_dial(root: etree._Element) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    findings: list[Finding] = []
    for dial in iter_local(console, "SpeedDial"):
        if not has_tap_binding(dial):
            continue
        caption = dial.attrib.get("Caption", "SpeedDial")
        multipliers = [
            function.attrib.get("Duration", "0") for function in findall_local(dial, "Function")
        ]
        if not multipliers and dial_controls_bpm(dial):
            continue  # the `--bpm-tap` build: its tap drives the global BPM
        if not multipliers:
            findings.append(
                Finding(
                    rule_id=EMPTY_RULE_ID,
                    severity=ERROR,
                    function=caption,
                    message_id="tap_dial_no_functions",
                )
            )
            continue
        if (
            len(multipliers) >= FLATTENING_FROM
            and len(set(multipliers)) == 1
            and len(set(dial_durations(root, dial))) > 1
        ):
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=caption,
                    message_id="tap_dial_same_multiplier",
                    fields={"count": len(multipliers)},
                )
            )
    return findings
