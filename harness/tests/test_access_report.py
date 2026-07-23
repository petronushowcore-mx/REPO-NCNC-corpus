from __future__ import annotations

import json
import unittest

from ncnc.access import (
    BoundaryHypothesis,
    ChannelCase,
    GreedyVersionSpaceAttack,
    LeakagePolicy,
    MembershipOracle,
    QueryBudgetExceeded,
    exact_factorisation_map,
    find_fibre_collisions,
)
from ncnc.report import render_json, render_text, run_reference_verification
from ncnc.scenarios import boundary_hypotheses, non_absorption_cases


class AccessTests(unittest.TestCase):
    def test_target_changing_fibre_blocks_exact_factorisation(self) -> None:
        cases = non_absorption_cases()
        collisions = find_fibre_collisions(cases)
        self.assertEqual(len(collisions), 1)
        self.assertEqual(collisions[0].left_case, "boundary-left")
        self.assertEqual(collisions[0].right_case, "boundary-right")
        self.assertIsNone(exact_factorisation_map(cases))

    def test_no_collision_allows_finite_factorisation_map(self) -> None:
        cases = (
            ChannelCase("a", {"visible": 1}, {"target": "x"}),
            ChannelCase("b", {"visible": 2}, {"target": "y"}),
        )
        mapping = exact_factorisation_map(cases)
        self.assertIsNotNone(mapping)
        self.assertEqual(len(mapping), 2)

    def test_refining_the_channel_changes_its_identity(self) -> None:
        coarse = non_absorption_cases()
        refined = tuple(
            ChannelCase(
                case.case_id,
                {
                    **case.optimizer_observation,
                    "imported_target": case.privileged_target,
                },
                case.privileged_target,
            )
            for case in coarse
        )
        self.assertTrue(find_fibre_collisions(coarse))
        self.assertFalse(find_fibre_collisions(refined))
        self.assertNotEqual(
            coarse[0].optimizer_observation, refined[0].optimizer_observation
        )

    def test_boundary_rejects_admitted_point_outside_domain(self) -> None:
        with self.assertRaises(ValueError):
            BoundaryHypothesis("bad", ("p0",), frozenset(("p1",)))

    def test_boundary_rejects_duplicate_domain_points(self) -> None:
        with self.assertRaises(ValueError):
            BoundaryHypothesis("bad", ("p0", "p0"), frozenset(("p0",)))

    def test_attack_rejects_same_name_forged_actual_boundary(self) -> None:
        declared = BoundaryHypothesis("B", ("p0",), frozenset())
        forged = BoundaryHypothesis("B", ("p0",), frozenset(("p0",)))
        with self.assertRaises(ValueError):
            GreedyVersionSpaceAttack().run((declared,), MembershipOracle(forged, 0))

    def test_attack_rejects_duplicate_hypothesis_names(self) -> None:
        left = BoundaryHypothesis("B", ("p0",), frozenset())
        right = BoundaryHypothesis("B", ("p0",), frozenset(("p0",)))
        with self.assertRaises(ValueError):
            GreedyVersionSpaceAttack().run((left, right), MembershipOracle(left, 0))

    def test_attack_rejects_mixed_domains_before_any_query(self) -> None:
        left = BoundaryHypothesis("L", ("p0",), frozenset())
        right = BoundaryHypothesis("R", ("p1",), frozenset())
        with self.assertRaises(ValueError):
            GreedyVersionSpaceAttack().run((left, right), MembershipOracle(left, 0))

    def test_leakage_policy_rejects_invalid_bounds(self) -> None:
        with self.assertRaises(ValueError):
            LeakagePolicy(-1, 0.0)
        with self.assertRaises(ValueError):
            LeakagePolicy(0, float("nan"))

    def test_two_queries_leave_four_hypotheses(self) -> None:
        hypotheses = boundary_hypotheses()
        actual = next(item for item in hypotheses if item.name == "B05")
        result = GreedyVersionSpaceAttack().run(
            hypotheses, MembershipOracle(actual, 2)
        )
        self.assertFalse(result.exact_reconstruction)
        self.assertTrue(result.budget_exhausted)
        self.assertEqual(len(result.remaining_hypotheses), 4)
        self.assertEqual(result.leakage_bits, 2.0)

    def test_four_queries_reconstruct_four_bit_boundary(self) -> None:
        hypotheses = boundary_hypotheses()
        actual = next(item for item in hypotheses if item.name == "B05")
        result = GreedyVersionSpaceAttack().run(
            hypotheses, MembershipOracle(actual, 4)
        )
        self.assertTrue(result.exact_reconstruction)
        self.assertEqual(result.remaining_hypotheses, ("B05",))
        self.assertEqual(result.leakage_bits, 4.0)

    def test_query_q_plus_one_is_rejected(self) -> None:
        actual = boundary_hypotheses()[0]
        oracle = MembershipOracle(actual, 1)
        oracle.query("p0")
        with self.assertRaises(QueryBudgetExceeded):
            oracle.query("p1")

    def test_repeated_query_consumes_budget(self) -> None:
        actual = boundary_hypotheses()[0]
        oracle = MembershipOracle(actual, 2)
        oracle.query("p0")
        oracle.query("p0")
        self.assertEqual(oracle.remaining, 0)
        self.assertEqual(len(oracle.events), 2)

    def test_leakage_policy_rejects_exact_reconstruction(self) -> None:
        hypotheses = boundary_hypotheses()
        actual = next(item for item in hypotheses if item.name == "B05")
        bounded = GreedyVersionSpaceAttack().run(
            hypotheses, MembershipOracle(actual, 2)
        )
        exact = GreedyVersionSpaceAttack().run(
            hypotheses, MembershipOracle(actual, 4)
        )
        policy = LeakagePolicy(2, 2.0)
        self.assertTrue(policy.accepts(bounded))
        self.assertFalse(policy.accepts(exact))

    def test_attack_is_deterministic(self) -> None:
        hypotheses = boundary_hypotheses()
        actual = next(item for item in hypotheses if item.name == "B09")
        first = GreedyVersionSpaceAttack().run(
            hypotheses, MembershipOracle(actual, 3)
        )
        second = GreedyVersionSpaceAttack().run(
            hypotheses, MembershipOracle(actual, 3)
        )
        self.assertEqual(first, second)


class ReportTests(unittest.TestCase):
    def test_reference_report_has_no_mutation_survivors(self) -> None:
        report = run_reference_verification()
        self.assertTrue(report.successful)
        self.assertEqual(report.mutation_survivors, ())
        self.assertGreaterEqual(len(report.mutations), 15)

    def test_report_digest_is_repeatable(self) -> None:
        first = run_reference_verification()
        second = run_reference_verification()
        self.assertEqual(first.digest, second.digest)
        self.assertEqual(render_text(first), render_text(second))

    def test_json_report_is_valid_and_contains_its_digest(self) -> None:
        report = run_reference_verification()
        parsed = json.loads(render_json(report))
        self.assertTrue(parsed["successful"])
        self.assertEqual(parsed["report_sha256"], report.digest)
        self.assertEqual(parsed["mutation_survivors"], [])

    def test_machine_limits_are_not_reported_as_passes(self) -> None:
        report = run_reference_verification()
        scoped = {item.check_id: item.status.value for item in report.checks}
        self.assertEqual(
            scoped["scope-personal-identity"], "NOT_MACHINE_DECIDABLE"
        )
        self.assertEqual(
            scoped["scope-host-nonbypassability"], "NOT_MACHINE_DECIDABLE"
        )


if __name__ == "__main__":
    unittest.main()
