"""A fixture as patched in a workspace: identity plus its DMX placement.

This reads only what the <Fixture> node stores - manufacturer, model, mode,
universe, address, channel count. Channel roles are not here; they come from the
matching definition via the capability layer, because the workspace does not
record them.
"""

from dataclasses import dataclass

from lxml import etree

from .xmlutil import find_local, iter_local


@dataclass(frozen=True)
class PatchedFixture:
    fixture_id: int
    manufacturer: str
    model: str
    mode: str
    universe: int
    address: int  # 0-based, as stored
    channels: int
    name: str

    @classmethod
    def from_element(cls, element: etree._Element) -> "PatchedFixture":
        return cls(
            fixture_id=int(_text(find_local(element, "ID"))),
            manufacturer=_text(find_local(element, "Manufacturer")),
            model=_text(find_local(element, "Model")),
            mode=_text(find_local(element, "Mode")),
            universe=int(_text(find_local(element, "Universe")) or "0"),
            address=int(_text(find_local(element, "Address")) or "0"),
            channels=int(_text(find_local(element, "Channels")) or "0"),
            name=_text(find_local(element, "Name")),
        )


def patched_fixtures(root: etree._Element) -> list[PatchedFixture]:
    """All patched fixtures in a workspace, in document order.

    Filters to <Fixture> nodes that carry a <Channels> child, so the fixture-ID
    references QLC+ writes inside scenes and groups are not mistaken for patched
    fixtures.
    """
    result = []
    for element in iter_local(root, "Fixture"):
        if find_local(element, "Channels") is None:
            continue
        result.append(PatchedFixture.from_element(element))
    return result


def _text(element: etree._Element | None) -> str:
    return (element.text or "").strip() if element is not None else ""
