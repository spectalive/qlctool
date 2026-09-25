"""The name part of a console frame caption, as every frame lookup compares it."""


def frame_caption_head(caption: str) -> str:
    """The text before " — ", stripped and casefolded.

    A frame caption is "<name> — <explanation>"; only the name identifies the
    frame, so a reworded explanation or a change of case still matches.
    """
    return caption.split(" — ", maxsplit=1)[0].strip().casefold()
