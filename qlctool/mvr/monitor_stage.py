"""The stage grid and every placed fixture, as `monitor_items` reads them."""

from dataclasses import dataclass

from ..monitor_node import MonitorItem


@dataclass(frozen=True)
class MonitorStage:
    # Width, height, depth of the stage grid in millimetres.
    stage: tuple[float, float, float]
    items: list[MonitorItem]
