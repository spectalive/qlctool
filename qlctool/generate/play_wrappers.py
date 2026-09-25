"""One-member Collections that isolate JUGAR picks from automatic state starts."""

from collections.abc import Sequence

from lxml import etree

from ..functions.collection import build_collection
from ..ids import next_function_id
from ..names.default_names import default_names
from ..names.names import Names
from ..workspace import Workspace
from ..xmlutil import findall_local
from .generated_play_wrappers import GeneratedPlayWrappers as _GeneratedPlayWrappers


def generate_play_wrappers(
    workspace: Workspace,
    color_ids: Sequence[int],
    rainbow_ids: Sequence[int],
    panel_effect_ids: Sequence[int],
    panel_manual_id: int | None,
    movement_ids: Sequence[int],
    gobo_ids: Sequence[int],
    prism_ids: Sequence[int],
    names: Names | None = None,
) -> _GeneratedPlayWrappers:
    """Wrap every play pick once, preserving each original function as its leaf."""
    vocabulary = default_names() if names is None else names

    def family(identifier: str) -> str:
        return vocabulary.render("path_play", family=vocabulary.display(identifier))

    functions = {
        int(function.attrib["ID"]): function
        for function in findall_local(workspace.engine, "Function")
        if "ID" in function.attrib
    }
    panels = _spread(panel_effect_ids, 12)
    if panel_manual_id is not None:
        panels.append(panel_manual_id)
    prefix = vocabulary.display("pick_prefix")
    gobos = vocabulary.render("path_play", family="Gobos")
    return _GeneratedPlayWrappers(
        color_ids=_wrap(workspace, functions, color_ids, prefix, family("path_family_colour")),
        rainbow_ids=_wrap(workspace, functions, rainbow_ids, prefix, family("path_family_colour")),
        panel_ids=_wrap(workspace, functions, panels, prefix, family("path_family_pixels")),
        movement_ids=_wrap(workspace, functions, movement_ids, prefix, family("path_family_heads")),
        gobo_ids=_wrap(workspace, functions, gobo_ids, prefix, gobos),
        prism_ids=_wrap(workspace, functions, prism_ids, prefix, family("path_prism")),
    )


def _spread(function_ids: Sequence[int], count: int) -> list[int]:
    """Pick a stable, evenly distributed subset without repeating an effect."""
    if len(function_ids) <= count:
        return list(function_ids)
    return [
        function_ids[round(index * (len(function_ids) - 1) / (count - 1))] for index in range(count)
    ]


def _wrap(
    workspace: Workspace,
    functions: dict[int, etree._Element],
    function_ids: Sequence[int],
    prefix: str,
    path: str,
) -> list[int]:
    """Build one monitored Collection per unique original function."""
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
                [original_id],
                path=path,
            )
        )
        wrappers.append(function_id)
    return wrappers
