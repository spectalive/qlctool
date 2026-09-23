"""A channel name as the tail of a GDTF wheel name: alphanumerics only."""


def wheel_name(text: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in text).strip("_") or "Wheel"
