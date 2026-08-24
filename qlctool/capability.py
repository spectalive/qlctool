"""Resolve a patched fixture's channels to roles, so generators can drive it.

Joins a PatchedFixture (which mode it runs) with its FixtureDefinition (what each
channel does) to answer the one question a scene generator asks: "which channel
offsets carry role X on this fixture?" A role can map to several offsets - an
8-segment RGB bar has eight red channels - so lookups return lists.
"""

from dataclasses import dataclass

from .definition import Capability, FixtureDefinition
from .fixture import PatchedFixture


@dataclass(frozen=True)
class FixtureCapabilities:
    fixture: PatchedFixture
    # channel offset (0-based, within the fixture) -> role or None
    roles_by_offset: list[str | None]
    # the same offsets -> that channel's labelled ranges (gobos, prism, colours)
    capabilities_by_offset: list[tuple[Capability, ...]]

    @classmethod
    def resolve(
        cls, fixture: PatchedFixture, definition: FixtureDefinition
    ) -> "FixtureCapabilities":
        if fixture.mode not in definition.modes:
            raise KeyError(
                f"fixture {fixture.name!r} uses mode {fixture.mode!r} "
                f"not in definition {definition.manufacturer}/{definition.model} "
                f"(modes: {sorted(definition.modes)})"
            )
        return cls(
            fixture=fixture,
            roles_by_offset=definition.mode_roles(fixture.mode),
            capabilities_by_offset=definition.mode_capabilities(fixture.mode),
        )

    def offsets_for_role(self, role: str) -> list[int]:
        return [i for i, r in enumerate(self.roles_by_offset) if r == role]

    def has_role(self, role: str) -> bool:
        return role in self.roles_by_offset

    def capabilities_for_role(self, role: str) -> list[tuple[int, tuple[Capability, ...]]]:
        """(offset, ranges) for every channel carrying this role."""
        return [
            (offset, self.capabilities_by_offset[offset])
            for offset in self.offsets_for_role(role)
        ]

    @property
    def roles(self) -> set[str]:
        return {r for r in self.roles_by_offset if r is not None}
