# The desk map: releasing a latched pick

`qlctool deskmap` writes the tablet desk's map (`schema: 2`). This page covers
one optional field of a control, `releaseTo`. dmxdesk reads the map with cJSON
and ignores the keys it does not know, so a desk that does not implement it
simply does not press anything on a release.

## Why the desk presses a hook

Picks stay latched (ruling D8, 2026-09-27). A pick in a family frame (colour,
pixels, heads, gobos, prism) stops the frame's hook when it starts, and when it
is toggled off QLC+ 5 restarts nothing: its solo frame has no restore. The show
itself leaves the release clean - every room state starts a floor under each
family it plays, so the LTP channels fall back to the family at rest - but the
look the room was running only comes back when somebody presses the frame's
hook. The pad and the keyboard leave that to the operator; the tablet does it.

## The field

```json
"gobo-shake-gobo-1": {
  "widget": 168,
  "role": "pick",
  "solo": 138,
  "action": "toggle",
  "releaseTo": { "5": 140, "6": 140, "7": 139, "8": 139 }
}
```

- **Key:** the decimal widget id of a control with `role: "state"` (JSON keys
  are strings; parse it back with `strtol`).
- **Value:** the widget id of the frame hook that state starts: a control with
  `role: "hook"` in the same `solo` frame.
- A state is listed only when it starts **exactly one** of the frame's hooks,
  read from the show's function graph. A state that starts none, or more than
  one, is left out: AUTO starts two or three of the heads', gobo and prism
  hooks through its energy levels, so which one is right depends on the level
  playing. There the desk presses nothing at all: the family sits on the
  floor - centred, gobo open, prism out - until AUTO's own next level step
  restarts the right hook, and `Ciclo Energia` holds a level for up to 480 s
  (240 s, 480 s, 40 s or 240 s depending on which one is running). An operator
  who wants the look back sooner presses the hook themselves.
- The object is omitted when it would be empty. Room-state controls never
  carry it.
- A control the desk places among the hooks can carry it too: `Colores
  simples`, `Pastel tenue`, `Multicolor` and `Mezcla` are latched picks of the
  colour frame in the graph.

## The contract

When the operator releases (toggles off) a control that has `releaseTo`:

1. Look up the widget of the room-state control that is on (`DESK_ON`).
2. If `releaseTo` has no entry for that state, press nothing.
3. Otherwise send `<hook>|255` - and only if the hook's widget is not already
   on. The hook is a Toggle: pressing it while it runs switches it off, which
   can happen when AUTO's energy cycle or the operator restarted it within
   the desk's press spacing. Send 255 only; QLC+'s web API toggles on 0 too.

The field is derived by `qlctool/desk_release_hooks.py`.
