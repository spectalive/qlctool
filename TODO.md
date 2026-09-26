# qlctool follow-up

- [x] **Flash Color leaves the lit smoke columns out (owner decision,
  2026-09-26).** `Flash Color` (and its desk burst's private copy) skipped
  every smoke fixture, so while held the four vertical LED fog machines kept
  the colour beneath, unstrobed, beside a flashing rig; `Flash 100%` has
  always written them white. Asked, the owner decided "Si, el flash enciende
  las maquinas de humo en blanco" and accepted the byte change. Closed by
  `7740c73 fix(generate): Flash Color lights the lit smoke machines white`:
  `rule_flash_lit_smoke` (a Flash scene that raises light on every non-smoke
  fixture with a dimmer or strobe channel and leaves a lit smoke machine
  unlit) bit Vibra on `Flash Color` only; `generate_flash_color` now writes
  each lit smoke machine `Flash 100%`'s white minus the pump. Vibra x3 and
  `Vibra.desk.json` re-baselined (diff: the four columns in `Flash Color` and
  its desk copy; the desk tile gains a `#ffffff` swatch). Test
  `tests/test_flash_colour_lit_smoke.py`.
- [x] **The SMC-PAD notes still point at `tools/smc-pad/` (2026-09-26).**
  Closed in round G: `generate/input_profile.py` (and so the generated
  `M-VAVE-SMC-PAD.qxi`), `generate/smc_pad_device.py` and
  `generate/smc_pad_colors.py` name `spectalive/smc-pad` (`midicap.swift`,
  `qlc_led_bridge.swift`). The profile now writes only what was measured, as
  QLC+ PR #2168 did by hand: the channel-aftertouch channel 37376 (never in
  the 2026-08-29 capture, bound by no show) is gone, and CC 28 carries the
  manual's name, `Stop (PARAR TODO)`; the console caption stays Pausa. The
  rig copy is rebaselined; Vibra x3 identical (the workspaces carry only the
  profile's name). Test
  `test_2026_09_26_the_profile_declares_only_what_was_measured`.
- [ ] **Verify desk bursts on the rig (2026-09-13).** Normal API priority
  cannot guarantee the Mac Flash's colour or shutter override. The generated
  map marks 15 cues with `burstNote`; durations are provisional. Over AUTO and
  a running shutter chase, compare each burst to its held source, confirm
  release and timeout, then tune `BURST_MS` if needed. Evidence and the
  per-hit judgment: [desk burst findings](docs/2026-09-13-desk-bursts-findings.md).
- [x] **A known model in a mode its definition lacks is warned as "no fixture
  definition" (2026-09-25).** `warn_unresolved` now tells the two cases
  apart from the same `resolved_definition` check as `rule_missing_definition`:
  unknown models keep the `--fixtures` advice (catalogue key
  `unresolved_models`), a known model in a missing mode is told to repatch in
  a mode the definition has, naming the model, the mode and the modes it has
  (`unresolved_mode`, en and es). `newshow` warns in the show's language.
  Closed by `fix(newshow): a known model in a missing mode is told to
  repatch, not to pass --fixtures`, test
  `tests/test_mode_mismatch_warning.py`; Vibra and the club warn nothing.
- [x] **`newshow`'s refusal blames the folder when every fixture is in a
  missing mode (2026-09-25).** `newshow_refusal` rendered
  `rig_without_definitions` ("found no fixture definition ... pass
  --fixtures") whenever nothing patched resolved, also when every definition
  was found and only the modes were wrong. It now renders
  `rig_without_definitions` only when no patched model is known, else
  `rig_without_modes` (en and es), which sends the user to the per-model
  warnings and asks for the repatch. The missing-model / missing-mode
  distinction lives once in `definition_outcome_of` (`DefinitionOutcome`),
  shared by `resolved_definition`, `warn_unresolved`,
  `rule_missing_definition` and the refusal. Closed by `fix(newshow): the
  refusal asks for a repatch when only the modes are missing`, test
  `tests/test_rig_minimum.py` (fails without the fix).
- [x] **`newshow` builds no show for a rig without movement or a dimmer
  (Plan C final review, 2026-09-25).** Closed in round G (2026-09-26):
  `generate_movement_families` returns empty families and
  `generate_dimmer_chases` returns None when the rig has nothing to move or
  chase, and every caller leaves them out; the heads frame, the aiming pad
  and the intensity frame are not drawn empty; the tempo lines and page 3's
  title choose a variant without heads or dimmer, and `rule_caption_promise`
  now holds those captions to a head (pan and tilt) and a fader dimmer.
  `rig_below_minimum` asks only for a fixture group (README, docs and both
  catalogues follow). Tests `tests/test_small_rig.py` (pars only, washes
  only, RGB-only heads: build, `check` clean, QLC+ loads, and the rule bites
  on a heads title put back); Vibra x3 and the club identical.
- [x] **A head with no colour keeps its Effect channel unowned (2026-09-25).**
  Seen building the gobo-spot regression rig: a BEAM 230W 7R with only its
  colour wheel channels stripped keeps `Atomization` (Effect group), and
  `check` reported `modo sin dueño` - `mode_park_pairs` was only called from
  colour looks, which never touch a fixture that mixes no colour. Closed by
  `fix(generate): the intensity levels park the Effect channel of a head no
  colour look reaches`: `energy_intensity` (ambient and full) and
  `dimmerless_intensity` (peak) add `mode_park_pairs` for a fixture with no
  RGB and no colour wheel (`outside_color_looks`), so Vibra's bytes do not
  move. The rig keeps the channel now; test
  `tests/test_colourless_head_park.py` (bites without the fix: two findings).
- [x] **Four-colour deal on a two-fixture group is a split (2026-09-25).**
  Same session: two Vortex pars as the only colour group -> `Rig 4 Colores 4`
  puts two complementary colours in one group (`complementarios en un mismo
  lavado`). Closed: `tests/test_quad_deal.py` builds two pars in a group of
  their own beside the club's heads and failed on `Rig 4 Colores 4` (180
  degrees, Par 1 / Par 2); `generate/quad_seats.py` moves the second member of
  a two-member group to the nearest seat that stays under the rule's own
  `COMPLEMENTARY_FROM` in every rotation (blue/green, red/yellow). Vibra
  identical x3 and QLC+ loaded; the club example regenerates byte for byte.
- [x] **Three long modules sit in the codeality baseline (2026-09-25).**
  The gate was red on them beside mypy, and the fix that turned it green was
  told not to restructure modules, so they were recorded as debt instead:
  `checks/run.py` 160 code lines, `generate/color_banks.py` 167 and
  `generate/matrix_effects.py` 155 (cap 150, BPY004). Closed by 415ff26
  (`canvas_of`, `default_canvas`, `applying_providers`), a3e5ac6
  (`bank_for_group`, `bank_wheel`, `GeneratedBank`) and 557a0d3
  (`add_matrix`, `matrix_pace`, `matrix_grid`,
  `matrix_group_name`, `GeneratedMatrices`), bodies moved verbatim; `baseline
  update` dropped the three BPY004 entries and the three modules' BPY001
  entries (more than one unit per module), and recorded three new BPY002
  entries, one per module, whose file name no longer matches its only unit
  (209 -> 206). Vibra identical x3.
- [x] **Three modules are not named after their unit (2026-09-25).** BPY002
  since the split above. Closed by e941b10: `checks/run.py` is
  `checks/check_workspace.py`, `generate/color_banks.py` is
  `generate/generate_color_banks.py` and `generate/matrix_effects.py` is
  `generate/generate_matrix_effects.py`; every importer in `qlctool/` and
  `tests/` (the controller-reach test starts from `check_workspace`) follows,
  and `baseline update` dropped the three entries (206 -> 203).
- [x] **CI's suite cannot meet the 120 s test budget (2026-09-25).** The
  gate on GitHub failed its pytest stage as `over-budget` on the four-core
  runners, where branch coverage falls back to the C tracer below 3.14: 286 s
  (run 36122117743), then 446 s on 3.11 and 397 s on 3.13 (run 36127233331).
  Solved by codeality-py 0.2.4's `CODEALITY_PY_TEST_BUDGET_SECONDS`, set to
  600 on the workflow's gate step; the local budget in `codeality-py.toml`
  stays 120 s. Closed by the green run 36131008406: 476.8 s on 3.11 and
  359.9 s on 3.13, under the 600 s budget.
- [ ] **CI's 3.11 leg uses 55-83% of its test budget (2026-09-25).** 476.8 s
  of 600 s in run 36131008406, 447.0 s (3.13: 391.8 s) in 36136963884, 496.9 s
  (3.13: 398.2 s) in 36156626545 after the check suite shared its one repeated
  build (fe126b1), 329.2 s (3.13: 399.8 s) in 36157628167 on the same code,
  and 466.8 s (3.13: 377.7 s) in 36158448357 on fe5a0ac: the leg varies by up
  to 170 s between runs, so one run under 60% of the budget does not close
  this. Measured locally, the show builds are not where the time goes:
  `tests/test_check.py` single-process went from 162.1 s to 155.9 s, and a
  canonical build costs 0.4-0.6 s while `check_workspace` costs about 1.6 s
  and runs 98 times, nearly all on a workspace the test has edited, so those
  cannot be shared (a few, and the gate test, run on unedited builds). Half
  of one `check_workspace` is `check_pick_darkens` (`instant_dark_fixtures`
  -> `instant_evaluator`).
  Profiled on 2026-09-26 (e8a8ae3): the instant evaluator keyed a node's memo
  on the frame's whole set of stopped hooks and rebuilt every (state, pick)
  pair from scratch; it now keys on the stopped hooks the node can reach and
  composes a pair from each root's cached result. One `check_workspace` on the
  frozen Vibra went from about 1.44 s (0.68 s of it `check_pick_darkens`) to
  about 1.23 s (0.37-0.46 s), and `tests/test_check.py` single-process from
  160.0 s to 142.7 s; every finding is identical (Vibra x3, DeluxeEventos2's
  791, an injected-bug Vibra and the club, byte for byte). The v0.1.4 tag
  run 36197886956 after it: 454.0 s on 3.11 (76%) and 395.2 s on 3.13, so
  the cache did not move CI beyond run-to-run noise.
  Round G (2026-09-26), local, `-n auto`, load 9-56 on 8 cores: the suite's
  summed test time was 480.9 s, 259.9 s of it `tests/test_check.py` (54%),
  whose ~100 `check_workspace` calls on edited workspaces cannot share a
  build. Two cuts to the check itself, every finding identical (2471
  findings, 1149 of them `pick_darkens`, over Vibra x3, DeluxeEventos,
  DeluxeEventos2 as shipped and rebuilt, its v5 copy, Pantera and the club):
  `pick_darkens` answers a pick that writes no colour, dimmer or strobe
  channel (movement, gobo, prism) from the state alone, once per frame
  (`pick_leaves_light_alone`), and every rule reads a scene's channels
  through the graph's parse cache (`ShowGraph.driven_of`) instead of
  re-parsing it once per rule. One check of Vibra-split: 1.16-1.22 s ->
  0.74-0.76 s. Suite: summed 480.9 s -> 393.9 s, `test_check.py` 259.9 s ->
  184.3 s, wall 69-73 s -> 55 s. Smallest next step: read the next CI runs'
  3.11 leg; close below 50% (300 s).
- [ ] **The ruff ratchet in `ruff.toml` (moved from vibra-lighting,
  2026-09-26).** `ruff check` and `ruff format --check` are clean, so what is
  left is the ignore list, counted with `ruff check . --select <codes>
  --preview --statistics`: D1 (public symbols without a docstring) 244,
  D205/D210 16, PLR0913/PLR0917 (too many parameters) 163, PLR0911/0912/0915
  19, PLR2004 (magic values: DMX channel numbers and QLC+ constants) 43,
  ARG001 9, RUF005/RUF059 13, E402 1. Smallest next step: take one code whose
  count is small (E402, ARG001), clear it and drop it from `ignore`, so the
  list can only shrink.
- [x] **Every `zip()` without `strict=` (B905), moved from vibra-lighting
  (2026-09-26).** 29 sites (12 in `qlctool/`, 17 in `tests/`), not the 13 the
  note counted. Every one pairs two lists built from the same source, so a
  length mismatch is a bug, not an intended cut: all 29 are `strict=True`
  and B905 left the `ignore` list (5965909). Vibra x3 identical.
- [ ] **The mypy ratchet in `mypy.ini` (moved from vibra-lighting,
  2026-09-26).** 70 modules carry `ignore_errors`; with every one of them
  switched off mypy finds 226 errors in 70 files, nearly all missing
  annotations (`lxml-stubs` is installed). Round G took
  `generate/canonical_show` off the list (from 71 modules and 260 errors).
  Smallest next step: annotate the smallest listed module and delete its
  section; a section is never added.
- [ ] **The codeality structural baseline (moved from vibra-lighting,
  2026-09-26).** `codeality-py check` gives 198 findings, all in the baseline
  (`baseline check`: 0 new, 198 known): BPY001 116, BPY002 72, BPY004 10. The
  ten oversize files, in code lines (cap 150, tests 300):
  `generate/live_console.py` 1159, `cli.py` 794, `generate/play_page.py` 785,
  `generate/movement_families.py` 574, `checks/family_frames.py` 272,
  `checks/rule_console.py` 177, `generate/unison_colors.py` 163,
  `tests/test_check.py` 2129, `tests/test_live_console.py` 677,
  `tests/test_canonical_show.py` 504. Round G split `canonical_show.py`
  (1061 code lines) into its stages (d555b53), Vibra x3 identical. Most of
  the BPY001 mass is the rules in `checks/` keeping their private helpers
  beside them. Smallest next step: split `live_console.py` the same way, one
  file per commit with the three Vibra hashes unchanged, then
  `codeality-py baseline update`. Constant tables are declared `[roles]
  data` in `codeality-py.toml`, which is the convention, not debt.
- [x] **A wheel whose only nameable detent is one no look asks for is not
  parked (2026-09-25).** `outside_color_looks` asked over every colour in
  `WHEEL_NAMES`; it now asks over the colours the looks request, the show's
  palette, which `build_canonical_show` hands both intensity generators.
  Closed by 3a34043, test `tests/test_unrequested_detent_park.py` (a BEAM 230W
  7R whose wheel names only UV, on a palette without purple or ultraviolet:
  `modo sin dueño` before, nothing after). Vibra identical x3.
- [x] **The vertical-smoke light chaser is built where nothing starts it
  (2026-09-25).** Vibra without its smoke machines (fixtures 17, 29-32)
  carried the panels' `Humo Vertical` chaser with no button to start it.
  Decision (the owner delegated it, 2026-09-25): the light is built only where
  a vertical column is. Closed by `fix(generate): the vertical-smoke light is
  built only where a column is patched`: `vertical_smoke_columns` (a smoke
  machine with a red channel, `is_lit_smoke`) is the one answer both
  `vertical_smoke_burst` and `vertical_smoke_light` ask, so they cannot drift.
  Tests `tests/test_vertical_smoke_columns.py` (the no-smoke build has one
  function fewer than the same build with the light forced; fails without the
  fix) and `tests/test_lit_smoke_wash.py` (the columns' LEDs stay a wash in
  every room colour, their LED master at full in the levels and their pump at
  zero, on Vibra and on Vibra without its fog-only machine). Vibra identical x3.
  - [ ] A `check` rule for a built function that no button, chaser,
    collection or input binding reaches would have seen this. Caveat: some
    functions are reached only through the input profile (the pad's
    bindings), so the rule must read the profile too, or it flags them.
- [-] **`Flash Color` leaves the lit smoke machines out of the strobe
  (2026-09-25).** Superseded by the owner's answer on 2026-09-26 ("Si, el
  flash enciende las maquinas de humo en blanco"): the columns go white, not
  strobing. Done in `7740c73` and `a6c6647` (v0.1.5); releasing the flash
  leaves nothing latched, measured in a live QLC+ 5.2.2 (vibra-lighting
  `TODO_LOG.md`, 2026-09-26).
- [x] **Page 4's matrices caption says "bars and panels" by proxy
  (2026-09-25).** `matrices_frame` was chosen for any rig with pixel groups
  and built-in effects, and the panels frame and library help said "panels"
  on any rig with built-in effects. Decision (the owner delegated it,
  2026-09-25): the nouns come from the fixtures' definitions, and Vibra's rig
  yields its current words. Closed by `fix(console): page 4 names bars and
  panels only where the rig has them`: `is_bar` (more than one pixel head,
  the `<Layout>` one row or one column holding exactly those heads) and
  `is_panel` (an internal programme, no pan or tilt, one cell or a grid of
  heads); `matrices_frame_caption`, `panels_frame_caption` and
  `library_help_lines` choose "bars and panels", the bars, the panels or the
  generic words; `caption_promises` promises a bar and a panel instead of a
  pixel group. Tests in `tests/test_caption_variants.py` (Vibra cut to both,
  bars only, panels only, neither; a club with CLB2.4 bars built end to end
  and checked clean; the club keeps its words) and
  `tests/test_mixed_rig_captions.py` (panels and no bars). Vibra identical x3.
- [x] **No `check` rule sees a caption that promises a missing function
  (2026-09-25).** The club's console named gobos, prism and panels it lacks;
  tests now cover the captions, but `qlctool check` had no rule for "a caption
  on a page or frame promises a function the show did not build". Closed by
  `rotulo que promete lo que no hay` (`checks/rule_caption_promise.py`):
  `checks/caption_promises.py` maps every identifier the four caption
  selectors can choose to what its text promises (gobo, prism, haze, beam
  wheel, pixel group, built-in effects); the rule finds a caption's identifier
  by matching it against every shipped catalogue and asks the patch through
  `promise_kept`. Two dated tests in `tests/test_check.py` put `tempo_2`, and
  the English `matrices_frame` and `library_2`, back on the club and the rule
  bites; Vibra (which matches seven promising captions) and the club stay
  clean. Limit: a `[names]` override of those captions is not judged.
- [x] **An English show's `check` reads in Spanish (ruling B10, 2026-09-25).**
  The controller decided (the owner delegated it) that the check side follows
  the spec's "Multilingual" section: every rule has an English identifier and
  a display name per language. Round 1 (026fca4, 64a10de): `Finding.rule_id`,
  a `[checks]` section in `es.toml` and `en.toml`, the rules named in
  `workspace_language` in one place, and the summary lines from `[messages]`.
  Round 2: every finding message is a `[findings]` entry (`message_id` and
  `fields`, with `Phrase` and `Joined` for catalogue words and lists), rendered
  in the workspace's language by `checks/named_findings.py`; the helper
  builders (`desk_burst_errors`, `family_frames`) return phrases, the promise
  words are catalogue entries, and the intensity plural is two entries.
  `named_in_order` is split into `named_findings` and `fixing_order`,
  `rule_display_name` is `display_name_of_rule`, no `Finding` passes its rule
  positionally, and `docs/checks.md` describes all 67 rules in one table.
  Evidence: Vibra's check output `cmp`-identical on the frozen Vibra and on
  the injected-bug copy (29 findings in 5 rules); every one of the 2296
  distinct findings the suite built before round 2 is rebuilt with the same
  Spanish message; the club without `--fixtures` reads English end to end.
  Tests `tests/test_check_finding_catalogue.py` (drift) and
  `tests/test_english_check_names.py` (dated).
- [x] **`deskmap`'s refusal of an invalid desk burst reads in Spanish
  (2026-09-25).** Closed by 0c8f7c4: `desk_burst_refusal` renders each
  finding's `message_id` with the vocabulary `build_deskmap` holds.
  `deskmap.py` is `build_deskmap.py`, and its two helpers and page assembly
  moved out verbatim (`desk_unique_key`, `desk_dial`, `desk_pages`), so it is
  under the cap (baseline 203 -> 201). Test
  `tests/test_english_desk_burst_refusal.py`.
- [x] **The deskmap refusal's frame stays English on a Spanish show (review
  of round C, 2026-09-26).** Closed 2026-09-26 (round D1): the frame is
  `[messages] desk_bursts_invalid` and the accent refusal
  `desk_burst_no_accent`, both locales, rendered with `build_deskmap`'s
  vocabulary. Test `test_2026_09_26_the_refusal_frame_reads_in_the_show_language_too`
  (`tests/test_english_desk_burst_refusal.py`), Spanish and English.
