"""The show as a graph: what starts what, and what runs at the same instant.

Every question worth asking about a show is a question about simultaneity. Two
functions that never run together cannot fight over a channel; two that always
do will fight over every channel they share. QLC+ writes that distinction into
the function types themselves:

- a **Collection** starts all its members at once, so its members are
  concurrent with each other;
- a **Chaser** plays its steps one after another, so its steps are alternatives
  and never concurrent - though the chaser as a whole is concurrent with
  whatever its own parent started beside it.

So the reach of a function - every channel it can drive through anything it
starts, at any step - is the right unit. If two concurrent members both reach
the same channel, the collision happens: at some step of some chaser, both are
writing it. That is how "two colour beds on one bar" is found without
simulating the night.
"""

from dataclasses import dataclass, field

from lxml import etree

from ..capability import FixtureCapabilities
from ..fixture_group import fixture_groups
from ..xmlutil import find_local, findall_local, localname
from .driven_channels import Driven, driven_channels
from .freeze_driven import freeze_driven
from .read_only_driven import ReadOnlyDriven

BRANCHING = ("Chaser", "Collection", "Sequence")
CONCURRENT = "Collection"


@dataclass(frozen=True)
class ShowGraph:
    """Every function in a workspace, indexed the way the checks ask for it."""

    functions: dict[int, etree._Element] = field(default_factory=dict)
    members: dict[int, tuple[int, ...]] = field(default_factory=dict)
    capabilities: dict[int, FixtureCapabilities] = field(default_factory=dict)
    # group id -> the (width, height) an RGBMatrix paints across. The grid, not
    # the head count: how long one pass of a script takes depends on it.
    grids: dict[int, tuple[int, int]] = field(default_factory=dict)
    # What each leaf drives, parsed once. A show is immutable while it is
    # checked, and the instant rules ask the same question of the same scene
    # hundreds of thousands of times: without this, one pass of every rule
    # re-parsed the FixtureVal text 620 951 times and took 11,5 s, which made
    # the suite 19 minutes long (2026-09-22). Keyed by the groups the matrices
    # are read against, because a matrix drives nothing outside its group.
    # Read-only (`freeze_driven`): 34 rules share these, and one that wrote
    # into what it was handed would change every later rule's answer.
    driven_cache: dict[tuple[object, ...], ReadOnlyDriven] = field(
        default_factory=dict, repr=False, compare=False
    )
    # And what each function reaches, for the same reason (`reach`).
    reach_cache: dict[tuple[object, ...], Driven] = field(
        default_factory=dict, repr=False, compare=False
    )
    # What each function starts, transitively: asked 36 000 times per pass.
    descendants_cache: dict[int, frozenset[int]] = field(
        default_factory=dict, repr=False, compare=False
    )
    # The hashable form of a `groups` mapping, by the object's identity, which
    # is kept alive alongside so the identity cannot be reused.
    groups_keys: dict[int, tuple[object, tuple[object, ...]]] = field(
        default_factory=dict, repr=False, compare=False
    )

    def name(self, function_id: int) -> str:
        function = self.functions.get(function_id)
        return (
            function.attrib.get("Name", str(function_id))
            if function is not None
            else str(function_id)
        )

    def kind(self, function_id: int) -> str:
        function = self.functions.get(function_id)
        return function.attrib.get("Type", "") if function is not None else ""

    def descendants(self, function_id: int) -> frozenset[int]:
        """Every function reachable from this one, itself included."""
        cached = self.descendants_cache.get(function_id)
        if cached is not None:
            return cached
        seen: set[int] = set()
        stack = [function_id]
        while stack:
            current = stack.pop()
            if current in seen or current not in self.functions:
                continue
            seen.add(current)
            stack.extend(self.members.get(current, ()))
        cached = frozenset(seen)
        self.descendants_cache[function_id] = cached
        return cached

    def groups_key(self, groups: dict[int, tuple[int, ...]]) -> tuple[object, ...]:
        """A hashable stand-in for one `groups` mapping, built once per mapping."""
        if not groups:
            # Every `{}` a rule passes is a new object: keyed by identity, each
            # call grew this table by one (round G review, 2026-09-26).
            return ()
        entry = self.groups_keys.get(id(groups))
        if entry is None or entry[0] is not groups:
            entry = (groups, tuple(sorted(groups.items())))
            self.groups_keys[id(groups)] = entry
        return entry[1]

    def driven(self, function_id: int, groups: dict[int, tuple[int, ...]]) -> ReadOnlyDriven:
        """Every channel one leaf drives, parsed once per graph."""
        key = (function_id, self.groups_key(groups))
        cached = self.driven_cache.get(key)
        if cached is None:
            function = self.functions[function_id]
            cached = freeze_driven(driven_channels(function, self.capabilities, groups))
            self.driven_cache[key] = cached
        return cached

    def driven_of(
        self, function: etree._Element, groups: dict[int, tuple[int, ...]]
    ) -> ReadOnlyDriven:
        """`driven` for a function element, parsed once when it is this graph's own.

        Most rules walk the graph's functions and asked `driven_channels`
        directly, re-parsing every scene once per rule (2026-09-26, round G).
        """
        identifier = function.get("ID")
        if identifier is None or self.functions.get(int(identifier)) is not function:
            return freeze_driven(driven_channels(function, self.capabilities, groups))
        return self.driven(int(identifier), groups)

    def collections(self, function_id: int) -> list[int]:
        """The Collections reachable from here - every point of simultaneity."""
        return [fid for fid in self.descendants(function_id) if self.kind(fid) == CONCURRENT]


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
    return ShowGraph(
        functions=functions,
        members=members,
        capabilities={c.fixture.fixture_id: c for c in capabilities},
        grids={group.group_id: (group.width, group.height) for group in fixture_groups(root)},
    )


