"""The name a person reads for a rule, in one shipped language."""

from ..names.load_catalogue import load_catalogue


def display_name_of_rule(rule_id: str, language: str) -> str | None:
    """The `[checks]` entry for `rule_id`, or None for a rule no catalogue names."""
    return load_catalogue(language)["checks"].get(rule_id)
