"""The generators' Spanish literals, retired module by module (Plan B, 2026-09-25).

Each task that routes a module's names through the catalogue appends it to
CONVERTED; from then on the module may not spell a catalogue word itself.
Task 12 asserts CONVERTED covers every generator module except ruling B6's.
"""

from pathlib import Path

from catalogue_chunks import catalogue_chunks
from spanish_literals import spanish_literals

PACKAGE = Path(__file__).resolve().parents[1] / "qlctool"

CONVERTED: tuple[str, ...] = ()


def test_converted_modules_spell_no_catalogue_word():
    chunks = catalogue_chunks()
    found = [hit for module in CONVERTED for hit in spanish_literals(PACKAGE / module, chunks)]
    assert found == []


def test_the_scanner_sees_a_spanish_name(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text(
        '"""Momento Fiesta in a docstring is fine."""\nNAME = "Momento Fiesta"\nAUTO = "AUTO"\n',
        encoding="utf-8",
    )
    assert spanish_literals(source, catalogue_chunks()) == ["sample.py:2 'Momento Fiesta'"]
