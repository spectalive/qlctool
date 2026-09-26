# The pad palette (`qlctool pad-palette`)

The M-VAVE SMC-PAD cannot light its own LEDs from QLC+: a small bridge holds
the pad's Bluetooth LED session and paints each pad when QLC+'s feedback says
the widget bound to it lit. The bridge reads which colour each pad wears from
this file, written from the saved show, so the pad under the finger and the
console button above it always read as the same surface.

```
qlctool pad-palette --out "Vibra.pads.json" "QLC+ Setups/Vibra.qxw"
```

## Where the colours come from

A pad is **lit** when the workspace binds a console widget to its input channel
*and* the pad's profile (`qlctool/controllers/smc_pad_profile.py`: the bindings
of `generate/smc_pad_bindings.py`, the colours of `generate/smc_pad_colors.py`)
gives that channel a colour. Every other pad of the two banks the show uses is
**free** and glows a faint grey, `(20, 20, 20)`: a pad that looks lit and does
nothing is a pad somebody will press. A workspace that binds no widget to any
pad writes an empty `pads` list.

## Format 1

The file is JSON with sorted keys, a one-space indent and a trailing newline,
so the same workspace always writes the same bytes.

| Field | Meaning |
|---|---|
| `format` | `1`. A reader refuses any other value. |
| `generator` | `"qlctool pad-palette"`. |
| `device` | the pad profile's name, `"smc-pad"`. |
| `midiChannel` | the MIDI channel the pads speak on, 1-based (10). |
| `show.workspace`, `show.key` | the workspace's file name and its slug. |
| `show.sha256` | the SHA-256 of the workspace the file was written from; a file whose hash no longer matches the workspace beside it is stale. |
| `pads` | every pad of banks 1 and 2 in note order, or `[]`. |

Each pad:

| Field | Meaning |
|---|---|
| `bank`, `pad` | the pad as the operator sees it: bank 1-2, pad 1-16 counting from the bottom-left. |
| `note` | the MIDI note it sends and QLC+'s feedback returns, 36-67. |
| `channel` | the QLC+ input channel the console binds (omni mode). |
| `control` | the catalogue identifier the bindings use (`"flash_full"`), or `null` for a free pad. |
| `widgets` | the ids of the console widgets bound to the pad's channel. |
| `active` | `[r, g, b]` while the function is active (feedback note on). |
| `idle` | `[r, g, b]` while it is idle: `active` divided by 6, rounded down. |
