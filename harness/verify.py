#!/usr/bin/env python3
"""Run the deterministic NCNC finite reference verification."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from ncnc.report import render_json, render_text, run_reference_verification


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Exhaust the finite NCNC reference fixtures and mutation teeth."
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="deterministic report format",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="optional UTF-8 output path; stdout is used by default",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_reference_verification()
    rendered = render_json(report) if args.format == "json" else render_text(report)
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    return 0 if report.successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