- [x] **Show `[names]` overrides do not reach the finding text (review of B10
  round 2, 2026-09-26).** Closed 2026-09-26 (round D1). A saved workspace
  records its language but not the words its description renamed, so the
  description is handed in: `check_workspace(..., names=)`,
  `named_findings(..., names)` and `qlctool check --description`, as
  `deskmap` already did. Without it nothing changes (Vibra's check output is
  identical). Test `tests/test_show_names_in_findings.py`: a renamed
  `full_white` in `wheel_white`'s message, and the club checked end to end
  with an override.
- [x] **An override that breaks ruling B7 crashes the build instead of being
  refused (final review of Plan B, 2026-09-25; moved from vibra-lighting).**
  `hit_button_flash = "BANG · Space"` failed in the desk bursts with "burst
  duration must be positive: bang". Closed 2026-09-26 (round D1):
  `reject_hit_button_heads` beside `reject_frame_head_renames` refuses an
  override after which the desk's own lookup (`desk_burst_identifier` over
  the show's names) no longer finds a `hit_button_*`'s own `hit_*`, naming
  the description. After the D1 review it asks exactly the desk's question:
  `hit_flash = "Red"` with its button refused (Red is also a colour), a
  leading glyph accepted, and a hit renamed with its button builds its desk
  burst. Tests `tests/test_hit_button_heads.py`.
