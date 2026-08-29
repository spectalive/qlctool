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
    # The QLC+ capability preset, "" when the range carries none. This is how a
    # definition states what a range *is* rather than what it is called, which
    # matters for the ranges a generator has to find on its own: which value
    # opens a mechanical shutter, above all.
    preset: str = ""

    @property
    def middle(self) -> int:
        """A value safely inside the range, which is what a scene should send."""
        return (self.minimum + self.maximum) // 2


@dataclass(frozen=True)
class Channel:
    name: str
    role: str | None
    capabilities: tuple[Capability, ...] = ()
    # The QLC+ channel group, verbatim. It is not decoration: QLC+ resets the
    # channels in the Intensity group every cycle and leaves every other group
    # holding its last value (`Universe::processFaders`), which is the whole
    # difference between a Flash that releases and one that latches.
    group: str = ""


@dataclass(frozen=True)
class Dimensions:
    """The fixture's own size in millimetres, as QLC+ draws it."""

    width: float
    height: float
    depth: float


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
    dimensions: Dimensions | None = None

    def mode_roles(self, mode: str) -> list[str | None]:
        """Roles in channel order for a mode, index-aligned with DMX offset."""
        return [self.channels[c].role for c in self.modes[mode]]

    def mode_capabilities(self, mode: str) -> list[tuple[Capability, ...]]:
        """Each offset's labelled ranges, index-aligned with mode_roles."""
        return [self.channels[c].capabilities for c in self.modes[mode]]

    def mode_groups(self, mode: str) -> list[str]:
        """Each offset's QLC+ channel group, index-aligned with mode_roles."""
        return [self.channels[c].group for c in self.modes[mode]]


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
        preset = ch.attrib.get("Preset")
        group_el = find_local(ch, "Group")
        group = group_el.text if group_el is not None else None
        # A channel written as a preset carries no <Group> of its own: QLC+
        # fills it in from the preset (`QLCChannel::setPreset`), and the group
        # is what decides whether QLC+ resets the channel every cycle. Reading
        # it back as empty would say "this latches" about a channel that does
        # not.
        if group is None and preset and preset.startswith("Intensity"):
            group = "Intensity"
        role = role_of(preset, group, name)
        capabilities = tuple(
            Capability(
                minimum=int(cap.attrib["Min"]),
                maximum=int(cap.attrib["Max"]),
                name=(cap.text or "").strip(),
                preset=cap.attrib.get("Preset", ""),
            )
            for cap in findall_local(ch, "Capability")
            if "Min" in cap.attrib and "Max" in cap.attrib
        )
        channels[name] = Channel(
            name=name, role=role, capabilities=capabilities, group=group or "",
        )

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

    physical = find_local(root, "Physical")
    size = find_local(physical, "Dimensions") if physical is not None else None
    dimensions = Dimensions(
        width=float(size.attrib.get("Width", 0)),
        height=float(size.attrib.get("Height", 0)),
        depth=float(size.attrib.get("Depth", 0)),
    ) if size is not None else None

    return FixtureDefinition(
        manufacturer=manufacturer,
        model=model,
        fixture_type=fixture_type,
        dimensions=dimensions,
        channels=channels,
        modes=modes,
    )


def _text(element: etree._Element | None) -> str:
    return (element.text or "").strip() if element is not None else ""
