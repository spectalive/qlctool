"""[timing]: BPM, the Beats clock, level lengths in seconds, and step timings in beats."""

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from ...names.names import Names
from ..show_timing import ShowTiming
from .beat_timing_value import beat_timing_value
from .duration_tables import DURATION_TABLES
from .identified_keys import identified_keys
from .milliseconds import milliseconds
from .read_durations import read_durations
from .reject_unknown_keys import reject_unknown_keys
from .table_at import table_at


def read_timing(table: Mapping[str, Any], base: ShowTiming, names: Names, where: str) -> ShowTiming:
    """The base timing with every stated key replacing its default (F7).

    Scalars merge key by key; a stated duration table or [timing.beat_timings]
    replaces the default one whole.
    """
    here = f"{where}: [timing]"
    allowed = ("bpm", "beats", "prism_step_s", "matrix_beats", "beat_timings", *DURATION_TABLES)
    reject_unknown_keys(table, allowed, here)
    changes: dict[str, Any] = {}
    if "bpm" in table:
        bpm = table["bpm"]
        if isinstance(bpm, bool) or not isinstance(bpm, int) or bpm <= 0:
            raise ValueError(f"{here} bpm is a positive whole number, got {bpm!r}")
        changes["bpm"] = bpm
    if "beats" in table:
        if not isinstance(table["beats"], bool):
            raise ValueError(f"{here} beats is true or false")
        changes["beats"] = table["beats"]
    for key, fields in DURATION_TABLES.items():
        if key in table:
            changes.update(read_durations(table_at(table, key, here), fields, f"{here} {key}"))
    if "prism_step_s" in table:
        changes["prism_step_ms"] = milliseconds(table["prism_step_s"], f"{here} prism_step_s")
    if "matrix_beats" in table:
        changes["matrix_beats"] = beat_timing_value(
            table["matrix_beats"], f"{here} matrix_beats", base.matrix_beats
        )
    if "beat_timings" in table:
        timings = table_at(table, "beat_timings", here)
        spelled = identified_keys(timings, names, "functions", f"{here} beat_timings")
        changes["beat_timings"] = {
            identifier: beat_timing_value(
                timings[spelling],
                f"{here} beat_timings.{spelling}",
                base.beat_timings.get(identifier),
            )
            for identifier, spelling in spelled.items()
        }
    return replace(base, **changes)
