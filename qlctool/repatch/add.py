"""Patch a new fixture into a workspace.

Channel count comes from the fixture definition's mode rather than the caller,
so a patch entry can never claim a width the fixture does not have - that is the
mismatch that silently shifts every fixture after it on the universe.
"""

from lxml import etree

from ..constants import QLC_NS
from ..fixture import patched_fixtures
from ..library import FixtureLibrary
from ..patch_conflicts import patch_conflicts
from ..xmlutil import find_local, findall_local


def add_fixture(
    root: etree._Element,
    library: FixtureLibrary,
    manufacturer: str,
    model: str,
    mode: str,
    universe: int,
    address: int,
    name: str | None = None,
    allow_overlap: bool = False,
) -> int:
    """Patch a fixture and return its new ID.

    address is 0-based, as the file stores it. Raises when the model or mode is
    unknown to the library, or when the placement overlaps an existing fixture.
    """
    definition = library.get(manufacturer, model)
    if definition is None:
        raise KeyError(f"library has no definition for {manufacturer}/{model}")
    if mode not in definition.modes:
        raise KeyError(
            f"{manufacturer}/{model} has no mode {mode!r} "
            f"(modes: {sorted(definition.modes)})"
        )

    engine = find_local(root, "Engine")
    if engine is None:
        raise ValueError("workspace has no <Engine> element")

    fixture_id = _next_fixture_id(root)
    element = etree.Element(f"{{{QLC_NS}}}Fixture")
    _child(element, "Manufacturer", manufacturer)
    _child(element, "Model", model)
    _child(element, "Mode", mode)
    _child(element, "ID", fixture_id)
    _child(element, "Name", name if name is not None else f"{model} #{fixture_id}")
    _child(element, "Universe", universe)
    _child(element, "Address", address)
    _child(element, "Channels", len(definition.modes[mode]))

    # Keep patch entries together: after the last existing one, else at the top
    # of the Engine, which is where QLC+ writes them.
    existing = [
        e for e in findall_local(engine, "Fixture")
        if find_local(e, "Channels") is not None
    ]
    if existing:
        existing[-1].addnext(element)
    else:
        engine.insert(0, element)

    introduced = [
        conflict for conflict in patch_conflicts(root)
        if fixture_id in (conflict.first.fixture_id, conflict.second.fixture_id)
    ]
    if introduced and not allow_overlap:
        engine.remove(element)
        raise ValueError(
            "patch would overlap: "
            + "; ".join(conflict.describe() for conflict in introduced)
        )
    return fixture_id


def _next_fixture_id(root: etree._Element) -> int:
    ids = [f.fixture_id for f in patched_fixtures(root)]
    return max(ids) + 1 if ids else 0


def _child(parent: etree._Element, name: str, value: object) -> None:
    element = etree.SubElement(parent, f"{{{QLC_NS}}}{name}")
    element.text = str(value)
