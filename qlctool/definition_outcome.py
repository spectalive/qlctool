"""What the library holds for one patched fixture: its model's definition, and its mode.

A fixture resolves when the library knows its model *and* that definition has
the mode it is patched in. The two ways of not resolving need different
advice - an unknown model wants a fixture folder, a known model in a missing
mode wants a repatch - so the distinction lives here, once, for the warning,
the check and the `newshow` refusal to share (2026-09-25 review).
"""

from dataclasses import dataclass

from .definition import FixtureDefinition


@dataclass(frozen=True)
class DefinitionOutcome:
    # The model's definition, whether or not it has the patched mode.
    definition: FixtureDefinition | None
    mode: str

    @property
    def model_known(self) -> bool:
        """The library has a definition for the fixture's model."""
        return self.definition is not None

    @property
    def resolved(self) -> bool:
        """The definition exists and carries the patched mode."""
        return self.definition is not None and self.mode in self.definition.modes
