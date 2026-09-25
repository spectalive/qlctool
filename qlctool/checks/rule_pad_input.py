"""A console bound to a surface that cannot press it.

2026-08-29: eight buttons on the manual page were bound to MIDI notes the pad
does not send. They had been written against SHIFT, and SHIFT turned out to be
a device-internal modifier - it picks the functions silkscreened on the pads
(SWING, LATCH, SYNC) and puts nothing on the wire. Nobody noticed because a
binding to a channel that never arrives looks exactly like a binding that
works: the widget is there, the number is there, and the pad is simply silent.

The same night showed the second half of it. `Vibra-split.qxw` declared no MIDI
input patch at all, so QLC+ loaded that show with nothing listening and every
binding in the file was inert until an operator built the patch by hand in the
Inputs/Outputs tab.

So the rule reads the wiring against the device, not against names:

- every `<Input>` channel a widget carries must be a channel the pad can
  actually send, which is the input profile's channel set;
- a workspace with any such binding must patch a MIDI input, or none of them
  fire;
- and no channel may be bound twice, because one pad pressing two widgets in
  the dark is a room doing two things at once.
"""

from lxml import etree

from ..generate.input_profile import build_input_profile
from ..input_binding import midi_input_patch
from ..xmlutil import localname
from .finding import ERROR, Finding
from .pad_bindings import pad_bindings

RULE_ID = "pad_input"
UNPATCHED_RULE_ID = "pad_bindings_without_input"
DOUBLE_RULE_ID = "pad_control_bound_twice"


def check_pad_input(root: etree._Element) -> list[Finding]:
    bindings = pad_bindings(root)
    if not bindings:
        return []

    findings: list[Finding] = []
    sendable = _profile_channels()
    for channel, captions in sorted(bindings.items()):
        if channel not in sendable:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=captions[0],
                    message_id="pad_input_unknown_channel",
                    fields={
                        "channel": channel,
                    },
                )
            )
        if len(captions) > 1:
            findings.append(
                Finding(
                    rule_id=DOUBLE_RULE_ID,
                    severity=ERROR,
                    function=captions[0],
                    message_id="pad_input_shared_channel",
                    fields={
                        "channel": channel,
                        "others": ", ".join(captions[1:]),
                    },
                )
            )

    if midi_input_patch(root) is None:
        findings.append(
            Finding(
                rule_id=UNPATCHED_RULE_ID,
                severity=ERROR,
                function="InputOutputMap",
                message_id="pad_input_no_input",
                fields={
                    "count": len(bindings),
                },
            )
        )
    return findings


def _profile_channels() -> set[int]:
    """The channel numbers the shipped input profile declares."""
    profile = etree.fromstring(build_input_profile())
    return {
        int(channel.attrib["Number"])
        for channel in profile.iter()
        if localname(channel) == "Channel"
    }
