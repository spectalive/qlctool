# Briefing: bounded bursts for the tablet desk (implementation, bounded)

Work only in `/Users/cristiandeluxe/p/DMX-Fixtures-bursts` (branch
`codex-bursts`), the `tools/qlctool` package and the `QLC+ Setups` it
regenerates. Read `AGENTS.md` at the root (the regeneration recipe: all three
shows, `--validate`; the rule-first convention: a check under
`tools/qlctool/qlctool/checks/` with a dated regression before a generator
changes), then `tools/qlctool/qlctool/generate/live_console.py` (the hits:
Flash buttons with Override priority over Scenes in the `GOLPES` frame,
w12..w18), `generate/play_page.py` (the ten colour hits, w53..w62),
`deskmap.py` and `desk_policy.py` (the desk map, roles, `SAFETY_*`),
`ids.py`, and `checks/rule_solo_handoff.py` as the model of a rule.

## Why

The tablet desk fires hits over a websocket. A Flash button pressed from
the tablet (255 on press, 0 on release) leaves the output on if the link
is lost mid-hold; QLC+ 5.2.2 has no lease. A **burst** does not: a Chaser in
SingleShot with one step whose hold is the burst's length ends itself on
the master. The tablet starts it on press with `QLC+API|setFunctionStatus|id|1`
and stops it on release with `|0`, both idempotent. Proven tonight on the
bench master with a hand-edited copy of Vibra.qxw (a private copy of scene
638 "Humo ON" as f812, chaser f813 SingleShot, one step hold 3000):
`FUNCTION|813|Running` 13 ms after the start, `Stopped` at 3009 ms with the
scene's own Stopped beside it; an early stop answered in 21 ms; a second
start while running did not restart or extend.

## What to build

For every hit the desk map carries as a held accent (LIVE: `flash`,
`flash-lento`, `flash-color`, `strobo`, `strobo-suave`, `humo-ya`,
`humo-vert`; COLOR: the ten colour hits), generate:

1. A private Scene copy of the hit's scene, same FixtureVal, named
   `Desk · <hit> (ráfaga)`, referenced by nothing else.
2. A Chaser `Desk · <hit> ráfaga N s`, RunOrder SingleShot, Direction
   Forward, one Step with Hold = the burst's ms and FadeIn/FadeOut 0,
   `<SpeedModes FadeIn="Common" FadeOut="Common" Duration="PerStep"/>`.
3. A VC Toggle button on the CONTROL page in a new frame `Ráfagas del desk`
   (below the tablet notes; it may be small), driving the chaser, so the
   desk validates the function through `/vc.json` as it does every cue.
4. In the desk map: the burst replaces the held accent in its section, as a
   control with `role: "burst"`, `burstMs`, `source: "<hit key>"`, the hit's
   caption and swatches, `function` the chaser id, `widget` the toggle.

Durations in `desk_policy.py`, one table the owner can tune, with these
first values and a comment that they are provisional: light flashes 8000,
strobes 4000, fog 3000, colour hits 8000.

Priority: the Mac's Flash buttons run their scenes with Override priority; a
chaser started by API runs at normal priority. Judge per hit whether the
look changes over a running state (fog and full-intensity flashes are HTP
and fine; colour hits over a colour wheel may mix; strobes may not win over
a running shutter chase). Generate them all, and record what you found per
hit in the findings; mark a doubtful one in the map with `burstNote`.

## Proof

- A rule `checks/rule_desk_bursts.py`: every burst chaser is SingleShot
  with exactly one step whose hold equals the policy's ms, its scene a
  private copy no other function references, the toggle's function the
  chaser; a dated regression test.
- `tests/test_deskmap.py`: the map carries the bursts with their fields and
  no held accent where a burst stands.
- Regenerate all three workspaces with `--validate` (set
  `QLCTOOL_QLCPLUS=/private/tmp/claude-501/-Users-cristiandeluxe-p-taq102/497681ef-06af-472d-aac5-e75724f0c7a4/scratchpad/qlcplus-4-pty.sh`,
  the pty wrapper the headless QLC+ 4.13 needs to print anything), then
  `qlctool deskmap` for `Vibra.desk.json`. Run the deskmap and check tests
  and the new rule; the full suite takes 33 minutes, run it only if time
  allows and say whether you did.
- Do not touch `/Users/cristiandeluxe/p/taq102`, nor any QLC+ instance on
  ports 9998 or 9999.

Commit on `codex-bursts` in plain messages; finish by writing
`tools/qlctool/docs/2026-09-13-desk-bursts-findings.md`: what changed, the
per-hit priority judgment, what the validation printed, anything undone.
