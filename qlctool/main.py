"""The qlctool command: parse the arguments and run the chosen command."""

from .build_parser import build_parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    status: int = args.func(args)
    return status
