"""One prism accent scene: the selected beams inserted, the rest parked."""

from .. import roles
from ..fixture_capabilities import FixtureCapabilities
from ..functions.scene import build_scene
from ..names.names import Names
from ..next_function_id import next_function_id
from ..workspace import Workspace
from .inserted_prism import inserted_prism
from .parked_prism import parked_prism


def prism_scene(
    workspace: Workspace,
    beams: list[FixtureCapabilities],
    vocabulary: Names,
    name: str,
    selected: set[int],
) -> int:
    values: dict[int, list[tuple[int, int]]] = {}
    for index, beam in enumerate(beams):
        wheel = beam.wheel_for_role(roles.PRISM)
        if wheel is None:
            raise ValueError("a prism fixture has no prism wheel")
        offset, positions = wheel
        inserted = inserted_prism(positions)
        parked = parked_prism(positions)
        values[beam.fixture.fixture_id] = [
            (offset, inserted.middle if index in selected else parked.middle)
        ]

    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_scene(
            function_id,
            vocabulary.render("prism_subset", subset=name),
            values,
            path=vocabulary.display("path_prisms"),
        )
    )
    return function_id
