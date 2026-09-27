"""Whether a speed dial taps the global BPM rather than writing into functions.

Only a QLC+ newer than the 5.2.2 this show runs honours it, which is why
`qlctool newshow --bpm-tap` is a build of its own rather than the default.
"""

from lxml import etree

from ..xmlutil import find_local


def dial_controls_bpm(dial: etree._Element) -> bool:
    control = find_local(dial, "ControlBPM")
    return control is not None and (control.text or "").strip() == "True"
