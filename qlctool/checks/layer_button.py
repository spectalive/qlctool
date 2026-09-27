"""One Toggle button of a latched layer: its function and its own widget."""

from dataclasses import dataclass

from lxml import etree


@dataclass(frozen=True)
class LayerButton:
    caption: str
    function_id: int
    widget: etree._Element
