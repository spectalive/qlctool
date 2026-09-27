"""The function a bar would start, resolved through its widget if it has one."""

from lxml import etree

from ..find_local import find_local
from ..vc.build_button import NO_FUNCTION
from .spectrum_bar_types import FUNCTION_BAR, WIDGET_BAR


def spectrum_bar_bound_function(bar: etree._Element, target: etree._Element | None) -> int | None:
    bar_type = bar.attrib.get("Type")
    if bar_type == FUNCTION_BAR:
        function_id_text = bar.attrib.get("FunctionID")
        return int(function_id_text) if function_id_text is not None else None
    if bar_type == WIDGET_BAR:
        if target is None:
            return None
        function = find_local(target, "Function")
        if function is None:
            return None
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        return None if function_id == NO_FUNCTION else function_id
    return None
