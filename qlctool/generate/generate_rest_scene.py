"""Clone a generated Scene as an explicit rest look for a play-family hook."""

from copy import deepcopy

from ..ids import next_function_id
from ..workspace import Workspace
from ..xmlutil import findall_local


def generate_rest_scene(
    workspace: Workspace,
    source_id: int,
    name: str,
    path: str,
) -> int:
    """Copy a source Scene's exact fixture values under a named rest function."""
    source = next(
        (
            function
            for function in findall_local(workspace.engine, "Function")
            if function.attrib.get("ID") == str(source_id)
        ),
        None,
    )
    if source is None or source.attrib.get("Type") != "Scene":
        raise ValueError(f"rest scene source {source_id} is not a Scene")

    function_id = next_function_id(workspace.root)
    rest = deepcopy(source)
    rest.attrib.update({"ID": str(function_id), "Name": name, "Path": path})
    workspace.add_function(rest)
    return function_id
