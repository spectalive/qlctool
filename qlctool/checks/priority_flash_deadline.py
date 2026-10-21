"""Whether QLC+ owns the maximum hold of a priority Flash button."""

from lxml import etree

from ..find_local import find_local
from ..iter_local import iter_local


def priority_flash_deadline(root: etree._Element, widget_id: int, duration: int) -> bool:
    for button in iter_local(root, "Button"):
        if button.get("ID") != str(widget_id):
            continue
        action = find_local(button, "Action")
        return bool(
            action is not None
            and action.text == "Flash"
            and action.get("Override") == "1"
            and action.get("ForceLTP") == "1"
            and action.get("MaxHold") == str(duration)
        )
    return False
