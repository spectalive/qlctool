"""Build the show graph from a workspace's Engine."""

from lxml import etree

from ..find_local import find_local
from ..findall_local import findall_local
from ..fixture_capabilities import FixtureCapabilities
from ..fixture_groups import fixture_groups
from ..xmlutil import localname
from .htp_offsets import htp_offsets
from .show_graph import BRANCHING, ShowGraph


def build_show_graph(root: etree._Element, capabilities: list[FixtureCapabilities]) -> ShowGraph:
    engine = find_local(root, "Engine")
    functions: dict[int, etree._Element] = {}
    members: dict[int, tuple[int, ...]] = {}
    for element in engine if engine is not None else ():
        if localname(element) != "Function" or "ID" not in element.attrib:
            continue
        function_id = int(element.attrib["ID"])
        functions[function_id] = element
        if element.attrib.get("Type") in BRANCHING:
            members[function_id] = tuple(
                int(step.text)
                for step in findall_local(element, "Step")
                if step.text and step.text.strip().isdigit()
            )
    by_id = {c.fixture.fixture_id: c for c in capabilities}
    return ShowGraph(
        functions=functions,
        members=members,
        capabilities=by_id,
        htp=htp_offsets(root, by_id),
        grids={group.group_id: (group.width, group.height) for group in fixture_groups(root)},
    )
