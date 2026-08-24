"""Index fixture definitions by (manufacturer, model).

Two sources feed the library: the custom .qxf in the repo's `QLC+ Fixtures`
folder, and the handful of QLC+ system definitions bundled under
`qlctool/library/system` (pulled from the show Mac, only the models the patch
actually uses). Repo definitions win on a name clash - that is what QLC+ does
with a user library too.
"""

from pathlib import Path

from .definition import FixtureDefinition, load_definition

REPO_ROOT = Path(__file__).resolve().parents[3]
REPO_FIXTURES = REPO_ROOT / "QLC+ Fixtures"
SYSTEM_FIXTURES = Path(__file__).resolve().parent / "library" / "system"


class FixtureLibrary:
    def __init__(self, definitions: dict[tuple[str, str], FixtureDefinition]):
        self._by_key = definitions

    @classmethod
    def load(
        cls,
        repo_dir: Path | None = None,
        system_dir: Path | None = None,
    ) -> "FixtureLibrary":
        definitions: dict[tuple[str, str], FixtureDefinition] = {}
        # System first, so a repo definition of the same model overrides it.
        for source in (system_dir or SYSTEM_FIXTURES, repo_dir or REPO_FIXTURES):
            if source is None or not source.is_dir():
                continue
            for qxf in sorted(source.glob("*.qxf")):
                definition = load_definition(qxf)
                definitions[(definition.manufacturer, definition.model)] = definition
        return cls(definitions)

    def get(self, manufacturer: str, model: str) -> FixtureDefinition | None:
        return self._by_key.get((manufacturer, model))

    def __len__(self) -> int:
        return len(self._by_key)
