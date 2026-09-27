"""An XML node's text or tail value, stripped of insignificant whitespace."""


def stripped_text(value: str | None) -> str:
    return (value or "").strip()
