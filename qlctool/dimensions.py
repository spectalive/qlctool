"""A fixture's own size in millimetres, as QLC+ draws it."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Dimensions:
    """The fixture's own size in millimetres, as QLC+ draws it."""

    width: float
    height: float
    depth: float
