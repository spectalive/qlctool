"""The gobo image a QLC+ range names, found by file name under the repo's gobos.

Looked up by basename because the folder a definition names (`BEAM-230W-7R/`)
is the one QLC+ has installed, not necessarily the one the repo keeps it in.
"""

from pathlib import Path


def find_gobo_image(resource: str, gobo_dir: Path | None) -> Path | None:
    if not resource or gobo_dir is None or not gobo_dir.is_dir():
        return None
    wanted = resource.replace("\\", "/").split("/")[-1]
    return next(iter(sorted(gobo_dir.rglob(wanted))), None)
