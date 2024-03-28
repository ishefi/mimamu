#!/usr/bin/env python

import sys
from argparse import ArgumentParser
from pathlib import Path

import pytest

base = Path(__file__).absolute().parent.parent
sys.path.extend([str(base)])


def main() -> None:
    parser = ArgumentParser("Run unit tests")
    parser.add_argument(
        "--no-coverage", action="store_true", help="Do not add in coverage options"
    )
    other_args, pytest_args = parser.parse_known_args()

    args = ["--durations=5", "-v", "--tb=short", "--color=yes"]

    args.extend(pytest_args)

    if all(arg.startswith("-") for arg in pytest_args):
        args.append("tests")

    has_config = any(arg.startswith("--cov-config") for arg in args)
    if not has_config and not other_args.no_coverage:
        args.extend(["--cov-config=pyproject.toml", "--cov=."])

    print(f"pytest {' '.join(args)}", file=sys.stderr)

    return_value = pytest.main(args)

    raise SystemExit(return_value)


if __name__ == "__main__":
    main()
