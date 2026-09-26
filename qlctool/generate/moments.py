"""Moments: the states a room is actually put into by hand, one press each.

`AUTO` covers the night going as expected. What it cannot cover is a moment -
somebody climbs on stage to speak, the room drops to a lull, the last track
needs everything at once. Those are not "levels" inside a cycle: they are a
takeover, and the operator wants one button that puts the whole room somewhere
and one button that gives it back to AUTO.

So a moment is a Collection that is *self-contained*: it brings its own colour
bed and its own layers, because the thing it replaces - AUTO - is stopped while
it runs. That is enforced by the console, not here: `AUTO` and the moments
share one solo frame, so starting either stops the other and the room is always
in exactly one state.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from ..functions.collection import build_collection
from ..ids import next_function_id
from ..names.default_names import default_names
from ..names.names import Names
from ..workspace import Workspace


@dataclass(frozen=True)
class Moment:
    """One room state: everything that runs while it is the state."""

    name: str
    members: Sequence[int | None]


def generate_moments(
    workspace: Workspace, moments: Sequence[Moment], names: Names | None = None
) -> dict[str, int]:
    """A Collection per moment; a moment with nothing in it is not generated.

    `names` is the show's vocabulary: the moments' folder is its `path_moments`.
    """
    vocabulary = default_names() if names is None else names
    path = vocabulary.display("path_moments")
    generated: dict[str, int] = {}
    for moment in moments:
        members = [member for member in moment.members if member is not None]
        if not members:
            continue
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_collection(function_id, moment.name, members, path=path))
        generated[moment.name] = function_id
    return generated
