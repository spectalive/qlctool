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
- [ ] **`newshow`'s refusal blames the folder when every fixture is in a
  missing mode (2026-09-25).** `newshow_refusal` renders
  `rig_without_definitions` ("found no fixture definition ... pass
  --fixtures") whenever nothing patched resolves, also when every definition
  was found and only the modes are wrong; the warning printed just above it
  now says "repatch". Smallest next step: choose `rig_without_definitions`
  only when no patched model is known, else a catalogue key that sends the
  user to the per-model warnings, with a dated test in
  `tests/test_rig_minimum.py`.
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
- [ ] **A head with no colour keeps its Effect channel unowned (2026-09-25).**
  Seen building the gobo-spot regression rig: a BEAM 230W 7R with only its
  colour wheel channels stripped keeps `Atomization` (Effect group), and
  `check` reports `modo sin dueño` - `mode_park_pairs` is only called from
  colour looks, which never touch a fixture that mixes no colour. The test rig
  strips that channel too. Smallest next step: park Effect channels on a look
  that lights such a head (dimmer or gobo scene), with a dated test.
- [ ] **Four-colour deal on a two-fixture group is a split (2026-09-25).**
  Same session: two Vortex pars as the only colour group -> `Rig 4 Colores 4`
  puts two complementary colours in one group (`complementarios en un mismo
  lavado`). Smallest next step: a dated small-rig test with a two-par group,
  then deal the four colours so no group gets exactly two opposite hues.
- [x] **Three long modules sit in the codeality baseline (2026-09-25).**
  The gate was red on them beside mypy, and the fix that turned it green was
  told not to restructure modules, so they were recorded as debt instead:
  `checks/run.py` 160 code lines, `generate/color_banks.py` 167 and
  `generate/matrix_effects.py` 155 (cap 150, BPY004). Closed by 415ff26
  (`canvas_of`, `default_canvas`, `applying_providers`), a3e5ac6
  (`bank_for_group`, `bank_wheel`, `GeneratedBank`) and 557a0d3
  (`add_matrix`, `matrix_pace`, `matrix_grid`,
  `matrix_group_name`, `GeneratedMatrices`), bodies moved verbatim; `baseline
  update` dropped the three BPY004 entries (209 -> 206; the three modules'
  BPY002 entries were re-recorded at their new lines). Vibra identical x3.
- [x] **CI's suite cannot meet the 120 s test budget (2026-09-25).** The
  gate on GitHub failed its pytest stage as `over-budget` on the four-core
  runners, where branch coverage falls back to the C tracer below 3.14: 286 s
  (run 36122117743), then 446 s on 3.11 and 397 s on 3.13 (run 36127233331).
  Solved by codeality-py 0.2.4's `CODEALITY_PY_TEST_BUDGET_SECONDS`, set to
  600 on the workflow's gate step; the local budget in `codeality-py.toml`
  stays 120 s. Closed by the green run 36131008406: 476.8 s on 3.11 and
  359.9 s on 3.13, under the 600 s budget.
- [ ] **CI's 3.11 leg uses 55-83% of its test budget (2026-09-25).** 476.8 s
  of 600 s in run 36131008406, 447.0 s in 36136963884, 496.9 s (3.13: 398.2 s)
  in 36156626545 after the check suite shared its one repeated build
  (fe126b1), and 329.2 s (3.13: 399.8 s) in 36157628167 on the same code:
  the leg varies by up to 170 s between runs, so one run under 60% of the
  budget does not close this. Measured locally, the show
  builds are not where the time goes: `tests/test_check.py` single-process
  went from 162.1 s to 155.9 s, and a canonical build costs 0.4-0.6 s while
  `check_workspace` costs about 1.6 s and runs 98 times, each on a workspace
  the test has edited, so it cannot be shared. Half of one `check_workspace`
  is `check_pick_darkens` (`instant_dark_fixtures` -> `instant_evaluator`).
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
- [ ] **No `check` rule sees a caption that promises a missing function
  (2026-09-25).** The club's console named gobos, prism and panels it lacks;
  tests now cover the captions, but `qlctool check` has no rule for "a caption
  on a page or frame promises a function the show did not build". It would
  reason about the catalogue identifiers the generator chose and the functions
  it built, never about names. Smallest next step: record, beside each
  generator-owned caption identifier, the `master` identifiers it promises,
  and have a rule report a caption whose promised functions are absent.
