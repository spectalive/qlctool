"""Which help-line identifier a caption is the text of, in any shipped language."""

from ..names.template_pattern import template_pattern
from .catalogue_spellings import catalogue_spellings

MIXES = "mixes_frame"
MATRICES = (
    "matrices_frame",
    "matrices_frame_bars",
    "matrices_frame_panels",
    "matrices_frame_groups",
)

# Each help line that names a frame, and the frame captions that keep its word.
HELP_LINE_FRAMES: dict[str, tuple[tuple[str, ...], ...]] = {
    "library_1": ((MIXES,), MATRICES),
    "library_1_no_mixes": (MATRICES,),
    "library_1_no_matrices": ((MIXES,),),
    "library_1_no_builtins": ((MIXES,), MATRICES),
    "library_1_no_builtins_no_mixes": (MATRICES,),
    "library_1_no_builtins_no_matrices": ((MIXES,),),
    "library_5": ((MIXES,), MATRICES),
    "library_5_no_mixes": (MATRICES,),
    "library_5_no_matrices": ((MIXES,),),
}


def help_line(caption: str) -> str | None:
    """The help-line identifier `caption` is the text of, in any shipped language."""
    for identifier in HELP_LINE_FRAMES:
        for text in catalogue_spellings(identifier):
            if template_pattern(text).fullmatch(caption):
                return identifier
    return None
