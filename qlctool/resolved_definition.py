"""The definition a patched fixture's channels can be read from, if there is one.

A fixture resolves when the library knows its model *and* that definition has
the mode it is patched in. Either one missing leaves its channels unreadable:
generators skip it and every rule is blind to it.
"""

from .definition import FixtureDefinition
from .definition_outcome_of import definition_outcome_of
from .fixture import PatchedFixture
from .library import FixtureLibrary


def resolved_definition(
    fixture: PatchedFixture, library: FixtureLibrary
) -> FixtureDefinition | None:
    """The fixture's definition when it carries the patched mode; None otherwise."""
    outcome = definition_outcome_of(fixture, library)
    return outcome.definition if outcome.resolved else None
