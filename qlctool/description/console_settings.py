"""The console a show is operated from: its screen, its keys, its held buttons."""

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ConsoleSettings:
    """Canvas size in pixels, one keyboard key per function, and the functions held not latched."""

    canvas: tuple[int, int]
    keys: Mapping[str, str]
    flash_functions: tuple[str, ...]
