"""Every QLC+ executable worth trying, best first."""

from collections.abc import Callable, Sequence
from pathlib import Path

from .qlcplus_bundles import qlcplus_bundles
from .runs_here import runs_here


def qlcplus_candidates(
    fixed: Sequence[str],
    applications: Path = Path("/Applications"),
    runnable: Callable[[str], bool] = runs_here,
) -> list[str]:
    """Versioned bundles newest first, then the fixed paths; only what can run.

    The widgets build (`qlcplus`) sorts before the QML build (`qlcplus-qml`)
    whatever its version: it is the only one that loads with no GUI at all.
    """
    ordered = [path for _, path in qlcplus_bundles(applications)]
    ordered += [path for path in fixed if Path(path).is_file()]
    usable = [path for path in dict.fromkeys(ordered) if runnable(path)]
    return sorted(usable, key=lambda path: Path(path).name == "qlcplus-qml")
