"""The generators' Spanish literals, retired module by module (Plan B, 2026-09-25).

Each task that routes a module's names through the catalogue appends it to
CONVERTED; from then on the module may not spell a catalogue word itself.
Since Task 12a CONVERTED covers every generator module except ruling B6's.
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
    "generate/page_control_title.py",
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
    "control_glyph.py",
    "generate/smc_pad_bindings.py",
    "generate/smc_pad_colors.py",
    "generate/live_console.py",
    "generate/play_page.py",
    "generate/desk_bursts.py",
    "desk_policy.py",
    "deskmap.py",
    "desk_burst_note.py",
    # Task 12a (2026-09-25): no catalogue word in them; the scanner holds them clean.
    "generate/beat_tempo.py",
    "generate/bind_pad.py",
    "generate/color_scene.py",
    "generate/dealt_wheel_color.py",
    "generate/generated_color_flashes.py",
    "generate/generated_play_wrappers.py",
    "generate/movement_aim.py",
    "generate/park_work_light.py",
    "generate/rest_scene.py",
    "generate/smc_pad_device.py",
    "generate/split_color_scene.py",
    "generate/stage_layout.py",
    "generate/stage_plot_layout.py",
    "generate/wheel_color_values.py",
    # Plan C Task 2 (2026-09-25): no catalogue word in them.
    "generate/haze_machines.py",
    "generate/rig_has_role.py",
)

# Ruling B6: modules that keep their literals, and why.
EXCLUDED = {
    "generate/input_profile.py",  # the SMC-PAD device file, byte-tested against the .qxi
    "generate/channel_probe.py",  # standalone `probe` command (B5)
    "generate/color_palette.py",  # standalone `palette` command (B5)
    "generate/vc_layout.py",  # standalone `layout` command (B5)
    "generate/__init__.py",
}


def test_converted_modules_spell_no_catalogue_word():
    chunks = catalogue_chunks()
    found = [hit for module in CONVERTED for hit in spanish_literals(PACKAGE / module, chunks)]
    assert found == []


def test_every_generator_module_is_converted_or_excluded():
    modules = {str(path.relative_to(PACKAGE)) for path in (PACKAGE / "generate").glob("*.py")}
    assert modules - set(CONVERTED) - EXCLUDED == set()
    # A stale exclusion names a module that no longer exists.
    assert EXCLUDED.issubset(modules)


def test_the_scanner_sees_a_spanish_name(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text(
        '"""Momento Fiesta in a docstring is fine."""\nNAME = "Momento Fiesta"\nAUTO = "AUTO"\n',
        encoding="utf-8",
    )
    assert spanish_literals(source, catalogue_chunks()) == ["sample.py:2 'Momento Fiesta'"]
