"""Every versioned QLC+ application bundle in a folder, newest version first.

The installers name their bundles `QLC+ 4.13.1.app` and `QLC+ 5.2.2.app`, so a
fixed list of paths finds none of them (2026-09-25: ten validation tests
skipped with QLC+ 5.2.2 installed).
"""

import re
from pathlib import Path


def qlcplus_bundles(
    applications: Path = Path("/Applications"),
) -> list[tuple[tuple[int, ...], str]]:
    """(version, executable) for each `qlcplus` / `qlcplus-qml` in a versioned bundle."""
    if not applications.is_dir():
        return []
    found: list[tuple[tuple[int, ...], str]] = []
    for bundle in sorted(applications.glob("QLC+ *.app")):
        match = re.fullmatch(r"QLC\+ (\d+(?:\.\d+)*)\.app", bundle.name)
        if match is None:
            continue
        version = tuple(int(part) for part in match.group(1).split("."))
        for name in ("qlcplus", "qlcplus-qml"):
            executable = bundle / "Contents" / "MacOS" / name
            if executable.is_file():
                found.append((version, str(executable)))
    return sorted(found, key=lambda entry: entry[0], reverse=True)
