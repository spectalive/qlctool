# What `qlctool check` looks for

`qlctool validate` asks QLC+ whether it can load a workspace. That is a low
bar: every bug this show has had loaded perfectly. `qlctool check` asks the
other question - **will the room do what the buttons promise** - and it asks it
of every button on the console.

```bash
qlctool check "QLC+ Setups/Vibra-split.qxw"
```

Every rule below exists because something went wrong in a real room. That is
the rule for adding one, too: find the cause, write a check that sees it, add a
regression test that puts the bug back, and run it over all three workspaces.

## How it reasons

Three ideas do all the work, and none of them involve a function's name.

**What a leaf function drives.** A Scene says exactly which channels it writes
and to what. An **EFX** writes pan/tilt, the dimmer, or RGB depending on each
fixture's `<Mode>`, and never a predictable value. An **RGBMatrix** writes red,
green and blue onto the heads of one fixture group and *nothing else* - not the
master dimmer, not the shutter. That last sentence is two of the bugs.

**What runs at the same instant.** A **Collection** starts all its members at
once, so they are concurrent. A **Chaser** plays its steps one at a time, so
steps are alternatives and never collide - which is exactly why the energy
levels are safe inside `Ciclo Energia` and were dangerous as three buttons.

That cuts both ways, and the second edge took longer to notice. "Can these two
fight over a channel" is a question about a state's whole **reach** - everything
it can drive at any step. "Is somebody owning this channel right now" is not:
merge the steps and the one that parks a wheel parks it on behalf of every step
that does not. The LTP restore rules therefore read a state one **instant** at a
time (`unowned_instant.py`), which is answered without enumerating instants -
two booleans per node, `any` over a chaser's steps and `all` over a collection's
members.

**What answers for what.** The console is built around a solo frame: the room
is in exactly one **state** (AUTO, a moment, the work light, the blackout) and
everything else is a **layer** pressed on top. A state runs with nothing
underneath it, so it answers for every fixture it colours by any means. A layer
answers only for the colour it states itself, in a Scene - a matrix on the
library page is not asked to open a dimmer, because it cannot, and the state
beneath it already did.

## The rules

