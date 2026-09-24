"""Which console frame a caption heads, by catalogue identifier, in any shipped language."""

from .names.names import Names


def desk_frame_identifier(caption: str, names: Names) -> str | None:
    """The `frames` identifier whose head matches this caption's head, or None.

    A frame caption is "<name> — <explanation>"; only the name identifies it,
    so a reworded explanation does not drop a page.
    """
    head = caption.split(" — ", maxsplit=1)[0].strip().casefold()
    for identifier in names.identifiers("frames"):
        for spelling in names.spellings(identifier):
            if spelling.split(" — ", maxsplit=1)[0].strip().casefold() == head:
                return identifier
    return None
