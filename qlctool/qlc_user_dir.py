"""Where QLC+ reads user fixture definitions and input profiles from.

Not where the repo keeps them: a definition in `QLC+ Fixtures/` does nothing
until a copy sits in this folder, and a stale copy is worse than none - QLC+
loads it without a word and `--validate` validates against it. Four of the
eleven copies on the author's machine were a week behind the repo on
2026-09-01, one of them the fog machine's pump group.
"""

import os
import sys
from pathlib import Path


def qlc_user_dir() -> Path:
    """QLC+'s per-user data folder, overridable with QLCTOOL_QLC_USER_DIR."""
    override = os.environ.get("QLCTOOL_QLC_USER_DIR")
    if override:
        return Path(override)
    if sys.platform != "darwin":
        return Path.home() / ".qlcplus"
    return Path.home() / "Library" / "Application Support" / "QLC+"
