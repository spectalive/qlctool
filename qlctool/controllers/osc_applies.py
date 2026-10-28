"""Whether a workspace listens to an OSC surface at all."""

from lxml import etree

from ..osc_input_patch import osc_input_patch


def osc_applies(root: etree._Element) -> bool:
    """True when a universe patches QLC+'s OSC plugin as its input."""
    return osc_input_patch(root) is not None
