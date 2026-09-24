"""One show, described: everything the generator used to hard-code for Vibra."""

from collections.abc import Mapping
from dataclasses import dataclass, field

from ..matrix_algorithms import CuratedScript
from .colour_settings import ColourSettings
from .console_settings import ConsoleSettings
from .fixture_tuning import FixtureTuning
from .show_timing import ShowTiming


@dataclass(frozen=True)
class ShowDescription:
    """A show's choices apart from the patch, which QLC+ keeps.

    `matrices` holds each fixture group's hand-tuned RGB scripts, in the order
    that group's cycle steps them; a group the patch lacks is simply unused.
    """

    colours: ColourSettings
    matrices: Mapping[str, tuple[CuratedScript, ...]]
    timing: ShowTiming
    tuning: FixtureTuning
    console: ConsoleSettings
    language: str = "es"
    # language -> identifier -> the show's own word for it ([names.<lang>]).
    names: Mapping[str, Mapping[str, str]] = field(default_factory=dict)
