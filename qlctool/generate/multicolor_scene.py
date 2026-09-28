"""One MultiColor accent scene: the selected beams' half-colour channel at full."""

from ..fixture_capabilities import FixtureCapabilities
from ..functions.build_scene import build_scene
from ..next_function_id import next_function_id
from ..workspace import Workspace


def multicolor_scene(
    workspace: Workspace,
    beams: list[FixtureCapabilities],
    offsets: list[int | None],
    name: str,
    selected: set[int],
) -> int:
    # This channel is one continuous 0-255 range, so its endpoints are the
    # honest off and full half-colour values rather than guessed positions.
    values = {
        beam.fixture.fixture_id: [(offset, 255 if index in selected else 0)]
        for index, (beam, offset) in enumerate(zip(beams, offsets, strict=True))
        if offset is not None
    }
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_scene(function_id, f"MultiColor - {name}", values, path="MultiColor")
    )
    return function_id
