"""Whether a console button's Action is a Toggle (or unset, which defaults to it)."""

from lxml import etree

from ..find_local import find_local


def is_toggle(button: etree._Element) -> bool:
    action = find_local(button, "Action")
    return action is None or (action.text or "").strip() in ("", "Toggle")
