"""Split a Mac console caption into the desk's two lines: name and explanation."""

import re


def split_caption(caption: str) -> tuple[str, str]:
    """A Mac caption into the desk's two lines: the name and the explanation.

    "AUTO — el show se lleva solo · Q" -> ("AUTO", "el show se lleva solo");
    "AUTO colores · W" -> ("AUTO colores", ""); "Rig Rojo" -> ("Rig Rojo", "").
    The key hint after " · " is the Mac keyboard's business, not the tablet's.
    """
    text = re.sub(r"\s·\s\S+$", "", caption).strip()
    head, sep, detail = text.partition(" — ")
    if not sep:
        # A two-colour contrast, "Cabezas Rojo / Resto Azul", reads as a
        # name and its second half rather than one long line.
        head, sep, detail = text.partition(" / ")
    return head.strip(), detail.strip() if sep else ""
