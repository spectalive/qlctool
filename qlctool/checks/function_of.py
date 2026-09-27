"""The function id a button carries, or None when it binds none."""

from lxml import etree

from ..find_local import find_local
from ..vc.build_button import NO_FUNCTION


def function_of(button: etree._Element) -> int | None:
    function = find_local(button, "Function")
    if function is None:
        return None
    function_id = int(function.attrib.get("ID", NO_FUNCTION))
    return None if function_id == NO_FUNCTION else function_id
