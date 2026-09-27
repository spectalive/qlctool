"""Build one monitored Collection per unique original function, and its companions."""

from collections.abc import Mapping, Sequence

from lxml import etree

from ..functions.build_collection import build_collection
from ..ids import next_function_id
from ..workspace import Workspace


def play_wrap(
    workspace: Workspace,
    functions: dict[int, etree._Element],
    function_ids: Sequence[int],
    prefix: str,
    path: str,
    companions: Mapping[int, Sequence[int]] | None = None,
) -> list[int]:
    wrappers: list[int] = []
    seen: set[int] = set()
    for original_id in function_ids:
        if original_id in seen:
            continue
        seen.add(original_id)
        original = functions.get(original_id)
        if original is None:
            raise ValueError(f"play wrapper source {original_id} is missing")
        name = original.get("Name")
        if name is None:
            raise ValueError(f"play wrapper source {original_id} has no name")
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(
                function_id,
                prefix + name,
                [original_id, *(companions or {}).get(original_id, ())],
                path=path,
            )
        )
        wrappers.append(function_id)
    return wrappers