def group_fixtures(root: etree._Element) -> dict[int, tuple[int, ...]]:
    return {group.group_id: group.fixture_ids for group in fixture_groups(root)}


def reach(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int,
    kinds: tuple[str, ...] | None = None,
) -> Driven:
    """Every channel this function can drive, through anything it starts.

    `kinds` restricts which leaf function types count - "what does this look
    *state* about colour" is a question about its Scenes, since a matrix paints
    a group's pixels and can say nothing about a fixture that has none.

    Values merge by the highest, because DMX does: QLC+ mixes intensity
    channels HTP, so what the room sees from two sources on one channel is the
    louder of them. `None` - an effect driving a channel to a value nobody can
    predict - beats any number, since it may be anything at any moment.

    Memoised on the graph, and handed out as a copy so a caller may write into
    it: the rules ask this of the same functions some sixteen thousand times
    per pass (2026-09-22).
    """
    key = (function_id, kinds, graph.groups_key(groups))
    cached = graph.reach_cache.get(key)
    if cached is None:
        cached = _reach(graph, groups, function_id, kinds)
        graph.reach_cache[key] = cached
    return {fixture_id: dict(pairs) for fixture_id, pairs in cached.items()}


def _reach(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    function_id: int,
    kinds: tuple[str, ...] | None,
) -> Driven:
    merged: Driven = {}
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None:
            continue
        if kinds is not None and function.attrib.get("Type") not in kinds:
            continue
        for fixture_id, pairs in graph.driven(member, groups).items():
            target = merged.setdefault(fixture_id, {})
            for offset, value in pairs.items():
                target[offset] = _higher(target.get(offset, 0), value)
    return merged


def merge(first: Driven, second: Driven) -> Driven:
    """Two functions running at once, mixed the way the room mixes them."""
    merged: Driven = {fixture: dict(pairs) for fixture, pairs in first.items()}
    for fixture_id, pairs in second.items():
        target = merged.setdefault(fixture_id, {})
        for offset, value in pairs.items():
            target[offset] = _higher(target.get(offset, 0), value)
    return merged


def _higher(current: int | None, incoming: int | None) -> int | None:
    """HTP, with None - an unpredictable effect - above every number."""
    if current is None or incoming is None:
        return None
    return max(current, incoming)


def lit(value: int | None) -> bool:
    """Whether a channel is doing something: unknown counts as doing something."""
    return value is None or value > 0
