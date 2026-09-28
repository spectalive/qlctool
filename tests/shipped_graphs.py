"""(name, graph, groups) of every shipped show, built once per call."""

from named_show import named_show as _show

from qlctool.capabilities_of import capabilities_of
from qlctool.checks.build_show_graph import build_show_graph
from qlctool.checks.group_fixtures import group_fixtures

SHOWS = ("Vibra.qxw", "Vibra-beats.qxw", "Vibra-split.qxw")


def shipped_graphs(library):
    """(name, graph, groups) of every shipped show, built once per call."""
    for name in SHOWS:
        workspace = _show(name)
        yield (
            name,
            build_show_graph(workspace.root, capabilities_of(workspace.root, library)),
            group_fixtures(workspace.root),
        )
