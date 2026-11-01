"""The catalogue identifier of a QLC+ capability preset."""

import re


def preset_identifier(preset: str) -> str:
    """"PrismEffectOn" -> "prism_effect_on": catalogue identifiers are snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", preset).lower()
