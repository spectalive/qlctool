"""The buttons, Toggles, hooks, hook families and owners of one family frame."""

from lxml import etree

Handoff = tuple[
    dict[int, etree._Element],
    dict[int, etree._Element],
    set[int],
    set[str],
    dict[str, set[int]],
]
