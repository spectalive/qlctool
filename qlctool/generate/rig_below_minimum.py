"""What a patch lacks of the smallest rig `newshow` builds a show for.

2026-09-25, Plan C final review: a pars-only patch stopped `newshow` with a
traceback from the movement generator ("no fixture in this workspace has both
pan and tilt"), a washes-only one with a traceback from the dimmer chases, and
a patch with no fixture group built a show `check` then flagged. The README
states the minimum - one pan/tilt fixture with a fader dimmer, one fixture
group - and this is where it is asked, once, before any generator runs.

The question is put to the capability layer the generators use, never to a
model name. A blade dimmer (`stepped_dimmer`) does not count: the dimmer
chases leave it out, so a rig whose only dimmer is one has nothing to chase.
"""

from lxml import etree

from .. import roles
from ..capabilities_of import capabilities_of
from ..fixture_group import fixture_groups
from ..library import FixtureLibrary
from ..names.names import Names
from ..stepped_dimmer import stepped_dimmer_offsets


def rig_below_minimum(root: etree._Element, library: FixtureLibrary, names: Names) -> list[str]:
    """Each missing part of the minimum, in the show's words; empty when the rig meets it."""
    missing = []
    if not any(
        caps.has_role(roles.PAN)
        and caps.has_role(roles.TILT)
        and caps.offsets_for_role(roles.DIMMER)
        and not stepped_dimmer_offsets(caps)
        for caps in capabilities_of(root, library)
    ):
        missing.append(names.display("rig_needs_pan_tilt_dimmer"))
    if not fixture_groups(root):
        missing.append(names.display("rig_needs_fixture_group"))
    return missing
