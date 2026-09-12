"""QLC+ 5.2.2's speed-dial multiplier enum, as the engine reads and caches it.

A speed dial stores per function three small integers (FadeIn, FadeOut,
Duration) that are not factors but indices into `VCSpeedDial::SpeedMultiplier`
(qmlui/virtualconsole/vcspeeddial.h): 0 None, 1 Zero, 2 OneSixteenth ... 6 One
... 10 Sixteen. `None` means the dial leaves that time alone, which is not the
same as multiplying by one. The engine caches the fractions in integer
thousandths (`cacheMultipliers`: 1000 / 16 = 62), so a sixteenth is 0.062 to
the show, not 0.0625.
"""

NAMES = ("None", "Zero", "1/16", "1/8", "1/4", "1/2", "1", "2", "4", "8", "16")
_THOUSANDTHS = (None, 0, 62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000)


def multiplier(raw: int) -> dict:
    """The enum value as the map carries it: raw, name and effective factor."""
    if not 0 <= raw < len(NAMES):
        raise ValueError(f"speed multiplier {raw} is outside the 5.2.2 enum")
    thousandths = _THOUSANDTHS[raw]
    return {
        "raw": raw,
        "name": NAMES[raw],
        "factor": None if thousandths is None else thousandths / 1000,
    }
