"""The next free Function ID a workspace can allocate."""

from lxml import etree

from .existing_function_ids import existing_function_ids


def next_function_id(root: etree._Element) -> int:
    ids = existing_function_ids(root)
    return max(ids) + 1 if ids else 0
