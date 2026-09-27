"""The longest a chaser's step holds, in milliseconds."""

from lxml import etree

from ..findall_local import findall_local


def chaser_longest_hold(function: etree._Element) -> int:
    holds = [int(step.attrib.get("Hold", 0) or 0) for step in findall_local(function, "Step")]
    return max(holds, default=0)