| Rule | What it catches | The night it comes from |
| --- | --- | --- |
| `intensidad` | A fixture given colour with nothing opening its dimmer, or with a labelled shutter left shut | The HYULIGHTS panels were the right colour and off all night (2026-08-26) |
| `rueda de color` | A look that colours a fixture group and writes nothing to the members of that group whose colour is a wheel | `BLANCO TOTAL` left the four BEAM 230W 7R black (2026-08-26) |
| `colores pisados` | Two concurrent members of one Collection reaching the same colour, wheel or pan/tilt channel | Two energy levels pressed at once turned the room white (2026-08-25) |
| `relojes de color` | A room state starting two chasers that each rotate colour on their own clock - a wheel of scenes and a cycle of matrices never land on the same colour | The bars sat on magenta while the wheel had the room on cyan: "van con los colores a su bola" (2026-08-26) |
| `efecto cortado` | A chaser holding an RGBMatrix for less than one full pass of its own animation | The LED bar started a Fill and never finished it (2026-08-26) |
| `estrobo en un ciclo` | A `Strobe` matrix sitting among the steps of a chaser instead of on its own button | The pixels blinked without anyone asking, half the time (2026-08-26) |
| `programa interno` | A scene stating a colour on a fixture without taking it out of its own built-in programme, which makes it ignore that colour. Since 2026-08-28 an owned mode channel is the one excuse: when every room state that lights the fixture also drives that channel (`Ciclo Paneles Mixto`), colour without the mode-off is a phase, not a gamble | The panels kept animating under looks that thought they were setting a colour (2026-08-26) |
| `rejilla` | A fixture group with empty cells in its grid, or heads outside it | Four panels sharing the bars' grid sat dark through half of every sweep (2026-08-26) |
| `humo` | A scene that raises the smoke machine *and* touches other fixtures | A pump swept up in an "all dimmers up" scene runs until the tank is empty |
| `consola` | A master sharing a solo frame with its own members; two buttons on one key; a widget past the edge of the screen; two Blackout buttons with conflicting local state | AUTO died the instant it was pressed |
| `estrobo demasiado rapido` | Anything with a strobe's shape - a chaser alternating lit and black on the same channels, a `Strobe` matrix - flashing above 4 Hz, the UK public-performance cap; 3-30 Hz is the photosensitive-epilepsy trigger band | `Strobo Rapido` shipped at 10 Hz over the whole rig and the checker was blind to it (Codex review, 2026-08-27) |
| `estrobo enganchado` | A looping strobe chaser reachable from any console button: one press and it flashes until somebody finds it. A strobe hit is a SingleShot burst that ends itself | The STROBO button was a Toggle over an endless loop (2026-08-27) |
| `flash sin escena` | A Flash button whose function is not a Scene - `Scene::flash` is the only implementation, so anything else half-works | Found wiring the highlight buttons, before it shipped (2026-08-27) |
| `flash sin estrobo` | A human-held Flash scene writing a fixture that has a strobe-capable channel while parking it in "Open"/"No function" - in this show a held flash *is* the strobe | "Esto no hace estrobo y antes lo hacía cuando le daba al espacio" (owner, at home over the FT232R, 2026-08-27) |
| `estrobo en manos del audio` | The other half of the same rule: a Flash button an AudioTriggers bar presses must *not* strobe - a strobe fired by whatever the PA does is a strobe nobody chose | Guarded when the flashes got their strobe back (2026-08-27) |
| `estrobo incompleto` | A strobe scene (all writes on strobe channels, at least one strobing) that skips patched fixtures which have a strobe-capable channel | `Strobo ON` drove only the labelled shutters: ten fixtures flashed, the seven Vortex and the panels held steady (2026-08-27) |
| `intensidad tapada` | Two concurrent members of one Collection writing the same dimmer channel to different definite values: HTP, the higher wins, the lower is dead code | "Ambiente = dimmer bajo" could never have worked while the colour wheel held every dimmer at 255 (2026-08-27) |
| `acento sin dueño` | A Flash scene moving an LTP wheel (gobo, prisma, colour) that some **instant** of a room state lights but never writes: on release the wheel stays where the flash left it | The prism flashed for one drop is still in the beam an hour later (2026-08-27) |
| `estrobo pegado` | The same LTP latch on the strobe channels: a Flash scene strobing a channel that some **instant** of a room state lights but never writes - on release the strobe simply keeps firing | "Se queda el estrobo para siempre": FLASH latched the four panels, the seven Vortex and the two mini heads until `Strobo OFF` by hand (owner, 2026-08-28) |
| `rejilla fuera de orden` | A fixture group whose cells are not in the order the fixtures stand in, so a matrix that means a direction sweeps the grid without sweeping the room | `Cabezas` walked its four rigged beams 1916, 9694, 4405, 7205 mm across the stage (2026-08-31) |
| `cabezas sin declarar` | A grouped fixture with several sets of colour channels whose definition declares fewer `<Head>` blocks: QLC+ invents one head, keeps the last channel of each colour, and a matrix paints one of the sets | The two MAC WASH 1915Z are three RGBW rings and declared no head at all (2026-08-31) |
| `familias de movimiento mezcladas` | One EFX moving wash-class and beam-class fixtures (told apart by the gobo wheel) with one geometry | Twelve movers shared a 100x100 EFX; a 7R needle ran wash-sized sweeps through faces (2026-08-27) |
| `binding a un control que el pad no manda` | A widget listening on a MIDI channel that is not in the pad's input profile - no control on the surface can send it | Eight buttons on the manual page were bound against SHIFT, which turned out to select the pad's own silkscreened functions and put nothing on the wire (2026-08-29) |
| `consola con bindings y sin entrada MIDI` | A workspace whose widgets carry `<Input>` bindings while no universe patches an input plugin: QLC+ opens the show with nothing listening | No shipped workspace declared the patch, so the pad did nothing until it was built by hand in the Inputs/Outputs tab (2026-08-29) |
| `zoom sin declarar` | A Scene that lights a fixture - dimmer or colour above zero - without writing the zoom channel its definition gives it. Which end is wide comes from the capability preset (`SmallToBig` / `BigToSmall`), never from the model | The two Mac Mah MAC WASH 1915Z arrived in place of the CromoWash and were the first fixtures here with a zoom on DMX: nothing wrote it, and an unwritten zoom is 0 - whichever end that is on the model. For a week the definition had it backwards and every look sent the washes to 6 degrees; ChamSys's personality settled it on 2026-09-02 (2026-08-29) |
| `un control atado a dos widgets` | Two widgets on one input channel - one pad firing both | Guarded when the pad map was generated (2026-08-29) |
| `rueda de color girando` | A scene that states a colour on the RGB fixtures and leaves a wheel-coloured fixture inside a rotation range of its wheel. A rotation range is not a colour: the wheel turns, and a narrow beam looking through it between two detents shows half of one colour and half of the next | "Las 7R no se abren del todo, están como una media luna": `Rig Multicolor 1` and `2` sent the beams' wheel to 186, inside its rotation range and near the slow end, so two of the twenty colour-clock steps split every beam (2026-08-29) |
| `dimmer a medias` | A scene or EFX writing an intermediate value to a dimmer whose definition describes it in labelled ranges - a mechanical blade, not a fader. Between the ends the blade covers part of the lens | "Las 7R no se abren del todo, están como una media luna ... el canal 7 de cada 7R está a la mitad en vez de abierto del todo": `Intensidad Ambiente` wrote 110 to every dimmer in the rig and the quiet level held it four minutes (2026-08-29) |
| `humo pegado` | A smoke button whose pump neither sits in the **Intensity** group - the only group QLC+ resets each cycle (`Universe::processFaders` -> `zeroIntensityChannels`) - nor is closed by the function itself (a haze chaser's off step, a SingleShot burst's last step) | "Le doy y no para de echar todo el rato, se supone que solo debe tirar cuando le de": the Fog channel was declared in Effect, so releasing the flash removed the flash's fader and changed nothing (2026-08-29) |
| `figura fuera del publico` | An EFX whose figure - centre plus half-size, per axis - leaves its family's measured pan/tilt window, the part of the room the audience is in | The aim was guessed twice the same night, landing on the floor and then on the wall, until the owner read the corners off the desk: pan 62-103 tilt 207-234 on BEAM #1, pan 76-108 tilt 212-230 on MAC WASH #1 (2026-08-29) |
| `movimiento sin apuntar` | An EFX moving heads whose tilt axis is centred on 127, the raw middle of the channel - what QLC+ writes when nobody aims the figure. Where mid-travel lands is per model: the floor on the 7R, the wall behind the stage on the washes | "Está todo el rato haciendo un circulo pequeño en el suelo": every movement EFX the generator had ever written carried the default `<Axis Name="Y"><Offset>127`, and mid-travel is the floor for the beams and the back wall for the washes (2026-08-29) |
| `cabezas paradas en el ciclo` | A Collection that is a step of a chaser - a block the show runs by itself - moving some heads with an EFX and leaving others still for the whole step. A Collection made of nothing but EFX is not a block: it is one movement QLC+ made the generator write twice (`efx_16bit`), and the heads it does not move are the other family's, moved by the chaser beside it (2026-09-02) | "Las 7R no se mueven", with only AUTO pressed: `Nivel Ambiente` ran the washes' slow shapes beside a static fan scene, so the four beams held one position for the level's four-minute hold (2026-08-29) |
| `unidades de tempo cruzadas` | A function in **Beats** tempo with a non-zero fade that starts something with a clock of its own - an EFX or an RGBMatrix. The chaser hands the fade over as a raw number and `EFX::loopDuration` subtracts it from its millisecond duration. A Collection in between changes nothing (`Collection::write` passes its override fades to every member), so the rule looks through Collections - which every split wash figure is since 2026-09-02 | "Las cabezas van super rapido a 120bpm y no completan los giros": the movement chasers were on Beats with a 10-beat crossfade, so a 16 s sweep became a 6 s one (2026-08-29) |
| `tempo en una coleccion` | A Collection carrying a `<Tempo>`. A Collection has no tempo - it starts its members - and QLC+ logs `Unknown collection tag: Tempo` and drops it | Read out of the show Mac's own QLC+ log (2026-08-29) |
| `modo sin dueño` | A fixture some function lights, carrying a channel it runs its own programmes on, that **no function in the show writes**. `programa interno` covers the ones whose ranges are named ("no function" plus an "auto"); this covers the rest - the MAC WASH's blanket `Function Mode`, the MiN Wash's `Movement Macros`, the CLB2.4's `Preprogrammed automatic Shows`, the fog machines' `Colour Change`. An unwritten channel keeps last night's value, and while it is up the fixture ignores position, colour and dimmer | "Las nuevas cabezas wash se quedaban mirando para abajo y hacían cosas raras como una especie de cambios de colores muy rápidos", with the movement aimed at the measured window and the colour on an eight-beat wheel (2026-08-30) |
| `columna automatica` | The pump of a fog machine **that carries lights** reachable from any button that latches - a Toggle, AUTO, an energy level. A lit machine is a column somebody fires on purpose, not haze: it belongs to a held Flash and nothing else. The fog-only machines are exactly the ones this rule leaves alone, because their timer is the show's business | "El humo vertical nunca debe dispararse solo" (owner, 2026-08-30) |
| `capa que se suma al estado` | A Toggle button whose Scene states a colour on a fixture the running state already colours. RGB is HTP, so the layer adds instead of replacing: red over cyan is white. A colour that replaces is a Flash with `ForceLTP` - the banks and the mixes are, since 2026-09-02 | AUTO on `Rig Cyan` plus key `1` = 255,255,255 on twenty-seven fixtures (cross-audit, 2026-09-02) |
| `estrobo sin negro` | A chaser with a strobe's shape, reachable from a layer button, whose dark steps write only Intensity-group channels: under a lit state the zeros lose the HTP compare and the strobe never reaches black. The honest strobe on a lit room is a held scene on the shutters | `Strobo Rapido` was white / state-colour, never white / black, and slewed the beams' colour wheel every 125 ms (cross-audit, 2026-09-02) |
| `capa que deja huella` | A Toggle button's Scene writing a non-zero value to an LTP channel that no room state ever writes: released, the value stays for the night | `MultiColor - Todas` left the 7R half-colour channel at 255 and every wheel colour came out split (cross-audit, 2026-09-02) |
| `estado que hereda` | A room state that lights a fixture without writing a wheel, its companions, focus, zoom or position that another state can leave showing: the solo frame swaps states and LTP keeps the old one's choice | `Todo Negro` -> `Blanco Total` after a party level: four white beams through a spinning prism on Gobo 5 (cross-audit, 2026-09-02) |
| `color sin dimmer en algun instante` | A state with a reachable instant that colours a fixture while no member writes its dimmer - asked per instant, because merged, another level's base hides the gap. A smoke machine's LEDs count; only its pump is sacred | `Intensidad Peak` shut the four vertical fog machines' pump and left their LED dimmer unwritten: dark for two of the four energy phases and all of `Momento Locura` (cross-audit, 2026-09-02) |
| `capa pisada por el ciclo` | A Toggle button's Scene on a wheel or a position that a chaser inside a state also steps: the step's new fader is appended after the button's and wins, so the pick lasts one step. A Flash with Override lasts as long as the hand | A gobo pick lasted 4 s under Fiesta, `Escenario` 15 s (cross-audit, 2026-09-02) |
| `familia con dueño` | A SoloFrame that offers a state-owned colour, position, gobo, prism or panel-mode family without every state hook, offers a state-reachable pick, or lets another button start a hook | The JUGAR play page needs its family hooks to stop the old state cleanly (2026-09-02) |
| `pick que apaga` | A latched family pick that stops the room-state hooks a SoloFrame monitors, then leaves a coloured fixture without a dimmer writer or with a labelled shutter closed | `Luz Charla` carried Momento Charla's dimmer base, so picking a colour stopped the hook and blacked out the room (2026-09-02) |
| `rueda fundida` | A scene started with a non-zero fade that writes a colour, gobo or prism wheel the fixture does not list in `<ExcludeFade>`: QLC+ fades LTP channels too, from the current value, so a mechanical wheel walks every detent in between. The generator pins the wheels (`exclude_fade`) | `Rueda Colores`'s 800 ms crossfade walked the 7R colour wheel Red -> Blue through orange, yellow and green, 21 steps every 3.3 s (cross-audit, 2026-09-02) |
| `blanco sin emisor blanco` | A Scene that writes red, green or blue on a fixture with a White channel and leaves that channel unwritten: the white LED is the fixture's truest white and stays at 0. `white_level` gives it the colour's share of white | Every white look left the Mini Led's White and the MAC WASH's three at zero (Codex, cross-audit 2026-09-02) |

