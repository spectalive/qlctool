"""Write the QLC+ input profile for the SMC-PAD from the map the show uses.

The profile is what QLC+ shows a person in the input tab: it turns the raw
channel number a binding carries into "Pad 13" or "Knob 1". It is only a label
layer - a binding fires with or without it - which is exactly why the shipped
one rotted unnoticed for a day: it still declared the pad's factory notes 4-19
while every binding in the workspace had moved to 36-51, so the tab named the
wrong control for every pad on the surface.

Generating it from `smc_pad_device` removes that failure: the profile and the
bindings now cannot disagree, and `tests/test_input_profile.py` fails if the
shipped file drifts from what this builds.
"""

from lxml import etree

from ..constants import XML_DECLARATION
from .control_channel import control_channel
from .input_profile_constants import (
    EDGE_BUTTONS,
    FIRST_KNOB_CC,
    HEADER_COMMENT,
    KNOBS,
    MANUFACTURER,
    MODEL,
    PROFILE_DOCTYPE,
)
from .pads_top_down import pads_top_down
from .profile_channel import profile_channel
from .profile_ns import PROFILE_NS
from .smc_pad_device import pad_channel


def build_input_profile() -> bytes:
    """The .qxi file, ready to write, for the pad this show is driven from."""
    root = etree.Element(f"{{{PROFILE_NS}}}InputProfile", nsmap={None: PROFILE_NS})  # type: ignore[dict-item]  # lxml takes None as the default-namespace key; lxml-stubs types the map Mapping[str, str]
    creator = etree.SubElement(root, f"{{{PROFILE_NS}}}Creator")
    etree.SubElement(creator, f"{{{PROFILE_NS}}}Name").text = "qlctool"
    etree.SubElement(creator, f"{{{PROFILE_NS}}}Version").text = "5.2.2"
    etree.SubElement(creator, f"{{{PROFILE_NS}}}Author").text = "Cristian Deluxe"
    etree.SubElement(root, f"{{{PROFILE_NS}}}Manufacturer").text = MANUFACTURER
    etree.SubElement(root, f"{{{PROFILE_NS}}}Model").text = MODEL
    etree.SubElement(root, f"{{{PROFILE_NS}}}Type").text = "MIDI"
    root.append(etree.Comment(HEADER_COMMENT))

    for bank in (1, 2):
        for pad in pads_top_down():
            label = f"Pad {pad}" if bank == 1 else f"Banco 2 - Pad {pad}"
            profile_channel(root, pad_channel(pad, bank=bank), label, "Button")
    for knob in range(1, KNOBS + 1):
        profile_channel(root, control_channel(FIRST_KNOB_CC + knob - 1), f"Knob {knob}", "Knob")
    for cc, label in EDGE_BUTTONS:
        profile_channel(root, control_channel(cc), label, "Button")

    body = etree.tostring(root, pretty_print=True, encoding="unicode")
    return f"{XML_DECLARATION}\n{PROFILE_DOCTYPE}\n{body}".encode()
