"""Parse a QLC+ fixture definition (.qxf) into channels and modes.

A definition is fixture-type knowledge: the channels a model exposes (each with a
role) and the modes that order a subset of them. A patched fixture in a workspace
only records manufacturer/model/mode, so this is where channel roles come from.
"""

from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from .roles import role_of
from .xmlutil import find_local, findall_local, iter_local


@dataclass(frozen=True)
class Channel:
    name: str
    role: str | None


@dataclass(frozen=True)
class FixtureDefinition:
    manufacturer: str
    model: str
    # channel name -> Channel
    channels: dict[str, Channel]
    # mode name -> ordered list of channel names
    modes: dict[str, list[str]]

    def mode_roles(self, mode: str) -> list[str | None]:
        """Roles in channel order for a mode, index-aligned with DMX offset."""
        return [self.channels[c].role for c in self.modes[mode]]


def load_definition(path: str | Path) -> FixtureDefinition:
    root = etree.parse(str(path)).getroot()

    manufacturer = _text(find_local(root, "Manufacturer"))
    model = _text(find_local(root, "Model"))

    channels: dict[str, Channel] = {}
    for ch in iter_local(root, "Channel"):
        name = ch.attrib.get("Name")
        if name is None:  # <Channel Number=..> refs inside <Mode> have no Name
            continue
        group_el = find_local(ch, "Group")
        group = group_el.text if group_el is not None else None
        role = role_of(ch.attrib.get("Preset"), group, name)
        channels[name] = Channel(name=name, role=role)

    modes: dict[str, list[str]] = {}
    for mode in iter_local(root, "Mode"):
        ordered = sorted(
            (
                (int(c.attrib["Number"]), c.text)
                for c in findall_local(mode, "Channel")
            ),
            key=lambda pair: pair[0],
        )
        modes[mode.attrib["Name"]] = [name for _, name in ordered]

    return FixtureDefinition(
        manufacturer=manufacturer,
        model=model,
        channels=channels,
        modes=modes,
    )


def _text(element: etree._Element | None) -> str:
    return (element.text or "").strip() if element is not None else ""
