"""The generators' Spanish literals, retired module by module (Plan B, 2026-09-25).

Each task that routes a module's names through the catalogue appends it to
CONVERTED; from then on the module may not spell a catalogue word itself.
Task 12 asserts CONVERTED covers every generator module except ruling B6's.
"""

from pathlib import Path

from catalogue_chunks import catalogue_chunks
from spanish_literals import spanish_literals

PACKAGE = Path(__file__).resolve().parents[1] / "qlctool"

CONVERTED: tuple[str, ...] = (
    "generate/builtin_effects.py",
    "generate/color_banks.py",
    "generate/color_flashes.py",
    "generate/flash_color.py",
    "generate/multicolor_scene.py",
    "generate/pixel_base.py",
    "generate/pixel_wheel_matrices.py",
    "generate/quad_color_scenes.py",
    "generate/rainbow_efx.py",
    "generate/unison_colors.py",
    "generate/panel_manual.py",
    "generate/panel_speed_auto.py",
    "generate/vertical_smoke_light.py",
    "generate/matrix_effects.py",
    "generate/beam_rainbow_spin.py",
    "color_wheel_match.py",
    "checks/detent_white.py",
    "efx_algorithms.py",
    "generate/movement_efx.py",
    "generate/movement_families.py",
    "generate/home_position.py",
    "generate/cross_position.py",
    "generate/fan_position.py",
    "generate/stage_aim.py",
    "generate/wheel_scenes.py",
    "generate/dealt_gobo_scenes.py",
    "generate/prism_spins.py",
    "generate/beam_subsets.py",
    "generate/dimmer_chases.py",
    "generate/dimmer_sequence.py",
    "generate/dimmerless_intensity.py",
    "generate/energy_intensity.py",
    "generate/energy_levels.py",
    "generate/smoke_auto.py",
    "generate/strobe_effects.py",
    "generate/vertical_smoke_burst.py",
    "generate/play_wrappers.py",
    "generate/gobo_shake.py",
    "generate/canonical_show.py",
    "generate/moments.py",
)


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
