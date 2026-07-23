from __future__ import annotations

from dataclasses import replace
import unittest

from ncnc.control import (
    EmptyDisposition,
    EmptySupportPolicy,
    EnforcementVerdict,
    Enforcer,
    TokenAuthority,
    TokenError,
)
from ncnc.core import (
    AssuranceMode,
    FiniteDynamics,
    MinervaOperator,
    ReservoirEngine,
    SealIntegrityError,
    Step,
    Tail,
)
from ncnc.scenarios import (
    _make_spec,
    _observation,
    _viability_clause,
    _viability_rule,
    empty_active_support_scenario,
    seal_recursive_gap_scenario,
    robust_branching_scenario,
)
from ncnc.core import History


class MutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ReservoirEngine()
        self.minerva = MinervaOperator(self.engine)
        self.scenario = robust_branching_scenario()
        self.output = self.minerva.generate(
            self.scenario.observation, self.scenario.spec
        )
        self.context = self.engine.assurance_context(
            AssuranceMode.ADAPTIVE_ROBUST,
            self.scenario.spec,
            self.scenario.history,
            0,
            2,
            runtime_regime="fixture",
        )
        self.authority = TokenAuthority(
            "mutation-enforcer",
            b"mutation-test-secret-material-32bytes!",
            engine=self.engine,
        )
        self.policy = EmptySupportPolicy(
            "empty-safe",
            "1",
            "safety-authority",
            EmptyDisposition.SAFE_MODE,
            "mutation fixture",
        )

    def enforcer(self) -> Enforcer:
        return Enforcer(self.authority, self.policy, decision_version="G_enf-v1")

    def token(self):
        return self.authority.issue(
            self.context,
            "b",
            issued_at=0,
            expires_at=2,
            decision_version="G_enf-v1",
        )

    def assert_rejected_token(self, token) -> None:
        decision = self.enforcer().decide(self.context, "b", token, now=0, runtime_regime="fixture")
        self.assertEqual(decision.verdict, EnforcementVerdict.REJECT)

    def test_every_seal_payload_field_is_commitment_bound(self) -> None:
        seal = self.output.seal
        mutations = (
            replace(seal, origin_time=1),
            replace(seal, horizon=1),
            replace(seal, root_history=seal.root_history.append("x", "y")),
            replace(seal, observation_commitment="00" * 32),
            replace(seal, interpreter_commitment="00" * 32),
            replace(seal, history_attribution="00" * 32),
            replace(seal, reservoir_commitment="00" * 32),
            replace(seal, spec_commitment="00" * 32),
            replace(seal, provenance=("forged",)),
            replace(seal, scheme="other"),
        )
        for mutation in mutations:
            with self.subTest(field=mutation):
                with self.assertRaises(SealIntegrityError):
                    mutation.verify()

    def test_seal_structural_bindings_reject_recommitment_forgery(self) -> None:
        """Commitment recompute alone must not launder inconsistent seal fields."""

        from ncnc.core import commitment

        seal = self.output.seal

        def rebind(mutated):
            payload = {
                "origin_time": mutated.origin_time,
                "horizon": mutated.horizon,
                "root_history": mutated.root_history,
                "observation_commitment": mutated.observation_commitment,
                "interpreter_commitment": mutated.interpreter_commitment,
                "history_attribution": mutated.history_attribution,
                "reservoir_commitment": mutated.reservoir_commitment,
                "spec_commitment": mutated.spec_commitment,
                "provenance": mutated.provenance,
                "scheme": mutated.scheme,
            }
            return replace(mutated, seal_commitment=commitment(payload))

        structural = (
            rebind(replace(seal, root_history=History("forged"))),
            rebind(
                replace(
                    seal,
                    snapshot=replace(seal.snapshot, time=seal.origin_time + 1),
                    reservoir_commitment=replace(
                        seal.snapshot, time=seal.origin_time + 1
                    ).digest,
                )
            ),
            rebind(
                replace(
                    seal,
                    snapshot=replace(seal.snapshot, remaining=0),
                    reservoir_commitment=replace(seal.snapshot, remaining=0).digest,
                )
            ),
            rebind(
                replace(
                    seal,
                    snapshot=replace(seal.snapshot, spec_commitment="00" * 32),
                    reservoir_commitment=replace(
                        seal.snapshot, spec_commitment="00" * 32
                    ).digest,
                )
            ),
        )
        for mutation in structural:
            with self.subTest(mutation=mutation):
                with self.assertRaises(SealIntegrityError):
                    mutation.verify()

    def test_snapshot_member_mutation_breaks_seal(self) -> None:
        snapshot = replace(
            self.output.seal.snapshot,
            tails=self.output.seal.snapshot.tails[:-1],
        )
        mutation = replace(self.output.seal, snapshot=snapshot)
        with self.assertRaises(SealIntegrityError):
            mutation.verify()

    def test_certificate_factor_mutation_breaks_seal(self) -> None:
        certificate = self.output.seal.snapshot.certificates[0]
        mutated_certificate = replace(
            certificate,
            verdict=replace(certificate.verdict, admissibility=False),
        )
        snapshot = replace(
            self.output.seal.snapshot,
            certificates=(mutated_certificate,)
            + self.output.seal.snapshot.certificates[1:],
        )
        with self.assertRaises(SealIntegrityError):
            replace(self.output.seal, snapshot=snapshot).verify()

    def test_every_token_payload_field_is_mac_bound(self) -> None:
        token = self.token()
        payload = token.payload
        mutations = (
            replace(payload, issuer="forged"),
            replace(payload, action="a"),
            replace(payload, mode=AssuranceMode.EXISTENTIAL),
            replace(payload, history_commitment="00" * 32),
            replace(payload, context_commitment="00" * 32),
            replace(payload, time=1),
            replace(payload, remaining=1),
            replace(payload, runtime_regime="forged"),
            replace(payload, issued_at=1),
            replace(payload, expires_at=1),
            replace(payload, decision_version="old"),
            replace(payload, enforcement_channel_version="old"),
        )
        for mutated_payload in mutations:
            with self.subTest(payload=mutated_payload):
                self.assert_rejected_token(replace(token, payload=mutated_payload))

    def test_action_outside_support_cannot_receive_token(self) -> None:
        with self.assertRaises(TokenError):
            self.authority.issue(
                self.context,
                "a",
                issued_at=0,
                expires_at=2,
                decision_version="G_enf-v1",
            )

    def test_current_fibre_blocks_successor_laundering(self) -> None:
        fixture = empty_active_support_scenario()
        root_reservoir = self.engine.reservoir(
            fixture.spec, fixture.history, 0, 1
        )
        bad_history = fixture.history.append("a", "bad")
        recomputed_terminal = self.engine.reservoir(
            fixture.spec, bad_history, 1, 0
        )
        adaptive = self.engine.adaptive_support(
            fixture.spec, fixture.history, 0, 1
        )
        geometry = self.engine.geometry_from_snapshot(root_reservoir)
        self.assertTrue(root_reservoir.tails)
        self.assertTrue(recomputed_terminal.tails)
        self.assertEqual(self.engine.existential_support(geometry), ("a",))
        self.assertFalse(geometry.fibre(Tail((Step("a", "bad"),))))
        self.assertNotIn("a", adaptive.actions)

    def test_recursive_k_blocks_shallow_fibre_only_mutant(self) -> None:
        history = History("root")
        dynamics = FiniteDynamics.from_mappings(
            "recursive-only",
            "1",
            "dynamics-authority",
            actions={"root": ("a",), "mid": ("x",)},
            disturbances={
                ("root", "a"): ("nominal",),
                ("mid", "x"): ("calm", "shock"),
            },
            successors={
                ("root", "a", "nominal"): ("mid",),
                ("mid", "x", "calm"): ("good",),
                ("mid", "x", "shock"): ("bad",),
            },
        )

        spec = _make_spec(
            spec_id="recursive-only",
            horizon=2,
            dynamics=dynamics,
            histories={"root": history},
            viability=_viability_rule(
                _viability_clause("viability:recursive-only", forbidden_states=("bad",))
            ),
        )
        root_reservoir = self.engine.reservoir(spec, history, 0, 2)
        current_fibre = self.engine.geometry_from_snapshot(root_reservoir).fibre(Tail((Step("a", "mid"),)))
        child_support = self.engine.adaptive_support(
            spec, history.append("a", "mid"), 1, 1
        )
        root_support = self.engine.adaptive_support(spec, history, 0, 2)
        self.assertTrue(current_fibre)
        self.assertEqual(child_support.actions, ())
        self.assertEqual(root_support.actions, ())

    def test_empty_active_support_cannot_fall_through_to_task_action(self) -> None:
        fixture = empty_active_support_scenario()
        context = self.engine.assurance_context(
            AssuranceMode.ADAPTIVE_ROBUST,
            fixture.spec,
            fixture.history,
            0,
            1,
            runtime_regime="fixture",
        )
        decision = self.enforcer().decide(context, "a", None, now=0, runtime_regime="fixture")
        self.assertEqual(decision.verdict, EnforcementVerdict.SAFE_MODE)
        self.assertIsNone(decision.action)

    def test_seal_rejects_unattested_history_observation_pair(self) -> None:
        """Def. 3.5: seal create must not accept a history that is not Int(observation)."""

        forged_history = History("forged-root")
        forged_snapshot = self.engine.reservoir(
            self.scenario.spec, forged_history, 0, self.scenario.spec.horizon
        )
        with self.assertRaises(SealIntegrityError):
            self.engine.create_seal(
                self.scenario.spec, forged_history, self.scenario.observation
            )
        # Even if a caller tries to bypass via SealRecord.create with matching snapshot:
        with self.assertRaises(SealIntegrityError):
            from ncnc.core import SealRecord

            SealRecord.create(
                self.scenario.spec,
                forged_history,
                forged_snapshot,
                self.scenario.observation,
            )

    def test_construction_guards_bite(self) -> None:
        from ncnc.core import (
            IdentityClause,
            IdentityRule,
            RuleRecord,
            SpecificationError,
            commitment,
        )

        with self.assertRaisesRegex(SpecificationError, "duplicate action declaration"):
            FiniteDynamics(
                "dup", "1", "x",
                actions_by_state=(("s", ("a",)), ("s", ("b",))),
                disturbances_by_state_action=(("s", "a", ("w",)), ("s", "b", ("w",))),
                successors_by_key=(("s", "a", "w", ("t",)), ("s", "b", "w", ("t",))),
            )
        with self.assertRaisesRegex(SpecificationError, "orphan disturbance row"):
            FiniteDynamics(
                "orph-d", "1", "x",
                actions_by_state=(("s", ("a",)),),
                disturbances_by_state_action=(
                    ("s", "a", ("w",)),
                    ("s", "ghost", ("w",)),
                ),
                successors_by_key=(("s", "a", "w", ("t",)),),
            )
        with self.assertRaisesRegex(SpecificationError, "orphan successor row"):
            FiniteDynamics(
                "orph-s", "1", "x",
                actions_by_state=(("s", ("a",)),),
                disturbances_by_state_action=(("s", "a", ("w",)),),
                successors_by_key=(
                    ("s", "a", "w", ("t",)),
                    ("s", "a", "ghost", ("t",)),
                ),
            )
        clause = IdentityClause("identity:bind", "1", "personal-authority")
        with self.assertRaisesRegex(
            SpecificationError, "does not commit to its executable clause"
        ):
            IdentityRule(
                RuleRecord(
                    "identity:bind", "1", "personal-authority",
                    implementation_digest=commitment("something-else"),
                ),
                clause,
            )

    def test_seal_verify_observation_rejects_wrong_preimage(self) -> None:
        from ncnc.core import PrivateObservation

        seal = self.output.seal
        seal.verify_observation(self.scenario.observation)
        wrong = PrivateObservation.from_mapping(
            "wrong", 0, {"history_key": "unknown"}
        )
        with self.assertRaises(SealIntegrityError):
            seal.verify_observation(wrong)



if __name__ == "__main__":
    unittest.main()
