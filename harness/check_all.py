#!/usr/bin/env python3
"""Run tests, executable verification and the cross-artifact gate as one bundle."""

from __future__ import annotations

import argparse
import ast
from hashlib import sha256
import io
import json
from pathlib import Path
import sys
import unittest

from build_manifest import EXCLUDED_NAME_SUFFIXES, check_manifest
from corpus_gate import run_gate
from ncnc.report import run_reference_verification


ROOT = Path(__file__).resolve().parent

LOCAL_MODULES = frozenset(
    ("ncnc", "check_all", "corpus_gate", "build_manifest", "verify", "tests")
)


def scan_third_party_imports(root: Path = ROOT) -> tuple[str, ...]:
    """Executable discriminator for the no-third-party-dependencies claim."""

    stdlib = set(sys.stdlib_module_names)
    offenders: list[str] = []
    for path in sorted(root.rglob("*.py")):
        if any(part in ("__pycache__", ".pytest_cache") for part in path.parts):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level > 0 or node.module is None:
                    continue
                names = [node.module.split(".")[0]]
            else:
                continue
            for name in names:
                if name not in stdlib and name not in LOCAL_MODULES:
                    offenders.append(f"{path.relative_to(root).as_posix()}:{name}")
    return tuple(offenders)


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_pinned_artifacts(
    reference_digest: str, gate_digest: str, *, root: Path = ROOT
) -> dict[str, object]:
    """Fail closed when expected digests or the package manifest drift."""

    report_path = root / "expected-report.json"
    gate_path = root / "expected-corpus-gate.json"
    errors: list[str] = []
    expected_report = expected_gate = None
    if not report_path.is_file():
        errors.append("missing expected-report.json")
    else:
        expected_report = _load_json(report_path)
        if expected_report.get("report_sha256") != reference_digest:
            errors.append("expected-report.json report_sha256 mismatch")
        if expected_report.get("successful") is not True:
            errors.append("expected-report.json is not successful")
    if not gate_path.is_file():
        errors.append("missing expected-corpus-gate.json")
    else:
        expected_gate = _load_json(gate_path)
        if expected_gate.get("report_sha256") != gate_digest:
            errors.append("expected-corpus-gate.json report_sha256 mismatch")
        if expected_gate.get("successful") is not True:
            errors.append("expected-corpus-gate.json is not successful")
    bundle_path = root / "expected-bundle.json"
    bundle_pin = None
    if not bundle_path.is_file():
        errors.append("missing expected-bundle.json")
    else:
        expected_bundle = _load_json(bundle_path)
        recorded = expected_bundle.get("bundle_sha256")
        body = {
            key: value
            for key, value in expected_bundle.items()
            if key != "bundle_sha256"
        }
        encoded = json.dumps(
            body, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        if sha256(encoded).hexdigest() != recorded:
            errors.append("expected-bundle.json bundle_sha256 mismatch")
        bundle_pin = recorded
        reference_block = expected_bundle.get("reference_report")
        gate_block = expected_bundle.get("corpus_gate")
        pins_block = expected_bundle.get("artifact_pins")
        if (
            not isinstance(reference_block, dict)
            or reference_block.get("sha256") != reference_digest
        ):
            errors.append("expected-bundle.json reference_report sha256 mismatch")
        if not isinstance(gate_block, dict) or gate_block.get("sha256") != gate_digest:
            errors.append("expected-bundle.json corpus_gate sha256 mismatch")
        # Only recomputable fields are pinned here. Pinning the stored tests or
        # top-level success literals would make the documented regeneration
        # fixed point non-convergent, because the first regeneration pass must
        # legitimately record its own transient failure.
        if not isinstance(pins_block, dict) or pins_block.get("manifest_ok") is not True:
            errors.append("expected-bundle.json artifact_pins manifest_ok is not true")
    manifest_ok = check_manifest(root)
    if not manifest_ok:
        errors.append("MANIFEST.sha256 does not match current package bytes")
    return {
        "report_pin": expected_report.get("report_sha256") if expected_report else None,
        "gate_pin": expected_gate.get("report_sha256") if expected_gate else None,
        "bundle_pin": bundle_pin,
        "manifest_ok": manifest_ok,
        "errors": errors,
        "successful": not errors,
    }


def refuse_self_poisoning_output(output: Path, *, root: Path = ROOT) -> str | None:
    """Reject --output writes that would falsify the manifest this bundle certifies."""

    resolved = output.resolve()
    if resolved != root and root not in resolved.parents:
        return None
    if resolved == root / "expected-bundle.json":
        return None
    if resolved.name.endswith(EXCLUDED_NAME_SUFFIXES):
        return None
    return (
        f"refusing --output {output}: an unmanaged write inside the harness tree "
        "would falsify the package manifest that this bundle just certified; "
        "use expected-bundle.json, a manifest-excluded *.ncnc-tmp name, "
        "or a path outside the tree"
    )


def run_bundle() -> dict[str, object]:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    stream = io.StringIO()
    test_result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    reference = run_reference_verification()
    gate = run_gate()
    pins = verify_pinned_artifacts(reference.digest, gate.digest)
    third_party = scan_third_party_imports()
    payload: dict[str, object] = {
        "schema": "ncnc-verification-bundle-v2",
        "tests": {
            "run": test_result.testsRun,
            "failures": len(test_result.failures),
            "errors": len(test_result.errors),
            "skipped": len(test_result.skipped),
            "successful": test_result.wasSuccessful(),
        },
        "reference_report": {
            "schema": reference.schema,
            "sha256": reference.digest,
            "successful": reference.successful,
        },
        "corpus_gate": {
            "schema": gate.schema,
            "sha256": gate.digest,
            "successful": gate.successful,
        },
        "artifact_pins": {
            "successful": pins["successful"],
            "errors": pins["errors"],
            "report_pin": pins["report_pin"],
            "gate_pin": pins["gate_pin"],
            "bundle_pin": pins["bundle_pin"],
            "manifest_ok": pins["manifest_ok"],
        },
        "stdlib_only": {
            "offenders": list(third_party),
            "successful": not third_party,
        },
    }
    payload["successful"] = bool(
        test_result.wasSuccessful()
        and reference.successful
        and gate.successful
        and pins["successful"]
        and not third_party
    )
    if not test_result.wasSuccessful():
        payload["test_output"] = stream.getvalue()
    if not pins["successful"]:
        payload["pin_errors"] = pins["errors"]
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    payload["bundle_sha256"] = sha256(encoded).hexdigest()
    return payload


def render_text(payload: dict[str, object]) -> str:
    tests = payload["tests"]
    reference = payload["reference_report"]
    gate = payload["corpus_gate"]
    assert isinstance(tests, dict)
    assert isinstance(reference, dict)
    assert isinstance(gate, dict)
    pins = payload.get("artifact_pins", {})
    assert isinstance(pins, dict)
    stdlib_only = payload.get("stdlib_only", {})
    assert isinstance(stdlib_only, dict)
    return "\n".join(
        (
            "NCNC verification bundle",
            f"successful: {str(payload['successful']).lower()}",
            f"tests: {tests['run']} run, {tests['failures']} failures, {tests['errors']} errors",
            f"reference_report: {reference['sha256']}",
            f"corpus_gate: {gate['sha256']}",
            f"artifact_pins: {str(pins.get('successful')).lower()}",
            f"stdlib_only: {str(stdlib_only.get('successful')).lower()}",
            f"bundle_sha256: {payload['bundle_sha256']}",
            "",
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the complete finite NCNC bundle.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.output is not None:
        refusal = refuse_self_poisoning_output(args.output)
        if refusal is not None:
            print(refusal, file=sys.stderr)
            return 2
    payload = run_bundle()
    rendered = (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.format == "json"
        else render_text(payload)
    )
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    return 0 if payload["successful"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
