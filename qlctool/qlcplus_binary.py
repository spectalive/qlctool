"""The QLC+ executable to validate a workspace with, if one is installed."""

import os
import shutil
from pathlib import Path

from .qlcplus_candidates import qlcplus_candidates

DEFAULT_BINARIES = (
    # 4.x first: it is the only build that loads with no GUI at all.
    "/Applications/QLC+ 4.app/Contents/MacOS/qlcplus",
    "/Applications/QLC+.app/Contents/MacOS/qlcplus",
    "/usr/bin/qlcplus",
    "/usr/local/bin/qlcplus",
    "/Applications/QLC+.app/Contents/MacOS/qlcplus-qml",
    "/usr/bin/qlcplus-qml",
    "/usr/local/bin/qlcplus-qml",
)


def qlcplus_binary() -> str | None:
    """The QLC+ executable to validate with, or None when none is installed."""
    override = os.environ.get("QLCTOOL_QLCPLUS")
    if override:
        return override if Path(override).exists() else None
    candidates = qlcplus_candidates(DEFAULT_BINARIES)
    if candidates:
        return candidates[0]
    return shutil.which("qlcplus") or shutil.which("qlcplus-qml")
