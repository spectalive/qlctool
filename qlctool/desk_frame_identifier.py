"""Which console frame a caption heads, by catalogue identifier, in any shipped language."""

from .names.frame_caption_head import frame_caption_head
from .names.names import Names


def desk_frame_identifier(caption: str, names: Names) -> str | None:
    """The `frames` identifier whose head matches this caption's head, or None.

    A frame caption is "<name> — <explanation>"; only the name identifies it,
    so a reworded explanation does not drop a page.
    """
    head = frame_caption_head(caption)
    for identifier in names.identifiers("frames"):
        for spelling in names.spellings(identifier):
            if frame_caption_head(spelling) == head:
                return identifier
    return None
