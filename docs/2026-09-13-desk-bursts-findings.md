# Desk bursts — 2026-09-13

## Delivered

All 17 desk accents now have independent bounded cues: seven on LIVE and ten
on COLOR. Each has a private Scene with the source's exact `FixtureVal`
contents and a Forward, SingleShot Chaser with one step, zero fades and
`SpeedModes FadeIn="Common" FadeOut="Common" Duration="PerStep"`.
`BURST_MS` in `qlctool/desk_policy.py` is the single provisional duration table.

The CONTROL page has a small `Ráfagas del desk` frame below tablet guidance,
in the space above the colour banks. Each burst has one keyless Toggle there.
The desk map keeps the source key, caption, swatches and section, replacing
its disabled held accent with `role: "burst"`, `burstMs`, `source`, the chaser
function and the toggle widget. Its action is `toggle` for VC validation;
the tablet must use explicit `setFunctionStatus` start/stop for burst presses
and releases as specified in the briefing. The map schema remains 2.

Each show gained 34 functions and 17 buttons. A structural comparison with
HEAD before this change confirmed that every existing function and button
retained its ID and complete XML contents. All three shows contain 846
functions and 593 buttons. `Vibra.desk.json` has 132 controls, all enabled;
17 are bursts and 15 carry a priority caveat in `burstNote`.

## Safety checks

`checks/rule_desk_bursts.py` is registered in `qlctool check`. It rejects
missing/duplicate controls, wrong function types, wrong run order, wrong
clock or timing, altered scene values, shared scenes, other function callers,
and extra console references (including dials). It identifies cues through
console placement and source values, not function names. Map export fails
closed on a burst finding.

The dated missing-burst regression was added and passed before the generator
changed. Mutation tests cover loss of the deadline, sharing a scene, an
automatic caller, a direct scene button, and bad or missing map bindings.

The existing vertical-column rule accepts only fully verified private desk
bursts in addition to held Flash buttons. An arbitrary SingleShot chaser does
not get an exception; a looping or automatically started burst is rejected.
`rule_smoke`, `rule_smoke_light`, and `rule_smoke_restore` are unchanged.
The latter still requires pump channels to reset safely. A burst ending removes
its own contribution; it cannot cancel another independently running fog cue,
such as the ambient haze rhythm.

## Priority judgment per hit

These are code and fixture-value judgments, not a new live-rig measurement.
The supplied briefing contains the earlier timing experiment; this task did
not repeat it against either protected master.

QLC+'s [Scene implementation](https://github.com/mcallegari/qlcplus/blob/master/engine/src/scene.cpp)
uses normal faders for a running scene; the Flash path supplies Override and
ForceLTP. Its [Universe implementation](https://github.com/mcallegari/qlcplus/blob/master/engine/src/universe.cpp)
orders faders by priority and insertion order and mixes intensity by HTP unless
ForceLTP applies. Consequently a later normal-priority state step can reclaim
an LTP shutter or colour-wheel channel. The [Chaser runner](https://github.com/mcallegari/qlcplus/blob/master/engine/src/chaserrunner.cpp)
uses the step clock in PerStep mode and finishes at the end of SingleShot.
These upstream sources were fetched during this task.

| Source key | Duration | Judgment over a running state | `burstNote` |
| --- | ---: | --- | --- |
| `flash` | 8000 ms | Full white intensity wins HTP. The source also strobes: later shutter and beam-colour steps may change that part of the look. | Yes |
| `flash-lento` | 8000 ms | Also full white, with a slower shutter rate, not half intensity. Same shutter and beam-colour priority caveat. | Yes |
| `flash-color` | 8000 ms | Raises dimmers and keeps the state's colour. Its shutter rate may lose to another shutter writer. | Yes |
| `strobo` | 4000 ms | Writes shutters only. A competing shutter chase can overwrite the fast rate; no dimmer or colour is added. | Yes |
| `strobo-suave` | 4000 ms | Writes shutters only at the slower rate. The same priority limit applies. | Yes |
| `humo-ya` | 3000 ms | Full pump output wins HTP; private scene retirement releases its own pump contribution. | No |
| `humo-vert` | 3000 ms | Pump and LED master win HTP; the state continues to supply the column's colour. | No |
| `rojo` | 8000 ms | Red adds by HTP; over cyan it can become white. Beam colour and shutter rate may be overwritten. | Yes |
| `verde` | 8000 ms | Green adds by HTP; over magenta it can become white. Beam colour and shutter rate may be overwritten. | Yes |
| `azul` | 8000 ms | Blue adds by HTP; over yellow it can become white. Beam colour and shutter rate may be overwritten. | Yes |
| `ultravioleta` | 8000 ms | The palette's purple RGB values mix with the state, so the UV-like hue is not guaranteed. Wheel and shutter priority is unchanged. | Yes |
| `amarillo` | 8000 ms | Yellow adds by HTP; a blue state can turn it white. Beam colour and shutter rate may be overwritten. | Yes |
| `cyan` | 8000 ms | Cyan adds by HTP; a red state can turn it white. Beam colour and shutter rate may be overwritten. | Yes |
| `magenta` | 8000 ms | Magenta adds by HTP; a green state can turn it white. Beam colour and shutter rate may be overwritten. | Yes |
| `blanco` | 8000 ms | Full white wins RGB intensity HTP, but beam colour and shutter rate are still vulnerable to later state steps. | Yes |
| `naranja` | 8000 ms | Orange's partial green and zero blue cannot suppress the state's higher values. Wheel and shutter priority is unchanged. | Yes |
| `rosa` | 8000 ms | Pink's partial blue and zero green cannot suppress the state's higher values. Wheel and shutter priority is unchanged. | Yes |

## Validation evidence

The package-local `.venv` was created with uv and used throughout (Python
3.14.7). `qlctool install --check` printed:

```text
QLC+ has every one of the repo's 12 file(s)
```

Each workspace was regenerated from its own patch and plot according to the
briefing, using the supplied QLC+ 4.13.1 pseudo-terminal wrapper:

| Workspace | Result printed by `newshow --validate` |
| --- | --- |
| `Vibra.qxw` | `Validated: QLC+ loaded it with no complaints` |
| `Vibra-beats.qxw` | `Validated: QLC+ loaded it with no complaints` |
| `Vibra-split.qxw` | `Validated: QLC+ loaded it with no complaints` |

The check suite's shipped-show gate passed on all three workspaces. This is
semantic validation in addition to QLC+ loading; the latter used 4.13.1 and
is not a claim of a fresh QLC+ 5.2.2 runtime or visual test.

- Desk map and burst mutation tests: 34 passed.
- Generator and console tests: 47 passed, including QLC+ loading.
- Final standalone `qlctool check Vibra-split.qxw` printed
  `580 botones revisados, ningun problema` and exited 0.
- Combined `test_check.py`, `test_deskmap.py`, and `test_desk_bursts.py` run:
  **139 passed in 1591.00 seconds (26m31s)**. Together with the 47 generator
  and console tests, 186 targeted tests passed.
- Ruff checks on all changed Python files and `git diff --check`: passed.
- Full package suite: not run; the briefing permits skipping its approximately
  33-minute run. The requested check and desk suites are run separately.

## Remaining verification

The provisional durations and priority caveats need a rig session over AUTO
and a running shutter chase. See the package [TODO](../TODO.md). No code was
changed in the tablet repository, no protected master was contacted, and no
QLC+ installed copies were changed. No live output or websocket timing is
claimed here. The work is committed locally on `codex-bursts`; deployment and
remote publication are outside this workspace-only task.
