"""The self-timed functions this one starts, looking through Collections."""

from .show_graph import ShowGraph

# Function kinds that time themselves in milliseconds whatever their parent
# is counting in.
SELF_TIMED = ("EFX", "RGBMatrix")


def self_timed_members(graph: ShowGraph, function_id: int) -> set[int]:
    found: set[int] = set()
    stack = list(graph.members.get(function_id, ()))
    while stack:
        member = stack.pop()
        kind = graph.kind(member)
        if kind in SELF_TIMED:
            found.add(member)
        elif kind == "Collection":
            stack.extend(graph.members.get(member, ()))
    return found
