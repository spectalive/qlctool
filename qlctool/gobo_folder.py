"""The bundle folder a definition expects a gobo image under.

A relative `Res1` is `<folder>/<file>` and QLC+ resolves it against its own
Gobos directory, so the folder name comes from the definition - not from the
repo folder the image happens to live in, which the reference workspace still
points at under its old name.
"""

import re
from pathlib import Path

_RES1 = re.compile(r'Res1="([^"/]+)/([^"]+)"')


def gobo_folder(fixtures_dir: Path, image: str) -> str | None:
    """The `Res1` folder naming this image in any definition, or None."""
    for definition in fixtures_dir.glob("*.qxf"):
        for folder, name in _RES1.findall(definition.read_text(encoding="utf-8")):
            if name == image:
                return str(folder)
    return None
