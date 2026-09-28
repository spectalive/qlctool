"""A fixture as patched in a workspace: identity plus its DMX placement.

This reads only what the <Fixture> node stores - manufacturer, model, mode,
universe, address, channel count. Channel roles are not here; they come from the
matching definition via the capability layer, because the workspace does not
record them.
"""

from dataclasses import dataclass

from lxml import etree

from .find_local import find_local
from .text_of import text_of


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
            fixture_id=int(text_of(find_local(element, "ID"))),
            manufacturer=text_of(find_local(element, "Manufacturer")),
            model=text_of(find_local(element, "Model")),
            mode=text_of(find_local(element, "Mode")),
            universe=int(text_of(find_local(element, "Universe")) or "0"),
            address=int(text_of(find_local(element, "Address")) or "0"),
            channels=int(text_of(find_local(element, "Channels")) or "0"),
            name=text_of(find_local(element, "Name")),
        )
