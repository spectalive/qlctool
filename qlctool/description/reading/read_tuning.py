"""[fixture_tuning]: beam focus, prism spin, flash strobe speeds, the talk light's white."""

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from ..fixture_tuning import FixtureTuning
from .reject_unknown_keys import reject_unknown_keys
from .rgb_value import rgb_value
from .table_at import table_at


def read_tuning(table: Mapping[str, Any], base: FixtureTuning, where: str) -> FixtureTuning:
    """The base tuning with every stated value replacing its default, key by key (F7)."""
    here = f"{where}: [fixture_tuning]"
    reject_unknown_keys(table, ("beam_focus", "prism_spin_slow", "strobe", "talk_white"), here)
    changes: dict[str, Any] = {}
    for key in ("beam_focus", "prism_spin_slow"):
        if key in table:
            value = table[key]
            if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 255:
                raise ValueError(f"{here} {key} is a DMX value 0-255, got {value!r}")
            changes[key] = value
    strobe = table_at(table, "strobe", here)
    reject_unknown_keys(strobe, ("fast", "slow"), f"{here} strobe")
    for key in ("fast", "slow"):
        if key in strobe:
            value = strobe[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value <= 1:
                raise ValueError(
                    f"{here} strobe.{key} is a share of the strobe run, above 0 and up to 1"
                )
            changes[f"strobe_{key}"] = float(value)
    if "talk_white" in table:
        changes["talk_white"] = rgb_value(table["talk_white"], f"{here} talk_white")
    return replace(base, **changes)
