"""The console's word for an EFX shape, catalogue-worded where one exists."""

from collections.abc import Callable

from ..efx_shape_identifiers import EFX_SHAPE_IDENTIFIERS


def label_of(display: Callable[[str], str], shape: str) -> str:
    return display(EFX_SHAPE_IDENTIFIERS[shape]) if shape in EFX_SHAPE_IDENTIFIERS else shape
