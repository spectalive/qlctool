"""What `build_wheels` made: the wheels, and how channels and ranges index them."""

from dataclasses import dataclass, field

from pygdtf import Wheel


@dataclass
class WheelPlan:
    wheels: list[Wheel] = field(default_factory=list)
    # channel name -> wheel name
    by_channel: dict[str, str] = field(default_factory=dict)
    # (channel name, capability index) -> 1-based slot index on that wheel
    slot_index: dict[tuple[str, int], int] = field(default_factory=dict)
    # (path on disk, name inside the archive)
    media: list[tuple[str, str]] = field(default_factory=list)
