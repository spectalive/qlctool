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
    "generate/generate_builtin_effects.py",
    "generate/generate_color_banks.py",
    "generate/generate_color_flashes.py",
    "generate/generate_flash_color.py",
    "generate/generate_multicolor_scenes.py",
    "generate/generate_pixel_base.py",
    "generate/generate_pixel_wheel_matrices.py",
    "generate/generate_quad_color_scenes.py",
    "generate/generate_rainbow_efx.py",
    "generate/generate_unison_colors.py",
    "generate/generate_panel_manual.py",
    "generate/generate_panel_speed_auto.py",
    "generate/generate_vertical_smoke_light.py",
    "generate/generate_matrix_effects.py",
    "generate/generate_beam_rainbow_spin.py",
    "color_wheel_pairs.py",
    "checks/detent_white.py",
    "efx_algorithms.py",
    "generate/generate_movement_efx.py",
    "generate/generate_movement_families.py",
    "generate/generate_home_position.py",
    "generate/generate_cross_position.py",
    "generate/generate_fan_position.py",
    "generate/generate_stage_aim.py",
    "generate/generate_wheel_scenes.py",
    "generate/without_wheel_blades.py",
    "generate/add_family_floors.py",
    "generate/prepend_collection_steps.py",
    "generate/written_channels.py",
    "generate/page_control_title.py",
    "generate/tempo_help_line.py",
    "generate/matrices_frame_caption.py",
    "generate/library_help_lines.py",
    "generate/wheel_only_fixture_ids.py",
    "generate/store_suffix.py",
    "generate/panels_frame_caption.py",
    "generate/generate_dealt_gobo_scenes.py",
    "generate/generate_prism_spins.py",
    "generate/generate_beam_subsets.py",
    "generate/generate_dimmer_chases.py",
    "generate/generate_dimmer_sequence.py",
    "generate/generate_dimmerless_intensity.py",
    "generate/generate_energy_intensity.py",
    "generate/generate_energy_levels.py",
    "generate/generate_smoke_auto.py",
    "generate/generate_strobe_effects.py",
    "generate/generate_vertical_smoke_burst.py",
    "generate/generate_play_wrappers.py",
    "generate/generate_gobo_shake.py",
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
    "generate/generate_moments.py",
    "glyph.py",
    "generate/smc_pad_bindings.py",
    "generate/function_colors.py",
    "generate/readable_foreground.py",
    "generate/pad_note.py",
    "generate/live_console.py",
    "generate/build_play_page.py",
    "generate/generate_desk_bursts.py",
    "placement.py",
    "build_deskmap.py",
    # 2026-09-25: split out of deskmap.py (now build_deskmap.py), which was converted.
    "desk_burst_refusal.py",
    "desk_dial.py",
    "desk_pages.py",
    "desk_unique_key.py",
    "desk_burst_note.py",
    # Task 12a (2026-09-25): no catalogue word in them; the scanner holds them clean.
    "generate/apply_beat_tempo.py",
    "generate/bind_pad.py",
    "generate/color_scene_values.py",
    "generate/dealt_wheel_color.py",
    "generate/generated_color_flashes.py",
    "generate/generated_play_wrappers.py",
    "generate/movement_aim.py",
    "generate/park_work_light.py",
    "generate/generate_rest_scene.py",
    "generate/smc_pad_device.py",
    "generate/split_color_scene_values.py",
    "generate/generate_stage_layout.py",
    "generate/apply_stage_plot.py",
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
    # 2026-09-26, en-sala round 1: the colour fixtures a bank key would skip.
    "generate/ungrouped_colour_fixture_ids.py",
    # 2026-09-26, en-sala round 2: the heads `Alternado` reverses.
    "generate/alternate_mirror.py",
    # 2026-09-26, en-sala round 2: what a build stage refuses to make.
    "generate/build_refusal_error.py",
    # 2026-09-26, en-sala round 2: the MACs held on a beam-only look.
    "generate/generate_wash_hold.py",
    # 2026-09-27, en-sala round 2 review: the heads a fan spreads.
    "generate/fan_heads.py",
    # 2026-09-27, en-sala DMX re-audit: the size a turned figure fits at.
    "generate/fit_rotated_figure.py",
    # 2026-09-27: the live console split; every table and page moved verbatim.
    "generate/console_layout.py",
    "generate/generated_console.py",
    "generate/console_ids.py",
    "generate/on_page.py",
    "generate/swatch.py",
    "generate/bank_caption.py",
    "generate/mix_caption.py",
    "generate/after_marker.py",
    "generate/before_marker.py",
    "generate/root_frame.py",
    "generate/function_names.py",
    "generate/set_canvas.py",
    "generate/wheel_frame.py",
    "generate/page_library.py",
    "generate/page_control.py",
    "generate/page_show.py",
    # 2026-09-27: page 1 cut along its frames, room states first.
    "generate/room_states.py",
    "generate/hits.py",
    "generate/panic.py",
    "generate/haze_row.py",
    "generate/tempo_dial.py",
    # 2026-09-27: page 3 cut along its frames, the bank column first.
    "generate/bank_column.py",
    "generate/intensity.py",
    "generate/grand_master.py",
    "generate/aim_pad.py",
    "generate/movement_dial.py",
    # 2026-09-27: page 4 cut along its frames, mixes first.
    "generate/mixes.py",
    "generate/matrix_frame.py",
    "generate/cycles.py",
    "generate/panels.py",
    "generate/speed_fader.py",
    "generate/live_matrix.py",
    "generate/library_help.py",
    # 2026-09-27: live_console's widget closures move to their own factories.
    "generate/button_factory.py",
    "generate/frame_factory.py",
    "generate/label_factory.py",
    "generate/master_button_factory.py",
    "generate/console_outer_frame.py",
    "generate/audio_triggers_row.py",
    "generate/play_page_call.py",
    "generate/console_widgets.py",
    # 2026-09-27, batch 5: split out of smc_pad_device.py, which was converted.
    "generate/control_channel.py",
    # 2026-09-27, batch 5: split out of the modules named alongside them below,
    # all of which were already converted.
    "generate/generated_builtins.py",
    "generate/generated_probe.py",
    "generate/generated_palette.py",
    "generate/moment.py",
    "generate/generated_rainbows.py",
    "generate/generated_wheel.py",
    "generate/fixture_val_pairs.py",
    "generate/generated_gobo_shake.py",
    "generate/spaced.py",
    "generate/generated_prism_spins.py",
    "generate/preset_value.py",
    "generate/wheel_halves.py",
    "generate/generated_stage.py",
    "generate/unplaced_fixtures.py",
    "generate/spread.py",
    # 2026-09-27, batch 5 continued: split out of the modules named alongside
    # them below, all of which were already converted.
    "generate/generated_smoke.py",
    "generate/beat_timing.py",
    "generate/beat_units.py",
    "generate/to_beats.py",
    "generate/generated_dimmers.py",
    "generate/half_lit.py",
    "generate/generated_intensity.py",
    "generate/intensity_scene.py",
    "generate/energy_level.py",
    "generate/generated_energy.py",
    # 2026-09-27, batch 5: split out of input_profile.py (excluded below, but
    # these carry no Spanish literal of their own).
    "generate/pads_top_down.py",
    "generate/profile_channel.py",
    "generate/profile_ns.py",
    # 2026-09-27, batch 5: split out of movement_efx.py (now generate_movement_efx.py),
    # which was converted.
    "generate/generated_movements.py",
    "generate/moving_head_ids.py",
    "generate/spread_offsets.py",
    # 2026-09-27, batch 5: split out of strobe_effects.py (now generate_strobe_effects.py)
    # and unison_colors.py (now generate_unison_colors.py), which were converted;
    # add_scene.py is shared by both.
    "generate/add_scene.py",
    "generate/generated_strobes.py",
    "generate/held_values.py",
    "generate/shutter_values.py",
    "generate/generated_unison.py",
    "generate/contrast_values.py",
    "generate/wheel_step.py",
    # 2026-09-27, batch 5: split out of vc_layout.py (now generate_vc_layout.py,
    # excluded below, but these carry no Spanish literal of their own). _console_frame was
    # identical to the existing root_frame.py and reuses it instead.
    "generate/generated_layout.py",
    "generate/first_free_y.py",
    "generate/background_for.py",
    "generate/grow_console.py",
    # 2026-09-27, batch 5: split out of play_wrappers.py (now generate_play_wrappers.py),
    # which was converted. spaced.py (split earlier out of gobo_shake.py, now
    # generate_gobo_shake.py) is generic now and
    # reused here instead of a second identical _spread.
    "generate/play_wrap.py",
    # 2026-09-27, batch 5: split out of beam_subsets.py (now generate_beam_subsets.py),
    # which was converted.
    "generate/generated_beam_subsets.py",
    "generate/inserted_prism.py",
    "generate/parked_prism.py",
    "generate/prism_scene.py",
    "generate/multicolor_offset.py",
    "generate/multicolor_scene.py",
    # 2026-09-27, batch 5: split out of movement_families.py (now
    # generate_movement_families.py), which was converted.
    "generate/envelope.py",
    "generate/generated_families.py",
    # 2026-09-27, batch 5: split out of play_page.py (now build_play_page.py),
    # which was converted.
    "generate/play_page_layout.py",
    "generate/grid_position.py",
    "generate/source_name.py",
    "generate/pick_caption.py",
    "generate/hook.py",
    "generate/bound_pick.py",
    "generate/pick.py",
    "generate/build_reset_strip.py",
    "generate/build_colour_hits.py",
    "generate/build_color_family.py",
    "generate/build_pixel_family.py",
    "generate/build_movement_family.py",
    "generate/build_gobo_family.py",
    "generate/build_prism_family.py",
)

# Ruling B6: modules that keep their literals, and why.
EXCLUDED = {
    "generate/input_profile.py",  # the SMC-PAD device file, byte-tested against the .qxi
    "generate/generate_channel_probe.py",  # standalone `probe` command (B5)
    "generate/generate_color_palette.py",  # standalone `palette` command (B5)
    "generate/generate_vc_layout.py",  # standalone `layout` command (B5)
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
