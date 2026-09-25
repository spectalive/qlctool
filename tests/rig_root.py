"""Where the suite finds a rig: its workspaces, stage plots, definitions and input profile.

The rig is the frozen copy in tests/data/rig. QLCTOOL_TEST_RIG points the suite
at any other rig laid out the same way (ruling C1).
"""

import os
from pathlib import Path


def _default() -> Path:
    here = Path(__file__).resolve().parent
    return here / "data" / "rig"


RIG_ROOT = (
    Path(os.environ["QLCTOOL_TEST_RIG"]) if os.environ.get("QLCTOOL_TEST_RIG") else _default()
)
