# qlctool follow-up

- [ ] **Verify desk bursts on the rig (2026-09-13).** Normal API priority
  cannot guarantee the Mac Flash's colour or shutter override. The generated
  map marks 15 cues with `burstNote`; durations are provisional. Over AUTO and
  a running shutter chase, compare each burst to its held source, confirm
  release and timeout, then tune `BURST_MS` if needed. Evidence and the
  per-hit judgment: [desk burst findings](docs/2026-09-13-desk-bursts-findings.md).
- [ ] **`newshow` only builds one rig shape (Plan C final review,
  2026-09-25).** Pars only -> traceback `no fixture in this workspace has both
  pan and tilt` (`movement_families.py`); washes only -> `no fixture in this
  workspace has a dimmer` (`dimmer_chases.py`); a rig with no fixture group
  builds but flags empty frames and strobe findings. The README states the
  minimum (a pan/tilt fixture with a dimmer, one group). Smallest next step:
  refuse a rig below it with a message instead of a traceback, then make each
  shape build clean with a dated test in `tests/test_small_rig.py`.
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
- [ ] **Five structural findings entered the codeality baseline (2026-09-25).**
  The gate was red on them beside mypy, and the fix that turned it green was
  told not to restructure modules, so they were recorded as debt instead:
  `checks/run.py` 160 code lines, `generate/color_banks.py` 167 and
  `generate/matrix_effects.py` 155 (cap 150, BPY004);
  `checks/function_references.py` holds four declarations (BPY001);
  `vibra/description.py` holds `vibra_description` (BPY002). Smallest next
  step: split each over-long module and move the three reference helpers
  into files of their own, then `codeality-py baseline update` so the
  entries drop out.
- [!] **CI's suite cannot meet the 120 s test budget (2026-09-25).** With
  mypy and the baseline green, the gate on GitHub still fails its pytest
  stage as `over-budget`: 640 passed in 446 s on 3.11 and 397 s on 3.13
  (run 36127233331; 286 s on run 36122117743). The budget was set on the
  local venv, Python 3.14, where coverage uses `sys.monitoring` and the
  suite takes 75 s on eight workers; the runner has four, and on 3.11 and
  3.13 branch coverage falls back to the C tracer. Measured locally with
  `COVERAGE_CORE=ctrace -n 4`: 300 s. The heaviest tests are the
  `test_check.py` show builds (up to 26 s each on the runner).
  `codeality-py.toml` says never to raise the budget, so this waits on the
  owner: a budget per environment, a larger runner, or cheaper show builds
  in `test_check.py`.
- [ ] **Page 4 counts the panels' effects as 42 on every rig (2026-09-25).**
  Seen fixing the club's captions: `library_2`, `library_6` and
  `panels_frame` say "42" in the catalogue, the number Vibra's panels have,
  while `generate_builtin_effects` builds `min(program.count)` scenes. A rig
  whose built-in effects number otherwise gets the lines with the wrong
  count. Smallest next step: render the count from `len(builtins.scene_ids)`
  through a `{count}` template, with a dated test on a rig with another
  count; Vibra's bytes stay as they are.
