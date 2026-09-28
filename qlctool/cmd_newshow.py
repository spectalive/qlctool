"""`qlctool newshow`: build a fresh show on an existing patch."""

import argparse
from pathlib import Path

from .description.described_files import described_files
from .description.description_names import description_names
from .description.load_show_description import load_show_description
from .finish import finish
from .generate.build_canonical_show import build_canonical_show
from .generate.build_refusal_error import BuildRefusalError
from .library_for import library_for
from .newshow_refusal import newshow_refusal
from .vibra.vibra_description import vibra_description
from .warn_unresolved import warn_unresolved
from .workspace import Workspace


def cmd_newshow(args: argparse.Namespace) -> int:
    if args.workspace is None and args.description is None:
        raise SystemExit("newshow needs a workspace or --description")
    try:
        if args.description:
            src, out = described_files(args.workspace, args.description, args.out)
        else:
            src = Path(args.workspace)
            out = Path(args.out) if args.out else src.with_name("Vibra.qxw")
        ws = Workspace.load(src)
        description = load_show_description(args.description, ws.root) if args.description else None
    except (ValueError, OSError) as error:
        # A mistake in the file the user wrote, or a patch it names that is not
        # there: say what and where, no traceback.
        raise SystemExit(str(error)) from error
    plot = args.plot
    if plot is None and description is not None and description.rig.stage_plot is not None:
        plot = str(description.rig.stage_plot)
    shown = description or vibra_description()
    beats = args.beats or shown.timing.beats
    auto_key = shown.console.keys.get("auto")
    auto_hint = f" (key {auto_key})" if auto_key else ""

    library = library_for(args.fixtures, src, description.rig.fixtures if description else ())
    vocabulary = description_names(shown)
    warn_unresolved(ws.root, library, vocabulary)
    refusal = newshow_refusal(ws.root, library, vocabulary)
    if refusal is not None:
        raise SystemExit(refusal)
    try:
        show = build_canonical_show(
            ws,
            library,
            with_layout=not args.no_buttons,
            plot_path=plot,
            beats=args.beats,
            bpm_tap=args.bpm_tap,
            description=description,
        )
    except BuildRefusalError as refused:
        raise SystemExit(str(refused)) from refused
    ws.save(out)

    colors = sum(len(b.scene_ids) + len(b.split_ids) for b in show.banks)
    print(
        f"Built a self-running show on the same patch: {show.function_count} "
        f"functions ({colors} colour scenes across {len(show.banks)} groups, "
        f"{len(show.matrix_ids)} matrices, {len(show.efx_ids)} movement EFX, "
        f"{len(show.gobo_ids)} gobos, {len(show.prism_ids)} prism, plus "
        f"dimmer chase, ping-pong and strobes), "
        f"{len(show.button_ids)} console buttons on one "
        f"{shown.console.canvas[0]}x{shown.console.canvas[1]} screen, "
        f"{show.stage_placed} fixtures placed in the 2D/3D view. "
        f"Press AUTO{auto_hint}."
    )
    if beats:
        print(
            "Chases are on Beats tempo and the beat generator is the audio "
            "input: pick one under QLC+ Configuration, or nothing advances."
        )
    if args.bpm_tap:
        print(
            "Chases are on Beats tempo and page 1's tap dial sets the global "
            "BPM. QLC+ 5.2.2 does NOT support that dial ('Unknown speed dial "
            "tag: ControlBPM') - this build is for a newer QLC+."
        )
    return finish(out, args.validate)
