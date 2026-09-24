"""Everything QLC+ has to be handed from a rig's configured folders, and whether it has it.

Three kinds of file, three destinations: the `.qxf` definitions and the `.qxi`
input profile go to QLC+'s user folder; the gobo images go inside the
application bundle, under the folder name each definition's `Res1` uses.
"""

from pathlib import Path

from .gobo_folder import gobo_folder
from .install_item import InstallItem
from .install_state import install_state
from .toolkit_config import ToolkitConfig


def install_plan(
    config: ToolkitConfig,
    user_dir: Path | None = None,
    gobo_dir: Path | None = None,
) -> list[InstallItem]:
    """Every configured file to install, in configuration order, each with its state."""
    items: list[InstallItem] = []
    if user_dir is not None:
        for folder in config.fixtures:
            for source in sorted(folder.glob("*.qxf")):
                items.append(install_state(source, user_dir / "Fixtures" / source.name))
        for folder in config.input_profiles:
            for source in sorted(folder.glob("*.qxi")):
                items.append(install_state(source, user_dir / "InputProfiles" / source.name))
    if gobo_dir is not None:
        for folder in config.gobos:
            for source in sorted(folder.glob("*/*.png")):
                target = next(
                    (f for d in config.fixtures if (f := gobo_folder(d, source.name)) is not None),
                    None,
                )
                if target is not None:
                    items.append(install_state(source, gobo_dir / target / source.name))
    return items
