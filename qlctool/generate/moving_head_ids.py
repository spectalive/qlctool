"""Fixture IDs that can be driven by an EFX: they have both pan and tilt."""

from .. import roles
from ..capabilities_of import capabilities_of
from ..fixture_library import FixtureLibrary
from ..workspace import Workspace


def moving_head_ids(workspace: Workspace, library: FixtureLibrary) -> list[int]:
    return [
        caps.fixture.fixture_id
        for caps in capabilities_of(workspace.root, library)
        if caps.has_role(roles.PAN) and caps.has_role(roles.TILT)
    ]
