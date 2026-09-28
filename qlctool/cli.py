"""Command-line entry point for qlctool.

Thin wrapper over the library so the owner can run generators without writing
Python: inspect a workspace, or generate a colour palette + cycle chaser into a
copy. Never overwrites the input - it always writes a new file.
"""

import argparse
from dataclasses import replace
from pathlib import Path

from .add_check_parser import add_check_parser
from .add_deskmap_parser import add_deskmap_parser
from .add_info_parser import add_info_parser
from .add_matrix_parser import add_matrix_parser
from .add_mcp_parser import add_mcp_parser
from .add_movement_parser import add_movement_parser
from .add_pad_palette_parser import add_pad_palette_parser
from .add_palette_parser import add_palette_parser
from .add_patch_parser import add_patch_parser
from .apply_install import apply_install
from .beam_landing import beam_landing
from .capabilities_of import capabilities_of
from .compose_workspace import compose_workspace
from .decompose_workspace import decompose_workspace
from .default_out import default_out
from .description.described_files import described_files
from .description.description_names import description_names
from .description.load_show_description import load_show_description
from .finish import finish
from .fixture_dirs import fixture_dirs
from .generate.apply_stage_plot import apply_stage_plot
from .generate.build_canonical_show import build_canonical_show
from .generate.build_refusal_error import BuildRefusalError
from .generate.generate_channel_probe import generate_channel_probe
from .generate.generate_stage_layout import DEFAULT_STAGE, generate_stage_layout
from .generate.generate_vc_layout import generate_vc_layout
from .generate.input_profile import build_input_profile
from .install_plan import install_plan
from .lay_out import lay_out
from .library_for import library_for
from .load_stage_plot import load_stage_plot
from .mvr.write_mvr import write_mvr
from .newshow_refusal import newshow_refusal
from .prop_item import POINTS_OF_VIEW
from .qlc_gobo_dir import qlc_gobo_dir
from .qlc_user_dir import qlc_user_dir
from .stage_size import stage_size
from .toolkit_config_from import toolkit_config_from
from .validate_workspace import validate_workspace
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


