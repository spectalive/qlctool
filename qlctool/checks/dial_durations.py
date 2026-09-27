"""The engine duration of each function a speed dial lists, in the dial's order.

A function the engine does not carry, or one with no `<Speed>`, reads as a
length of its own, so a dial over dangling ids is still judged flattening.
"""

from lxml import etree

from ..xmlutil import find_local, findall_local


def dial_durations(root: etree._Element, dial: etree._Element) -> list[str]:
    engine = find_local(root, "Engine")
    speeds: dict[str, str] = {}
    for function in engine if engine is not None else ():
        speed = find_local(function, "Speed")
        if speed is not None:
            speeds[function.get("ID", "")] = speed.get("Duration", "0")
    # The dial writes the id as the element's text (`VCSpeedDial::saveXML`).
    listed = [(function.text or "").strip() for function in findall_local(dial, "Function")]
    return [speeds.get(function_id, f"?{function_id}") for function_id in listed]
