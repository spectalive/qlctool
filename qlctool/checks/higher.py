"""HTP, with None - an unpredictable effect - above every number."""


def higher(current: int | None, incoming: int | None) -> int | None:
    if current is None or incoming is None:
        return None
    return max(current, incoming)
