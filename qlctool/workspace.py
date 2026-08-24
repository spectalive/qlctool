"""Load and save a QLC+ workspace (.qxw) with a semantic round-trip guarantee.

The class keeps the full lxml tree in memory so higher-level generators mutate
only the nodes they target and leave everything else untouched. Saving restores
the exact header QLC+ expects (`<?xml ...?>`, `<!DOCTYPE Workspace>`) so the
result loads back into QLC+ unchanged in meaning.

Formatting note: the first save normalizes indentation to lxml's pretty-print
style rather than Qt's single-space style. That is cosmetic - QLC+ ignores it -
and it settles after the first save, so subsequent diffs stay minimal.
"""

from pathlib import Path

from lxml import etree

from .constants import DOCTYPE, XML_DECLARATION


class Workspace:
    def __init__(self, tree: etree._ElementTree):
        self._tree = tree

    @classmethod
    def load(cls, path: str | Path) -> "Workspace":
        # remove_blank_text lets pretty_print reindent cleanly on save; the
        # blank text we drop is insignificant whitespace QLC+ never reads.
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(str(path), parser)
        return cls(tree)

    @property
    def root(self) -> etree._Element:
        return self._tree.getroot()

    def to_bytes(self) -> bytes:
        # Serialize the root element, not the tree: tostring(tree) would re-emit
        # the DOCTYPE from docinfo and we add our own header below.
        body = etree.tostring(self.root, pretty_print=True, encoding="unicode")
        header = f"{XML_DECLARATION}\n{DOCTYPE}\n"
        return (header + body).encode("utf-8")

    def save(self, path: str | Path) -> None:
        Path(path).write_bytes(self.to_bytes())
