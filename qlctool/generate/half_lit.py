"""Every other fixture at full, the rest at zero.

The lit half opens its shutter too - a beam at full dimmer behind a closed
shutter shows nothing. The dark half is left alone: its dimmer at zero is
already black, and closing the shutter as well only adds a second thing to
reopen.
"""

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from ..functions.scene import build_scene
from ..names.names import Names
from ..next_function_id import next_function_id
from ..shutter_open import shutter_open_pairs
from ..workspace import Workspace
from ..zoom_wide_pairs import zoom_wide_pairs


def half_lit(
    workspace: Workspace,
    dimmable: list[FixtureCapabilities],
    remainder: int,
    path: str,
    vocabulary: Names,
) -> int:
    values: dict[int, list[tuple[int, int]]] = {}
    for index, capability in enumerate(dimmable):
        lit = index % 2 == remainder
        pairs = [
            (offset, 255 if lit else 0) for offset in capability.offsets_for_role(roles.DIMMER)
        ]
        if lit:
            pairs += shutter_open_pairs(capability)
            pairs += zoom_wide_pairs(capability)
        values[capability.fixture.fixture_id] = pairs
    function_id = next_function_id(workspace.root)
    name = vocabulary.display("dimmer_odd" if remainder else "dimmer_even")
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id
