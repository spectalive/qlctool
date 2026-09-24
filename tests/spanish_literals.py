"""Find the words a generator still spells itself instead of asking the catalogue."""

import ast
from pathlib import Path

from docstring_ids import docstring_ids
from literal_strip import LITERAL_STRIP


def spanish_literals(path: Path, chunks: frozenset[str]) -> list[str]:
    """`file:line 'literal'` for each non-docstring string that is a catalogue chunk."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = docstring_ids(tree)
    return [
        f"{path.name}:{node.lineno} {node.value!r}"
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
        and node.value.strip(LITERAL_STRIP) in chunks
    ]
