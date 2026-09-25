"""The QLC+ fixture types that make smoke or haze: what `is_smoke` reads.

A hazer is a smoke machine to every generator and rule: it has a pump to
park, it takes no dimmer, it lights nothing. Before 2026-09-25 only "Smoke"
counted, so a Hazer-typed fixture satisfied page 3's "y humo" while nothing
on the console fired it (re-review of the caption-promise rule).
"""

SMOKE_TYPES: tuple[str, ...] = ("smoke", "hazer")
