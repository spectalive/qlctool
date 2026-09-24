"""Curated matrix scripts, grouped by the fixture group they were tuned for."""

from collections.abc import Iterable

from ..matrix_algorithms import CuratedScript


def matrices_by_group(scripts: Iterable[CuratedScript]) -> dict[str, tuple[CuratedScript, ...]]:
    """Group name -> its scripts, each group keeping the order it was given in."""
    grouped: dict[str, list[CuratedScript]] = {}
    for script in scripts:
        grouped.setdefault(script.group_name, []).append(script)
    return {group: tuple(entries) for group, entries in grouped.items()}
