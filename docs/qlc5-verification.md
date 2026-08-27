# What the installed QLC+ 5.2.2 really loads

`docs/superpowers/plans/2026-08-27-qlc-audit-verification.md` confirmed a set
of QLC+5-only feature claims against the source clone at `~/p/qlcplus`, which
is `master`/5.3.0-git. The show runs a different, older binary. This document
re-checks the claims that section B14 flagged as the strongest
installed-version risks, against the actual binary on this machine, not the
source.

## Binary under test

```
$ /Applications/QLC+.app/Contents/MacOS/qlcplus-qml --version
Q Light Controller Plus version 5.2.2
This program is licensed under the terms of the Apache 2.0 license.
```

Every probe run's log opens with the same banner line, so each result below
is tied to this exact binary, not to the source clone.

## Method

Each XML-shape claim got the smallest valid 4.13-format `.qxw` that exercises
it: the `Creator`/`InputOutputMap`/one-`Fixture` header copied from
`QLC+ Setups/Vibra-split.qxw`, plus the one construct under test. Probes live
in `tools/qlctool/tests/probes/`.

Each probe was run through `qlctool.validate.validate_workspace()` - the same
loader `qlctool validate` uses - which launches the installed
`qlcplus-qml` headless (`-d -m -o <file>`), waits for its end-of-load markers,
kills it, and returns the full captured log.

A clean load (`ok=True`) is necessary but not sufficient: `validate_workspace`
only flags a curated set of fatal markers (`No fixture definition`,
`overlapping with fixture`, etc.) as errors. It does **not** flag QLC+'s own
`"Unknown ... tag"` warnings, which is exactly what fires when a parser drops
an element it doesn't recognize (`Doc::loadXML`, `VCFrame::loadXML`,
`VCSlider::loadXML` and `RGBMatrix::loadXML` all end their tag-dispatch loop
with such a warning, per the same source clone). So every log below was
additionally grepped for `Unknown` and read in full, and a probe only counts
as confirming a *tag or element* when no such warning names it.

That check has a real limit: two of the claims are decoded from **attribute
or text values on an already-recognized tag** (which `SliderMode`/`ControlMode`
string wins, whether a `BlendMode="..."` attribute was even looked at). The
engine's own string-to-enum converters (`stringToSliderMode`,
`stringToControlMode`, `Universe::stringToBlendMode`) silently fall back to a
default on any value they don't recognize - no warning either way - and a
`hasAttribute()` check on an attribute name the parser doesn't know about is
just as silent. A headless load cannot tell "recognized and applied" apart
from "silently defaulted" in that case. Those rows are marked accordingly
below rather than overclaimed as fully confirmed.

No QLC+ instance was left running by any of these runs; the machine's own
already-open instance (a separate PID, present before and after) was
untouched throughout.

## Results

