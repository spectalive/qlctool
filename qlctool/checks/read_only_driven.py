"""What a leaf drives, as the show graph hands it out: fixture -> channel -> value.

The same shape as `Driven`, but read-only at both levels, so a rule cannot
change the graph's cached answer for the rules after it (round G review,
2026-09-26).
"""

from collections.abc import Mapping
from typing import TypeAlias

ReadOnlyDriven: TypeAlias = Mapping[int, Mapping[int, int | None]]
