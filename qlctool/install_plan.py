"""Everything QLC+ has to be handed from this repo, and whether it has it.

Three kinds of file, three destinations: the `.qxf` definitions and the `.qxi`
input profile go to QLC+'s user folder; the gobo images go inside the
application bundle, under the folder name each definition's `Res1` uses -
which is not the repo folder's name, because the reference workspace still
points at the old one.
"""

import filecmp
import re
from pathlib import Path

from .install_item import MISSING, STALE, SYNCED, InstallItem
from .library import REPO_ROOT

_RES1 = re.compile(r'Res1="([^"/]+)/([^"]+)"')


def install_plan(
    repo_root: Path = REPO_ROOT,
    user_dir: Path | None = None,
    gobo_dir: Path | None = None,
) -> list[InstallItem]:
    """Every file to install, in repo order, each with its current state."""
    items: list[InstallItem] = []
    if user_dir is not None:
        for source in sorted((repo_root / "QLC+ Fixtures").glob("*.qxf")):
            items.append(_item(source, user_dir / "Fixtures" / source.name))
        for source in sorted((repo_root / "QLC+ InputProfiles").glob("*.qxi")):
            items.append(_item(source, user_dir / "InputProfiles" / source.name))
    if gobo_dir is not None:
        for source in sorted((repo_root / "QLC+ Setups" / "Gobos").glob("*/*.png")):
            folder = _gobo_folder(repo_root, source.name)
            if folder is not None:
                items.append(_item(source, gobo_dir / folder / source.name))
    return items


def _item(source: Path, destination: Path) -> InstallItem:
    if not destination.exists():
        state = MISSING
    elif filecmp.cmp(source, destination, shallow=False):
        state = SYNCED
    else:
        state = STALE
    return InstallItem(source, destination, state)


def _gobo_folder(repo_root: Path, image: str) -> str | None:
    """The bundle folder a definition expects this image under, if any does."""
    for definition in (repo_root / "QLC+ Fixtures").glob("*.qxf"):
        for folder, name in _RES1.findall(definition.read_text(encoding="utf-8")):
            if name == image:
                return str(folder)
    return None
