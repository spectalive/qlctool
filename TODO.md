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
