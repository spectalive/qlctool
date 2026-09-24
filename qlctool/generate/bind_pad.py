"""Bind one console widget to the pad, when the pad has a control for it."""

from collections.abc import Mapping

from lxml import etree

from ..vc.input_source import build_input_source


def bind_pad(
    widget: etree._Element, bindings: Mapping[str, int], name: str, source_id: int = 0
) -> None:
    """Append the `<Input>` for `name`'s pad control; nothing when there is no pad or no control."""
    channel = bindings.get(name)
    if channel is not None:
        build_input_source(widget, channel, source_id=source_id)
