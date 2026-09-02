"""Everything QLC+ has to be handed from this repo, and whether it has it.

Three kinds of file, three destinations: the `.qxf` definitions and the `.qxi`
input profile go to QLC+'s user folder; the gobo images go inside the
application bundle, under the folder name each definition's `Res1` uses.
"""

from pathlib import Path

from .gobo_folder import gobo_folder
from .install_item import InstallItem
from .install_state import install_state
from .library import REPO_ROOT


def install_plan(
    repo_root: Path = REPO_ROOT,
    user_dir: Path | None = None,
    gobo_dir: Path | None = None,
) -> list[InstallItem]:
    """Every file to install, in repo order, each with its current state."""
    items: list[InstallItem] = []
    if user_dir is not None:
        for source in sorted((repo_root / "QLC+ Fixtures").glob("*.qxf")):
            items.append(install_state(source, user_dir / "Fixtures" / source.name))
        for source in sorted((repo_root / "QLC+ InputProfiles").glob("*.qxi")):
            items.append(install_state(source, user_dir / "InputProfiles" / source.name))
    if gobo_dir is not None:
        for source in sorted((repo_root / "QLC+ Setups" / "Gobos").glob("*/*.png")):
            folder = gobo_folder(repo_root / "QLC+ Fixtures", source.name)
            if folder is not None:
                items.append(install_state(source, gobo_dir / folder / source.name))
    return items
