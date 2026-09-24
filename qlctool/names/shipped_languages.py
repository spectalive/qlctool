"""The languages a catalogue ships for."""

from .catalogue_dir import CATALOGUE_DIR


def shipped_languages() -> tuple[str, ...]:
    """Every `<language>.toml` in the catalogue folder, sorted."""
    return tuple(sorted(path.stem for path in CATALOGUE_DIR.glob("*.toml")))
