"""The Vibra show as a description: the default the generator falls back to."""

from ..description.matrices_by_group import matrices_by_group
from ..description.show_description import ShowDescription
from ..matrix_algorithms import CURATED_MATRICES
from .colours import VIBRA_COLOURS
from .console import VIBRA_CONSOLE
from .timing import VIBRA_TIMING
from .tuning import VIBRA_TUNING


def vibra_description() -> ShowDescription:
    """Today's Vibra values, exactly as the generator used to hard-code them."""
    return ShowDescription(
        colours=VIBRA_COLOURS,
        matrices=matrices_by_group(CURATED_MATRICES),
        timing=VIBRA_TIMING,
        tuning=VIBRA_TUNING,
        console=VIBRA_CONSOLE,
    )
