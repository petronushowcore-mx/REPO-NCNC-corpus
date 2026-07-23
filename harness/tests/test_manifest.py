from __future__ import annotations

from contextlib import redirect_stderr
import io
import json
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from build_manifest import MANIFEST_NAME, check_manifest, manifest_entries, manifest_text


class ManifestTests(unittest.TestCase):
    def test_manifest_is_sorted_and_excludes_generated_noise(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "z.txt").write_text("z", encoding="utf-8")
            (root / "a.txt").write_text("a", encoding="utf-8")
            (root / MANIFEST_NAME).write_text("ignored", encoding="utf-8")
            (root / "leftover.ncnc-tmp").write_text("ignored", encoding="utf-8")
            cache = root / "__pycache__"
            cache.mkdir()
            (cache / "x.pyc").write_bytes(b"ignored")
            entries = manifest_entries(root)
            self.assertEqual(tuple(relative for _, relative in entries), ("a.txt", "z.txt"))

    def test_manifest_excludes_pytest_cache(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "kept.txt").write_text("kept", encoding="utf-8")
            cache = root / ".pytest_cache"
            (cache / "v" / "cache").mkdir(parents=True)
            (cache / "CACHEDIR.TAG").write_text("ignored", encoding="utf-8")
            (cache / "v" / "cache" / "nodeids").write_text("ignored", encoding="utf-8")
            entries = manifest_entries(root)
            self.assertEqual(tuple(relative for _, relative in entries), ("kept.txt",))

    def test_manifest_keeps_regular_file_named_pytest_cache(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b"not a cache directory"
            target = root / ".pytest_cache"
            target.write_bytes(payload)
            self.assertEqual(
                manifest_entries(root),
                ((sha256(payload).hexdigest(), ".pytest_cache"),),
            )
            (root / MANIFEST_NAME).write_text(
                manifest_text(root), encoding="utf-8", newline="\n"
            )
            self.assertTrue(check_manifest(root))
            target.write_bytes(b"mutated bytes")
            with redirect_stderr(io.StringIO()):
                self.assertFalse(check_manifest(root))

    def test_manifest_hashes_exact_file_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = bytes.fromhex("65786163742d627974657300ff")
            (root / "payload.bin").write_bytes(payload)
            self.assertEqual(
                manifest_entries(root),
                ((sha256(payload).hexdigest(), "payload.bin"),),
            )

    def test_manifest_check_detects_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "paper.txt"
            target.write_text("sealed", encoding="utf-8")
            (root / MANIFEST_NAME).write_text(
                manifest_text(root), encoding="utf-8", newline="\n"
            )
            self.assertTrue(check_manifest(root))
            target.write_text("changed", encoding="utf-8")
            with redirect_stderr(io.StringIO()):
                self.assertFalse(check_manifest(root))



class ArtifactPinTests(unittest.TestCase):
    REPORT_DIGEST = "a" * 64
    GATE_DIGEST = "b" * 64

    @staticmethod
    def _write_pin(root: Path, name: str, digest: str, *, successful: bool = True) -> None:
        (root / name).write_text(
            json.dumps({"report_sha256": digest, "successful": successful}),
            encoding="utf-8",
            newline="\n",
        )

    @staticmethod
    def _write_bundle_pin(
        root: Path,
        reference_digest: str,
        gate_digest: str,
        *,
        manifest_ok: bool = True,
        corrupt_digest: bool = False,
    ) -> None:
        body = {
            "reference_report": {"sha256": reference_digest},
            "corpus_gate": {"sha256": gate_digest},
            "artifact_pins": {"manifest_ok": manifest_ok},
        }
        encoded = json.dumps(
            body, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        recorded = sha256(encoded).hexdigest()
        if corrupt_digest:
            recorded = "0" * 64
        (root / "expected-bundle.json").write_text(
            json.dumps({**body, "bundle_sha256": recorded}),
            encoding="utf-8",
            newline="\n",
        )

    def _seal_manifest(self, root: Path, *, ensure_bundle: bool = True) -> None:
        if ensure_bundle and not (root / "expected-bundle.json").is_file():
            self._write_bundle_pin(root, self.REPORT_DIGEST, self.GATE_DIGEST)
        (root / MANIFEST_NAME).write_text(
            manifest_text(root), encoding="utf-8", newline="\n"
        )

    def test_pin_verifier_detects_digest_mismatch(self) -> None:
        from check_all import verify_pinned_artifacts

        pins = verify_pinned_artifacts("0" * 64, "1" * 64)
        self.assertFalse(pins["successful"])
        self.assertTrue(
            any("report_sha256 mismatch" in err for err in pins["errors"])
        )

    def test_pin_verifier_passes_on_consistent_fixture(self) -> None:
        from check_all import verify_pinned_artifacts

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_pin(root, "expected-report.json", self.REPORT_DIGEST)
            self._write_pin(root, "expected-corpus-gate.json", self.GATE_DIGEST)
            self._seal_manifest(root)
            pins = verify_pinned_artifacts(
                self.REPORT_DIGEST, self.GATE_DIGEST, root=root
            )
            self.assertTrue(pins["successful"])
            self.assertEqual(pins["errors"], [])
            self.assertTrue(pins["manifest_ok"])

    def test_pin_verifier_detects_missing_expected_report(self) -> None:
        from check_all import verify_pinned_artifacts

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_pin(root, "expected-corpus-gate.json", self.GATE_DIGEST)
            self._seal_manifest(root)
            pins = verify_pinned_artifacts(
                self.REPORT_DIGEST, self.GATE_DIGEST, root=root
            )
            self.assertFalse(pins["successful"])
            self.assertIn("missing expected-report.json", pins["errors"])
            self.assertIsNone(pins["report_pin"])

    def test_pin_verifier_detects_missing_expected_gate(self) -> None:
        from check_all import verify_pinned_artifacts

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_pin(root, "expected-report.json", self.REPORT_DIGEST)
            self._seal_manifest(root)
            pins = verify_pinned_artifacts(
                self.REPORT_DIGEST, self.GATE_DIGEST, root=root
            )
            self.assertFalse(pins["successful"])
            self.assertIn("missing expected-corpus-gate.json", pins["errors"])
            self.assertIsNone(pins["gate_pin"])

    def test_pin_verifier_detects_unsuccessful_pins(self) -> None:
        from check_all import verify_pinned_artifacts

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_pin(
                root, "expected-report.json", self.REPORT_DIGEST, successful=False
            )
            self._write_pin(
                root, "expected-corpus-gate.json", self.GATE_DIGEST, successful=False
            )
            self._seal_manifest(root)
            pins = verify_pinned_artifacts(
                self.REPORT_DIGEST, self.GATE_DIGEST, root=root
            )
            self.assertFalse(pins["successful"])
            self.assertIn("expected-report.json is not successful", pins["errors"])
            self.assertIn("expected-corpus-gate.json is not successful", pins["errors"])
            self.assertTrue(pins["manifest_ok"])

    def test_pin_verifier_detects_gate_pin_digest_mismatch(self) -> None:
        from check_all import verify_pinned_artifacts

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_pin(root, "expected-report.json", self.REPORT_DIGEST)
            self._write_pin(root, "expected-corpus-gate.json", "c" * 64)
            self._seal_manifest(root)
            pins = verify_pinned_artifacts(
                self.REPORT_DIGEST, self.GATE_DIGEST, root=root
            )
            self.assertFalse(pins["successful"])
            self.assertIn(
                "expected-corpus-gate.json report_sha256 mismatch", pins["errors"]
            )

    def test_pin_verifier_detects_stale_manifest(self) -> None:
        from check_all import verify_pinned_artifacts

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_pin(root, "expected-report.json", self.REPORT_DIGEST)
            self._write_pin(root, "expected-corpus-gate.json", self.GATE_DIGEST)
            self._seal_manifest(root)
            (root / "drifted.txt").write_text("late write", encoding="utf-8")
            with redirect_stderr(io.StringIO()):
                pins = verify_pinned_artifacts(
                    self.REPORT_DIGEST, self.GATE_DIGEST, root=root
                )
            self.assertFalse(pins["successful"])
            self.assertFalse(pins["manifest_ok"])
            self.assertIn(
                "MANIFEST.sha256 does not match current package bytes", pins["errors"]
            )

    def test_pin_verifier_detects_missing_bundle_pin(self) -> None:
        from check_all import verify_pinned_artifacts

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_pin(root, "expected-report.json", self.REPORT_DIGEST)
            self._write_pin(root, "expected-corpus-gate.json", self.GATE_DIGEST)
            self._seal_manifest(root, ensure_bundle=False)
            pins = verify_pinned_artifacts(
                self.REPORT_DIGEST, self.GATE_DIGEST, root=root
            )
            self.assertFalse(pins["successful"])
            self.assertIn("missing expected-bundle.json", pins["errors"])
            self.assertIsNone(pins["bundle_pin"])

    def test_pin_verifier_detects_bundle_digest_mismatch(self) -> None:
        from check_all import verify_pinned_artifacts

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_pin(root, "expected-report.json", self.REPORT_DIGEST)
            self._write_pin(root, "expected-corpus-gate.json", self.GATE_DIGEST)
            self._write_bundle_pin(
                root, self.REPORT_DIGEST, self.GATE_DIGEST, corrupt_digest=True
            )
            self._seal_manifest(root)
            pins = verify_pinned_artifacts(
                self.REPORT_DIGEST, self.GATE_DIGEST, root=root
            )
            self.assertFalse(pins["successful"])
            self.assertIn("expected-bundle.json bundle_sha256 mismatch", pins["errors"])

    def test_pin_verifier_detects_bundle_reference_drift(self) -> None:
        from check_all import verify_pinned_artifacts

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_pin(root, "expected-report.json", self.REPORT_DIGEST)
            self._write_pin(root, "expected-corpus-gate.json", self.GATE_DIGEST)
            self._write_bundle_pin(root, "d" * 64, self.GATE_DIGEST)
            self._seal_manifest(root)
            pins = verify_pinned_artifacts(
                self.REPORT_DIGEST, self.GATE_DIGEST, root=root
            )
            self.assertFalse(pins["successful"])
            self.assertIn(
                "expected-bundle.json reference_report sha256 mismatch", pins["errors"]
            )

    def test_pin_verifier_detects_bundle_manifest_flag(self) -> None:
        from check_all import verify_pinned_artifacts

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_pin(root, "expected-report.json", self.REPORT_DIGEST)
            self._write_pin(root, "expected-corpus-gate.json", self.GATE_DIGEST)
            self._write_bundle_pin(
                root, self.REPORT_DIGEST, self.GATE_DIGEST, manifest_ok=False
            )
            self._seal_manifest(root)
            pins = verify_pinned_artifacts(
                self.REPORT_DIGEST, self.GATE_DIGEST, root=root
            )
            self.assertFalse(pins["successful"])
            self.assertIn(
                "expected-bundle.json artifact_pins manifest_ok is not true",
                pins["errors"],
            )

    def test_stdlib_scan_bites_on_third_party_import(self) -> None:
        from check_all import scan_third_party_imports

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "clean.py").write_text(
                "import json\nfrom ncnc.core import History\n", encoding="utf-8"
            )
            self.assertEqual(scan_third_party_imports(root), ())
            (root / "dirty.py").write_text("import numpy\n", encoding="utf-8")
            self.assertEqual(scan_third_party_imports(root), ("dirty.py:numpy",))

    def test_expected_bundle_pin_is_successful_and_self_consistent(self) -> None:
        import check_all
        from corpus_gate import run_gate
        from ncnc.report import run_reference_verification

        bundle_path = check_all.ROOT / "expected-bundle.json"
        self.assertTrue(bundle_path.is_file())
        data = json.loads(bundle_path.read_text(encoding="utf-8"))
        recorded = data.pop("bundle_sha256")
        encoded = json.dumps(
            data, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        self.assertEqual(sha256(encoded).hexdigest(), recorded)

        # Fresh evidence: recompute the reference report and the corpus gate
        # instead of trusting the stored success literals.
        fresh_reference = run_reference_verification()
        fresh_gate = run_gate()
        self.assertIs(fresh_reference.successful, True)
        self.assertIs(fresh_gate.successful, True)
        self.assertEqual(data["reference_report"]["sha256"], fresh_reference.digest)
        self.assertIs(data["reference_report"]["successful"], True)
        self.assertEqual(data["corpus_gate"]["sha256"], fresh_gate.digest)
        self.assertIs(data["corpus_gate"]["successful"], True)

        with redirect_stderr(io.StringIO()):
            pins = check_all.verify_pinned_artifacts(
                fresh_reference.digest, fresh_gate.digest
            )
        self.assertTrue(pins["successful"])
        self.assertIs(data["artifact_pins"]["manifest_ok"], True)
        self.assertEqual(data["artifact_pins"]["errors"], [])

        # The tests block is the only non-recomputable part of the bundle
        # (recomputing it here would recurse). Require internal consistency:
        # the stored top-level flag must equal the AND of the four stored
        # block flags, so a bundle cannot claim success its blocks contradict.
        # A strict literal-True assertion on the tests block would make the
        # regeneration fixed point non-convergent.
        self.assertGreater(data["tests"]["run"], 0)
        self.assertIs(
            data["successful"],
            bool(
                data["tests"]["successful"]
                and data["reference_report"]["successful"]
                and data["corpus_gate"]["successful"]
                and data["artifact_pins"]["successful"]
            ),
        )


class OutputRefusalTests(unittest.TestCase):
    def test_in_tree_output_paths_are_refused(self) -> None:
        import check_all

        stray = check_all.ROOT / "tests" / "stray-bundle.json"
        self.assertIsNotNone(check_all.refuse_self_poisoning_output(stray))
        self.assertIsNotNone(
            check_all.refuse_self_poisoning_output(check_all.ROOT / "bundle.json")
        )

    def test_sanctioned_output_paths_are_allowed(self) -> None:
        import check_all

        self.assertIsNone(
            check_all.refuse_self_poisoning_output(
                check_all.ROOT / "expected-bundle.json"
            )
        )
        self.assertIsNone(
            check_all.refuse_self_poisoning_output(check_all.ROOT / "probe.ncnc-tmp")
        )
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNone(
                check_all.refuse_self_poisoning_output(Path(directory) / "bundle.json")
            )

    def test_cli_refuses_in_tree_output_before_writing(self) -> None:
        import check_all

        stray = check_all.ROOT / "tests" / "stray-bundle.json"
        with redirect_stderr(io.StringIO()) as stderr:
            exit_code = check_all.main(["--format", "json", "--output", str(stray)])
        self.assertEqual(exit_code, 2)
        self.assertFalse(stray.exists())
        self.assertIn("refusing --output", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
