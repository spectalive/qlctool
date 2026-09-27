"""Turn a function name into a filesystem-safe slug for fragment filenames.

Purely cosmetic - the manifest, not the filename, drives recomposition - but a
readable slug makes the decomposed tree diffable and browsable.
"""

import re
import unicodedata


def slugify(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return cleaned or "sin-nombre"
