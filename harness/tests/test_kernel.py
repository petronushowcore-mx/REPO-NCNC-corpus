from __future__ import annotations

from dataclasses import replace
import unittest
from ncnc.core import (
    AssuranceMode,
    CertificateIntegrityError,
    commitment,
    History,
    HorizonError,
    MinervaOperator,
    ReservoirEngine,
    SealIntegrityError,
    SpecificationError,
    Step,
    Tail,
)
from ncnc.scenarios import (
    _interpreter,
    _observation,
    boundary_intervention_specs,
    empty_active_support_scenario,
    empty_reservoir_scenario,
    robust_branching_scenario,
    seal_recursive_gap_scenario,
    seal_recomputation_divergence_scenario,
)


class KernelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ReservoirEngine()
        self.minerva = MinervaOperator(self.engine)
        self.scenario = robust_branching_scenario()

    def test_gamma_h0_is_single_empty_tail(self) -> None:
        history = self.scenario.history.append("b", "robust1").append(
            "continue", "terminal"
        )
        self.assertEqual(
            self.engine.reachable_tails(self.scenario.spec, history, 2, 0),
            (Tail.empty(),),
        )

    def test_negative_horizon_is_rejected(self) -> None:
        with self.assertRaises(HorizonError):
            self.engine.reachable_tails(
                self.scenario.spec, self.scenario.history, 0, -1
            )

    def test_reversed_validity_envelope_is_rejected(self) -> None:
        with self.assertRaises(SpecificationError):
            replace(self.scenario.spec.validity, not_before=2, not_after=1)

    def test_boundary_rejects_source_reference_mismatch(self) -> None:
        boundary = self.scenario.spec.declaration.boundary
        with self.assertRaises(SpecificationError):
            replace(boundary.sources[0], source_id="forged-source")

    def test_boundary_compilation_record_tracks_sources(self) -> None:
        boundary = self.scenario.spec.declaration.boundary
        compiled = boundary.compile().record
        self.assertEqual(compiled.version, boundary.version)
        self.assertEqual(
            compiled.ground_refs,
            tuple(source.source_id for source in boundary.sources),
        )
        source = boundary.sources[0]
        changed_source = replace(
            source,
            clause=replace(
                source.clause,
                default_allow=not source.clause.default_allow,
            ),
        )
        changed_boundary = replace(
            boundary,
            sources=(changed_source,) + boundary.sources[1:],
        )
        self.assertNotEqual(
            compiled.implementation_digest,
            changed_boundary.compile().record.implementation_digest,
        )

    def test_declaration_rejects_boundary_version_mismatch(self) -> None:
        declaration = self.scenario.spec.declaration
        with self.assertRaises(SpecificationError):
            replace(
                declaration,
                boundary=replace(
                    declaration.boundary,
                    version="forged-version",
                ),
            )

    def test_boundary_revision_recompiles_admissibility(self) -> None:
        left, right = boundary_intervention_specs()
        revised = replace(left.spec, declaration=right.spec.declaration)
        left_tail = Tail((Step("L", "terminal"),))
        right_tail = Tail((Step("R", "terminal"),))
        self.assertNotIn("admissibility", type(left.spec).__dataclass_fields__)
        self.assertEqual(
            (
                left.spec.admissibility(0, 1, left.history, left_tail),
                left.spec.admissibility(0, 1, left.history, right_tail),
                revised.admissibility(0, 1, left.history, left_tail),
                revised.admissibility(0, 1, left.history, right_tail),
            ),
            (True, False, False, True),
        )
    def test_boundary_intervention_swaps_whole_action_fibre(self) -> None:
        left, right = boundary_intervention_specs()
        left_reachable = self.engine.reachable_tails(left.spec, left.history, 0, 1)
        right_reachable = self.engine.reachable_tails(right.spec, right.history, 0, 1)
        left_reservoir = self.engine.reservoir(left.spec, left.history, 0, 1)
        right_reservoir = self.engine.reservoir(right.spec, right.history, 0, 1)
        self.assertEqual(left_reachable, right_reachable)
        self.assertEqual(
            {tail.first_action for tail in left_reservoir.tails}, {"L"}
        )
        self.assertEqual(
            {tail.first_action for tail in right_reservoir.tails}, {"R"}
        )
        self.assertEqual(len(left_reservoir.tails), len(right_reservoir.tails))
        self.assertEqual(len(left_reservoir.tails), 1)

    def test_runtime_regime_mismatch_blocks_assurance_construction(self) -> None:
        with self.assertRaises(SpecificationError):
            self.engine.assurance_context(
                AssuranceMode.ADAPTIVE_ROBUST,
                self.scenario.spec,
                self.scenario.history,
                0,
                2,
                runtime_regime="changed-regime",
            )

    def test_assurance_modes_bind_exact_geometry_commitment(self) -> None:
        output = self.minerva.generate(
            self.scenario.observation, self.scenario.spec
        )
        geometry = self.engine.geometry_from_snapshot(output.reservoir)
        existential = self.engine.assurance_context(
            AssuranceMode.EXISTENTIAL,
            self.scenario.spec,
            self.scenario.history,
            0,
            2,
            runtime_regime="fixture",
        )
        adaptive = self.engine.assurance_context(
            AssuranceMode.ADAPTIVE_ROBUST,
            self.scenario.spec,
            self.scenario.history,
            0,
            2,
            runtime_regime="fixture",
        )
        seal_relative = self.engine.assurance_context(
            AssuranceMode.SEAL_RELATIVE,
            self.scenario.spec,
            self.scenario.history,
            0,
            2,
            runtime_regime="fixture",
            seal=output.seal,
            prefix=Tail.empty(),
        )
        self.assertEqual(existential.geometry_commitment, geometry.digest)
        self.assertEqual(adaptive.current_geometry_commitment, geometry.digest)
        self.assertEqual(seal_relative.origin_geometry_commitment, geometry.digest)

    def test_interpreter_uses_frozen_declared_lookup(self) -> None:
        histories = {"root": History("original")}
        interpreter = _interpreter(histories, name="frozen-lookup")
        observation = _observation("frozen-lookup", 0, "root")
        before = interpreter.interpret(observation)
        histories["root"] = History("forged")
        after = interpreter.interpret(observation)
        self.assertEqual(before, after)
        self.assertEqual(after.current_state, "original")

    def test_every_reachable_tail_has_exact_h_pairs(self) -> None:
        tails = self.engine.reachable_tails(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        self.assertTrue(tails)
        self.assertEqual({len(tail.steps) for tail in tails}, {2})

    def test_joint_verdict_is_boolean_conjunction(self) -> None:
        tails = self.engine.reachable_tails(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        bad = next(tail for tail in tails if tail.steps[0].next_state == "bad1")
        verdict = self.engine.joint_verdict(
            self.scenario.spec, self.scenario.history, 0, 2, bad
        )
        self.assertTrue(verdict.identity)
        self.assertTrue(verdict.admissibility)
        self.assertIn(False, verdict.viability)
        self.assertFalse(verdict.admitted)

    def test_joint_verdict_h0_has_empty_viability_product(self) -> None:
        history = self.scenario.history.append("b", "robust1").append(
            "continue", "terminal"
        )
        verdict = self.engine.joint_verdict(
            self.scenario.spec, history, 2, 0, Tail.empty()
        )
        self.assertEqual(verdict.viability, ())
        self.assertTrue(verdict.admitted)

    def test_reservoir_is_reachable_joint_verdict_filter(self) -> None:
        reachable = self.engine.reachable_tails(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        expected = tuple(
            tail
            for tail in reachable
            if self.engine.joint_verdict(
                self.scenario.spec, self.scenario.history, 0, 2, tail
            ).admitted
        )
        reservoir = self.engine.reservoir(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        self.assertEqual(reservoir.tails, expected)

    def test_each_reservoir_member_has_replayable_witness_metadata(self) -> None:
        reservoir = self.engine.reservoir(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        self.assertEqual(len(reservoir.tails), len(reservoir.certificates))
        for tail, certificate in zip(reservoir.tails, reservoir.certificates):
            self.assertEqual(certificate.tail, tail)
            self.assertTrue(certificate.reachability_witnesses)
            self.assertTrue(
                all(len(path) == 2 for path in certificate.reachability_witnesses)
            )
            self.assertTrue(certificate.verdict.admitted)
            self.assertEqual(certificate.spec_commitment, self.scenario.spec.digest)

    def test_snapshot_and_all_certificates_recompute_cleanly(self) -> None:
        reservoir = self.engine.reservoir(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        audit = self.engine.assert_snapshot(self.scenario.spec, reservoir)
        self.assertTrue(audit.valid)
        self.assertTrue(all(item.valid for item in audit.certificate_audits))

    def test_snapshot_audit_reports_invalid_suffix_without_escaping(self) -> None:
        reservoir = self.engine.reservoir(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        malformed = replace(reservoir, remaining=-1)
        audit = self.engine.audit_snapshot(self.scenario.spec, malformed)
        self.assertFalse(audit.valid)
        self.assertFalse(audit.suffix_binding)
        certificate_audit = self.engine.audit_certificate(
            self.scenario.spec,
            self.scenario.history,
            0,
            -1,
            reservoir.certificates[0],
        )
        self.assertFalse(certificate_audit.valid)

    def test_certificate_recomputation_rejects_forged_grounding(self) -> None:
        reservoir = self.engine.reservoir(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        forged = replace(reservoir.certificates[0], ground_refs=("forged",))
        mutated = replace(
            reservoir,
            certificates=(forged,) + reservoir.certificates[1:],
        )
        audit = self.engine.audit_snapshot(self.scenario.spec, mutated)
        self.assertFalse(audit.valid)
        self.assertFalse(audit.certificate_audits[0].ground_binding)
        with self.assertRaises(CertificateIntegrityError):
            self.engine.assert_snapshot(self.scenario.spec, mutated)

    def test_snapshot_recomputation_rejects_complete_paired_omission(self) -> None:
        reservoir = self.engine.reservoir(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        mutated = replace(
            reservoir,
            tails=reservoir.tails[:-1],
            certificates=reservoir.certificates[:-1],
        )
        audit = self.engine.audit_snapshot(self.scenario.spec, mutated)
        self.assertTrue(audit.pairing_exact)
        self.assertFalse(audit.admitted_tail_set_exact)

    def test_geometry_is_exact_prefix_family_of_reservoir(self) -> None:
        reservoir = self.engine.reservoir(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        geometry = self.engine.geometry_from_snapshot(reservoir)
        prefixes = {Tail.empty()}
        for tail in reservoir.tails:
            prefixes.update(
                tail.prefix(length) for length in range(1, reservoir.remaining + 1)
            )
        expected = tuple(
            (
                prefix,
                tuple(
                    tail
                    for tail in reservoir.tails
                    if tail.steps[: len(prefix.steps)] == prefix.steps
                ),
            )
            for prefix in sorted(prefixes)
        )
        self.assertEqual(geometry.reservoir_commitment, reservoir.digest)
        self.assertEqual(
            tuple((item.prefix, item.tails) for item in geometry.fibres),
            expected,
        )

    def test_geometry_rejects_missing_prefix_fibre(self) -> None:
        geometry = self.engine.geometry(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        with self.assertRaises(SpecificationError):
            replace(geometry, fibres=geometry.fibres[:-1])

    def test_projection_is_exact_first_coordinate_image(self) -> None:
        reservoir = self.engine.reservoir(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        geometry = self.engine.geometry_from_snapshot(reservoir)
        support = self.engine.existential_support(geometry)
        projected = tuple(
            sorted(
                {
                    item.prefix.first_action
                    for item in geometry.fibres
                    if len(item.prefix.steps) == 1 and item.tails
                }
            )
        )
        self.assertEqual(support, projected)
    def test_present_support_is_undefined_at_h0(self) -> None:
        history = self.scenario.history.append("b", "robust1").append(
            "continue", "terminal"
        )
        geometry = self.engine.geometry(self.scenario.spec, history, 2, 0)
        with self.assertRaises(HorizonError):
            self.engine.existential_support(geometry)
        with self.assertRaises(HorizonError):
            self.engine.adaptive_support(self.scenario.spec, history, 2, 0)

    def test_adaptive_support_excludes_existential_only_action(self) -> None:
        geometry = self.engine.geometry(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        existential = self.engine.existential_support(geometry)
        adaptive = self.engine.adaptive_support(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        self.assertEqual(existential, ("a", "b"))
        self.assertEqual(adaptive.actions, ("b",))

    def test_current_fibre_and_recursive_k_are_both_recorded(self) -> None:
        adaptive = self.engine.adaptive_support(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        evidence = adaptive.evidence_for("b")
        self.assertIsNotNone(evidence)
        self.assertEqual(len(evidence.branches), 2)
        for branch in evidence.branches:
            self.assertTrue(branch.current_fibre)
            self.assertTrue(branch.recursive_continuation)
            self.assertIsNotNone(branch.child_support_digest)

    def test_k0_equals_terminal_reservoir_nonemptiness(self) -> None:
        good = self.scenario.history.append("b", "robust1").append(
            "continue", "terminal"
        )
        self.assertEqual(
            self.engine.continuation_indicator(self.scenario.spec, good, 2, 0),
            bool(self.engine.reservoir(self.scenario.spec, good, 2, 0).tails),
        )

    def test_adaptive_one_step_closure_holds_for_every_declared_branch(self) -> None:
        adaptive = self.engine.adaptive_support(
            self.scenario.spec, self.scenario.history, 0, 2
        )
        evidence = adaptive.evidence_for("b")
        self.assertTrue(evidence.valid)
        declared = {
            (w, x)
            for w in self.scenario.spec.dynamics.disturbances(
                self.scenario.history, "b", 0
            )
            for x in self.scenario.spec.dynamics.successors(
                self.scenario.history, "b", w, 0
            )
        }
        visited = {(branch.disturbance, branch.successor) for branch in evidence.branches}
        self.assertEqual(visited, declared)

    def test_seal_relative_support_recomputes_sealed_snapshot(self) -> None:
        output = self.minerva.generate(self.scenario.observation, self.scenario.spec)
        seal = output.seal
        truncated_snapshot = replace(
            seal.snapshot,
            tails=seal.snapshot.tails[:-1],
            certificates=seal.snapshot.certificates[:-1],
        )
        forged = replace(
            seal,
            snapshot=truncated_snapshot,
            reservoir_commitment=truncated_snapshot.digest,
        )
        forged = replace(
            forged,
            seal_commitment=commitment(
                {
                    "origin_time": forged.origin_time,
                    "horizon": forged.horizon,
                    "root_history": forged.root_history,
                    "observation_commitment": forged.observation_commitment,
                    "interpreter_commitment": forged.interpreter_commitment,
                    "history_attribution": forged.history_attribution,
                    "reservoir_commitment": forged.reservoir_commitment,
                    "spec_commitment": forged.spec_commitment,
                    "provenance": forged.provenance,
                    "scheme": forged.scheme,
                }
            ),
        )
        forged.verify()
        with self.assertRaisesRegex(
            CertificateIntegrityError,
            "complete admitted tail-set",
        ):
            self.engine.seal_relative_support(forged, Tail.empty())
    def test_seal_relative_prefix_preservation(self) -> None:
        output = self.minerva.generate(self.scenario.observation, self.scenario.spec)
        root_support = self.engine.seal_relative_support(output.seal, Tail.empty())
        self.assertEqual(root_support.actions, ("b",))
        prefix = Tail((Step("b", "robust1"),))
        next_support = self.engine.seal_relative_support(output.seal, prefix)
        self.assertEqual(next_support.actions, ("continue",))
        final_prefix = prefix.append("continue", "terminal")
        self.assertTrue(self.engine.geometry_from_snapshot(output.seal.snapshot).fibre(final_prefix))

    def test_seal_relative_k_sigma_blocks_shallow_fibre_only_action(self) -> None:
        fixture = seal_recursive_gap_scenario()
        output = self.minerva.generate(fixture.observation, fixture.spec)
        support = self.engine.seal_relative_support(output.seal, Tail.empty())
        evidence = support.evidence_for("enter")
        self.assertIsNotNone(evidence)
        self.assertTrue(evidence.branches[0].conditional_fibre)
        self.assertFalse(evidence.branches[0].recursive_continuation)
        self.assertIsNotNone(evidence.branches[0].child_support_digest)
        self.assertEqual(support.actions, ())
        self.assertFalse(
            self.engine.seal_continuation_indicator(output.seal, Tail.empty())
        )

    def test_seal_relative_assurance_stops_after_validity_expiry(self) -> None:
        short_spec = replace(
            self.scenario.spec,
            validity=replace(self.scenario.spec.validity, not_after=0),
        )
        output = self.minerva.generate(self.scenario.observation, short_spec)
        prefix = Tail((Step("b", "robust1"),))
        history = self.scenario.history.extend(prefix)
        with self.assertRaises(SpecificationError):
            self.engine.assurance_context(
                AssuranceMode.SEAL_RELATIVE,
                short_spec,
                history,
                1,
                1,
                runtime_regime="fixture",
                seal=output.seal,
                prefix=prefix,
            )

    def test_seal_support_has_no_action_at_terminal_index(self) -> None:
        output = self.minerva.generate(self.scenario.observation, self.scenario.spec)
        terminal_prefix = Tail(
            (Step("b", "robust1"), Step("continue", "terminal"))
        )
        with self.assertRaises(HorizonError):
            self.engine.seal_relative_support(output.seal, terminal_prefix)

    def test_recomputed_and_original_seal_supports_can_diverge(self) -> None:
        fixture = seal_recomputation_divergence_scenario()
        output = self.minerva.generate(
            fixture.scenario.observation, fixture.scenario.spec
        )
        history = fixture.scenario.history.extend(fixture.realised_prefix)
        adaptive = self.engine.adaptive_support(fixture.scenario.spec, history, 1, 1)
        sealed = self.engine.seal_relative_support(output.seal, fixture.realised_prefix)
        self.assertEqual(adaptive.actions, fixture.expected_adaptive)
        self.assertEqual(sealed.actions, fixture.expected_seal_relative)
        self.assertNotEqual(adaptive.actions, sealed.actions)

    def test_later_theta_cannot_replace_origin_seal(self) -> None:
        fixture = seal_recomputation_divergence_scenario()
        output = self.minerva.generate(
            fixture.scenario.observation, fixture.scenario.spec
        )
        revised = replace(fixture.scenario.spec, model_version="2")
        history = fixture.scenario.history.extend(fixture.realised_prefix)
        with self.assertRaises(SealIntegrityError):
            self.engine.assurance_context(
                AssuranceMode.SEAL_RELATIVE,
                revised,
                history,
                1,
                1,
                seal=output.seal,
                prefix=fixture.realised_prefix,
                runtime_regime="fixture",
            )

    def test_nonempty_reservoir_can_have_empty_active_support(self) -> None:
        fixture = empty_active_support_scenario()
        output = self.minerva.generate(fixture.observation, fixture.spec)
        adaptive = self.engine.adaptive_support(fixture.spec, fixture.history, 0, 1)
        sealed = self.engine.seal_relative_support(output.seal, Tail.empty())
        self.assertTrue(output.reservoir.tails)
        self.assertEqual(adaptive.actions, ())
        self.assertEqual(sealed.actions, ())

    def test_empty_reservoir_forces_empty_active_support(self) -> None:
        fixture = empty_reservoir_scenario()
        output = self.minerva.generate(fixture.observation, fixture.spec)
        geometry = self.engine.geometry_from_snapshot(output.reservoir)
        existential = self.engine.existential_support(geometry)
        adaptive = self.engine.adaptive_support(fixture.spec, fixture.history, 0, 1)
        self.assertEqual(output.reservoir.tails, ())
        self.assertEqual(existential, ())
        self.assertEqual(adaptive.actions, ())

    def test_seal_verify_rejects_history_snapshot_disagreement(self) -> None:
        from ncnc.core import commitment

        output = self.minerva.generate(self.scenario.observation, self.scenario.spec)
        seal = output.seal
        forged_history = History("forged-root")
        payload = {
            "origin_time": seal.origin_time,
            "horizon": seal.horizon,
            "root_history": forged_history,
            "observation_commitment": seal.observation_commitment,
            "interpreter_commitment": seal.interpreter_commitment,
            "history_attribution": seal.history_attribution,
            "reservoir_commitment": seal.reservoir_commitment,
            "spec_commitment": seal.spec_commitment,
            "provenance": seal.provenance,
            "scheme": seal.scheme,
        }
        mutated = replace(
            seal,
            root_history=forged_history,
            seal_commitment=commitment(payload),
        )
        with self.assertRaises(SealIntegrityError):
            mutated.verify()


if __name__ == "__main__":
    unittest.main()
