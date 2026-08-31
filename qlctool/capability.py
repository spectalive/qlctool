"""Resolve a patched fixture's channels to roles, so generators can drive it.

Joins a PatchedFixture (which mode it runs) with its FixtureDefinition (what each
channel does) to answer the one question a scene generator asks: "which channel
offsets carry role X on this fixture?" A role can map to several offsets - an
8-segment RGB bar has eight red channels - so lookups return lists.
"""

from dataclasses import dataclass

from . import roles
from .definition import Capability, Dimensions, FixtureDefinition
from .fixture import PatchedFixture


@dataclass(frozen=True)
class FixtureCapabilities:
    fixture: PatchedFixture
    # channel offset (0-based, within the fixture) -> role or None
    roles_by_offset: list[str | None]
    # the same offsets -> that channel's labelled ranges (gobos, prism, colours)
    capabilities_by_offset: list[tuple[Capability, ...]]
    # and their QLC+ channel groups, which decide whether QLC+ resets a channel
    # every cycle or leaves it holding the last value written
    groups_by_offset: list[str]
    # the <Head> blocks this mode declares, as channel offsets. Empty means the
    # definition declares none and QLC+ will invent a single head holding every
    # channel - see FixtureDefinition.heads.
    declared_heads: tuple[tuple[int, ...], ...] = ()
    fixture_type: str = ""
    dimensions: Dimensions | None = None

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
            groups_by_offset=definition.mode_groups(fixture.mode),
            declared_heads=definition.mode_heads(fixture.mode),
            fixture_type=definition.fixture_type,
            dimensions=definition.dimensions,
        )

    @property
    def is_smoke(self) -> bool:
        return self.fixture_type.lower() == "smoke"

    @property
    def is_lit_smoke(self) -> bool:
        """A smoke machine that carries its own lights.

        Its pump is still sacred - only the smoke scenes fire it - but the LED
        half is an ordinary RGB fixture: it joins the colour bed and the
        blackout like a PAR on the floor. The split is safe because the pump
        is typed with the dedicated smoke role, never as the dimmer.
        """
        return self.is_smoke and roles.RED in self.roles_by_offset

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

    def wheel_for_role(self, role: str) -> tuple[int, tuple[Capability, ...]] | None:
        """The one channel whose labelled ranges *are* this role's positions.

        A role can land on more than one channel of the same fixture - a colour
        wheel and the continuous half-colour channel beside it are both in the
        Colour group, a gobo wheel and its shake channel are both Gobo. Only one
        of them is the wheel: the one with the positions on it. Sending a wheel
        position to the others parks the wheel off its detent, or drives an
        unrelated effect with a number that means nothing there.

        Returns None when the fixture has no channel for the role at all.
        """
        channels = self.capabilities_for_role(role)
        if not channels:
            return None
        # Ties go to the lower offset, which is where a wheel sits relative to
        # the fine/shake channel that follows it.
        return max(channels, key=lambda item: (len(item[1]), -item[0]))

    @property
    def roles(self) -> set[str]:
        return {r for r in self.roles_by_offset if r is not None}
