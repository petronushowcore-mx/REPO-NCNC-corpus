from __future__ import annotations

import unittest

from corpus_gate import evaluate_surfaces, load_surfaces, run_gate


class CorpusGateTests(unittest.TestCase):
    def test_actual_pair_and_harness_satisfy_contract(self) -> None:
        report = run_gate()
        self.assertTrue(report.successful, [c for c in report.checks if not c.passed])

    def test_missing_assurance_context_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["formal"] = surfaces["formal"].replace(
            r"\mathsf{AssurCtx}_t", r"\mathsf{RemovedCtx}_t"
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "formal-object-contract")
        self.assertFalse(check.passed)

    def test_missing_runtime_regime_contract_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["core"] = surfaces["core"].replace(
            "runtime_regime: str", "removed_regime: str"
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "harness-certificate-contract")
        self.assertFalse(check.passed)

    def test_missing_manifest_entrypoint_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["readme"] = surfaces["readme"].replace(
            "`MANIFEST.sha256`", "`REMOVED-MANIFEST`"
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "readme-entrypoint-contract")
        self.assertFalse(check.passed)

    def test_missing_manifest_builder_contract_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["manifest_builder"] = surfaces["manifest_builder"].replace(
            "def manifest_entries(", "def removed_manifest_entries("
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "harness-manifest-contract")
        self.assertFalse(check.passed)

    def test_missing_authority_scoped_replay_contract_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["control"] = surfaces["control"].replace(
            "def consume_decision(", "def removed_consume_decision("
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "harness-enforcement-contract")
        self.assertFalse(check.passed)

    def test_missing_recurrence_contract_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["control"] = surfaces["control"].replace(
            "class HistoryFutureRecurrence:", "class RemovedRecurrence:"
        )
        report = evaluate_surfaces(surfaces)
        check = next(
            c for c in report.checks if c.check_id == "harness-recurrence-contract"
        )
        self.assertFalse(check.passed)

    def test_missing_recursive_k_sigma_contract_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["core"] = surfaces["core"].replace(
            "def seal_continuation_indicator(", "def removed_seal_indicator("
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "harness-k-sigma-contract")
        self.assertFalse(check.passed)

    def test_missing_generator_input_binding_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["control"] = surfaces["control"].replace(
            "recurrence next generator input commitment mismatch",
            "removed generator input mismatch",
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "harness-recurrence-contract")
        self.assertFalse(check.passed)

    def test_stale_empty_reservoir_language_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["map"] += "\nCode: not yet created\n"
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "stale-language-residue")
        self.assertFalse(check.passed)

    def test_missing_boundary_type_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["core"] = surfaces["core"].replace(
            "class ConstitutiveBoundary:", "class RemovedBoundary:"
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "harness-boundary-contract")
        self.assertFalse(check.passed)

    def test_missing_boundary_compilation_path_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["core"] = surfaces["core"].replace(
            "return self.declaration.boundary.compile()",
            "return removed_independent_admissibility",
        )
        report = evaluate_surfaces(surfaces)
        check = next(
            c for c in report.checks if c.check_id == "harness-boundary-contract"
        )
        self.assertFalse(check.passed)

    def test_incomplete_prefix_family_derivation_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["core"] = surfaces["core"].replace(
            "tail.prefix(length) for length in range(1, snapshot.remaining + 1)",
            "tail.prefix(length) for length in range(1, snapshot.remaining)",
        )
        report = evaluate_surfaces(surfaces)
        check = next(
            c for c in report.checks if c.check_id == "harness-geometry-contract"
        )
        self.assertFalse(check.passed)

    def test_missing_action_substitution_mutation_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["report"] = surfaces["report"].replace(
            "F17-action-substitution",
            "removed-action-substitution",
        )
        report = evaluate_surfaces(surfaces)
        check = next(
            c for c in report.checks if c.check_id == "harness-report-contract"
        )
        self.assertFalse(check.passed)
    def test_missing_boundary_fibre_report_check_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["report"] = surfaces["report"].replace(
            "P4.1a-T14-boundary-fibre", "removed-boundary-fibre-check"
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "harness-report-contract")
        self.assertFalse(check.passed)

    def test_five_link_drift_fence_is_load_bearing_on_every_surface(self) -> None:
        formal_compile = "\n".join(
            (
                r"B_{u,t}^{v_B}",
                r"&\xrightarrow{\ \mathsf{compile}\ }",
                r"A_{u,t,0:H},\\",
            )
        )
        cases = (
            (
                "formal",
                formal_compile,
                formal_compile.replace(r"\mathsf{compile}", r"\mathsf{removed}"),
            ),
            (
                "bridge",
                "Boundary → executable admissibility → admitted tails → exact "
                "prefix–fibre geometry → existential support.",
                "Boundary → executable admissibility → admitted tails → existential support.",
            ),
            (
                "map",
                r"| `B → A` | `\mathsf{compile}(B)` |",
                r"| `B → A` | `\mathsf{removed}(B)` |",
            ),
            (
                "readme",
                r"`\mathcal G(\mathcal R)\xrightarrow{\mathsf{First}}\Pi^{\exists}`",
                r"`\mathcal G(\mathcal R)\xrightarrow{\mathsf{First}}\Pi`",
            ),
            (
                "verification_map",
                r"| `\mathcal R → \mathcal G(\mathcal R)` | `PrefixFibreGeometry`, "
                r"`geometry_from_snapshot`, `assert_geometry` |",
                r"| `\mathcal R → \mathcal G(\mathcal R)` | removed geometry |",
            ),
            (
                "report",
                "an authorised B revision creates a different admissible region, "
                "which changes R, G(R) and existential support before execution",
                "an authorised B revision changes existential support before execution",
            ),
        )
        for surface, anchor, broken in cases:
            with self.subTest(surface=surface, anchor=anchor):
                surfaces = load_surfaces()
                self.assertIn(anchor, surfaces[surface])
                surfaces[surface] = surfaces[surface].replace(anchor, broken, 1)
                report = evaluate_surfaces(surfaces)
                check = next(
                    c
                    for c in report.checks
                    if c.check_id == "five-link-architecture-contract"
                )
                self.assertFalse(check.passed)

    def test_control_character_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["readme"] += "\x0b"
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "public-control-characters")
        self.assertFalse(check.passed)

    def test_missing_recompute_guard_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["control"] = surfaces["control"].replace(
            "def recompute_context(", "def removed_recompute_context("
        )
        report = evaluate_surfaces(surfaces)
        check = next(
            c for c in report.checks if c.check_id == "harness-enforcement-contract"
        )
        self.assertFalse(check.passed)

    def test_missing_clause_binding_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["core"] = surfaces["core"].replace(
            "rule record does not commit to its executable clause",
            "rule record accepted without commitment",
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "harness-clause-contract")
        self.assertFalse(check.passed)

    def test_missing_dynamics_guard_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["core"] = surfaces["core"].replace(
            "orphan successor row for undeclared triple",
            "orphan successor row silently ignored",
        )
        report = evaluate_surfaces(surfaces)
        check = next(
            c for c in report.checks if c.check_id == "harness-dynamics-contract"
        )
        self.assertFalse(check.passed)

    def test_missing_stdlib_scan_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["bundle_builder"] = surfaces["bundle_builder"].replace(
            "def scan_third_party_imports(", "def removed_import_scan("
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "harness-bundle-contract")
        self.assertFalse(check.passed)

    def test_missing_ledger_fixture_is_detected(self) -> None:
        surfaces = load_surfaces()
        surfaces["scenarios"] = surfaces["scenarios"].replace(
            "ledger=_wear_ledger(", "ledger=_removed_ledger("
        )
        report = evaluate_surfaces(surfaces)
        check = next(
            c for c in report.checks if c.check_id == "harness-ledger-scenario-contract"
        )
        self.assertFalse(check.passed)

    def test_topology_inflation_fence_is_load_bearing(self) -> None:
        surfaces = load_surfaces()
        surfaces["formal"] = surfaces["formal"].replace(
            "They need not occupy four physical services",
            "They occupy four physical services",
        )
        report = evaluate_surfaces(surfaces)
        check = next(c for c in report.checks if c.check_id == "scope-no-topology-inflation")
        self.assertFalse(check.passed)


if __name__ == "__main__":
    unittest.main()
