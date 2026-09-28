"""Every Chaser/Collection/Sequence's members, transitively."""

from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.localname import localname


def members_of(root):
    """function id -> the function ids it starts, transitively."""
    direct = {}
    for function in find_local(root, "Engine"):
        if localname(function) != "Function":
            continue
        if function.attrib.get("Type") not in ("Chaser", "Collection", "Sequence"):
            continue
        direct[int(function.attrib["ID"])] = {
            int(step.text) for step in findall_local(function, "Step") if step.text
        }

    def expand(fid, seen):
        for member in direct.get(fid, ()):
            if member in seen:
                continue
            seen.add(member)
            expand(member, seen)
        return seen

    return {fid: expand(fid, set()) for fid in direct}
