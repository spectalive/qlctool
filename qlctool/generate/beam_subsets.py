"""Restore the per-beam accents that the hand-built console made reachable.

The generated prism wheel already owns the all-beams on and off positions, but
an operator also needs to pick individual beams and mirrored pairs. Those
looks cannot be inferred from fixture names or fixed channel numbers: the
fixture definition says which patched fixtures have a prism, where that wheel
lives, and which neighbouring Colour channel is the continuous half-colour
effect rather than the colour wheel itself.
"""

from dataclasses import dataclass, field

from .. import roles
from ..capabilities_of import capabilities_of
from ..definition import Capability
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace

_SUBSETS = (
    ("1", (0,)),
    ("2", (1,)),
    ("3", (2,)),
    ("4", (3,)),
    ("1 y 3", (0, 2)),
    ("2 y 4", (1, 3)),
)


@dataclass(frozen=True)
class GeneratedBeamSubsets:
    prism_scene_ids: list[int] = field(default_factory=list)
    multicolor_scene_ids: list[int] = field(default_factory=list)


def generate_beam_subsets(
    workspace: Workspace,
    library: FixtureLibrary,
) -> GeneratedBeamSubsets:
    """Build address-ordered single-beam and mirrored-pair accent scenes."""
    beams = sorted(
        (
            capability
            for capability in capabilities_of(workspace.root, library)
            if not capability.is_smoke and capability.has_role(roles.PRISM)
        ),
        key=lambda capability: capability.fixture.address,
    )
    if not beams:
        return GeneratedBeamSubsets()

    subsets = [(name, indices) for name, indices in _SUBSETS if max(indices) < len(beams)]
    prism_scene_ids = [
        _prism_scene(workspace, beams, name, set(indices)) for name, indices in subsets
    ]

    multicolor_offsets = [_multicolor_offset(beam) for beam in beams]
    if any(offset is None for offset in multicolor_offsets):
        return GeneratedBeamSubsets(prism_scene_ids=prism_scene_ids)

    multicolor_scene_ids = [
        _multicolor_scene(
            workspace,
            beams,
            multicolor_offsets,
            "Todas",
            set(range(len(beams))),
        ),
        _multicolor_scene(workspace, beams, multicolor_offsets, "Off", set()),
    ]
    multicolor_scene_ids.extend(
        _multicolor_scene(workspace, beams, multicolor_offsets, name, set(indices))
        for name, indices in subsets
    )
    return GeneratedBeamSubsets(
        prism_scene_ids=prism_scene_ids,
        multicolor_scene_ids=multicolor_scene_ids,
    )


def _prism_scene(workspace, beams, name: str, selected: set[int]) -> int:
    values = {}
    for index, beam in enumerate(beams):
        wheel = beam.wheel_for_role(roles.PRISM)
        if wheel is None:
            raise ValueError("a prism fixture has no prism wheel")
        offset, positions = wheel
        inserted = _inserted_prism(positions)
        parked = _parked_prism(positions)
        values[beam.fixture.fixture_id] = [
            (offset, inserted.middle if index in selected else parked.middle)
        ]

    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, f"Prisma - {name}", values, path="Prismas"))
    return function_id


def _inserted_prism(positions: tuple[Capability, ...]) -> Capability:
    for position in positions:
        preset = position.preset.lower()
        name = position.name.lower()
        if ("prism" in preset and preset.endswith("on")) or "insert" in name:
            return position
    raise ValueError("a prism wheel has no labelled inserted position")


def _parked_prism(positions: tuple[Capability, ...]) -> Capability:
    for position in positions:
        preset = position.preset.lower()
        if ("prism" in preset and preset.endswith("off")) or position.name.lower() == "none":
            return position
    if positions:
        return positions[0]
    raise ValueError("a prism wheel has no positions")


def _multicolor_offset(beam) -> int | None:
    wheel = beam.wheel_for_role(roles.COLOR_MACRO)
    if wheel is None:
        return None
    wheel_offset, _ = wheel
    for offset in beam.offsets_for_role(roles.COLOR_MACRO):
        if offset == wheel_offset:
            continue
        ranges = beam.capabilities_by_offset[offset]
        if len(ranges) == 1 and ranges[0].minimum == 0 and ranges[0].maximum == 255:
            return offset
    return None


def _multicolor_scene(
    workspace,
    beams,
    offsets: list[int | None],
    name: str,
    selected: set[int],
) -> int:
    # This channel is one continuous 0-255 range, so its endpoints are the
    # honest off and full half-colour values rather than guessed positions.
    values = {
        beam.fixture.fixture_id: [(offset, 255 if index in selected else 0)]
        for index, (beam, offset) in enumerate(zip(beams, offsets))
        if offset is not None
    }
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_scene(function_id, f"MultiColor - {name}", values, path="MultiColor")
    )
    return function_id
