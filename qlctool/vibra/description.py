"""The Vibra show as a description: the default the generator falls back to."""

from ..description.identify_description import identify_description
from ..description.matrices_by_group import matrices_by_group
from ..description.show_description import ShowDescription
from ..matrix_algorithms import CURATED_MATRICES
from ..names.default_names import default_names
from .colours import VIBRA_COLOURS
from .console import VIBRA_CONSOLE
from .timing import VIBRA_TIMING
from .tuning import VIBRA_TUNING


def vibra_description() -> ShowDescription:
    """Today's Vibra values, named by catalogue identifier."""
    spoken = ShowDescription(
        colours=VIBRA_COLOURS,
        matrices=matrices_by_group(CURATED_MATRICES),
        timing=VIBRA_TIMING,
        tuning=VIBRA_TUNING,
        console=VIBRA_CONSOLE,
    )
    return identify_description(spoken, default_names())
