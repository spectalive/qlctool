"""Index fixture definitions by (manufacturer, model).

Two sources feed the library: the folders a rig names for its own .qxf
(`fixture_dirs`), and the handful of QLC+ system definitions bundled under
`qlctool/library/system`. A rig's definitions win on a name clash - that is what
QLC+ does with a user library too - and among the rig's folders the first wins.
"""

from collections.abc import Sequence
from pathlib import Path

from .definition import FixtureDefinition, load_definition
from .fixture_dirs import fixture_dirs as resolve_fixture_dirs

SYSTEM_FIXTURES = Path(__file__).resolve().parent / "library" / "system"


class FixtureLibrary:
    def __init__(
        self,
        definitions: dict[tuple[str, str], FixtureDefinition],
        sources: tuple[Path, ...] = (),
    ):
        self._by_key = definitions
        self.sources = sources

    @classmethod
    def load(
        cls,
        fixture_dirs: Sequence[Path] | None = None,
        system_dir: Path | None = None,
    ) -> "FixtureLibrary":
        folders = tuple(resolve_fixture_dirs() if fixture_dirs is None else fixture_dirs)
        definitions: dict[tuple[str, str], FixtureDefinition] = {}
        # System first and the rig's first folder last, so it overrides the rest.
        for source in (system_dir or SYSTEM_FIXTURES, *reversed(folders)):
            if not source.is_dir():
                continue
            for qxf in sorted(source.glob("*.qxf")):
                definition = load_definition(qxf)
                definitions[(definition.manufacturer, definition.model)] = definition
        return cls(definitions, folders)

    def get(self, manufacturer: str, model: str) -> FixtureDefinition | None:
        return self._by_key.get((manufacturer, model))

    def __len__(self) -> int:
        return len(self._by_key)
