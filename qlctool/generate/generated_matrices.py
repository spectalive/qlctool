"""The RGBMatrix functions one call generated, and the chaser that steps them."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedMatrices:
    matrix_ids: list[int]
    chaser_id: int | None
