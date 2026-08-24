"""Build the <Appearance> block every Virtual Console widget carries.

QLC+ writes it for every widget, always with the same five children, so a
generated widget that omits it looks different from a hand-built one in the file
even though QLC+ would fill in defaults.
"""

from lxml import etree

from ..constants import QLC_NS

DEFAULT = "Default"


def build_appearance(
    parent: etree._Element,
    frame_style: str = "None",
    foreground: str = DEFAULT,
    background: str = DEFAULT,
) -> etree._Element:
    """Append an <Appearance> to parent; colours are ARGB decimals or Default."""
    appearance = etree.SubElement(parent, f"{{{QLC_NS}}}Appearance")
    for name, value in (
        ("FrameStyle", frame_style),
        ("ForegroundColor", foreground),
        ("BackgroundColor", background),
        ("BackgroundImage", "None"),
        ("Font", DEFAULT),
    ):
        etree.SubElement(appearance, f"{{{QLC_NS}}}{name}").text = value
    return appearance
