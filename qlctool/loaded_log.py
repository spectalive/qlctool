"""What validation read from QLC+, and whether it saw loading finish."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LoadedLog:
    """QLC+'s log as read, and whether the QML build's end-of-load marker was in it.

    `marker_seen` is always True for the 4.x build, which has no marker and is
    judged done when its log goes quiet.
    """

    text: str
    marker_seen: bool