| Claim | Probe | Evidence | Verdict |
| --- | --- | --- | --- |
| Palettes (`<Palette>`) load in a 4.13-format file (B6) | `probe-palette.qxw` | `ok=True`; full log has no `Unknown engine tag: Palette` (the catch-all `Doc::loadXML` prints for any element it doesn't dispatch). Two palettes loaded: a `Color` and a `Dimmer` with `Fan="Linear"` fanning attributes. | CONFIRMED-ON-5.2.2 |
| VC Slider accepts `SliderMode` `GrandMaster` from v4 XML (B4) | `probe-gm-slider.qxw` | `ok=True`; no `Unknown slider tag`, `Unknown frame tag`, or `Unknown Virtual Console tag` for either `<Slider>` widget or its `<SliderMode>` child - the widget was not dropped. The *specific* string-to-enum decode of `"GrandMaster"`/`"Submaster"` (`vcslider.cpp` `stringToSliderMode`, which falls back to `Adjust` silently on any unmatched string) has no headless-observable signal either way; not independently confirmed beyond "the tag is accepted." | CONFIRMED-ON-5.2.2 (tag/widget accepted; exact enum decode not independently observable, see Method) |
| VC Slider accepts `SliderMode` `Submaster` from v4 XML (B4) | `probe-gm-slider.qxw` (second `<Slider>`) | Same probe/log as above. | CONFIRMED-ON-5.2.2 (same caveat) |
| RGBMatrix `<Property>` script parameters load (A5/B1) | `probe-matrix-property.qxw` | `ok=True`; log line `"Plasma" script loaded` confirms the scripted algorithm resolved; no `Unknown RGB matrix tag` for `<Property Name="presetIndex" Value="2"/>`. | CONFIRMED-ON-5.2.2 |
| RGBMatrix indexed `<Color Index="...">` loads (A5/B1) | `probe-matrix-property.qxw` (`<Color Index="0">`/`<Color Index="1">`, no `<MonoColor>`) | Same run. No `Unknown RGB matrix tag` for either `<Color>` element. | CONFIRMED-ON-5.2.2 |
| `BlendMode` attribute on `<Function>` loads (B8) | `probe-blendmode.qxw` (`<Function ... BlendMode="Additive">`) | `ok=True`, clean log. `BlendMode` is read via `attrs.hasAttribute(KXMLQLCFunctionBlendMode)` in `Function::loader` with no catch-all warning path for an unrecognized attribute name - a clean load cannot distinguish "attribute recognized and applied" from "attribute name not checked for in this build, silently ignored." | INCONCLUSIVE - no distinguishing signal is obtainable from a headless load; see Method |
| `ControlMode` `Dimmer` loads (B8) | `probe-controlmode.qxw` (`<ControlMode>Dimmer</ControlMode>`) | `ok=True`; no `Unknown RGB matrix tag: ControlMode` - the wrapping element is accepted. The specific `"Dimmer"` -> `ControlModeDimmer` decode (`stringToControlMode`, which falls back to `ControlModeRgb` silently) has the same non-observability as the slider modes above. | CONFIRMED-ON-5.2.2 (tag accepted; exact enum decode not independently observable, see Method) |
| Web interface flags `-w`/`-wp` exist (B11) | `qlcplus-qml --help` | Help text lists `-w, --web`, `--wp, --web-port <port>`, and also `--wa, --web-auth` (not asked for but present). Direct behavioral evidence, not a probe file. | CONFIRMED-ON-5.2.2 |
| Kiosk `-k` exists (B12) | `qlcplus-qml --help` | Help text lists `-k, --kiosk  Enable kiosk mode (only Virtual Console)`. | CONFIRMED-ON-5.2.2 |
| `-p` operate flag exists at all (documented only for v4) | `qlcplus-qml --help` | Full option list is `-h/--help-all/-v/-o/-9/-f/-k/-l/-d/-g/-3/-m/-w/--wp/--wa/-a` - no `-p` and no `-c` anywhere. `-p` was a v4 widgets-build flag; this v5 QML build has no equivalent. | NOT-ON-5.2.2 |

## Full `--help` capture

```
$ /Applications/QLC+.app/Contents/MacOS/qlcplus-qml --help
Q Light Controller Plus version 5.2.2
...
Options:
  -h, --help                  Displays help on commandline options.
  --help-all                  Displays help, including generic Qt options.
  -v, --version               Displays version information.
  -o, --open                  Specify a file to open.
  -9, --openlast              Open the file from last session.
  -f, --fullscreen            Start the application in fullscreen mode
  -k, --kiosk                 Enable kiosk mode (only Virtual Console)
  -l, --locale <locale>       Specify a language to use.
  -d, --debug                 Enable debug messages.
  -g, --log                   Log debug messages to a file.
  -3, --no3d                  Disable the 3D preview.
  -m, --nowm                  The OS doesn't provide a window manager
  -w, --web                   Enable remote web access
  --wp, --web-port <port>     Set the port to use for web access
  --wa, --web-auth            Enable remote web access with users
                              authentication
  -a, --web-auth-file <file>  Specify a file where to store web access basic
                              authentication credentials
```

No `-w`/web-access instance was started to reach this output - `--help`
prints and exits on its own, unlike `-o`, which starts the engine and stays
up (see `docs/qlcplus-environment.md`).

## What this means for downstream tasks

- Task 3 (GrandMaster slider): the `SliderMode` `GrandMaster` tag is accepted
  by the installed binary; proceed, with the residual caveat noted above.
- Task 5 (matrix `Property`/indexed colors): both constructs are confirmed on
  the installed binary; proceed.
- Task 8 (CLI flags runbook): `-w`, `--wp`, `--wa`, `-k`, `-f` are confirmed
  present; `-p` and `-c` are confirmed absent and must not appear in the
  runbook as if this build supported them.
- `BlendMode` (B8) is INCONCLUSIVE on this evidence. It gates no task named in
  this plan; if a future task depends on it, it needs either a stronger probe
  (one that produces an observably different result depending on blend mode,
  e.g. via the 3D preview or a saved-and-reloaded round trip) or acceptance of
  the residual risk.
