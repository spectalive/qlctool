"""Build a Virtual Console <Button> that fires one function.

A button is the console's unit of operation: caption, geometry, the function ID
it triggers, and how it triggers it. Toggle starts and stops the function; Flash
runs it while held. Two actions drive no function at all - Blackout toggles the
DMX blackout, and StopAll stops every running function, which is the panic
button a room needs when a look goes wrong and nobody knows which button
started it.
"""

from lxml import etree

from ..constants import QLC_NS
from .appearance import DEFAULT, build_appearance
from .window_state import build_window_state

# Function::invalidId() - what QLC+ stores for a button that drives nothing.
NO_FUNCTION = 4294967295

TOGGLE = "Toggle"
FLASH = "Flash"
BLACKOUT = "Blackout"
STOP_ALL = "StopAll"


def build_button(
    parent: etree._Element,
    widget_id: int,
    caption: str,
    function_id: int | None,
    x: int,
    y: int,
    width: int,
    height: int,
    action: str = TOGGLE,
    key: str | None = None,
    background: str = DEFAULT,
    foreground: str = DEFAULT,
    font: str = DEFAULT,
    intensity: int = 100,
    stop_all_fade_ms: int = 0,
    flash_override: bool = False,
    flash_force_ltp: bool = False,
) -> etree._Element:
    """Append a <Button> to parent and return it.

    key is a QLC+ keyboard shortcut as it writes them - "Space", "1", "Q", ".".
    flash_override marks a Flash button "Override priority": its scene beats
    every other channel owner while held (VCButton saves it as Override="1" on
    the Action element), which is what makes a white hit read over a running
    colour bed instead of merely joining it.
    flash_force_ltp (ForceLTP="1") additionally writes the scene's HTP
    channels as LTP - `universe->write(..., forceLTP=true)` skips the
    highest-takes-precedence compare - so a held colour *replaces* the state's
    colour instead of adding to it; red over cyan is red, not white.
    """
    button = etree.SubElement(parent, f"{{{QLC_NS}}}Button")
    button.set("Caption", caption)
    button.set("ID", str(widget_id))
    button.set("Icon", "")

    build_window_state(button, x, y, width, height)
    build_appearance(button, background=background, foreground=foreground, font=font)

    function = etree.SubElement(button, f"{{{QLC_NS}}}Function")
    function.set("ID", str(NO_FUNCTION if function_id is None else function_id))
    action_element = etree.SubElement(button, f"{{{QLC_NS}}}Action")
    if action == STOP_ALL and stop_all_fade_ms:
        action_element.set("FadeOut", str(stop_all_fade_ms))
    if action == FLASH and flash_override:
        action_element.set("Override", "1")
    if action == FLASH and flash_force_ltp:
        action_element.set("ForceLTP", "1")
    action_element.text = action
    shortcut = etree.SubElement(button, f"{{{QLC_NS}}}Key")
    if key is not None:
        shortcut.text = key
    level = etree.SubElement(button, f"{{{QLC_NS}}}Intensity")
    level.set("Adjust", "False")
    level.text = str(intensity)
    return button
