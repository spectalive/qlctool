"""An RGBMatrix's flash rate, when it runs the Strobe algorithm."""

from lxml import etree

from ..xmlutil import find_local

STROBE_ALGORITHM = "Strobe"
# MasterTimer runs at 50 Hz; a zero-duration step flips every other tick.
TICK_FLASH_HZ = 25.0


def matrix_flash_rate(function: etree._Element) -> float | None:
    algorithm = find_local(function, "Algorithm")
    if algorithm is None or (algorithm.text or "").strip() != STROBE_ALGORITHM:
        return None
    speed = find_local(function, "Speed")
    duration = int(speed.attrib.get("Duration", "0")) if speed is not None else 0
    if duration <= 0:
        return TICK_FLASH_HZ
    return 1000.0 / (2 * duration)
