"""The intensity base each energy level stands on - and nothing else owns.

Colour and intensity used to travel together: every colour scene drove every
dimmer to 255, which worked until the show wanted a quiet level. Intensity
mixes HTP - the highest write wins - so "Ambiente with the dimmers low" was
impossible while the colour wheel held them at full all night (Codex review,
2026-08-27). The split is the fix: colour scenes state colour, and each level
carries exactly one of these scenes as its intensity owner. A level change is
then really a brightness change, because nobody else is bidding.

Covered is everything with an intensity *path* the toolkit can open - a dimmer
channel, or a shutter whose open range the definition labels (the MiN Wash has
no dimmer role at all; its light lives behind the shutter channel). Excluded
are the fixtures somebody else owns: smoke, and the pixel groups whose
intensity is `Pixeles ON` - two owners at different values is the exact bug
this exists to end.
"""

from collections.abc import Sequence

from ..color_wheel_pairs import WHEEL_NAMES
from ..fixture_capabilities import FixtureCapabilities
from ..names.default_names import default_names
from ..names.names import Names
from ..outside_color_looks import outside_color_looks
from ..workspace import Workspace
from .generated_intensity import GeneratedIntensity
from .intensity_scene import FULL_LEVEL, intensity_scene

# The quiet level's dimmer: visibly down from full, nowhere near dark. A first
# guess for the venue, like the level holds themselves. It reaches every dimmer
# that is a fader; the ones that are a blade go to full instead.
AMBIENT_LEVEL = 110


def generate_energy_intensity(
    workspace: Workspace,
    capabilities: list[FixtureCapabilities],
    exclude_fixture_ids: Sequence[int] = (),
    names: Names | None = None,
    look_colours: Sequence[str] = tuple(WHEEL_NAMES),
) -> GeneratedIntensity:
    """Two scenes: the rig's dimmers low, and at full - shutters open in both.

    `look_colours` are the colours the show's looks request (its palette): a
    head whose wheel shows none of them is parked here (`outside_color_looks`).
    """
    vocabulary = default_names() if names is None else names
    path = vocabulary.display("path_levels")
    excluded = set(exclude_fixture_ids)
    outside = {
        c.fixture.fixture_id for c in capabilities if outside_color_looks(c, look_colours, names)
    }
    ambient = intensity_scene(
        workspace,
        capabilities,
        excluded,
        vocabulary.display("ambient_intensity"),
        AMBIENT_LEVEL,
        path,
        outside,
    )
    full = intensity_scene(
        workspace,
        capabilities,
        excluded,
        vocabulary.display("full_intensity"),
        FULL_LEVEL,
        path,
        outside,
    )
    return GeneratedIntensity(ambient_id=ambient, full_id=full)
