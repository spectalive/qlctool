"""A function's catalogue name with the play page's own pick prefix stripped."""

from ..names.names import Names


def source_name(name: str, vocabulary: Names) -> str:
    return name.removeprefix(vocabulary.display("pick_prefix"))
