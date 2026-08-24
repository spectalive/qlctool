"""Build a Virtual Console <Button> that fires one function.

A button is the console's unit of operation: caption, geometry, the function ID
it triggers, and how it triggers it. Toggle starts and stops the function; Flash
runs it while held.
"""

from lxml import etree

from ..constants import QLC_NS
from .appearance import DEFAULT, build_appearance
from .window_state import build_window_state


def build_button(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    function_id: int,
    x: int,
    y: int,
    width: int,
    height: int,
    action: str = "Toggle",
    background: str = DEFAULT,
    intensity: int = 100,
) -> etree._Element:
    """Append a <Button> to parent and return it."""
    button = etree.SubElement(parent, f"{{{QLC_NS}}}Button")
    button.set("Caption", caption)
    button.set("ID", str(widget_id))
    button.set("Icon", "")

    build_window_state(button, x, y, width, height)
    build_appearance(button, background=background)

    function = etree.SubElement(button, f"{{{QLC_NS}}}Function")
    function.set("ID", str(function_id))
    etree.SubElement(button, f"{{{QLC_NS}}}Action").text = action
    etree.SubElement(button, f"{{{QLC_NS}}}Key")
    level = etree.SubElement(button, f"{{{QLC_NS}}}Intensity")
    level.set("Adjust", "False")
    level.text = str(intensity)
    return button
