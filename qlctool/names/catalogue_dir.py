"""Where the shipped catalogues live: one `<language>.toml` per language."""

from pathlib import Path

CATALOGUE_DIR = Path(__file__).resolve().parent.parent / "locales"
