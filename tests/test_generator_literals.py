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
    "generate/generate_color_banks.py",
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
    "generate/generate_matrix_effects.py",
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
    "generate/tempo_help_line.py",
    "generate/matrices_frame_caption.py",
    "generate/library_help_lines.py",
    "generate/panels_frame_caption.py",
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
    "generate/add_base_looks.py",
    "generate/add_colour_wheels.py",
    "generate/add_energy_levels.py",
    "generate/add_haze_dimmers_strobes.py",
    "generate/add_intensity_bases.py",
    "generate/add_moments.py",
    "generate/add_movement.py",
    "generate/add_panel_looks.py",
    "generate/add_pixel_layers.py",
    "generate/add_play_wrappers.py",
    "generate/add_rainbows.py",
    "generate/add_show_console.py",
    "generate/add_wheel_looks.py",
    "generate/apply_show_tempo.py",
    "generate/blackout_scene.py",
    "generate/build_canonical_show.py",
    "generate/cycle_algorithms.py",
    "generate/default_matrix_algorithms.py",
    "generate/first_of.py",
    "generate/flat_scene.py",
    "generate/movement_tempo_functions.py",
    "generate/prism_choreography.py",
    "generate/show_build.py",
    "generate/show_chaser.py",
    "generate/show_collection.py",
    "generate/show_path.py",
    "generate/start_show_build.py",
    "generate/steps_are_scenes.py",
    "generate/tap_dial_functions.py",
    "generate/timed_parts.py",
    "generate/wheel_colors_of.py",
    "generate/moments.py",
    "control_glyph.py",
    "generate/smc_pad_bindings.py",
    "generate/smc_pad_colors.py",
    "generate/pad_note.py",
    "generate/live_console.py",
    "generate/play_page.py",
    "generate/desk_bursts.py",
    "desk_policy.py",
    "build_deskmap.py",
    # 2026-09-25: split out of deskmap.py (now build_deskmap.py), which was converted.
    "desk_burst_refusal.py",
    "desk_dial.py",
    "desk_pages.py",
    "desk_unique_key.py",
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
    # 2026-09-25: the rig minimum asks the catalogue for every word it reports.
    "generate/rig_below_minimum.py",
    "generate/is_pixel_group.py",
    "generate/all_self_animating.py",
    "generate/fader_dimmed.py",
    # 2026-09-25: split out of color_banks.py (now generate_color_banks.py), which was converted.
    "generate/bank_for_group.py",
    "generate/bank_wheel.py",
    "generate/generated_bank.py",
    # 2026-09-25: split out of matrix_effects.py (now generate_matrix_effects.py), which was converted.
    "generate/add_matrix.py",
    "generate/generated_matrices.py",
    "generate/matrix_grid.py",
    "generate/matrix_group_name.py",
    "generate/matrix_pace.py",
    # 2026-09-25: the four-colour deal's seats; no catalogue word in it.
    "generate/quad_seats.py",
    "generate/opposite_split.py",
    # 2026-09-26, round G: which tempo line closes page 1's help; identifiers only.
    "generate/tempo_close_line.py",
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
