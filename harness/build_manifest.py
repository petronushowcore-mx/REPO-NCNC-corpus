#!/usr/bin/env python3
"""Write or verify the deterministic SHA-256 inventory for this harness."""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
MANIFEST_NAME = "MANIFEST.sha256"
EXCLUDED_PARTS = frozenset(("__pycache__", ".pytest_cache"))
EXCLUDED_SUFFIXES = frozenset((".pyc",))
EXCLUDED_NAME_SUFFIXES = (".ncnc-tmp",)


def distributable_files(root: Path = ROOT) -> tuple[Path, ...]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"symbolic links are outside the manifest contract: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if relative.as_posix() == MANIFEST_NAME:
            continue
        # Match cache names against directory components only (parts[:-1]) so a
        # regular file that happens to be named e.g. ".pytest_cache" stays hashed.
        if any(part in EXCLUDED_PARTS for part in relative.parts[:-1]):
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        if path.name.endswith(EXCLUDED_NAME_SUFFIXES):
            continue
        files.append(path)
    return tuple(sorted(files, key=lambda item: item.relative_to(root).as_posix()))


def manifest_entries(root: Path = ROOT) -> tuple[tuple[str, str], ...]:
    return tuple(
        (
            sha256(path.read_bytes()).hexdigest(),
            path.relative_to(root).as_posix(),
        )
        for path in distributable_files(root)
    )


def manifest_text(root: Path = ROOT) -> str:
    return "".join(f"{digest}  {relative}\n" for digest, relative in manifest_entries(root))


def check_manifest(root: Path = ROOT) -> bool:
    path = root / MANIFEST_NAME
    if not path.is_file():
        print(f"missing {MANIFEST_NAME}", file=sys.stderr)
        return False
    expected = manifest_text(root)
    actual = path.read_text(encoding="utf-8")
    if actual != expected:
        print(f"{MANIFEST_NAME} does not match current package bytes", file=sys.stderr)
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="replace the manifest")
    mode.add_argument("--check", action="store_true", help="verify the current manifest")
    args = parser.parse_args(argv)
    path = ROOT / MANIFEST_NAME
    if args.write:
        path.write_text(manifest_text(ROOT), encoding="utf-8", newline="\n")
        print(f"wrote {path.name} ({len(manifest_entries(ROOT))} files)")
        return 0
    if check_manifest(ROOT):
        print(f"verified {path.name} ({len(manifest_entries(ROOT))} files)")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
