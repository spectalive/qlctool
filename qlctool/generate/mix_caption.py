"""The caption a two-colour mix button wears: two codes, a slash between.

Moved verbatim out of `live_console` (2026-09-27 split).
"""

from collections.abc import Mapping


def mix_caption(name: str, mix_code: Mapping[str, str]) -> str:
    """ "Rojo / Azul PAR" reads as "Ro/Az" on a 44px button.

    Two letters, not one: Azul and Amarillo both start with an A, so a
    one-letter code gave six pairs of buttons the same label.
    """
    parts = [p.strip() for p in name.split(" / ")]
    if len(parts) < 2:
        return ""
    first = parts[0].split(" ")[0]
    second = parts[1].split(" ")[0]
    return f"{mix_code.get(first, first[:2])}/{mix_code.get(second, second[:2])}"
