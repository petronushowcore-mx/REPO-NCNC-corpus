from __future__ import annotations

from dataclasses import replace
import unittest

from ncnc.control import (
    EmptyDisposition,
    EmptySupportError,
    EmptySupportPolicy,
    EnforcementVerdict,
    Enforcer,
    ExecutionError,
    HistoryFutureRecurrence,
    MediatedExecutor,
    RecurrenceError,
    TaskSelector,
    TokenAuthority,
    TokenError,
    TraceLedger,
    causal_intervention_witness,
)
from ncnc.core import (
    AdaptiveAssurance,
    AssuranceMode,
    ExistentialAssurance,
    InterpretationError,
    MinervaOperator,
    ReservoirEngine,
    SealRelativeAssurance,
    Step,
    Tail,
)
from ncnc.scenarios import (
    empty_active_support_scenario,
    recurrence_update_inputs,
    robust_branching_scenario,
)


class ControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ReservoirEngine()
        self.minerva = MinervaOperator(self.engine)
        self.scenario = robust_branching_scenario()
        self.output = self.minerva.generate(
            self.scenario.observation, self.scenario.spec
        )
        self.authority = TokenAuthority(
            "test-enforcer",
            b"control-test-secret-material-at-least-32",
            engine=self.engine,
        )
        self.policy = EmptySupportPolicy(
            "safe-empty",
            "1",
            "safety-authority",
            EmptyDisposition.SAFE_MODE,
            "no supported action",
        )
        self.enforcer = Enforcer(
            self.authority, self.policy, decision_version="G_enf-v1"
        )

    def adaptive_context(self) -> AdaptiveAssurance:
        context = self.engine.assurance_context(
            AssuranceMode.ADAPTIVE_ROBUST,
            self.scenario.spec,
            self.scenario.history,
            0,
            2,
            runtime_regime="fixture",
        )
        self.assertIsInstance(context, AdaptiveAssurance)
        return context

    def fresh_token(self, context: AdaptiveAssurance):
        return self.authority.issue(
            context,
            "b",
            issued_at=0,
            expires_at=2,
            decision_version="G_enf-v1",
        )

    def recurrence_fixture(self):
        context = self.adaptive_context()
        token = self.fresh_token(context)
        decision = self.enforcer.decide(
            context, "b", token, now=0, runtime_regime="fixture"
        )
        trace = MediatedExecutor(self.authority).attempt(
            self.scenario.spec,
            self.scenario.history,
            "b",
            "shock",
            "robust1",
            decision,
            time=0,
            runtime_regime="fixture",
        )
        provenance = HistoryFutureRecurrence.provenance_token(
            self.output.seal.seal_commitment, trace.digest
        )
        next_spec, next_observation = recurrence_update_inputs(
            self.scenario, trace.post_history, provenance
        )
        record, next_output = HistoryFutureRecurrence.advance(
            self.engine,
            self.scenario.spec,
            self.output,
            self.scenario.observation,
            context,
            decision,
            self.authority,
            trace,
            next_spec,
            next_observation,
            next_runtime_regime="fixture",
        )
        return (
            context,
            decision,
            trace,
            provenance,
            next_spec,
            next_observation,
            record,
            next_output,
        )

    def test_assurance_context_is_mode_specific(self) -> None:
        existential = self.engine.assurance_context(
            AssuranceMode.EXISTENTIAL,
            self.scenario.spec,
            self.scenario.history,
            0,
            2,
            runtime_regime="fixture",
        )
        adaptive = self.adaptive_context()
        sealed = self.engine.assurance_context(
            AssuranceMode.SEAL_RELATIVE,
            self.scenario.spec,
            self.scenario.history,
            0,
            2,
            seal=self.output.seal,
            prefix=Tail.empty(),
            runtime_regime="fixture",
        )
        self.assertIsInstance(existential, ExistentialAssurance)
        self.assertIsInstance(adaptive, AdaptiveAssurance)
        self.assertIsInstance(sealed, SealRelativeAssurance)
        self.assertNotEqual(existential.digest, adaptive.digest)
        self.assertNotEqual(adaptive.digest, sealed.digest)

    def test_selector_is_partial_on_empty_support(self) -> None:
        fixture = empty_active_support_scenario()
        context = self.engine.assurance_context(
            AssuranceMode.ADAPTIVE_ROBUST,
            fixture.spec,
            fixture.history,
            0,
            1,
            runtime_regime="fixture",
        )
        with self.assertRaises(EmptySupportError):
            TaskSelector().select(context, {})

    def test_empty_active_support_uses_sealed_handler(self) -> None:
        fixture = empty_active_support_scenario()
        context = self.engine.assurance_context(
            AssuranceMode.ADAPTIVE_ROBUST,
            fixture.spec,
            fixture.history,
            0,
            1,
            runtime_regime="fixture",
        )
        decision = self.enforcer.decide(context, None, None, now=0, runtime_regime="fixture")
        self.assertEqual(decision.verdict, EnforcementVerdict.SAFE_MODE)
        self.assertEqual(decision.empty_handler_commitment, self.policy.digest)

    def test_valid_token_is_bound_to_complete_adaptive_context(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        self.assertEqual(token.payload.action, "b")
        self.assertEqual(token.payload.mode, AssuranceMode.ADAPTIVE_ROBUST)
        self.assertEqual(token.payload.history_commitment, context.history.digest)
        self.assertEqual(token.payload.context_commitment, context.digest)
        self.assertEqual(token.payload.remaining, 2)
        self.assertEqual(token.payload.runtime_regime, "fixture")
        self.assertEqual(context.validity, self.scenario.spec.validity)
        self.assertEqual(context.runtime_regime, "fixture")

    def test_valid_token_admits_once(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        first = self.enforcer.decide(context, "b", token, now=0, runtime_regime="fixture")
        second = self.enforcer.decide(context, "b", token, now=0, runtime_regime="fixture")
        self.assertEqual(first.verdict, EnforcementVerdict.ADMIT)
        self.assertEqual(second.verdict, EnforcementVerdict.REJECT)
        self.assertIn("replay", second.reason)

    def test_missing_token_fails_closed(self) -> None:
        decision = self.enforcer.decide(self.adaptive_context(), "b", None, now=0, runtime_regime="fixture")
        self.assertEqual(decision.verdict, EnforcementVerdict.REJECT)

    def test_cross_mode_token_reuse_is_rejected(self) -> None:
        adaptive = self.adaptive_context()
        token = self.fresh_token(adaptive)
        existential = self.engine.assurance_context(
            AssuranceMode.EXISTENTIAL,
            self.scenario.spec,
            self.scenario.history,
            0,
            2,
            runtime_regime="fixture",
        )
        decision = self.enforcer.decide(existential, "b", token, now=0, runtime_regime="fixture")
        self.assertEqual(decision.verdict, EnforcementVerdict.REJECT)

    def test_token_action_mutation_is_rejected(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        mutated = replace(token, payload=replace(token.payload, action="a"))
        decision = self.enforcer.decide(context, "b", mutated, now=0, runtime_regime="fixture")
        self.assertEqual(decision.verdict, EnforcementVerdict.REJECT)

    def test_token_history_mutation_is_rejected(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        mutated = replace(
            token,
            payload=replace(token.payload, history_commitment="00" * 32),
        )
        decision = self.enforcer.decide(context, "b", mutated, now=0, runtime_regime="fixture")
        self.assertEqual(decision.verdict, EnforcementVerdict.REJECT)

    def test_token_signature_mutation_is_rejected(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        decision = self.enforcer.decide(
            context, "b", replace(token, signature="00" * 32), now=0,
            runtime_regime="fixture",
        )
        self.assertEqual(decision.verdict, EnforcementVerdict.REJECT)

    def test_expired_token_is_rejected(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        decision = self.enforcer.decide(context, "b", token, now=3, runtime_regime="fixture")
        self.assertEqual(decision.verdict, EnforcementVerdict.REJECT)

    def test_token_expiry_cannot_outlive_assurance_validity(self) -> None:
        short_spec = replace(
            self.scenario.spec,
            validity=replace(self.scenario.spec.validity, not_after=2),
        )
        context = self.engine.assurance_context(
            AssuranceMode.ADAPTIVE_ROBUST,
            short_spec,
            self.scenario.history,
            0,
            2,
            runtime_regime="fixture",
        )
        with self.assertRaises(TokenError):
            self.authority.issue(
                context,
                "b",
                issued_at=0,
                expires_at=3,
                decision_version="G_enf-v1",
            )

    def test_runtime_regime_change_is_rejected_before_enforcement(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        decision = self.enforcer.decide(
            context,
            "b",
            token,
            now=0,
            runtime_regime="changed-regime",
        )
        self.assertEqual(decision.verdict, EnforcementVerdict.REJECT)
        self.assertIn("runtime regime", decision.reason)

    def test_wrong_decision_version_is_rejected(self) -> None:
        context = self.adaptive_context()
        token = self.authority.issue(
            context,
            "b",
            issued_at=0,
            expires_at=2,
            decision_version="old-enforcer",
        )
        decision = self.enforcer.decide(context, "b", token, now=0, runtime_regime="fixture")
        self.assertEqual(decision.verdict, EnforcementVerdict.REJECT)
        self.assertIn("decision version", decision.reason)

    def test_mediated_executor_changes_history_only_after_admit(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        admit = self.enforcer.decide(context, "b", token, now=0, runtime_regime="fixture")
        reject = self.enforcer.decide(context, "b", None, now=0, runtime_regime="fixture")
        executor = MediatedExecutor(self.authority)
        executed = executor.attempt(
            self.scenario.spec,
            self.scenario.history,
            "b",
            "shock",
            "robust1",
            admit,
            time=0,
            runtime_regime="fixture",
        )
        blocked = executor.attempt(
            self.scenario.spec,
            self.scenario.history,
            "b",
            "shock",
            "robust1",
            reject,
            time=0,
            runtime_regime="fixture",
        )
        self.assertTrue(executed.executed)
        self.assertFalse(blocked.executed)
        self.assertNotEqual(executed.post_history, blocked.post_history)
        self.assertTrue(causal_intervention_witness(executed, blocked))

    def test_executor_rejects_runtime_regime_change(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        admit = self.enforcer.decide(
            context,
            "b",
            token,
            now=0,
            runtime_regime="fixture",
        )
        with self.assertRaises(ExecutionError):
            MediatedExecutor(self.authority).attempt(
                self.scenario.spec,
                self.scenario.history,
                "b",
                "shock",
                "robust1",
                admit,
                time=0,
                runtime_regime="changed-regime",
            )

    def test_executor_rejects_successor_outside_declared_dynamics(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        admit = self.enforcer.decide(context, "b", token, now=0, runtime_regime="fixture")
        with self.assertRaises(ExecutionError):
            MediatedExecutor(self.authority).attempt(
                self.scenario.spec,
                self.scenario.history,
                "b",
                "shock",
                "forged",
                admit,
                time=0,
                runtime_regime="fixture",
            )

    def test_forged_admit_decision_is_rejected_by_executor(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        admit = self.enforcer.decide(context, "b", token, now=0, runtime_regime="fixture")
        forged = replace(admit, authorization_tag="00" * 32)
        with self.assertRaises(ExecutionError):
            MediatedExecutor(self.authority).attempt(
                self.scenario.spec,
                self.scenario.history,
                "b",
                "shock",
                "robust1",
                forged,
                time=0,
                runtime_regime="fixture",
            )

    def test_execution_decision_is_bound_to_history_spec_and_time(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        admit = self.enforcer.decide(context, "b", token, now=0, runtime_regime="fixture")
        cases = (
            (
                replace(self.scenario.history, initial_state="other"),
                self.scenario.spec,
                0,
            ),
            (
                self.scenario.history,
                replace(self.scenario.spec, model_version="forged-version"),
                0,
            ),
            (self.scenario.history, self.scenario.spec, 1),
        )
        for history, spec, time in cases:
            with self.subTest(history=history, spec=spec.digest, time=time):
                with self.assertRaises(ExecutionError):
                    MediatedExecutor(self.authority).attempt(
                        spec,
                        history,
                        "b",
                        "shock",
                        "robust1",
                        admit,
                        time=time,
                        runtime_regime="fixture",
                    )

    def test_execution_decision_is_one_shot(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        admit = self.enforcer.decide(context, "b", token, now=0, runtime_regime="fixture")
        executor = MediatedExecutor(self.authority)
        executor.attempt(
            self.scenario.spec,
            self.scenario.history,
            "b",
            "shock",
            "robust1",
            admit,
            time=0,
            runtime_regime="fixture",
        )
        with self.assertRaises(ExecutionError):
            executor.attempt(
                self.scenario.spec,
                self.scenario.history,
                "b",
                "shock",
                "robust1",
                admit,
                time=0,
                runtime_regime="fixture",
            )

    def test_replay_state_is_authority_scoped_for_all_verdicts(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        admit = self.enforcer.decide(
            context, "b", token, now=0, runtime_regime="fixture"
        )
        reject = self.enforcer.decide(
            context, "b", None, now=0, runtime_regime="fixture"
        )
        MediatedExecutor(self.authority).attempt(
            self.scenario.spec,
            self.scenario.history,
            "b",
            "shock",
            "robust1",
            admit,
            time=0,
            runtime_regime="fixture",
        )
        with self.assertRaises(ExecutionError):
            MediatedExecutor(self.authority).attempt(
                self.scenario.spec,
                self.scenario.history,
                "b",
                "shock",
                "robust1",
                admit,
                time=0,
                runtime_regime="fixture",
            )
        MediatedExecutor(self.authority).attempt(
            self.scenario.spec,
            self.scenario.history,
            "b",
            "shock",
            "robust1",
            reject,
            time=0,
            runtime_regime="fixture",
        )
        with self.assertRaises(ExecutionError):
            MediatedExecutor(self.authority).attempt(
                self.scenario.spec,
                self.scenario.history,
                "b",
                "shock",
                "robust1",
                reject,
                time=0,
                runtime_regime="fixture",
            )

    def test_trace_ledger_is_append_only_and_mutation_detecting(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        reject = self.enforcer.decide(context, "b", None, now=0, runtime_regime="fixture")
        admit = self.enforcer.decide(context, "b", token, now=0, runtime_regime="fixture")
        executor = MediatedExecutor(self.authority)
        blocked = executor.attempt(
            self.scenario.spec,
            self.scenario.history,
            "b",
            "shock",
            "robust1",
            reject,
            time=0,
            runtime_regime="fixture",
        )
        executed = executor.attempt(
            self.scenario.spec,
            self.scenario.history,
            "b",
            "shock",
            "robust1",
            admit,
            time=0,
            runtime_regime="fixture",
        )
        ledger = TraceLedger().append(blocked).append(executed)
        ledger.verify()
        forged_entry = replace(ledger.entries[0], entry_commitment="00" * 32)
        forged_ledger = replace(
            ledger, entries=(forged_entry,) + ledger.entries[1:]
        )
        with self.assertRaises(ExecutionError):
            forged_ledger.verify()

    def test_trace_ledger_rejects_discontinuous_history(self) -> None:
        context = self.adaptive_context()
        token = self.fresh_token(context)
        admit = self.enforcer.decide(context, "b", token, now=0, runtime_regime="fixture")
        reject = self.enforcer.decide(context, "b", None, now=0, runtime_regime="fixture")
        executor = MediatedExecutor(self.authority)
        executed = executor.attempt(
            self.scenario.spec,
            self.scenario.history,
            "b",
            "shock",
            "robust1",
            admit,
            time=0,
            runtime_regime="fixture",
        )
        blocked_from_root = executor.attempt(
            self.scenario.spec,
            self.scenario.history,
            "b",
            "shock",
            "robust1",
            reject,
            time=0,
            runtime_regime="fixture",
        )
        with self.assertRaises(ExecutionError):
            TraceLedger().append(executed).append(blocked_from_root)

    def test_history_future_recurrence_verifies_complete_link(self) -> None:
        context, decision, trace, provenance, next_spec, next_observation, record, next_output = (
            self.recurrence_fixture()
        )
        record.verify(
            self.engine,
            self.scenario.spec,
            self.output,
            self.scenario.observation,
            context,
            decision,
            self.authority,
            trace,
            next_spec,
            next_output,
            next_observation,
            next_runtime_regime="fixture",
        )
        self.assertEqual(next_output.history, trace.post_history)
        self.assertIn(provenance, next_spec.provenance)

    def test_history_future_recurrence_rejects_false_append(self) -> None:
        context, decision, trace, _, next_spec, next_observation, _, next_output = (
            self.recurrence_fixture()
        )
        forged = replace(trace, post_history=self.scenario.history)
        with self.assertRaisesRegex(
            RecurrenceError, "recurrence post-history is not the exact append"
        ):
            HistoryFutureRecurrence.create(
                self.engine,
                self.scenario.spec,
                self.output,
                self.scenario.observation,
                context,
                decision,
                self.authority,
                forged,
                next_spec,
                next_output,
                next_observation,
                next_runtime_regime="fixture",
            )

    def test_history_future_recurrence_rejects_missing_provenance(self) -> None:
        context, decision, trace, provenance, next_spec, next_observation, _, _ = (
            self.recurrence_fixture()
        )
        unlinked = replace(
            next_spec,
            provenance=tuple(item for item in next_spec.provenance if item != provenance),
        )
        with self.assertRaisesRegex(
            RecurrenceError,
            "recurrence provenance link is absent from the next specification",
        ):
            HistoryFutureRecurrence.advance(
                self.engine,
                self.scenario.spec,
                self.output,
                self.scenario.observation,
                context,
                decision,
                self.authority,
                trace,
                unlinked,
                next_observation,
                next_runtime_regime="fixture",
            )

    def test_history_future_recurrence_rejects_forged_decision(self) -> None:
        context, decision, trace, _, next_spec, next_observation, record, next_output = (
            self.recurrence_fixture()
        )
        forged = replace(decision, authorization_tag="00" * 32)
        with self.assertRaisesRegex(
            RecurrenceError, "recurrence enforcement decision authentication mismatch"
        ):
            record.verify(
                self.engine,
                self.scenario.spec,
                self.output,
                self.scenario.observation,
                context,
                forged,
                self.authority,
                trace,
                next_spec,
                next_output,
                next_observation,
                next_runtime_regime="fixture",
            )

    def test_history_future_recurrence_rejects_detached_successor(self) -> None:
        context, decision, trace, _, next_spec, next_observation, record, next_output = (
            self.recurrence_fixture()
        )
        detached = replace(next_output, history=self.scenario.history)
        with self.assertRaisesRegex(
            RecurrenceError, "recurrence next output is detached from its seal"
        ):
            record.verify(
                self.engine,
                self.scenario.spec,
                self.output,
                self.scenario.observation,
                context,
                decision,
                self.authority,
                trace,
                next_spec,
                detached,
                next_observation,
                next_runtime_regime="fixture",
            )

    def test_history_future_recurrence_rejects_prior_observation_substitution(self) -> None:
        context, decision, trace, _, next_spec, next_observation, record, next_output = (
            self.recurrence_fixture()
        )
        substituted = replace(
            self.scenario.observation, observation_id="substituted-prior"
        )
        with self.assertRaisesRegex(
            RecurrenceError, "recurrence prior observation/seal mismatch"
        ):
            record.verify(
                self.engine,
                self.scenario.spec,
                self.output,
                substituted,
                context,
                decision,
                self.authority,
                trace,
                next_spec,
                next_output,
                next_observation,
                next_runtime_regime="fixture",
            )

    def test_history_future_recurrence_rejects_undeclared_generator_input(self) -> None:
        context, decision, trace, _, next_spec, next_observation, record, next_output = (
            self.recurrence_fixture()
        )
        contaminated = replace(
            next_output, generator_input_commitment="undeclared-future-oracle"
        )
        with self.assertRaisesRegex(
            RecurrenceError, "recurrence next generator input commitment mismatch"
        ):
            record.verify(
                self.engine,
                self.scenario.spec,
                self.output,
                self.scenario.observation,
                context,
                decision,
                self.authority,
                trace,
                next_spec,
                contaminated,
                next_observation,
                next_runtime_regime="fixture",
            )

    def test_history_future_recurrence_rejects_link_commitment_mutation(self) -> None:
        context, decision, trace, _, next_spec, next_observation, record, next_output = (
            self.recurrence_fixture()
        )
        mutated = replace(record, link_commitment="00" * 32)
        with self.assertRaisesRegex(
            RecurrenceError, "recurrence link commitment mismatch"
        ):
            mutated.verify(
                self.engine,
                self.scenario.spec,
                self.output,
                self.scenario.observation,
                context,
                decision,
                self.authority,
                trace,
                next_spec,
                next_output,
                next_observation,
                next_runtime_regime="fixture",
            )

    def test_interpreter_failure_prevents_reservoir_generation(self) -> None:
        observation = replace(
            self.scenario.observation,
            attributes=(("history_key", "ambiguous"),),
        )
        with self.assertRaises(InterpretationError):
            self.minerva.generate(observation, self.scenario.spec)


if __name__ == "__main__":
    unittest.main()
