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
- [ ] **Page 4's matrices caption says "bars and panels" by proxy
  (2026-09-25).** `matrices_frame_caption` picks `matrices_frame` ("patterns
  on the bars and panels") for any rig with pixel groups and built-in effects,
  without checking that the pixel fixtures are bars or that the fixtures with
  programmes are panels. The library help and the panels frame likewise still
  say "panels" and "Effect N" on every rig with built-in effects (the count is
  the rig's since this round). A wording that names what the rig has ("pixel
  fixtures") changes Vibra's text, so it needs the owner's consent to
  re-record the three Vibra hashes. Smallest next step: ask the owner, then
  choose the noun from the capabilities of the fixtures the matrices and the
  built-in effects actually use.
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
