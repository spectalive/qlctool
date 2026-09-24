"""[[groups.<group>.matrices]]: hand-tuned RGB scripts, per fixture group of the patch."""

from collections.abc import Mapping
from typing import Any

from lxml import etree

from ...argb import RGB
from ...fixture_group import fixture_groups
from ...matrix_algorithms import CuratedScript
from ...names.names import Names
from .list_at import list_at
from .read_matrix_script import read_matrix_script
from .reject_unknown_keys import reject_unknown_keys
from .table_at import table_at


def read_matrices(
    table: Mapping[str, Any] | None,
    base: Mapping[str, tuple[CuratedScript, ...]],
    palette: Mapping[str, RGB],
    names: Names,
    root: etree._Element,
    where: str,
) -> dict[str, tuple[CuratedScript, ...]]:
    """Group -> scripts. A stated group must be one the patch has, like a stage plot's ids.

    A stated [groups] replaces every default group's scripts, not only its own (R6, F7).
    """
    matrices = dict(base)
    if table is not None:
        matrices = {}
        patched = [group.name for group in fixture_groups(root)]
        for group in table:
            here = f"{where}: [groups.{group}]"
            if group not in patched:
                raise ValueError(
                    f"{here} names a fixture group the patch does not have; "
                    f"the patch has: {', '.join(patched)}"
                )
            settings = table_at(table, group, f"{where}: [groups]")
            reject_unknown_keys(settings, ("matrices",), here)
            matrices[group] = tuple(
                read_matrix_script(entry, group, names, f"{here} matrices[{index}]")
                for index, entry in enumerate(list_at(settings, "matrices", here))
            )
    missing = sorted({c for s in matrices.values() for m in s for c in m.colors} - set(palette))
    if missing:
        raise ValueError(
            f"{where}: [groups] matrices use colours the palette lacks: {', '.join(missing)}"
        )
    return matrices
