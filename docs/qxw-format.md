# The `.qxw` workspace format

Reverse-engineered from the production workspaces and confirmed against the
QLC+ source (`engine/src/function.cpp`). Everything here is verified by tests in
`tools/qlctool/tests`, most of them by rebuilding the real show's own functions
node for node.

## Shape

Root `<Workspace>` with `Creator`, `Engine`, `VirtualConsole`, `SimpleDesk`
(4.x only) and `InputOutputMap`. Every element lives in the namespace
`http://www.qlcplus.org/Workspace`, and the file opens with
`<?xml version="1.0" encoding="UTF-8"?>` and `<!DOCTYPE Workspace>`.

`Engine` holds the rig and the show: `InputOutputMap`, `Fixture`,
`FixtureGroup`, `ChannelsGroup`, `Function`, `Monitor`.

## Three traps, each of which has cost time

1. **The same tag name is a definition in one place and a reference in
   another.** `<Fixture>` is a patched fixture in the Engine, a member block
   inside an EFX, and a reference in a Virtual Console XY pad. `<Function>` is a
   function in the Engine and a reference from every VC button - and on a
   SpeedDial it carries no `ID` at all. `<FixtureGroup>` is a group definition
   in the Engine and a plain ID reference inside an RGBMatrix. Filter by what
   the node carries: a patched fixture has `<Channels>`, a real function is a
   direct child of `<Engine>`.
2. **`4294967295` is QLC+'s invalid-ID sentinel** (`0xFFFFFFFF`), and an
   unassigned VC button stores it. Counting it when allocating the next function
   ID pushes every generated ID past the 32-bit range QLC+ stores - a file that
   looks fine and is quietly broken.
3. **A fixture is referenced from six places**, and unpatching it means clearing
   all of them: `<FixtureVal ID>` in every scene, the `<Fixture><ID>` block in
   every EFX, `<Fixture ID>` in a VC XY pad, and the `Fixture=` attribute on
   fixture-group `<Head>` and VC slider `<Channel>`.

## Fixture (in `Engine`)

Child order as QLC+ writes it: `Manufacturer`, `Model`, `Mode`, `ID`, `Name`,
`Universe`, `Address`, `Channels`. `Universe` and `Address` are **0-based** in
the file; the QLC+ UI shows addresses 1-based.

## Function types

`Scene`, `Chaser`, `EFX`, `Collection`, `Sequence`, `RGBMatrix`, `Show`,
`Audio`, `Video`, `Script` - the constants in `function.cpp`.

### Scene

`<Function ID Type="Scene" Name Path>` + `<Speed FadeIn FadeOut Duration/>` +
one `<FixtureVal ID="n">ch,val,ch,val,…</FixtureVal>` per fixture. Channel index
is 0-based within the fixture, value 0-255. An empty `<FixtureVal ID="n"/>`
includes the fixture with no values. QLC+ drops zero-valued channels when *it*
saves; a written 0 is kept and means "drive this to zero".

`Path` is the folder the QLC+ UI files the function under, and it is what the
toolkit groups Virtual Console frames by.

### Chaser

