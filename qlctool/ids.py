"""Allocate unique Function IDs within a workspace.

QLC+ references functions by integer ID everywhere - chaser steps, VC buttons,
collections - so a generated function needs an ID no existing one uses. IDs are
not required to be contiguous, only unique, so max+1 is safe and cheap.
"""

from lxml import etree

from .xmlutil import iter_local


def existing_function_ids(root: etree._Element) -> set[int]:
    ids = set()
    for function in iter_local(root, "Function"):
        raw = function.attrib.get("ID")
        if raw is not None:
            ids.add(int(raw))
    return ids


def next_function_id(root: etree._Element) -> int:
    ids = existing_function_ids(root)
    return max(ids) + 1 if ids else 0
