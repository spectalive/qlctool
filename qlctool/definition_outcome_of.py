"""Ask the library about one patched fixture, once."""

from .definition_outcome import DefinitionOutcome
from .fixture import PatchedFixture
from .library import FixtureLibrary


def definition_outcome_of(fixture: PatchedFixture, library: FixtureLibrary) -> DefinitionOutcome:
    """The fixture's model definition, if any, beside the mode it is patched in."""
    return DefinitionOutcome(library.get(fixture.manufacturer, fixture.model), fixture.mode)
