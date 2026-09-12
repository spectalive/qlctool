"""The M-VAVE SMC-PAD's wire behaviour, measured on the rig, as channel numbers.

Everything that has to agree about this pad - the console's `<Input>` bindings,
the QLC+ input profile in `QLC+ InputProfiles/`, the LED bridge - derives its
numbers from here, because when they were written out three times by hand they
drifted: the shipped profile still declared the pad's factory notes 4-19 while
the workspace was bound to 36-51, and eight of the console's bindings sat on
notes no button on the device can send.

**This is the pad's factory map, which is the whole point.** Re-measured
2026-08-29 immediately after a factory reset from MidiSuite, and every number
below came back identical - so the show needs no pad configuration at all, and
a pad knocked out of shape is restored by resetting it rather than by
reconfiguring it control by control. (An earlier capture that day read notes
4-19 and got written into the shipped input profile; that was the pad sitting
in some non-factory preset, not the default.)

Measured 2026-08-29 with `tools/smc-pad/midicap.swift`, owner pressing:

- The pads speak on MIDI channel 10 and are numbered as the panel silkscreens
  them - PAD1 bottom-left, PAD13 top-left, like a Launchpad. PAD13 sent note
  48, PAD1 note 36 and PAD16 note 51, so within a bank the note is
  `FIRST_PAD_NOTE + pad - 1` counting up from the bottom-left.
- **PAD BANK** (right edge) moves the whole surface a bank up: PAD1 answered 52
  instead of 36, so a bank is 16 notes. That is the pad's only second layer -
  the console's JUGAR/page-2 hooks live on bank 2.
- **SHIFT** sends no MIDI at all. It selects the functions silkscreened on the
  pads themselves (SWING, LATCH, SYNC, TAP TEMPO), which are internal to the
  device. Nothing on the console can be bound to it, which is why the JUGAR
  controls use PAD BANK instead.
- The arrows `<` and `>` send CC 25 and CC 26 and do **not** change the bank -
  pressed between three hits of the same pad, the note never moved. So they are
  safe as the console's page arrows.
- The knobs send CC 30-37 absolute, and the five buttons under the arrows
  CC 27 (play), 28 (pause), 29 (record), all on MIDI channel 1.

Because the device splits its controls over two MIDI channels, the QLC+ MIDI
input must run in omni mode (`midichannel="16"`, `MAX_MIDI_CHANNELS` in
`plugins/midi/src/common/midiprotocol.cpp`). In omni QLC+ ORs the 0-based MIDI
channel into bits 12+ of the input channel number, and offsets notes by 128
(`CHANNEL_OFFSET_NOTE`); a control change is its CC number unchanged.

The bank the pad powers up in is **remembered by the device**, not by the show:
a pad left on bank 2 fires the JUGAR/page-2 hooks where the show page expects
its hits. `docs/show-operation.md` says so where an operator will read it.
"""

# 1-based, the way both the pad's manual and QLC+'s own UI count MIDI channels.
PAD_MIDI_CHANNEL = 10
CONTROL_MIDI_CHANNEL = 1

# QLC+'s omni-mode input channel arithmetic (plugins/midi/src/common).
OMNI_CHANNEL_SHIFT = 12
NOTE_OFFSET = 128

PADS = 16
FIRST_PAD_NOTE = 36


def pad_channel(pad: int, bank: int = 1) -> int:
    """The QLC+ input channel for physical pad 1-16 on bank 1 or 2."""
    if not 1 <= pad <= PADS:
        raise ValueError(f"pad {pad} is not one of the device's 1-{PADS}")
    if bank not in (1, 2):
        raise ValueError(f"bank {bank}: the show only uses the pad's first two")
    note = FIRST_PAD_NOTE + (bank - 1) * PADS + pad - 1
    return ((PAD_MIDI_CHANNEL - 1) << OMNI_CHANNEL_SHIFT) + NOTE_OFFSET + note


def control_channel(cc: int) -> int:
    """The QLC+ input channel for a knob or button's control change."""
    if not 0 <= cc <= 127:
        raise ValueError(f"CC {cc} is outside MIDI's 0-127")
    return ((CONTROL_MIDI_CHANNEL - 1) << OMNI_CHANNEL_SHIFT) + cc
