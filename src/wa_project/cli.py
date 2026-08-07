"""Command-line workflow for editing a WeakAuras import."""

from __future__ import annotations

import argparse
from pathlib import Path

from .build import DEFAULT_OUTPUT, build, inspect_package, validate


def _cmd_build(output: Path) -> None:
    package = build(output=output)
    groups = package.get("c", [])
    children = sum(
        len(group.get("c", []))
        for group in groups
        if isinstance(group, dict) and isinstance(group.get("c", []), list)
    )
    print(f"Built {output}")
    print(f"root: {package.get('d', {}).get('id', '<missing>')}")
    print(f"groups: {len(groups) if isinstance(groups, list) else '<not a list>'}")
    print(f"children: {children}")


def _cmd_inspect() -> None:
    summary = inspect_package()
    for key, value in summary.items():
        print(f"{key}: {value}")


def _cmd_validate() -> None:
    validate()
    print("Validated code-defined package")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    build_parser = commands.add_parser("build", help="build the final WA import string")
    build_parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)

    commands.add_parser("inspect", help="inspect the code-defined package")

    commands.add_parser("validate", help="validate the code-defined round trip")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "build":
        _cmd_build(args.output)
    elif args.command == "inspect":
        _cmd_inspect()
    elif args.command == "validate":
        _cmd_validate()


if __name__ == "__main__":
    main()