- [x] **`qlctool check` still lives in `cli.py` (review of round D1,
  2026-09-26).** Closed in round G: `cmd_check` and its parser moved to
  `cmd_check.py` and `add_check_parser.py`, the `pad-palette` shape; `cli.py`
  only wires them (945 -> 917 lines).
- [x] **Most of `function_references`' paths have no test (Task 2a review,
  2026-09-25; moved from vibra-lighting).** Closed 2026-09-26 (round D1):
  `tests/test_dangling_reference_paths.py` breaks a clock `<Schedule
  Function>`, an XY pad `<FuncID>`, a cue list `<Chaser>`, a Show's
  `ShowFunction` and `Track SceneID`, and a Sequence's `BoundScene` one at a
  time; the rule bites on every one, so it needed no fix.
- [x] **`is_panel` calls a plain PAR with a built-in programme a panel
  (review of 4b50144..655b97d, 2026-09-25).** Closed by f195b2a: a one-cell
  fixture is a panel only with a panel's body (`has_panel_face`: a
  `<Dimensions>` face half again as wide as tall, and shallower than tall).
  Vibra's WX-60WPS is 250 x 130 x 70; the LED PAR 64 AT3 (274 x 268 x 433),
  the SlimPAR T6 (84 x 226 x 181) and every other PAR fail it. Of the 32
  upstream modes it accepted, 6 remain: the Wash FX and Frost FX Bar W grids
  (three modes) and the KLS-180-6 and PartyBar2 light bars (three modes). Test `tests/test_par_is_not_a_panel.py`;
  Vibra identical x3.
