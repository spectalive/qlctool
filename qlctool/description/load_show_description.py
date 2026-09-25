"""Read a show description and check it against the patch it claims to describe.

The patch stays in QLC+; the description says what to do with it. Like a stage
plot (`stage_plot.load_stage_plot`), it is bound to a patch: a matrix tuned for
a fixture group the workspace does not have is refused, loudly, rather than
silently generating nothing. Every section is optional and falls back to the
Vibra show's values, except [controllers], which falls back to none.
"""

from pathlib import Path

from lxml import etree

from ..names.shipped_names import shipped_names
from ..vibra.vibra_description import vibra_description
from .reading.description_sections import DESCRIPTION_SECTIONS
from .reading.read_console import read_console
from .reading.read_controllers import read_controllers
from .reading.read_matrices import read_matrices
from .reading.read_names import read_names
from .reading.read_palette import read_palette
from .reading.read_rig import read_rig
from .reading.read_show import read_show
from .reading.read_timing import read_timing
from .reading.read_toml_file import read_toml_file
from .reading.read_tuning import read_tuning
from .reading.reject_unknown_keys import reject_unknown_keys
from .reading.table_at import table_at
from .show_description import ShowDescription


def load_show_description(path: str | Path, root: etree._Element) -> ShowDescription:
    """The description at `path`, named by identifier, validated against `root`'s patch."""
    source = Path(path)
    where = str(source)
    document = read_toml_file(source)
    reject_unknown_keys(document, DESCRIPTION_SECTIONS, where)
    base = vibra_description()
    name, language = read_show(table_at(document, "show", where), source)
    overrides = read_names(table_at(document, "names", where), where)
    names = shipped_names(language, overrides)
    colours = read_palette(table_at(document, "palette", where), base.colours, names, where)
    groups = table_at(document, "groups", where) if "groups" in document else None
    return ShowDescription(
        colours=colours,
        matrices=read_matrices(groups, base.matrices, colours.palette, names, root, where),
        timing=read_timing(table_at(document, "timing", where), base.timing, names, where),
        tuning=read_tuning(table_at(document, "fixture_tuning", where), base.tuning, where),
        console=read_console(table_at(document, "console", where), base.console, names, where),
        language=language,
        names=overrides,
        controllers=read_controllers(table_at(document, "controllers", where), where),
        name=name,
        rig=read_rig(table_at(document, "rig", where), source),
    )
