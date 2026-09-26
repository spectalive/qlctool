"""A `Driven` wrapped read-only at both levels, for the show graph's cache."""

from types import MappingProxyType

from .driven_channels import Driven
from .read_only_driven import ReadOnlyDriven


def freeze_driven(driven: Driven) -> ReadOnlyDriven:
    """Read-only views of `driven` and of each fixture's channels; nothing is copied."""
    return MappingProxyType(
        {fixture_id: MappingProxyType(pairs) for fixture_id, pairs in driven.items()}
    )
