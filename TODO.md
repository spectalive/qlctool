# qlctool follow-up

> Consolidated from the accessible agent conversation history of this
> project. Last reviewed: 2026-10-12. History coverage: Partial. Not re-audited
> during the 2026-10-12 format migration.
>
> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`
> verified complete · `[-]` obsolete or superseded. Closed work moves to
> `TODO_LOG.md`.

- [ ] **Desk bursts on a combined HTP dimmer/strobe channel (C2b, measured
  2026-09-27).** The tablet's bursts are Chasers started with
  `setFunctionStatus`, so the button's ForceLTP never applies, and on the
  MiN Wash (channel 5, dimmer and strobe in one HTP channel) the level's 255
  outbids every strobe value. Marking that channel `ForcedLTP` in the
  workspace `<Fixture>` is not sound. Measured on a :9995 copy of
  Vibra-split: the burst read 236 while it ran and the level's 255 came back
  when it ended, but toggling FIESTA off left the channel at 255 ("Open")
  with nothing running while every other intensity, the 7R blade included,
  went to 0. Read in `~/p/qlcplus/engine/src`: `setChannelCapability` gives
  a ForcedLTP channel an LTP mask without the Intensity bit, so it is not
  zeroed each tick, the grand master skips it (`applyGM`), a fade-out
  targets 0 only for Intensity channels (`GenericFader::setFadeOut`), and
  blackout outputs `m_blackoutValues`, which keep non-HTP values: the rig's
  one channel that neither fades, dims, blacks out nor goes dark when its
  state stops. Smallest alternatives: (a) the levels write that channel at
  its "100%" dimmer value (8 on the MiN) instead of 255, so under HTP every
  strobe value (135-239) outbids it - one generator change and one rule
  (a strobe that no running level can outbid); (b) bursts that reach a
  forced-LTP flash some other way (a widget press of the console's
  ForceLTP flash button). The MiN are spares today (ruling D2), so nothing
  on the rig shows it yet. Caveats of (a), to measure before adopting it
  (round 3 review, M-7): the MiN channel is inverted (0-7 Closed, 8-134 =
  100-0%), so under HTP two concurrent level writers give the darker dim,
  not the brighter; a grand master in Intensity mode scales 8 down into
  0-7 "Closed" instead of dimming; and a fade passes through "Closed" on
  its way to 100%.
- [ ] **Verify desk bursts on the rig (2026-09-13).** Normal API priority
  cannot guarantee the Mac Flash's colour or shutter override. The generated
  map marks 15 cues with `burstNote`; durations are provisional. Over AUTO and
  a running shutter chase, compare each burst to its held source, confirm
  release and timeout, then tune `BURST_MS` if needed. Evidence and the
  per-hit judgment: [desk burst findings](docs/2026-09-13-desk-bursts-findings.md).
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
  184.3 s, wall 69-73 s -> 55 s. The v0.1.11 tag run 36331022760
  (2026-09-27) after those cuts: 575.6 s on 3.11 (96% of 600) and 433.4 s on
  3.13, so the cuts did not reach CI and the leg was one slow runner from
  failing as over-budget. The CI budget was raised to 900 s the same day
  (the budget guards against a hang, not a slow leg); the local 120 s stays.
  Two more tag runs read on 2026-10-19 (the pytest check's own
  `duration_seconds` in `gh run view --log`, budget 900 s): v0.1.12 run
  36333272097 548.2 s on 3.11 (61%; job 573 s wall with setup) and 443.7 s
  on 3.13 (the run failed on codeality-py structural findings, not on a
  test), v0.2.0 run 36371259619 522.4 s on 3.11 (58%; job 548 s) and 490.3 s
  on 3.13 (job 519 s). Since 15ac3a1 only a tag, a pull request or a manual
  run starts the 3.11 leg, so readings arrive one per release.
  Smallest next step: read the next CI runs' 3.11 leg against 900 s; close
  below 50% (450 s) on three runs in a row.
- [ ] **The MiN Wash sit at full in Ambiente (ruling D2, en-sala audit
  2026-09-26).** Their one Dimmer/Strobe channel is in the Intensity group
  and inverted (8 = 100 %, 134 = 0 %), and the levels hold it at 255 "Open"
  through `shutter_open_pairs`, so they are at full while every other fixture
  sits at 110 in Ambiente. Only the strobe was fixed (ForceLTP on the flash
  and strobe buttons, `rule_strobe_masked_by_htp`); the dim was left on
  purpose because both MiN Wash are spares, hidden in the stage plot. Cost if
  they are ever rigged: two washes too bright in every quiet level. Smallest
  next step, when one is rigged: a level that dims a fixture whose only
  intensity path is a combined dimmer/strobe channel writes the dimmer range
  value for that level, with a `check` rule that compares its brightness to
  the level's.
- [ ] **The first bank's wheels colour the ungrouped fixtures too (ruling D9, accepted cost, 2026-09-26):** `Colores`/`Mezcla` of that bank step its keyed solids and splits, which carry the CLB2.4 PARs and fog LED columns, so while a wheel runs over the room wheel the six sum HTP; next step if it bites: point those wheels at extra-free copies appended after the last function.
- [ ] **The ruff ratchet in `ruff.toml` (moved from vibra-lighting,
  2026-09-26).** `ruff check` and `ruff format --check` are clean, so what is
  left is the ignore list, counted with `ruff check . --select <codes>
  --preview --statistics`: D1 (public symbols without a docstring) 244,
  D205/D210 16, PLR0913/PLR0917 (too many parameters) 163, PLR0911/0912/0915
  19, PLR2004 (magic values: DMX channel numbers and QLC+ constants) 43,
  RUF005/RUF059 13. E402 (1) and ARG001 (9) were cleared on 2026-09-27
  (96988c0): the nine unused arguments were dropped from their signatures,
  each with one caller, Vibra x3 identical. RUF005/RUF059 were cleared and
  left `ignore` the same day (72bde18). Recounted on 2026-10-19 (ruff
  0.16.5): D1 465 (D103 373, D101 54, D102 27, D105 5, D104 5, D100 1; D107
  is a permanent ignore), D205/D210 29, PLR0913/PLR0917 223, PLR0911/0912/0915
  22, PLR2004 45, RUF005/RUF059 0, PLW2901/SIM105 0. Smallest next step: drop
  PLW2901 and SIM105 from `ignore` (0 findings), then take D205/D210.
