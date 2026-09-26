"""What a patch lacks of the smallest rig `newshow` builds a show for.

2026-09-25, Plan C final review: a pars-only patch stopped `newshow` with a
traceback from the movement generator ("no fixture in this workspace has both
pan and tilt"), a washes-only one with a traceback from the dimmer chases, and
a patch with no fixture group built a show `check` then flagged. The minimum
was then asked here, once, before any generator ran: a fixture with pan and
tilt, a fixture the dimmer chases keep, and one fixture group.

2026-09-26, round G: the movement and the dimmer chases are optional now.
A rig with nothing that pans and tilts gets no movement, no heads frame and
no aiming pad; a rig with no fader dimmer gets no dimmer chase; the captions
that would promise either choose their variant from the rig
(`tests/test_small_rig.py` builds, checks and validates pars only, washes
only and RGB-only heads). What is left is the one thing every page of the
console is laid out from: a fixture group.

Round G review (2026-09-26): of two fixtures at least. Every model and mode
in the test library was built one, two and four at a time
(`tests/test_every_single_model_rig.py`); a lone fixture failed its own check
in two ways the generator cannot help - the odd/even strobe has no odd half,
and with no two-fixture mix the tap dial re-timed only the colour wheels,
all at one length - while every two- and four-fixture rig passes.

The question is put to the patch, never to a model name.
"""

from lxml import etree

from ..fixture_group import fixture_groups
from ..names.names import Names


def rig_below_minimum(root: etree._Element, names: Names) -> list[str]:
    """Each missing part of the minimum, in the show's words; empty when the rig meets it."""
    if any(len(group.fixture_ids) >= 2 for group in fixture_groups(root)):
        return []
    return [names.display("rig_needs_fixture_group")]
