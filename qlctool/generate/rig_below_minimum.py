"""What a patch lacks of the smallest rig `newshow` builds a show for.

2026-09-25, Plan C final review: a pars-only patch stopped `newshow` with a
traceback from the movement generator ("no fixture in this workspace has both
pan and tilt"), a washes-only one with a traceback from the dimmer chases, and
a patch with no fixture group built a show `check` then flagged. The minimum
is what those generators require and no more: some fixture with pan and tilt,
some fixture the dimmer chases keep, and one fixture group. It is asked here,
once, before any generator runs.

The first version of this unit asked for one fixture with pan, tilt and a
dimmer together, and refused six PC-64 pars beside two MiN Wash heads, a rig
that builds (294 functions). The dimmer test is therefore the chase's own:
a fader dimmer (`fader_dimmed`) on a fixture that is neither in a pixel group
(`is_pixel_group`, whose matrix owns its intensity) nor running programmes of
its own (`all_self_animating`). Asking every group, not only those that get a
matrix, can only make this stricter than the build, never looser.

The question is put to the capability layer the generators use, never to a
model name.
"""

from lxml import etree

from .. import roles
from ..capabilities_of import capabilities_of
from ..fixture_group import fixture_groups
from ..library import FixtureLibrary
from ..names.names import Names
from .all_self_animating import all_self_animating
from .fader_dimmed import fader_dimmed
from .is_pixel_group import is_pixel_group


def rig_below_minimum(root: etree._Element, library: FixtureLibrary, names: Names) -> list[str]:
    """Each missing part of the minimum, in the show's words; empty when the rig meets it."""
    caps = capabilities_of(root, library)
    groups = fixture_groups(root)
    pixels = {
        fixture_id
        for group in groups
        if is_pixel_group(caps, group.fixture_ids)
        for fixture_id in group.fixture_ids
    }
    missing = []
    if not any(c.has_role(roles.PAN) and c.has_role(roles.TILT) for c in caps):
        missing.append(names.display("rig_needs_pan_tilt"))
    if not any(
        fader_dimmed(c)
        and c.fixture.fixture_id not in pixels
        and not all_self_animating(caps, (c.fixture.fixture_id,))
        for c in caps
    ):
        missing.append(names.display("rig_needs_dimmer"))
    if not groups:
        missing.append(names.display("rig_needs_fixture_group"))
    return missing