`Speed`, `Direction` (Forward/Backward), `RunOrder`
(Loop/SingleShot/PingPong/**Random**), `SpeedModes`, then
`<Step Number FadeIn Hold FadeOut>funcID</Step>` per step.

**`SpeedModes` decides whose timing is real, and it is not obvious.**
`<SpeedModes FadeIn FadeOut Duration/>` is `Common` or `PerStep` per field.
With `Duration="Common"` every step lasts the chaser's own `<Speed Duration>`
and the per-step `Hold` is ignored; with `PerStep` each step lasts
`FadeIn + Hold`, which is how QLC+ derives a step's duration on load
(`ChaserStep::loadXML`). The switch is `ChaserRunner::stepDuration`.

Two consequences:

- **A duration of 0 is not "no limit", it is "already over".** `write()`
  advances as soon as `elapsed >= duration`, so a chaser with duration 0 walks
  one step per engine tick - about 50 a second. A whole show of those, started
  together, looks like QLC+ has hung.
- **A Speed Dial and `Chaser::tap()` only reach a `Common` chaser.**
  `Chaser::tap()` returns immediately in `PerStep`, and the dial writes the
  chaser's duration, which `PerStep` never reads. So `Common` is the default to
  want, and `PerStep` is for a chaser whose steps genuinely differ - a smoke
  burst followed by a long wait.

### Collection

`<Function Type="Collection">` + `<Step Number="n">funcID</Step>`. Members run
**together**, not in sequence - this is what an unattended show uses at the top.

### EFX

Uniform across all 30 in the show: one `<Fixture>` block per participant (`ID`,
`Head`, `Mode`, `Direction`, `StartOffset`), then `PropagationMode`
(Parallel/Serial/Asymmetric), `Speed`, `Direction`, `RunOrder`, `Algorithm`
(Circle/Eight/Line/Diamond/Square/Leaf/Lissajous), `Width`, `Height`,
`Rotation`, `StartOffset`, `IsRelative`, `<Axis Name="X">` and
`<Axis Name="Y">`, each with `Offset`/`Frequency`/`Phase`.

`Direction` and `StartOffset` appear at **both** levels - read the direct
children, not the first match. QLC+ defaults: X frequency 2 phase 90, Y
frequency 3 phase 0; frequency and phase only matter for Lissajous.

### RGBMatrix

Child order: `Speed`, `Direction`, `RunOrder`, `Algorithm`, colour,
`ControlMode`, `FixtureGroup`, `Property*`.

- `<Algorithm Type="Script">Even/Odd</Algorithm>` names an RGB script installed
  with QLC+; `<Algorithm Type="Plain"/>` is a solid colour.
- **The colour changed in QLC+ 4.14**: 4.13 writes `<MonoColor>` plus an
  optional `<EndColor>`, as opaque 32-bit ARGB decimals (4294901760 = red).
  4.14 and 5.x write an indexed list instead: `<Color Index="0">`,
  `<Color Index="1">`. QLC+ still reads the old shape, but a file mixing both is
  a trap - write the one the target show uses.
- `<FixtureGroup>` is a group ID, or `4294967295` for every fixture.
- `<Property Name Value/>` carries the script's own parameters (`blockSize`,
  `presetIndex`, `taillength`, …).

Script algorithms this show uses: Alternate, Even/Odd, Fill, Fill From Center,
Fill Unfill, Gradient, One By One, Opposite, Random Column, Stripes From Center,
Strobe, Waves.

### FixtureGroup

`ID`, `<Name>`, `<Size X Y>`, and a `<Head X Y Fixture="fid">head</Head>` grid.
A fixture appears once per head, so group membership is the set of `Fixture=`
values.

## Virtual Console

`<VirtualConsole>` holds one root `<Frame>` and a `<Properties>` block with the
canvas `<Size Width Height>` and the grand master.

Widgets: `Frame`, `SoloFrame` (one child active at a time), `Button`, `Label`,
`Slider`, `XYPad`, `SpeedDial`, `Matrix`, `AudioTriggers`, `Clock`, `CueList`.
QLC+ 5 renamed the RGB-matrix control class to `VCAnimation` but kept its tag
`Matrix`, so the same file works in both. Each carries a unique
`ID`, a `<WindowState Visible X Y Width Height/>` and an `<Appearance>` block of
five children (`FrameStyle`, `ForegroundColor`, `BackgroundColor`,
`BackgroundImage`, `Font`); colours are ARGB decimals or `Default`.

A button is `<Button Caption ID Icon>` + `WindowState` + `Appearance` +
`<Function ID="n"/>` + `<Action>` (Toggle/Flash) + `<Key>` (QLC+ spells them
`Space`, `1`, `Q`, `.`) + `<Intensity Adjust="False">100</Intensity>`.

**A solo frame stops functions, and it does not only listen to clicks.** A
Toggle button emits `functionStarting` whenever its function starts - including
when something else started it (`VCButton::slotFunctionRunning`) - and the
enclosing `VCSoloFrame` answers by calling `notifyFunctionStarting` on every
other widget in it, which stops their functions. So **a function and the
functions it starts must never share a solo frame**: press AUTO, AUTO starts
`Rueda Colores`, that button reports it, and the frame stops AUTO. Identical in
the 4.x and 5.x sources.

`<ExcludeMonitored>True</ExcludeMonitored>` narrows it to buttons somebody
actually pressed, which stops a chaser's own steps from cutting each other, but
it does **not** save a parent that was pressed by hand.

Other widgets, as this repo's shows use them:

- `<SoloFrame>` / `<Frame>`: `AllowChildren`, `AllowResize`, `ShowHeader`,
  `ShowEnableButton`, `Collapsed`, `Disabled`, plus `Mixing` and
  `ExcludeMonitored` on a solo frame.
- Multipage: `<Multipage PagesNum CurrentPage/>` on the frame, optional
  `<Next><Key>…` / `<Previous><Key>…`, `<PagesLoop>`, and each child carries
  `Page="n"` (absent means page 0). The page arrows live in the frame header,
  so `ShowHeader` has to be `True`.
- `<XYPad>`: one `<Fixture ID Head>` per driven fixture, each with
  `<Axis ID="X"|"Y" LowLimit HighLimit Reverse/>` where the limits are 0-1
  fractions of the fixture's range, then `<Pan Position>` and `<Tilt Position>`.
- `<SpeedDial>`: `<AbsoluteValue Minimum Maximum/>`, `<Time>` in ms, and one
  `<Function FadeIn FadeOut Duration>funcID</Function>` per driven function -
  those three attributes are *multiplier* enum values, not times
  (`VCSpeedDialFunction::SpeedMultiplier`: 0 = none, 6 = x1).
- `<AudioTriggers BarsNumber>`: one `<SpectrumBar Name Type MinThreshold
  MaxThreshold Divisor Index WidgetID/>` per bound band. `Type` is
  `AudioBar::BarType` - 1 DMX channels, 2 a function, 3 another VC widget.
- `<Slider>`: `SliderMode` is `Level`, `Playback` or `Submaster` - **there is no
  speed mode**. A "speed" slider is either a Level slider on a real DMX channel
  or it does nothing at all.

## Version differences seen in this repo

The same show exists saved by three versions, all in `QLC+ Setups/`:

| Version | File | What differs |
| --- | --- | --- |
| 4.13.1 | `DeluxeEventos2.qxw` | `<MonoColor>`/`<EndColor>`; has `SimpleDesk` |
| 4.14.3 | `DeluxeEventos2_qlc4143.qxw` | `<Color Index>`; chaser durations filled in; `Property` order differs |
| 5.2.2 | `DeluxeEventos2_qlcv5.qxw` | `<Color Index>`; no `SimpleDesk`; different `CurrentWindow` |

Contents are identical - same 377 functions, same names, verified by semantic
diff. They are kept as test material so the builders are exercised against all
three.

## Editing rule

Never hand-edit a `.qxw`: one malformed node corrupts the whole show. Edit
through the toolkit, which parses, mutates only the targeted nodes, and proves
the result both ways (see [toolkit.md](toolkit.md)).
