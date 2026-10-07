"""Parse a QLC+ fixture definition (.qxf) into channels and modes.

A definition is fixture-type knowledge: the channels a model exposes (each with a
role) and the modes that order a subset of them. A patched fixture in a workspace
only records manufacturer/model/mode, so this is where channel roles come from.
"""

from pathlib import Path
from typing import cast

from lxml import etree

from .capability import Capability
from .channel import Channel
from .dimensions import Dimensions
from .find_local import find_local
from .findall_local import findall_local
from .fixture_definition import FixtureDefinition
from .iter_local import iter_local
from .optics_of import optics_of
from .role_of import role_of
from .text_of import text_of


def load_definition(path: str | Path) -> FixtureDefinition:
    root = etree.parse(str(path)).getroot()

    manufacturer = text_of(find_local(root, "Manufacturer"))
    model = text_of(find_local(root, "Model"))
    fixture_type = text_of(find_local(root, "Type"))

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
                resource=cap.attrib.get("Res1", ""),
                resource2=cap.attrib.get("Res2", ""),
            )
            for cap in findall_local(ch, "Capability")
            if "Min" in cap.attrib and "Max" in cap.attrib
        )
        channels[name] = Channel(
            name=name,
            role=role,
            capabilities=capabilities,
            group=group or "",
        )

    modes: dict[str, list[str]] = {}
    heads: dict[str, tuple[tuple[int, ...], ...]] = {}
    for mode in iter_local(root, "Mode"):
        ordered = sorted(
            ((int(c.attrib["Number"]), c.text) for c in findall_local(mode, "Channel")),
            key=lambda pair: pair[0],
        )
        mode_name = cast(str, mode.attrib["Name"])
        modes[mode_name] = [cast(str, name) for _, name in ordered]
        heads[mode_name] = tuple(
            tuple(
                int(channel.text)
                for channel in findall_local(head, "Channel")
                if channel.text and channel.text.strip().isdigit()
            )
            for head in findall_local(mode, "Head")
        )

    physical = find_local(root, "Physical")
    size = find_local(physical, "Dimensions") if physical is not None else None
    dimensions = (
        Dimensions(
            width=float(size.attrib.get("Width", 0)),
            height=float(size.attrib.get("Height", 0)),
            depth=float(size.attrib.get("Depth", 0)),
        )
        if size is not None
        else None
    )
    optics = optics_of(physical) if physical is not None else None

    return FixtureDefinition(
        manufacturer=manufacturer,
        model=model,
        fixture_type=fixture_type,
        dimensions=dimensions,
        channels=channels,
        modes=modes,
        heads=heads,
        optics=optics,
    )
