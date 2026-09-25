# qlctool follow-up

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
- [ ] **`newshow` builds no show for a rig without movement or a dimmer
  (Plan C final review, 2026-09-25).** Pars only stopped at a traceback `no
  fixture in this workspace has both pan and tilt` (`movement_families.py`),
  washes only at `no fixture in this workspace has a dimmer`
  (`dimmer_chases.py`), and a rig with no fixture group built but flagged
  empty frames and strobe findings. Since 2026-09-25 `newshow` refuses a patch
  below the README's minimum (a pan/tilt fixture, a fixture with a fader
  dimmer outside a pixel group and not self-animating, one fixture group) up
  front, with a catalogue message and exit 1
  (`generate/rig_below_minimum.py`, `tests/test_rig_minimum.py`). Still open:
  building a show for a pars-only or washes-only rig. Smallest next step: make
  the movement and dimmer generators optional when the rig lacks them, one
  shape at a time, each with a dated test in `tests/test_small_rig.py`.
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
- [ ] **Three modules are not named after their unit (2026-09-25).** BPY002
  since the split above: `checks/run.py` holds `check_workspace`,
  `generate/color_banks.py` holds `generate_color_banks` and
  `generate/matrix_effects.py` holds `generate_matrix_effects`. Smallest next
  step: rename each module after its unit (or the unit after the file) and
  let `baseline update` drop the three entries. `checks/run.py` is imported
  across `qlctool/` and `tests/` (and by the rule-provider contract test), so
  its rename is a coordinated one.
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
  Smallest next step: profile `check_pick_darkens` and cache the instant
  states it recomputes per pick, measured with `--durations` before and after.
- [ ] **A wheel whose only nameable detent is one no look asks for is not
  parked (2026-09-25).** `outside_color_looks` tries every colour in
  `WHEEL_NAMES`, but the looks only ask for the show's palette: a colour wheel
  whose only position `color_wheel_pairs` can name is one no look requests
  (only "UV", say) counts as inside the looks, so neither the colour looks nor
  the intensity levels park its self-running channel. No rig in the repo has
  such a wheel (review of ecc61b5). Smallest next step: build a definition
  with such a wheel, show `modo sin dueño` on it, then ask `color_wheel_pairs`
  over the colours the looks request instead of `WHEEL_NAMES`.
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
- [ ] **`Flash Color` leaves the lit smoke machines out of the strobe
  (2026-09-25).** Found pinning the owner's rule that a smoke machine with RGB
  is a wash even with no smoke (`tests/test_lit_smoke_wash.py`):
  `generate_flash_color` skips every `is_smoke` fixture, the lit ones too, so
  while `Flash Color` (and its desk burst) is held the four vertical columns
  keep their colour and level but do not strobe with the room. No look skips
  their RGB. Smallest next step: ask the owner whether the columns should
  strobe with the room; if yes, skip only `is_smoke and not is_lit_smoke`
  there, as `color_scene_values` does, and re-record Vibra's three hashes.
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
- [ ] **`deskmap`'s refusal of an invalid desk burst reads in Spanish
  (2026-09-25).** `build_deskmap` raises "invalid desk bursts: ..." joining
  `Finding.message`, which outside `check_workspace` is the Spanish rendering.
  Smallest next step: render each finding's `message_id` with the vocabulary
  `build_deskmap` already holds (`checks/rendered_value.py`).
- [ ] **`is_panel` calls a plain PAR with a built-in programme a panel
  (review of 4b50144..655b97d, 2026-09-25).** `qlctool/is_panel.py:26`: the
  one-cell case (`heads == 1`, layout 1 x 1) accepts any single-head fixture
  that neither pans nor tilts and has an `internal_program`, so 26 plain PAR
  modes in the upstream QLC+ library (e.g. LED PAR 64 AT3, SlimPAR T6) are
  "panels", and page 4 would name panels on a rig of PARs. Not changed yet:
  Vibra's panels (fixtures 24, 25, 27, 28, WX-60WPS) declare one head and a
  1 x 1 layout, so the obvious fix darkens Vibra's own words. Smallest next
  step: read what those four declare (heads, `<Layout>`, physical size) and
  choose the panel noun's extra condition from that - more than one head, a
  `<Layout>` larger than one cell, or a physical shape - with a dated test
  that builds a PAR 64 AT3 rig and a Vibra panel rig and keeps Vibra's bytes.
