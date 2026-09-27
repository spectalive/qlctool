"""Restore the per-beam accents that the hand-built console made reachable.

The generated prism wheel already owns the all-beams on and off positions, but
an operator also needs to pick individual beams and mirrored pairs. Those
looks cannot be inferred from fixture names or fixed channel numbers: the
fixture definition says which patched fixtures have a prism, where that wheel
lives, and which neighbouring Colour channel is the continuous half-colour
effect rather than the colour wheel itself.
"""

from .. import roles
from ..capabilities_of import capabilities_of
from ..fixture_library import FixtureLibrary
from ..names.default_names import default_names
from ..names.names import Names
from ..workspace import Workspace
from .generated_beam_subsets import GeneratedBeamSubsets
from .multicolor_offset import multicolor_offset
from .multicolor_scene import multicolor_scene
from .prism_scene import prism_scene

# A single beam is its own number; a pair is named by a catalogue identifier.
_SUBSETS = (
    ("1", (0,)),
    ("2", (1,)),
    ("3", (2,)),
    ("4", (3,)),
    ("subset_odd", (0, 2)),
    ("subset_even", (1, 3)),
)


def generate_beam_subsets(
    workspace: Workspace,
    library: FixtureLibrary,
    names: Names | None = None,
) -> GeneratedBeamSubsets:
    """Build address-ordered single-beam and mirrored-pair accent scenes."""
    vocabulary = default_names() if names is None else names
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

    subsets = [
        (key if key.isdigit() else vocabulary.display(key), indices)
        for key, indices in _SUBSETS
        if max(indices) < len(beams)
    ]
    prism_scene_ids = [
        prism_scene(workspace, beams, vocabulary, name, set(indices)) for name, indices in subsets
    ]

    multicolor_offsets = [multicolor_offset(beam) for beam in beams]
    if any(offset is None for offset in multicolor_offsets):
        return GeneratedBeamSubsets(prism_scene_ids=prism_scene_ids)

    multicolor_scene_ids = [
        multicolor_scene(
            workspace,
            beams,
            multicolor_offsets,
            vocabulary.display("subset_all"),
            set(range(len(beams))),
        ),
        multicolor_scene(workspace, beams, multicolor_offsets, "Off", set()),
    ]
    multicolor_scene_ids.extend(
        multicolor_scene(workspace, beams, multicolor_offsets, name, set(indices))
        for name, indices in subsets
    )
    return GeneratedBeamSubsets(
        prism_scene_ids=prism_scene_ids,
        multicolor_scene_ids=multicolor_scene_ids,
    )
