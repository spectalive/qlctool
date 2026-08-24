"""Allocate unique Function IDs within a workspace.

QLC+ references functions by integer ID everywhere - chaser steps, VC buttons,
collections - so a generated function needs an ID no existing one uses. IDs are
not required to be contiguous, only unique, so max+1 is safe and cheap.

Only the Engine's own <Function> children count. The Virtual Console writes
`<Function ID="..."/>` too, as a *reference* from a button or slider, and an
unassigned button carries QLC+'s invalid-ID sentinel 4294967295 - counting that
as an existing function pushes the next ID past the 32-bit range QLC+ stores,
which is exactly the kind of silent corruption this toolkit exists to avoid.
"""

from lxml import etree

from .xmlutil import find_local, findall_local


def existing_function_ids(root: etree._Element) -> set[int]:
    engine = find_local(root, "Engine")
    if engine is None:
        return set()
    return {
        int(function.attrib["ID"])
        for function in findall_local(engine, "Function")
        if "ID" in function.attrib
    }


def next_function_id(root: etree._Element) -> int:
    ids = existing_function_ids(root)
    return max(ids) + 1 if ids else 0