Dimmer and shutter collisions between a bed and a level are **not** reported.
QLC+ mixes intensity HTP on purpose, and the design - a colour bed underneath,
a level on top - depends on two functions being able to ask for brightness at
once. What `intensidad tapada` rejects is the case where they ask for
*different* brightnesses concurrently, because then one of them is a lie.
Since 2026-08-27 the two ownerships are separate: colour scenes state colour
only, and each energy level (and each moment) carries one intensity base -
`Intensidad Ambiente` low, `Intensidad Total` full - beside its colour.

## What it found on its first run

Four bugs, in a show that had already been fixed twice by hand:

- every per-group colour bank and every two-colour mix skipped the beams, so
  "the heads are red" left four of them on last night's colour;
- `Rueda Mezcla` did the same across the whole rig;
- every matrix button relied on a dimmer that nothing was opening;
- and once the banks were fixed, the beams turned out to be in two fixture
  groups at once, so two mix wheels wrote their colour wheel together.

The last one was a decision about the rig rather than the code, and it is the
shape these findings tend to have: the check does not fix anything, it turns
"a veces acertamos" into one question with a right answer.

## How long an animation is

An RGBMatrix does not run "for a while": it walks a fixed number of frames and
starts again, and how many depends on the script **and on the grid it paints**.
`matrix_step_count` carries those numbers, read out of `rgbMapStepCount` in
QLC+ 5.2.2's own RGBScripts for the default properties the generator writes:

| Script | Frames in one pass | On the 8x3 bars |
| --- | --- | --- |
| `Fill` | the grid's width | 8 |
| `Waves` | width + tail, one less on an odd width | 12 |
| `Even/Odd`, `Alternate`, `Opposite`, `Strobe` | 2 | 2 |
| `One By One` | width x height | 24 |
| Plain (solid colour) | 1 | 1 |
| anything else | `max(width, height)` - too much time rather than too little | 8 |

The cycle holds each matrix for one full pass at its own speed, floored at two
seconds so a solid colour still gets a moment and capped at eight so nothing
drags. A function on **Beats** tempo is skipped by the check: its numbers are
thousandths of a beat, and how long a beat lasts is the room's business.

## The one shutter subtlety

Whether a fixture is open depends on where its shutter *is*, not on whether
anybody wrote to it. A CLB2.4 head labels DMX 0 "no strobe", so an untouched
channel is already open; a BEAM 230W 7R puts open near the top, so an untouched
channel is shut. Only the labelled range separates those two, and reading it
wrong is either two hundred false alarms or a fixture dark that nobody warned
about.
