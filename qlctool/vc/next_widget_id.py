"""The next free Virtual Console widget ID a workspace can assign."""

from lxml import etree

from .existing_widget_ids import existing_widget_ids


def next_widget_id(root: etree._Element) -> int:
    ids = existing_widget_ids(root)
    return max(ids) + 1 if ids else 0
