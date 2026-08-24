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
class Capability:
    """One labelled DMX range of a channel - a gobo, a colour, prism on/off."""

    minimum: int
    maximum: int
    name: str

    @property
    def middle(self) -> int:
        """A value safely inside the range, which is what a scene should send."""
        return (self.minimum + self.maximum) // 2


@dataclass(frozen=True)
class Channel:
    name: str
    role: str | None
    capabilities: tuple[Capability, ...] = ()


@dataclass(frozen=True)
class FixtureDefinition:
    manufacturer: str
    model: str
    # <Type>: Moving Head, Color Changer, Smoke, ... - a smoke machine must
    # never be swept up in a "all dimmers to full" scene.
    fixture_type: str
    # channel name -> Channel
    channels: dict[str, Channel]
    # mode name -> ordered list of channel names
    modes: dict[str, list[str]]

    def mode_roles(self, mode: str) -> list[str | None]:
        """Roles in channel order for a mode, index-aligned with DMX offset."""
        return [self.channels[c].role for c in self.modes[mode]]

    def mode_capabilities(self, mode: str) -> list[tuple[Capability, ...]]:
        """Each offset's labelled ranges, index-aligned with mode_roles."""
        return [self.channels[c].capabilities for c in self.modes[mode]]


def load_definition(path: str | Path) -> FixtureDefinition:
    root = etree.parse(str(path)).getroot()

    manufacturer = _text(find_local(root, "Manufacturer"))
    model = _text(find_local(root, "Model"))
    fixture_type = _text(find_local(root, "Type"))

    channels: dict[str, Channel] = {}
    for ch in iter_local(root, "Channel"):
        name = ch.attrib.get("Name")
        if name is None:  # <Channel Number=..> refs inside <Mode> have no Name
            continue
        group_el = find_local(ch, "Group")
        group = group_el.text if group_el is not None else None
        role = role_of(ch.attrib.get("Preset"), group, name)
        capabilities = tuple(
            Capability(
                minimum=int(cap.attrib["Min"]),
                maximum=int(cap.attrib["Max"]),
                name=(cap.text or "").strip(),
            )
            for cap in findall_local(ch, "Capability")
            if "Min" in cap.attrib and "Max" in cap.attrib
        )
        channels[name] = Channel(name=name, role=role, capabilities=capabilities)

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
        fixture_type=fixture_type,
        channels=channels,
        modes=modes,
    )


def _text(element: etree._Element | None) -> str:
    return (element.text or "").strip() if element is not None else ""