def cmd_probe(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else default_out(src)

    base = {}
    for pair in (args.base or "").split(","):
        if not pair:
            continue
        channel, value = pair.split("=", 1)
        base[int(channel) - 1] = int(value)

    ws = Workspace.load(src)
    result = generate_channel_probe(
        ws, args.fixture, value=args.value, base_values=base, hold=args.hold
    )
    lay_out(ws, [*result.scene_ids, result.chaser_id], args.buttons)
    ws.save(out)

    print(
        f"Generated {len(result.scene_ids)} probe scenes for fixture {args.fixture} + 1 walk chaser"
    )
    return finish(out, args.validate)


def cmd_layout(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else default_out(src)

    ws = Workspace.load(src)
    layout = generate_vc_layout(ws, columns=args.columns)
    ws.save(out)

    print(f"Laid out {len(layout.button_ids)} buttons in {len(layout.frame_ids)} frame(s)")
    return finish(out, args.validate)


def cmd_stage(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else default_out(src)

    ws = Workspace.load(src)
    library = library_for(args.fixtures, src)
    warn_unresolved(ws.root, library)
    if args.plot:
        plot = apply_stage_plot(ws, load_stage_plot(args.plot, ws.root))
        ws.save(out)
        print(
            f"Applied {plot.name!r}: {len(plot.rigged)} fixtures rigged, "
            f"{len(plot.spare)} spare and hidden, on a "
            f"{plot.stage[0]}x{plot.stage[1]}x{plot.stage[2]} m stage seen "
            f"from the {plot.point_of_view}."
        )
        # Where each beam ends up, because an angle that looks right in the
        # preview can still be putting the light on the DJ's face.
        caps = {c.fixture.fixture_id: c for c in capabilities_of(ws.root, library)}
        for item in sorted(plot.items, key=lambda i: i.fixture_id):
            if item.hidden or item.fixture_id not in caps:
                continue
            landing = beam_landing(item, caps[item.fixture_id])
            where = f"floor at z={landing.z:.0f}" if landing.z is not None else landing.reason
            print(f"  [{item.fixture_id:>2}] {plot.places[item.fixture_id]}\n       {where}")
        return finish(out, args.validate)

    stage = generate_stage_layout(
        ws,
        library,
        stage=stage_size(args.stage),
        point_of_view=args.pov,
    )
    ws.save(out)

    print(
        f"Placed {stage.placed} fixtures on a "
        f"{stage.stage[0]}x{stage.stage[1]}x{stage.stage[2]} m stage, "
        f"seen from the {stage.point_of_view}:"
    )
    for band, fixture_ids in stage.rows.items():
        print(f"  {band:<7} {len(fixture_ids)}: {fixture_ids}")
    return finish(out, args.validate)


def cmd_mvr(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else src.with_suffix(".mvr")
    gobos = Path(args.gobos) if args.gobos else src.parent / "Gobos"
    ws = Workspace.load(src)
    library = library_for(args.fixtures, src)
    warn_unresolved(ws.root, library)
    export = write_mvr(ws, library, out, gobos)
    print(
        f"Wrote {export.path}: {len(export.fixtures)} fixtures placed, "
        f"{len(export.gdtf_files)} GDTF fixture types inside."
    )
    for name in export.gdtf_files:
        print(f"  {name}")
    for name, why in export.skipped.items():
        print(f"  skipped {name}: {why}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    result = validate_workspace(args.workspace)
    if result.ok:
        print(f"{args.workspace}: QLC+ loaded it with no complaints")
        return 0
    print(f"{args.workspace}: QLC+ reported {len(result.errors)} problem(s)")
    for error in result.errors:
        print(f"  {error}")
    return 1


def cmd_install(args: argparse.Namespace) -> int:
    """Hand QLC+ the configured definitions, profile and gobos - or say what it lacks.

    The fixture folders follow ruling B3 (`--fixtures`, QLCTOOL_FIXTURES, then
    the nearest qlctool.toml); the profiles and gobos come from qlctool.toml.
    A definition the repo fixed and QLC+ never received is the silent failure
    this exists for: the show loads, validates and runs on last week's channel
    map. `--check` is the question, exit 1 is the answer.
    """
    config = toolkit_config_from(Path.cwd())
    fixtures = fixture_dirs(args.fixtures or (), (), None, Path.cwd())
    if fixtures:
        config = replace(config, fixtures=fixtures)
    items = install_plan(config, user_dir=qlc_user_dir(), gobo_dir=qlc_gobo_dir())
    behind = [item for item in items if item.needs_copy]
    if not args.check:
        for item in apply_install(behind):
            print(f"  {item.state:<8} {item.source.name} -> {item.destination}")
        print(f"{len(behind)} file(s) copied, {len(items) - len(behind)} already in sync")
        return 0
    for item in behind:
        print(f"  {item.state:<8} {item.source.name} -> {item.destination}")
    if behind:
        print(
            f"QLC+ is behind the repo on {len(behind)} of {len(items)} file(s); run qlctool install"
        )
        return 1
    print(f"QLC+ has every one of the configured {len(items)} file(s)")
    return 0


def cmd_input_profile(args: argparse.Namespace) -> int:
    """Write the SMC-PAD's QLC+ input profile from the map the show uses."""
    Path(args.out).write_bytes(build_input_profile())
    print(f"Wrote {args.out}")
    return 0


def cmd_decompose(args: argparse.Namespace) -> int:
    decompose_workspace(args.workspace, args.out_dir)
    print(
        f"Decomposed {args.workspace} -> {args.out_dir}/ (skeleton.qxw, functions/, manifest.json)"
    )
    return 0


def cmd_compose(args: argparse.Namespace) -> int:
    compose_workspace(args.src_dir, args.out)
    print(f"Composed {args.src_dir}/ -> {args.out}")
    return finish(Path(args.out), args.validate)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qlctool", description=__doc__)
    parser.add_argument(
        "--fixtures",
        action="append",
        metavar="DIR",
        help="a folder of .qxf definitions; repeat for more (default: qlctool.toml)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_info_parser(sub)
    add_palette_parser(sub)
    add_matrix_parser(sub)
    add_movement_parser(sub)
    add_patch_parser(sub)

    p_new = sub.add_parser(
        "newshow",
        help="build a fresh show on an existing patch: strip the functions, "
        "generate palette + matrices + movement + console",
    )
    p_new.add_argument(
        "workspace",
        nargs="?",
        help="the show to take the patch from (default: the description's [rig] workspace)",
    )
    p_new.add_argument(
        "--description",
        metavar="FILE",
        help="a show description (.toml): palette, matrices, timing, console, controllers",
    )
    p_new.add_argument(
        "--out",
        help="output file (default: Vibra.qxw beside the workspace; with --description, "
        "the description's [rig] output, and newshow refuses when neither is given)",
    )
    p_new.add_argument(
        "--plot",
        metavar="FILE",
        help="stage plot to place the rig with, instead of the generated band layout",
    )
    p_new.add_argument("--no-buttons", action="store_true", help="skip the Virtual Console layout")
    p_new.add_argument(
        "--beats",
        action="store_true",
        help="run the chases on the music's beat: Beats tempo "
        "plus the audio input as beat generator (needs an "
        "audio input picked in QLC+, or nothing advances)",
    )
    p_new.add_argument(
        "--bpm-tap",
        action="store_true",
        help="the build for a QLC+ newer than 5.2.2: chases in "
        "Beats tempo and page 1's tap dial driving the "
        "global BPM (ControlBPM), which 5.2.2 ignores",
    )
    p_new.add_argument(
        "--validate", action="store_true", help="load the result in QLC+ and fail on any problem"
    )
    p_new.set_defaults(func=cmd_newshow)

    p_prb = sub.add_parser(
        "probe",
        help="one scene per DMX channel of a fixture, to find out on site what each channel does",
    )
    p_prb.add_argument("workspace")
    p_prb.add_argument("fixture", type=int, help="fixture ID (see `qlctool info`)")
    p_prb.add_argument(
        "--value", type=int, default=255, help="value to drive the channel under test (default 255)"
    )
    p_prb.add_argument(
        "--base",
        metavar="CH=VAL,...",
        help="channels to hold steady while probing, 1-based "
        "(e.g. a dimmer that must be open: 7=255)",
    )
    p_prb.add_argument(
        "--hold", type=int, default=3000, help="ms per step in the walk chaser (default 3000)"
    )
    p_prb.add_argument("--buttons", action="store_true", help="also add Virtual Console buttons")
    p_prb.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_prb.add_argument(
        "--validate", action="store_true", help="load the result in QLC+ and fail on any problem"
    )
    p_prb.set_defaults(func=cmd_probe)

    p_lay = sub.add_parser(
        "layout",
        help="add Virtual Console buttons for every function that has a folder",
    )
    p_lay.add_argument("workspace")
    p_lay.add_argument("--columns", type=int, default=6, help="buttons per row (default 6)")
    p_lay.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_lay.add_argument(
        "--validate", action="store_true", help="load the result in QLC+ and fail on any problem"
    )
    p_lay.set_defaults(func=cmd_layout)

    p_stage = sub.add_parser(
        "stage",
        help="place every fixture in the 2D/3D view: a row per band, spread across the stage",
    )
    p_stage.add_argument("workspace")
    p_stage.add_argument(
        "--plot",
        metavar="FILE",
        help="a written stage plot to apply verbatim; without it the layout is "
        "generated from what each fixture can do",
    )
    p_stage.add_argument(
        "--stage",
        metavar="WxHxD",
        help="stage size in metres (default "
        f"{DEFAULT_STAGE[0]}x{DEFAULT_STAGE[1]}x{DEFAULT_STAGE[2]})",
    )
    p_stage.add_argument(
        "--pov",
        default="front",
        choices=sorted(POINTS_OF_VIEW),
        help="point of view the 2D view opens in (default front)",
    )
    p_stage.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_stage.add_argument(
        "--validate", action="store_true", help="load the result in QLC+ and fail on any problem"
    )
    p_stage.set_defaults(func=cmd_stage)

    p_mvr = sub.add_parser(
        "mvr",
        help="export the placed rig as an MVR package with a GDTF per definition, "
        "for BlenderDMX or any GDTF visualiser",
    )
    p_mvr.add_argument("workspace")
    p_mvr.add_argument("--out", help="output file (default: <workspace>.mvr next to it)")
    p_mvr.add_argument(
        "--gobos",
        metavar="DIR",
        help="folder holding the gobo images the definitions name "
        "(default: Gobos/ next to the workspace)",
    )
    p_mvr.set_defaults(func=cmd_mvr)

    p_val = sub.add_parser("validate", help="load a workspace in headless QLC+ and report problems")
    p_val.add_argument("workspace")
    p_val.set_defaults(func=cmd_validate)

    add_check_parser(sub)

    p_inst = sub.add_parser(
        "install",
        help="copy the configured fixture definitions, input profiles and gobos "
        "into the installed QLC+; --check only reports what it is missing",
    )
    p_inst.add_argument(
        "--check",
        action="store_true",
        help="report stale or missing copies and exit 1 on any, copy nothing",
    )
    p_inst.set_defaults(func=cmd_install)

    p_prof = sub.add_parser(
        "input-profile",
        help="write the SMC-PAD's QLC+ input profile from the show's own map",
    )
    p_prof.add_argument("out", help="destination .qxi file")
    p_prof.set_defaults(func=cmd_input_profile)

    p_dec = sub.add_parser("decompose", help="split a workspace into a git-diffable fragment tree")
    p_dec.add_argument("workspace")
    p_dec.add_argument("out_dir")
    p_dec.set_defaults(func=cmd_decompose)

    add_deskmap_parser(sub)
    add_pad_palette_parser(sub)
    add_mcp_parser(sub)

    p_com = sub.add_parser("compose", help="rebuild a workspace from a fragment tree")
    p_com.add_argument("src_dir")
    p_com.add_argument("out")
    p_com.add_argument(
        "--validate",
        action="store_true",
        help="load the result in headless QLC+ and fail on any problem it reports",
    )
    p_com.set_defaults(func=cmd_compose)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
