"""Whether a workspace is bound to a MIDI pad at all."""

from lxml import etree

from ..checks.pad_bindings import pad_bindings


def smc_pad_applies(root: etree._Element) -> bool:
    """True when any widget listens on an input channel - what `rule_pad_input` checks."""
    return bool(pad_bindings(root))
