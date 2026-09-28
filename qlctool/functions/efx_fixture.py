"""One fixture's participation in an EFX - the moving-head pattern generator."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EFXFixture:
    """One fixture's participation in an EFX.

    start_offset is the phase in degrees (0-359) that spreads fixtures around
    the path. mode is the EFX fixture mode QLC+ stores; the show only uses 0.
    """

    fixture_id: int
    head: int = 0
    mode: int = 0
    direction: str = "Forward"
    start_offset: int = 0
