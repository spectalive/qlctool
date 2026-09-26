"""The default I/O patches QLC+ keeps in its own settings, named by key only.

At startup, before any workspace is loaded, QLC+ opens the input and output
patches stored under `/inputmap/universeN/...` and `/outputmap/universeN/...`
in its settings (`InputOutputMap::loadDefaults`, called from `qmlui/app.cpp`
and `ui/src/app.cpp`; QLC+ 4's I/O manager writes them). An offline copy of a
workspace cannot reach them, so validation looks for them first (2026-09-26,
second review of round D6). Only key names are read back; values never are.
"""

import plistlib
from pathlib import Path

# QSettings for organisation domain qlcplus.org and application "Q Light
# Controller Plus", as both builds set them: the macOS plist (keys flattened
# with dots) and the Linux INI files (one [section] per group).
PLIST = "Library/Preferences/org.qlcplus.Q Light Controller Plus.plist"
INI = (
    ".config/qlcplus.org/Q Light Controller Plus.conf",
    ".config/qlcplus/Q Light Controller Plus.conf",
)
GROUPS = ("inputmap", "outputmap")


def saved_io_patches(home: Path | None = None) -> list[str]:
    """Where QLC+'s settings hold default I/O patches: `file: key` per key, sorted."""
    root = Path.home() if home is None else home
    found: list[str] = []
    plist = root / PLIST
    if plist.is_file():
        with plist.open("rb") as handle:
            keys = plistlib.load(handle).keys()
        found += [f"{plist}: {key}" for key in keys if key.split(".")[0].lower() in GROUPS]
    for name in INI:
        ini = root / name
        if ini.is_file():
            for line in ini.read_text(errors="replace").splitlines():
                section = line.strip().strip("[]").split("/")[0].lower()
                if line.startswith("[") and section in GROUPS:
                    found.append(f"{ini}: {line.strip()}")
    return sorted(found)
