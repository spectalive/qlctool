"""One show, described: everything the generator used to hard-code for Vibra."""

from collections.abc import Mapping
from dataclasses import dataclass

from ..matrix_algorithms import CuratedScript
from .console_settings import ConsoleSettings
from .fixture_tuning import FixtureTuning
from .show_timing import ShowTiming


@dataclass(frozen=True)
class ShowDescription:
    """A show's choices apart from the patch, which QLC+ keeps.

    `matrices` holds each fixture group's hand-tuned RGB scripts, in the order
    that group's cycle steps them; a group the patch lacks is simply unused.
    """

    matrices: Mapping[str, tuple[CuratedScript, ...]]
    timing: ShowTiming
    tuning: FixtureTuning
    console: ConsoleSettings
