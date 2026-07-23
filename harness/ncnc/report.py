"""Deterministic executable report for the finite reference instrument."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Callable

from .access import (
    GreedyVersionSpaceAttack,
    LeakagePolicy,
    MembershipOracle,
    QueryBudgetExceeded,
    exact_factorisation_map,
    find_fibre_collisions,
)
from .control import (
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
from .core import (
    AdmissibilityCase,
    AssuranceMode,
    BoundarySourceRole,
    CertificateIntegrityError,
    History,
    HorizonError,
    IdentityCase,
    IdentityClause,
    IdentityRule,
    InterpretationError,
    MinervaOperator,
    ReservoirEngine,
    RuleRecord,
    SealIntegrityError,
    Step,
    SpecificationError,
    Tail,
    WearLedger,
    canonical_json,
    commitment,
    identity_rule_from_clause,
    viability_rule_from_clause,
)
from .scenarios import (
    boundary_intervention_specs,
    wear_accumulation_scenario,
    boundary_hypotheses,
    budget_geometry_comparison,
    empty_active_support_scenario,
    empty_reservoir_scenario,
    equal_identity_different_budget_scenarios,
    hidden_lineage_scenarios,
    non_absorption_cases,
    predicate_intervention_specs,
    recurrence_update_inputs,
    robust_branching_scenario,
    seal_recomputation_divergence_scenario,
    seal_recursive_gap_scenario,
)


class Status(str, Enum):
    ESTABLISHED = "ESTABLISHED_ON_FINITE_FIXTURE"
    REFUTED = "REFUTED_ON_FINITE_FIXTURE"
    INCONCLUSIVE = "INCONCLUSIVE"
    NOT_MACHINE_DECIDABLE = "NOT_MACHINE_DECIDABLE"


@dataclass(frozen=True, slots=True)
class CheckResult:
    check_id: str
    status: Status
    claim: str
    evidence: Any

    def canonical_data(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "status": self.status,
            "claim": self.claim,
            "evidence": self.evidence,
        }


@dataclass(frozen=True, slots=True)
class MutationResult:
    mutation_id: str
    detected: bool
    mechanism: str

    def canonical_data(self) -> dict[str, Any]:
        return {
            "mutation_id": self.mutation_id,
            "detected": self.detected,
            "mechanism": self.mechanism,
        }


@dataclass(frozen=True, slots=True)
class ReferenceReport:
    schema: str
    checks: tuple[CheckResult, ...]
    mutations: tuple[MutationResult, ...]
    limitations: tuple[str, ...]

    @property
    def mutation_survivors(self) -> tuple[str, ...]:
        return tuple(item.mutation_id for item in self.mutations if not item.detected)

    @property
    def successful(self) -> bool:
        return (
            not any(item.status is Status.REFUTED for item in self.checks)
            and not self.mutation_survivors
        )

    @property
    def digest(self) -> str:
        return commitment(self)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "checks": self.checks,
            "mutations": self.mutations,
            "limitations": self.limitations,
            "mutation_survivors": self.mutation_survivors,
            "successful": self.successful,
        }


def _check(check_id: str, claim: str, condition: bool, evidence: Any) -> CheckResult:
    return CheckResult(
        check_id,
        Status.ESTABLISHED if condition else Status.REFUTED,
        claim,
        evidence,
    )


def _caught(exc_type: type[BaseException], fn: Callable[[], Any], expected: str) -> bool:
    """True only when fn raises exc_type AND raises it from the guard this probe targets.

    `expected` is required: matching on the exception TYPE alone made the whole mutation
    battery unfalsifiable. Several guards on one path raise the same error class, so
    deleting the guard a probe claims to exercise left that probe green — a neighbouring
    guard answered in its place. Observed directly: deleting the observation-digest guard
    in `Seal.verify_observation` changed no probe result at all, because the interpreter
    then raised `InterpretationError`, which is re-wrapped as `SealIntegrityError` and
    caught just the same. A probe that cannot fail certifies nothing.

    Prefix match, not equality, so messages carrying a variable tail (an offending key, a
    count) stay pinned to their guard without pinning the incidental detail.
    """

    try:
        fn()
    except exc_type as exc:
        return str(exc).startswith(expected)
    return False


def run_reference_verification() -> ReferenceReport:
    engine = ReservoirEngine()
    minerva = MinervaOperator(engine)
    checks: list[CheckResult] = []
    mutations: list[MutationResult] = []

    robust = robust_branching_scenario()
    robust_output = minerva.generate(robust.observation, robust.spec)
    robust_snapshot_audit = engine.assert_snapshot(robust.spec, robust_output.reservoir)
    robust_geometry = engine.geometry(robust.spec, robust.history, 0, 2)
    engine.assert_geometry(robust_output.reservoir, robust_geometry)
    expected_prefixes = {Tail.empty()}
    for tail in robust_output.reservoir.tails:
        expected_prefixes.update(
            tail.prefix(length) for length in range(1, robust_output.reservoir.remaining + 1)
        )
    expected_geometry = tuple(
        (
            prefix,
            tuple(
                tail
                for tail in robust_output.reservoir.tails
                if tail.steps[: len(prefix.steps)] == prefix.steps
            ),
        )
        for prefix in sorted(expected_prefixes)
    )
    projected_from_geometry = tuple(
        sorted(
            {
                prefix.first_action
                for prefix, fibre in expected_geometry
                if len(prefix.steps) == 1 and fibre
            }
        )
    )
    existential = engine.existential_support(robust_geometry)
    adaptive = engine.adaptive_support(robust.spec, robust.history, 0, 2)
    checks.append(
        _check(
            "D3.2-reservoir",
            "reservoir is exactly the admitted reachable-tail filter",
            bool(robust_output.reservoir.tails)
            and robust_snapshot_audit.valid
            and all(cert.verdict.admitted for cert in robust_output.reservoir.certificates)
            and len(robust_output.reservoir.tails)
            == len(robust_output.reservoir.certificates),
            {
                "reachable": len(engine.reachable_tails(robust.spec, robust.history, 0, 2)),
                "admitted": len(robust_output.reservoir.tails),
                "certificate_digests": tuple(
                    cert.digest for cert in robust_output.reservoir.certificates
                ),
                "recomputation_audit": robust_snapshot_audit,
            },
        )
    )
    checks.append(
        _check(
            "D3.2a-prefix-fibre-geometry",
            "G(R) is the exact prefix-indexed fibre family of the sealed reservoir",
            robust_geometry.reservoir_commitment == robust_output.reservoir.digest
            and robust_geometry.spec_commitment == robust_output.reservoir.spec_commitment
            and robust_geometry.history == robust_output.reservoir.history
            and robust_geometry.time == robust_output.reservoir.time
            and robust_geometry.remaining == robust_output.reservoir.remaining
            and tuple(
                (item.prefix, item.tails) for item in robust_geometry.fibres
            )
            == expected_geometry,
            {
                "reservoir_commitment": robust_output.reservoir.digest,
                "geometry_commitment": robust_geometry.digest,
                "prefix_fibres": expected_geometry,
            },
        )
    )
    checks.append(
        _check(
            "D3.3-P4.1",
            "existential support is projected from the one-step fibres of G(R)",
            existential == ("a", "b")
            and existential == projected_from_geometry,
            {
                "geometry_commitment": robust_geometry.digest,
                "projected_actions": projected_from_geometry,
                "existential_support": existential,
            },
        )
    )
    checks.append(
        _check(
            "D3.4-T2",
            "adaptive support uses every branch, current fibres and recursive K",
            adaptive.actions == ("b",)
            and adaptive.evidence_for("b") is not None
            and adaptive.evidence_for("b").valid,
            {
                "adaptive_support": adaptive.actions,
                "branch_counts": {
                    item.action: len(item.branches) for item in adaptive.evidence
                },
                "a_branch_validity": tuple(
                    branch.valid for branch in adaptive.evidence_for("a").branches
                ),
            },
        )
    )

    terminal_history = (
        robust.history.append("b", "robust1").append("continue", "terminal")
    )
    terminal = engine.reservoir(robust.spec, terminal_history, 2, 0)
    terminal_geometry = engine.geometry(robust.spec, terminal_history, 2, 0)
    checks.append(
        _check(
            "H0-domain",
            "H=0 is the terminal reservoir base and has no present support",
            terminal.tails == (Tail.empty(),)
            and _caught(
                HorizonError,
                lambda: engine.existential_support(terminal_geometry),
                "present support is undefined at terminal horizon",
            ),
            {"terminal_tails": terminal.tails},
        )
    )

    origin_seal = robust_output.seal
    root_seal_support = engine.seal_relative_support(origin_seal, Tail.empty())
    prefix_one = Tail((Step("b", "robust1"),))
    prefix_one_support = engine.seal_relative_support(origin_seal, prefix_one)
    prefix_two = prefix_one.append("continue", "terminal")
    final_fibre = engine.geometry_from_snapshot(origin_seal.snapshot).fibre(prefix_two)
    checks.append(
        _check(
            "T1-T4.6",
            "seal-relative selection preserves original conditional fibres",
            root_seal_support.actions == ("b",)
            and prefix_one_support.actions == ("continue",)
            and bool(final_fibre),
            {
                "k0_support": root_seal_support.actions,
                "k1_support": prefix_one_support.actions,
                "k2_fibre": tuple(tail.digest for tail in final_fibre),
                "origin_seal": origin_seal.seal_commitment,
            },
        )
    )

    thin_failures = engine.thin_temporal_restriction_failures(
        robust.spec, robust.history, 0, 2
    )
    checks.append(
        _check(
            "T13-thin-temporal-restriction",
            "admitted full tails retain identity and admissibility at every prefix",
            not thin_failures,
            {
                "audited_tails": tuple(
                    tail.digest for tail in robust_output.reservoir.tails
                ),
                "depths": tuple(range(robust.spec.horizon + 1)),
                "failures": thin_failures,
            },
        )
    )

    terminal_only_identity = identity_rule_from_clause(
        IdentityClause(
            "identity:terminal-only-prefix-counterexample",
            "1",
            "personal-authority",
            cases=(IdentityCase(history_length=1, verdict=False),),
            default_allow=True,
        ),
        ground_refs=robust.spec.declaration.identity.record.ground_refs,
    )
    terminal_only_spec = replace(
        robust.spec,
        spec_id="robust-branching:terminal-only-prefix-counterexample",
        declaration=replace(
            robust.spec.declaration,
            identity=terminal_only_identity,
        ),
    )
    terminal_only_failures = engine.thin_temporal_restriction_failures(
        terminal_only_spec, robust.history, 0, 2
    )
    failure_classes = {
        (prefix_length, factor)
        for _, prefix_length, factor in terminal_only_failures
    }
    mutations.append(
        MutationResult(
            "F18-prefix-verdict-inflation",
            bool(terminal_only_failures)
            and failure_classes == {(1, "identity")},
            "terminal-only identity admits full tails but the restriction audit "
            "reports every rejected one-step prefix",
        )
    )

    prefix_sensitive_source = robust.spec.declaration.boundary.sources[0]
    prefix_sensitive_clause = replace(
        prefix_sensitive_source.clause,
        cases=prefix_sensitive_source.clause.cases
        + (
            AdmissibilityCase(
                "s0",
                1,
                allowed_action_paths=(("forbidden-prefix",),),
            ),
        ),
    )
    prefix_sensitive_source = replace(
        prefix_sensitive_source,
        clause=prefix_sensitive_clause,
    )
    prefix_sensitive_boundary = replace(
        robust.spec.declaration.boundary,
        sources=(prefix_sensitive_source,)
        + robust.spec.declaration.boundary.sources[1:],
    )
    prefix_sensitive_spec = replace(
        robust.spec,
        spec_id="robust-branching:prefix-sensitive-admissibility",
        declaration=replace(
            robust.spec.declaration,
            boundary=prefix_sensitive_boundary,
        ),
    )
    prefix_sensitive_failures = engine.thin_temporal_restriction_failures(
        prefix_sensitive_spec, robust.history, 0, 2
    )
    admissibility_failure_classes = {
        (prefix_length, factor)
        for _, prefix_length, factor in prefix_sensitive_failures
    }
    mutations.append(
        MutationResult(
            "F18-prefix-admissibility-inflation",
            bool(prefix_sensitive_failures)
            and admissibility_failure_classes == {(1, "admissibility")},
            "horizon-two admissibility admits full tails but the restriction audit "
            "reports every rejected horizon-one prefix",
        )
    )

    seal_gap = seal_recursive_gap_scenario()
    seal_gap_output = minerva.generate(seal_gap.observation, seal_gap.spec)
    seal_gap_support = engine.seal_relative_support(
        seal_gap_output.seal, Tail.empty()
    )
    seal_gap_branch = seal_gap_support.evidence_for("enter").branches[0]
    checks.append(
        _check(
            "D4.5-KSigma-recursion",
            "seal-relative support requires recursive original-seal continuation",
            bool(seal_gap_branch.conditional_fibre)
            and not seal_gap_branch.recursive_continuation
            and seal_gap_branch.child_support_digest is not None
            and seal_gap_support.actions == ()
            and not engine.seal_continuation_indicator(
                seal_gap_output.seal, Tail.empty()
            ),
            {
                "shallow_fibre": seal_gap_branch.conditional_fibre,
                "child_support": seal_gap_branch.child_support_digest,
                "recursive_support": seal_gap_support.actions,
            },
        )
    )

    divergence = seal_recomputation_divergence_scenario()
    divergence_output = minerva.generate(
        divergence.scenario.observation, divergence.scenario.spec
    )
    divergence_history = divergence.scenario.history.extend(divergence.realised_prefix)
    divergence_adaptive = engine.adaptive_support(
        divergence.scenario.spec, divergence_history, 1, 1
    )
    divergence_sealed = engine.seal_relative_support(
        divergence_output.seal, divergence.realised_prefix
    )
    checks.append(
        _check(
            "D4.5-adaptive-seal-separation",
            "adaptive recomputation and original-seal fidelity remain distinct",
            divergence_adaptive.actions == divergence.expected_adaptive
            and divergence_sealed.actions == divergence.expected_seal_relative,
            {
                "adaptive": divergence_adaptive.actions,
                "seal_relative": divergence_sealed.actions,
            },
        )
    )

    revised_spec = replace(divergence.scenario.spec, model_version="2")
    changed_theta_rejected = _caught(
        SealIntegrityError,
        lambda: engine.assurance_context(
            AssuranceMode.SEAL_RELATIVE,
            revised_spec,
            divergence_history,
            1,
            1,
            seal=divergence_output.seal,
            prefix=divergence.realised_prefix,
            runtime_regime="fixture",
        ),
        "a fresh specification cannot replace the origin seal",
    )
    checks.append(
        _check(
            "Theta-lineage",
            "a changed construction specification cannot rescue an earlier seal",
            changed_theta_rejected,
            {"original": divergence.scenario.spec.digest, "revised": revised_spec.digest},
        )
    )

    predicate_left, predicate_right = predicate_intervention_specs()
    left_reservoir = minerva.generate(
        predicate_left.observation, predicate_left.spec
    ).reservoir
    right_reservoir = minerva.generate(
        predicate_right.observation, predicate_right.spec
    ).reservoir
    all_non_identity_true = all(
        cert.verdict.admissibility and all(cert.verdict.viability)
        for cert in left_reservoir.certificates + right_reservoir.certificates
    )
    checks.append(
        _check(
            "T3-predicate-intervention",
            "identity intervention changes the reservoir on an unmasked disagreement",
            all_non_identity_true
            and tuple(tail.digest for tail in left_reservoir.tails)
            != tuple(tail.digest for tail in right_reservoir.tails),
            {
                "left": tuple(tail.digest for tail in left_reservoir.tails),
                "right": tuple(tail.digest for tail in right_reservoir.tails),
                "non_identity_factors_true": all_non_identity_true,
            },
        )
    )

    boundary_left, boundary_right = boundary_intervention_specs()
    boundary_left_reachable = engine.reachable_tails(
        boundary_left.spec, boundary_left.history, 0, 1
    )
    boundary_right_reachable = engine.reachable_tails(
        boundary_right.spec, boundary_right.history, 0, 1
    )
    boundary_left_output = minerva.generate(
        boundary_left.observation, boundary_left.spec
    )
    boundary_right_output = minerva.generate(
        boundary_right.observation, boundary_right.spec
    )
    boundary_left_reservoir = boundary_left_output.reservoir
    boundary_right_reservoir = boundary_right_output.reservoir
    boundary_left_geometry = engine.geometry_from_snapshot(boundary_left_reservoir)
    boundary_right_geometry = engine.geometry_from_snapshot(boundary_right_reservoir)
    engine.assert_geometry(boundary_left_reservoir, boundary_left_geometry)
    engine.assert_geometry(boundary_right_reservoir, boundary_right_geometry)
    boundary_left_support = engine.existential_support(boundary_left_geometry)
    boundary_right_support = engine.existential_support(boundary_right_geometry)
    boundary_specs = (boundary_left.spec, boundary_right.spec)
    boundary_binding = all(
        "admissibility" not in type(spec).__dataclass_fields__
        and spec.admissibility.record
        == spec.declaration.boundary.compile().record
        and tuple(
            source.source_id for source in spec.declaration.boundary.sources
        )
        == spec.admissibility.record.ground_refs
        and spec.declaration.boundary.subject_id == spec.declaration.subject_id
        and spec.declaration.boundary.version == spec.declaration.version
        and spec.declaration.boundary.version == spec.admissibility.record.version
        for spec in boundary_specs
    )

    def source_conjunction_is_load_bearing(
        scenario: Any, admitted_action: str, rejected_action: str
    ) -> bool:
        boundary = scenario.spec.declaration.boundary
        subject_source = next(
            source
            for source in boundary.sources
            if source.role is BoundarySourceRole.SUBJECT
        )
        shared_source = next(
            source
            for source in boundary.sources
            if source.role is BoundarySourceRole.SHARED
        )
        subject_only = Tail((Step(admitted_action, "blocked"),))
        shared_only = Tail((Step(rejected_action, "terminal"),))
        jointly_admitted = Tail((Step(admitted_action, "terminal"),))
        compiled = scenario.spec.admissibility
        return (
            subject_source.clause(0, 1, scenario.history, subject_only)
            and not shared_source.clause(0, 1, scenario.history, subject_only)
            and not compiled(0, 1, scenario.history, subject_only)
            and not subject_source.clause(0, 1, scenario.history, shared_only)
            and shared_source.clause(0, 1, scenario.history, shared_only)
            and not compiled(0, 1, scenario.history, shared_only)
            and subject_source.clause(0, 1, scenario.history, jointly_admitted)
            and shared_source.clause(0, 1, scenario.history, jointly_admitted)
            and compiled(0, 1, scenario.history, jointly_admitted)
        )

    conjunction_load_bearing = (
        source_conjunction_is_load_bearing(boundary_left, "L", "R")
        and source_conjunction_is_load_bearing(boundary_right, "R", "L")
    )
    checks.append(
        _check(
            "D2.2a-boundary-compilation",
            "B compiles source clauses by conjunction into the sole executable A",
            boundary_binding and conjunction_load_bearing,
            {
                "left_boundary": boundary_left.spec.declaration.boundary,
                "right_boundary": boundary_right.spec.declaration.boundary,
                "left_compiled_A": boundary_left.spec.admissibility.record,
                "right_compiled_A": boundary_right.spec.admissibility.record,
                "source_conjunction_load_bearing": conjunction_load_bearing,
            },
        )
    )
    forged_boundary_version = replace(
        boundary_left.spec.declaration.boundary,
        version="forged-version",
    )
    boundary_version_mismatch_rejected = _caught(
        SpecificationError,
        lambda: replace(
            boundary_left.spec.declaration,
            boundary=forged_boundary_version,
        ),
        "boundary version does not match declaration version",
    )
    mutations.append(
        MutationResult(
            "F11-boundary-version-mismatch",
            boundary_version_mismatch_rejected,
            "the declaration rejects a boundary from another version before A is used",
        )
    )
    unmasked_boundary_intervention = all(
        verdict.identity and all(verdict.viability)
        for scenario, reachable in (
            (boundary_left, boundary_left_reachable),
            (boundary_right, boundary_right_reachable),
        )
        for verdict in (
            engine.joint_verdict(scenario.spec, scenario.history, 0, 1, tail)
            for tail in reachable
        )
    )
    left_subject = next(
        source
        for source in boundary_left.spec.declaration.boundary.sources
        if source.role is BoundarySourceRole.SUBJECT
    )
    right_subject = next(
        source
        for source in boundary_right.spec.declaration.boundary.sources
        if source.role is BoundarySourceRole.SUBJECT
    )
    left_shared = next(
        source
        for source in boundary_left.spec.declaration.boundary.sources
        if source.role is BoundarySourceRole.SHARED
    )
    right_shared = next(
        source
        for source in boundary_right.spec.declaration.boundary.sources
        if source.role is BoundarySourceRole.SHARED
    )
    left_fibre = tuple(
        tail for tail in boundary_left_reachable if tail.first_action == "L"
    )
    right_fibre = tuple(
        tail for tail in boundary_right_reachable if tail.first_action == "R"
    )
    left_subject_region = tuple(
        tail
        for tail in boundary_left_reachable
        if left_subject.clause(0, 1, boundary_left.history, tail)
    )
    right_subject_region = tuple(
        tail
        for tail in boundary_right_reachable
        if right_subject.clause(0, 1, boundary_right.history, tail)
    )
    left_compiled_region = tuple(
        tail
        for tail in left_subject_region
        if left_shared.clause(0, 1, boundary_left.history, tail)
    )
    right_compiled_region = tuple(
        tail
        for tail in right_subject_region
        if right_shared.clause(0, 1, boundary_right.history, tail)
    )
    region_swap = (
        tuple(tail.digest for tail in boundary_left_reachable)
        == tuple(tail.digest for tail in boundary_right_reachable)
        and left_subject_region == left_fibre
        and right_subject_region == right_fibre
        and tuple(tail.digest for tail in boundary_left_reservoir.tails)
        == tuple(tail.digest for tail in left_compiled_region)
        and tuple(tail.digest for tail in boundary_right_reservoir.tails)
        == tuple(tail.digest for tail in right_compiled_region)
        and boundary_left_support == ("L",)
        and boundary_right_support == ("R",)
        and boundary_left_geometry.fibres != boundary_right_geometry.fibres
    )
    checks.append(
        _check(
            "P4.1a-T14-boundary-fibre",
            "an authorised B revision creates a different admissible region, which changes R, G(R) and existential support before execution",
            boundary_binding
            and conjunction_load_bearing
            and unmasked_boundary_intervention
            and region_swap,
            {
                "reachable_carrier": tuple(
                    tail.digest for tail in boundary_left_reachable
                ),
                "left_subject_region": tuple(
                    tail.digest for tail in left_subject_region
                ),
                "right_subject_region": tuple(
                    tail.digest for tail in right_subject_region
                ),
                "left_compiled_region": tuple(
                    tail.digest for tail in left_compiled_region
                ),
                "right_compiled_region": tuple(
                    tail.digest for tail in right_compiled_region
                ),
                "left_geometry": boundary_left_geometry.digest,
                "right_geometry": boundary_right_geometry.digest,
                "left_support": boundary_left_support,
                "right_support": boundary_right_support,
                "identity_and_viability_unmasked": unmasked_boundary_intervention,
            },
        )
    )
    checks.append(
        _check(
            "P6.2a-cardinality-collision",
            "equal reservoir cardinality does not determine G(R) or existential support",
            len(boundary_left_reservoir.tails)
            == len(boundary_right_reservoir.tails)
            == 1
            and boundary_left_geometry.fibres != boundary_right_geometry.fibres
            and boundary_left_support != boundary_right_support,
            {
                "left_cardinality": len(boundary_left_reservoir.tails),
                "right_cardinality": len(boundary_right_reservoir.tails),
                "left_geometry": boundary_left_geometry.fibres,
                "right_geometry": boundary_right_geometry.fibres,
                "left_support": boundary_left_support,
                "right_support": boundary_right_support,
            },
        )
    )
    hidden_left, hidden_right = hidden_lineage_scenarios()
    hidden_left_output = minerva.generate(hidden_left.observation, hidden_left.spec)
    hidden_right_output = minerva.generate(hidden_right.observation, hidden_right.spec)
    hidden_ledger = hidden_left.spec.viability.clause.ledger
    hidden_left_support = engine.existential_support(
        engine.geometry(hidden_left.spec, hidden_left.history, 0, 1)
    )
    hidden_right_support = engine.existential_support(
        engine.geometry(hidden_right.spec, hidden_right.history, 0, 1)
    )
    equal_ledger_different_identity = (
        hidden_left.history.current_state == hidden_right.history.current_state
        and hidden_left.spec.viability.clause.ledger
        == hidden_right.spec.viability.clause.ledger
        and hidden_ledger is not None
        and hidden_left_support != hidden_right_support
        and hidden_left_output.reservoir.digest != hidden_right_output.reservoir.digest
    )
    budget_low, budget_high = equal_identity_different_budget_scenarios()
    budget_low_output = minerva.generate(budget_low.observation, budget_low.spec)
    budget_high_output = minerva.generate(budget_high.observation, budget_high.spec)
    low_ledger = budget_low.spec.viability.clause.ledger
    high_ledger = budget_high.spec.viability.clause.ledger
    low_tails = {tail.digest for tail in budget_low_output.reservoir.tails}
    high_tails = {tail.digest for tail in budget_high_output.reservoir.tails}
    equal_identity_different_ledger = (
        budget_low.spec.declaration.identity == budget_high.spec.declaration.identity
        and low_ledger is not None
        and high_ledger is not None
        and low_ledger != high_ledger
        and low_ledger.tau_b != high_ledger.tau_b
        and high_tails < low_tails
        and bool(high_tails)
        and all(
            cert.verdict.identity
            for cert in budget_low_output.reservoir.certificates
            + budget_high_output.reservoir.certificates
        )
    )
    checks.append(
        _check(
            "P6.1-two-ledgers",
            "equal sealed ledgers need not fix identity and equal identity need not fix the ledger",
            equal_ledger_different_identity and equal_identity_different_ledger,
            {
                "same_ledger_countermodel": {
                    "visible_state": hidden_left.history.current_state,
                    "sealed_ledger": hidden_ledger,
                    "left_support": hidden_left_support,
                    "right_support": hidden_right_support,
                    "left_reservoir": hidden_left_output.reservoir.digest,
                    "right_reservoir": hidden_right_output.reservoir.digest,
                },
                "same_identity_countermodel": {
                    "low_ledger": low_ledger,
                    "high_ledger": high_ledger,
                    "low_tails": tuple(sorted(low_tails)),
                    "high_tails": tuple(sorted(high_tails)),
                    "tau_values": (low_ledger.tau_b, high_ledger.tau_b),
                },
            },
        )
    )

    budget = budget_geometry_comparison()
    current_reservoir = minerva.generate(
        budget.current.observation, budget.current.spec
    ).reservoir
    later_reservoir = minerva.generate(
        budget.later.observation, budget.later.spec
    ).reservoir
    current_actions = {tail.first_action for tail in current_reservoir.tails}
    later_actions = {tail.first_action for tail in later_reservoir.tails}
    checks.append(
        _check(
            "P6.2-nonmonotone-geometry",
            "reservoir geometry can expand while the sealed remaining budget decreases",
            budget.tau_later < budget.tau_current
            and budget.current.spec.viability.clause.ledger is not None
            and budget.later.spec.viability.clause.ledger is not None
            and budget.current.spec.viability.clause.ledger.tau_b == budget.tau_current
            and budget.later.spec.viability.clause.ledger.tau_b == budget.tau_later
            and not later_actions.issubset(current_actions),
            {
                "tau_current": budget.tau_current,
                "tau_later": budget.tau_later,
                "current_ledger": budget.current.spec.viability.clause.ledger,
                "later_ledger": budget.later.spec.viability.clause.ledger,
                "current_actions": tuple(sorted(current_actions)),
                "later_actions": tuple(sorted(later_actions)),
            },
        )
    )

    exhausted_clause = replace(
        budget.later.spec.viability.clause,
        clause_id="viability:budget-geometry-exhausted",
        ledger=WearLedger(
            phi_load=budget.later.spec.viability.clause.ledger.capacity,
            capacity=budget.later.spec.viability.clause.ledger.capacity,
            version="1",
            authority="budget-authority",
        ),
    )
    exhausted_spec = replace(
        budget.later.spec,
        spec_id="budget-geometry-exhausted",
        viability=viability_rule_from_clause(
            exhausted_clause,
            ground_refs=budget.later.spec.viability.record.ground_refs,
        ),
    )
    exhausted_reservoir = engine.reservoir(
        exhausted_spec, budget.later.history, 1, 1
    )
    mutations.append(
        MutationResult(
            "F7-budget-viability-coupling",
            bool(later_reservoir.tails) and not exhausted_reservoir.tails,
            "exhausting the sealed wear ledger empties the recomputed reservoir, "
            "so the budget genuinely flows through the viability factor",
        )
    )
    # Accumulation tooth: the sealed ledger must wear across recurrence updates,
    # not reset at every construction. The probe compares the charged successor
    # clause against the uncharged one on the same fixture, so neutering `charge`
    # (returning the clause unchanged) makes the two agree and turns this red.
    wear_scenario = wear_accumulation_scenario()
    wear_first = engine.reservoir(
        wear_scenario.spec, wear_scenario.history, 0, 1
    )
    realised_step = Tail((Step("step", "live"),))
    charged_clause = wear_scenario.spec.viability.clause.charge(realised_step)
    charged_spec = replace(
        wear_scenario.spec,
        spec_id="wear-accumulation:charged-successor",
        root_time=1,
        viability=viability_rule_from_clause(
            charged_clause,
            ground_refs=wear_scenario.spec.viability.record.ground_refs,
        ),
        validity=replace(
            wear_scenario.spec.validity, not_before=1, not_after=6
        ),
    )
    uncharged_spec = replace(
        wear_scenario.spec,
        spec_id="wear-accumulation:uncharged-successor",
        root_time=1,
        validity=replace(
            wear_scenario.spec.validity, not_before=1, not_after=6
        ),
    )
    successor_history = wear_scenario.history.append("step", "live")
    charged_reservoir = engine.reservoir(charged_spec, successor_history, 1, 1)
    uncharged_reservoir = engine.reservoir(uncharged_spec, successor_history, 1, 1)
    mutations.append(
        MutationResult(
            "F7-wear-accumulation",
            bool(wear_first.tails)
            and not charged_reservoir.tails
            and bool(uncharged_reservoir.tails),
            "the first step is admitted, charging its wear into the successor "
            "ledger empties the next reservoir, and skipping the charge would "
            "wrongly readmit it",
        )
    )

    existential_context = engine.assurance_context(
        AssuranceMode.EXISTENTIAL, robust.spec, robust.history, 0, 2,
        runtime_regime="fixture",
    )
    adaptive_context = engine.assurance_context(
        AssuranceMode.ADAPTIVE_ROBUST, robust.spec, robust.history, 0, 2,
        runtime_regime="fixture",
    )
    checks.append(
        _check(
            "Val-assurance-context",
            "assurance evidence binds the validity envelope and checked runtime regime",
            existential_context.validity == robust.spec.validity
            and adaptive_context.validity == robust.spec.validity
            and existential_context.runtime_regime == robust.spec.validity.regime
            and adaptive_context.runtime_regime == robust.spec.validity.regime,
            {
                "validity": robust.spec.validity,
                "runtime_regime": adaptive_context.runtime_regime,
            },
        )
    )
    selector = TaskSelector()
    choice_a = selector.select(existential_context, {"a": 2.0, "b": 1.0})
    choice_b = selector.select(existential_context, {"a": 1.0, "b": 2.0})
    checks.append(
        _check(
            "P4.2-T5",
            "task goals can change selection without changing the reservoir",
            choice_a == "a" and choice_b == "b",
            {
                "choice_goal_a": choice_a,
                "choice_goal_b": choice_b,
                "reservoir": robust_output.reservoir.digest,
            },
        )
    )

    authority = TokenAuthority(
        "fixture-enforcer",
        b"ncnc-fixture-secret-material-32bytes!!",
        engine=engine,
    )
    empty_policy = EmptySupportPolicy(
        "empty-support-safe-mode",
        "1",
        "safety-authority",
        EmptyDisposition.SAFE_MODE,
        "no active assurance support",
    )
    enforcer = Enforcer(authority, empty_policy)
    action = selector.select(adaptive_context, {"b": 1.0})
    token = authority.issue(
        adaptive_context,
        action,
        issued_at=0,
        expires_at=2,
        decision_version="G_enf-v1",
    )
    admit = enforcer.decide(adaptive_context, action, token, now=0, runtime_regime="fixture")
    reject = enforcer.decide(adaptive_context, action, None, now=0, runtime_regime="fixture")
    executor = MediatedExecutor(authority)
    admitted_trace = executor.attempt(
        robust.spec,
        robust.history,
        action,
        "shock",
        "robust1",
        admit,
        time=0,
        runtime_regime="fixture",
    )
    blocked_trace = executor.attempt(
        robust.spec,
        robust.history,
        action,
        "shock",
        "robust1",
        reject,
        time=0,
        runtime_regime="fixture",
    )
    trace_ledger = TraceLedger().append(blocked_trace).append(admitted_trace)
    trace_ledger.verify()
    checks.append(
        _check(
            "P5.4-T4",
            "matched enforcement-verdict intervention changes realised execution",
            admit.verdict is EnforcementVerdict.ADMIT
            and reject.verdict is EnforcementVerdict.REJECT
            and causal_intervention_witness(admitted_trace, blocked_trace),
            {
                "admitted_trace": admitted_trace,
                "blocked_trace": blocked_trace,
                "authenticated_trace_ledger": trace_ledger,
            },
        )
    )

    recurrence_provenance = HistoryFutureRecurrence.provenance_token(
        robust_output.seal.seal_commitment, admitted_trace.digest
    )
    next_spec, next_observation = recurrence_update_inputs(
        robust, admitted_trace.post_history, recurrence_provenance
    )
    recurrence_record, next_output = HistoryFutureRecurrence.advance(
        engine,
        robust.spec,
        robust_output,
        robust.observation,
        adaptive_context,
        admit,
        authority,
        admitted_trace,
        next_spec,
        next_observation,
        next_runtime_regime="fixture",
    )
    checks.append(
        _check(
            "D8.6-P8.7-T12",
            "history-generated recurrence binds support evidence, authenticated decision, "
            "pre-action seal, exact append, successor interpretation, provenance and seal",
            recurrence_record.prior_seal_commitment
            == robust_output.seal.seal_commitment
            and recurrence_record.assurance_context_commitment
            == adaptive_context.digest
            and recurrence_record.enforcement_decision_commitment == admit.digest
            and recurrence_record.execution_trace_commitment == admitted_trace.digest
            and recurrence_record.prior_generator_input_commitment
            == robust_output.generator_input_commitment
            and recurrence_record.next_generator_input_commitment
            == next_output.generator_input_commitment
            and next_output.history == admitted_trace.post_history
            and recurrence_record.provenance_link in next_spec.provenance
            and recurrence_record.next_seal_commitment
            == next_output.seal.seal_commitment,
            {
                "recurrence": recurrence_record,
                "prior_history": robust_output.history,
                "post_history": admitted_trace.post_history,
                "next_reservoir": next_output.reservoir.digest,
            },
        )
    )

    empty = empty_active_support_scenario()
    empty_output = minerva.generate(empty.observation, empty.spec)
    empty_context = engine.assurance_context(
        AssuranceMode.ADAPTIVE_ROBUST, empty.spec, empty.history, 0, 1,
        runtime_regime="fixture",
    )
    empty_decision = enforcer.decide(empty_context, None, None, now=0, runtime_regime="fixture")
    empty_r = empty_reservoir_scenario()
    empty_r_output = minerva.generate(empty_r.observation, empty_r.spec)
    empty_r_context = engine.assurance_context(
        AssuranceMode.EXISTENTIAL, empty_r.spec, empty_r.history, 0, 1,
        runtime_regime="fixture",
    )
    empty_r_decision = enforcer.decide(
        empty_r_context, None, None, now=0, runtime_regime="fixture"
    )
    checks.append(
        _check(
            "F13-T10-active-support",
            "empty active support invokes sealed safe semantics for empty R and non-empty R",
            bool(empty_output.reservoir.tails)
            and not empty_context.actions
            and _caught(
                EmptySupportError,
                lambda: selector.select(empty_context, {}),
                "selector is partial: empty active support must use its sealed handler",
            )
            and empty_decision.verdict is EnforcementVerdict.SAFE_MODE
            and not empty_r_output.reservoir.tails
            and not empty_r_context.actions
            and _caught(
                EmptySupportError,
                lambda: selector.select(empty_r_context, {}),
                "selector is partial: empty active support must use its sealed handler",
            )
            and empty_r_decision.verdict is EnforcementVerdict.SAFE_MODE,
            {
                "nonempty_r_empty_support": {
                    "reservoir_size": len(empty_output.reservoir.tails),
                    "active_support": empty_context.actions,
                    "handler": empty_decision.verdict,
                },
                "empty_r": {
                    "reservoir_size": len(empty_r_output.reservoir.tails),
                    "active_support": empty_r_context.actions,
                    "handler": empty_r_decision.verdict,
                },
                "handler_commitment": empty_policy.digest,
            },
        )
    )

    channel_cases = non_absorption_cases()
    collisions = find_fibre_collisions(channel_cases)
    checks.append(
        _check(
            "T5.3-T6",
            "complete declared optimizer channel contains a target-changing fibre",
            len(collisions) == 1 and exact_factorisation_map(channel_cases) is None,
            {"collisions": collisions},
        )
    )

    hypotheses = boundary_hypotheses()
    actual = next(item for item in hypotheses if item.name == "B05")
    bounded_attack = GreedyVersionSpaceAttack().run(
        hypotheses, MembershipOracle(actual, budget=2)
    )
    full_attack = GreedyVersionSpaceAttack().run(
        hypotheses, MembershipOracle(actual, budget=4)
    )
    leakage_policy = LeakagePolicy(maximum_queries=2, maximum_bits=2.0)
    checks.append(
        _check(
            "T7-query-budget",
            "bounded query access leaves more than one boundary hypothesis",
            leakage_policy.accepts(bounded_attack)
            and not bounded_attack.exact_reconstruction
            and full_attack.exact_reconstruction,
            {"bounded": bounded_attack, "unbounded_fixture": full_attack},
        )
    )

    bad_observation = replace(
        robust.observation, attributes=(("history_key", "unknown"),)
    )
    checks.append(
        _check(
            "Minerva-interpreter",
            "observation-to-history interpretation is explicit and fails on ambiguity",
            _caught(
                InterpretationError,
                lambda: minerva.generate(bad_observation, robust.spec),
                "interpreter rejected observation",
            ),
            {"interpreter": robust.spec.interpreter.record},
        )
    )

    # Integrity and mutation teeth.
    geometry_tamper_snapshot = replace(
        robust_output.reservoir,
        tails=robust_output.reservoir.tails[:-1],
    )
    tampered_geometry = replace(
        engine.geometry_from_snapshot(geometry_tamper_snapshot),
        reservoir_commitment=robust_output.reservoir.digest,
    )
    mutations.append(
        MutationResult(
            "F16-geometry-fibre-tamper",
            _caught(
                CertificateIntegrityError,
                lambda: engine.assert_geometry(
                    robust_output.reservoir, tampered_geometry
                ),
                "geometry fibres do not match the exact snapshot prefix fibres",
            ),
            "a self-consistent but truncated prefix-fibre family cannot be rebound to the sealed reservoir",
        )
    )
    forged_append_trace = replace(admitted_trace, post_history=robust.history)
    mutations.append(
        MutationResult(
            "F17-history-append",
            _caught(
                RecurrenceError,
                lambda: HistoryFutureRecurrence.create(
                    engine,
                    robust.spec,
                    robust_output,
                    robust.observation,
                    adaptive_context,
                    admit,
                    authority,
                    forged_append_trace,
                    next_spec,
                    next_output,
                    next_observation,
                    next_runtime_regime="fixture",
                ),
                "recurrence post-history is not the exact append",
            ),
            "the recurrence independently reconstructs the exact immutable append",
        )
    )
    wide_context = existential_context
    wide_token = authority.issue(
        wide_context,
        "b",
        issued_at=0,
        expires_at=2,
        decision_version="G_enf-v1",
    )
    wide_admit = enforcer.decide(
        wide_context, "b", wide_token, now=0, runtime_regime="fixture"
    )
    wide_trace = MediatedExecutor(authority).attempt(
        robust.spec,
        robust.history,
        "b",
        "shock",
        "robust1",
        wide_admit,
        time=0,
        runtime_regime="fixture",
    )
    substituted_action_trace = replace(
        wide_trace,
        action="a",
        post_history=wide_trace.pre_history.append("a", wide_trace.successor),
    )
    mutations.append(
        MutationResult(
            "F17-action-substitution",
            _caught(
                RecurrenceError,
                lambda: HistoryFutureRecurrence.create(
                    engine,
                    robust.spec,
                    robust_output,
                    robust.observation,
                    wide_context,
                    wide_admit,
                    authority,
                    substituted_action_trace,
                    next_spec,
                    next_output,
                    next_observation,
                    next_runtime_regime="fixture",
                ),
                "recurrence enforcement decision does not bind the admitted step",
            ),
            "the realised event must carry the exact action bound by the authenticated decision",
        )
    )
    missing_provenance_spec = replace(
        next_spec,
        provenance=tuple(
            item for item in next_spec.provenance if item != recurrence_provenance
        ),
    )
    mutations.append(
        MutationResult(
            "F17-successor-provenance",
            _caught(
                RecurrenceError,
                lambda: HistoryFutureRecurrence.advance(
                    engine,
                    robust.spec,
                    robust_output,
                    robust.observation,
                    adaptive_context,
                    admit,
                    authority,
                    admitted_trace,
                    missing_provenance_spec,
                    next_observation,
                    next_runtime_regime="fixture",
                ),
                "recurrence provenance link is absent from the next specification",
            ),
            "the successor specification must bind the prior seal and executed trace",
        )
    )
    forged_recurrence_decision = replace(admit, authorization_tag="00" * 32)
    mutations.append(
        MutationResult(
            "F17-decision-authentication",
            _caught(
                RecurrenceError,
                lambda: recurrence_record.verify(
                    engine,
                    robust.spec,
                    robust_output,
                    robust.observation,
                    adaptive_context,
                    forged_recurrence_decision,
                    authority,
                    admitted_trace,
                    next_spec,
                    next_output,
                    next_observation,
                    next_runtime_regime="fixture",
                ),
                "recurrence enforcement decision authentication mismatch",
            ),
            "the recurrence authenticates its ADMIT decision independently of trace fields",
        )
    )
    detached_next_output = replace(next_output, history=robust.history)
    mutations.append(
        MutationResult(
            "F17-successor-history",
            _caught(
                RecurrenceError,
                lambda: recurrence_record.verify(
                    engine,
                    robust.spec,
                    robust_output,
                    robust.observation,
                    adaptive_context,
                    admit,
                    authority,
                    admitted_trace,
                    next_spec,
                    detached_next_output,
                    next_observation,
                    next_runtime_regime="fixture",
                ),
                "recurrence next output is detached from its seal",
            ),
            "the next interpreted history remains attached to its successor seal",
        )
    )
    mutations.append(
        MutationResult(
            "F17-prior-observation",
            _caught(
                RecurrenceError,
                lambda: recurrence_record.verify(
                    engine,
                    robust.spec,
                    robust_output,
                    replace(robust.observation, observation_id="wrong-prior"),
                    adaptive_context,
                    admit,
                    authority,
                    admitted_trace,
                    next_spec,
                    next_output,
                    next_observation,
                    next_runtime_regime="fixture",
                ),
                "recurrence prior observation/seal mismatch",
            ),
            "the recurrence starts from the concrete pre-action observation preimage",
        )
    )
    contaminated_next_output = replace(
        next_output, generator_input_commitment=commitment("undeclared-future-oracle")
    )
    mutations.append(
        MutationResult(
            "F17-generator-input",
            _caught(
                RecurrenceError,
                lambda: recurrence_record.verify(
                    engine,
                    robust.spec,
                    robust_output,
                    robust.observation,
                    adaptive_context,
                    admit,
                    authority,
                    admitted_trace,
                    next_spec,
                    contaminated_next_output,
                    next_observation,
                    next_runtime_regime="fixture",
                ),
                "recurrence next generator input commitment mismatch",
            ),
            "the certified generator interface rejects an uncommitted logical input",
        )
    )
    mutations.append(
        MutationResult(
            "F17-link-commitment",
            _caught(
                RecurrenceError,
                lambda: replace(
                    recurrence_record, link_commitment="00" * 32
                ).verify(
                    engine,
                    robust.spec,
                    robust_output,
                    robust.observation,
                    adaptive_context,
                    admit,
                    authority,
                    admitted_trace,
                    next_spec,
                    next_output,
                    next_observation,
                    next_runtime_regime="fixture",
                ),
                "recurrence link commitment mismatch",
            ),
            "one commitment binds every recurrence field",
        )
    )
    tampered_snapshot = replace(
        origin_seal.snapshot, tails=origin_seal.snapshot.tails[:-1]
    )
    tampered_seal = replace(origin_seal, snapshot=tampered_snapshot)
    mutations.append(
        MutationResult(
            "F1-retrospective-reservoir",
            _caught(
                SealIntegrityError, tampered_seal.verify,
                "reservoir snapshot no longer matches the seal",
            ),
            "origin reservoir commitment mismatch",
        )
    )
    tampered_certificate = replace(
        origin_seal.snapshot.certificates[0],
        verdict=replace(origin_seal.snapshot.certificates[0].verdict, identity=False),
    )
    tampered_cert_snapshot = replace(
        origin_seal.snapshot,
        certificates=(tampered_certificate,) + origin_seal.snapshot.certificates[1:],
    )
    tampered_cert_seal = replace(origin_seal, snapshot=tampered_cert_snapshot)
    mutations.append(
        MutationResult(
            "F16-certificate-verdict",
            _caught(
                SealIntegrityError, tampered_cert_seal.verify,
                "reservoir snapshot no longer matches the seal",
            ),
            "certificate bundle changes the sealed reservoir commitment",
        )
    )
    bad_signature_token = replace(token, signature="00" * 32)
    bad_signature_decision = enforcer.decide(
        adaptive_context, action, bad_signature_token, now=0,
        runtime_regime="fixture",
    )
    mutations.append(
        MutationResult(
            "F16-token-signature",
            bad_signature_decision.verdict is EnforcementVerdict.REJECT,
            bad_signature_decision.reason,
        )
    )
    token_for_a = authority.issue(
        existential_context,
        "a",
        issued_at=0,
        expires_at=2,
        decision_version="G_enf-v1",
    )
    changed_action_decision = Enforcer(authority, empty_policy).decide(
        existential_context, "b", token_for_a, now=0,
        runtime_regime="fixture",
    )
    mutations.append(
        MutationResult(
            "F16-token-action-binding",
            changed_action_decision.verdict is EnforcementVerdict.REJECT,
            changed_action_decision.reason,
        )
    )
    cross_mode_token = authority.issue(
        adaptive_context,
        action,
        issued_at=1,
        expires_at=2,
        decision_version="G_enf-v1",
    )
    cross_mode_decision = Enforcer(authority, empty_policy).decide(
        existential_context,
        action,
        cross_mode_token,
        now=1,
        runtime_regime="fixture",
    )
    mutations.append(
        MutationResult(
            "F16-cross-mode-token-reuse",
            cross_mode_decision.verdict is EnforcementVerdict.REJECT,
            cross_mode_decision.reason,
        )
    )
    expired_decision = Enforcer(authority, empty_policy).decide(
        adaptive_context,
        action,
        cross_mode_token,
        now=3,
        runtime_regime="fixture",
    )
    mutations.append(
        MutationResult(
            "F16-expired-token",
            expired_decision.verdict is EnforcementVerdict.REJECT,
            expired_decision.reason,
        )
    )
    regime_changed_decision = Enforcer(authority, empty_policy).decide(
        adaptive_context,
        action,
        token,
        now=0,
        runtime_regime="changed-regime",
    )
    mutations.append(
        MutationResult(
            "F16-runtime-regime-mismatch",
            regime_changed_decision.verdict is EnforcementVerdict.REJECT,
            regime_changed_decision.reason,
        )
    )
    validity_expired_decision = Enforcer(authority, empty_policy).decide(
        adaptive_context,
        action,
        token,
        now=robust.spec.validity.not_after + 1,
        runtime_regime=robust.spec.validity.regime,
    )
    mutations.append(
        MutationResult(
            "F16-validity-expiry",
            validity_expired_decision.verdict is EnforcementVerdict.REJECT,
            validity_expired_decision.reason,
        )
    )
    handcrafted_context = replace(
        existential_context,
        actions=existential_context.actions + ("c",),
        action_tail_witnesses=existential_context.action_tail_witnesses
        + (("c", ("00" * 32,)),),
    )
    mutations.append(
        MutationResult(
            "F10-handcrafted-assurance",
            _caught(
                TokenError,
                lambda: authority.issue(
                    handcrafted_context,
                    "c",
                    issued_at=0,
                    expires_at=2,
                    decision_version="G_enf-v1",
                ),
                "assurance context does not recompute from the engine",
            ),
            "a self-consistent but hand-built assurance context is refused a token "
            "because the anchored engine cannot reproduce it",
        )
    )
    # A field-versus-field geometry comparison is an alias check: both sides come
    # from the presented object, so a forger who rewrites them together passes it.
    # The probe therefore forges a SELF-CONSISTENT wrong geometry — support and
    # context agree with each other — so only engine recomputation can refuse it.
    # A geometry object validates its own fibre family, so the forgery uses a
    # geometry that is internally valid but belongs to a different reservoir.
    foreign_geometry = terminal_geometry
    forged_geometry_context = replace(
        adaptive_context,
        current_geometry_commitment=foreign_geometry.digest,
        support=replace(
            adaptive_context.support, current_geometry=foreign_geometry.digest
        ),
    )
    mutations.append(
        MutationResult(
            "F10-forged-self-consistent-geometry",
            _caught(
                TokenError,
                lambda: authority.issue(
                    forged_geometry_context,
                    action,
                    issued_at=0,
                    expires_at=2,
                    decision_version="G_enf-v1",
                ),
                "assurance context does not recompute from the engine",
            ),
            "an assurance context whose geometry evidence is internally consistent "
            "but does not belong to the engine's reservoir is refused by "
            "recomputation, not by comparing two fields of the same payload",
        )
    )
    unregistered_spec_context = replace(
        existential_context, spec_commitment="ff" * 32
    )
    mutations.append(
        MutationResult(
            "F10-unregistered-spec",
            _caught(
                TokenError,
                lambda: authority.issue(
                    unregistered_spec_context,
                    "b",
                    issued_at=0,
                    expires_at=2,
                    decision_version="G_enf-v1",
                ),
                "assurance specification is not registered with the engine",
            ),
            "an assurance context naming a specification the engine never processed "
            "fails closed at issuance",
        )
    )
    mutations.append(
        MutationResult(
            "F8-unsealed-prefix-support",
            _caught(
                SealIntegrityError,
                lambda: engine.seal_relative_support(
                    origin_seal, Tail((Step("a", "bad1"),))
                ),
                "realised prefix is outside the sealed reservoir",
            ),
            "a realised prefix that is reachable but was never admitted into the "
            "original seal cannot be given seal-relative support at all",
        )
    )
    tiny_oracle = MembershipOracle(actual, budget=1)
    tiny_oracle.query("p0")
    mutations.append(
        MutationResult(
            "F6-query-budget-overrun",
            _caught(
                QueryBudgetExceeded, lambda: tiny_oracle.query("p1"),
                "sealed membership-query budget exhausted",
            ),
            "q+1 query is rejected",
        )
    )
    mutations.append(
        MutationResult(
            "F10-verdict-field-forgery",
            _caught(
                ExecutionError,
                lambda: MediatedExecutor(authority).attempt(
                    robust.spec,
                    robust.history,
                    action,
                    "shock",
                    "robust1",
                    replace(reject, verdict=EnforcementVerdict.ADMIT),
                    time=0,
                    runtime_regime="fixture",
                ),
                "enforcement-decision authentication mismatch",
            ),
            "flipping only the verdict field of an authenticated REJECT does not "
            "produce an executable ADMIT: the tag covers the verdict",
        )
    )
    forged_admit = replace(admit, authorization_tag="00" * 32)
    mutations.append(
        MutationResult(
            "F10-forged-admit-decision",
            _caught(
                ExecutionError,
                lambda: MediatedExecutor(authority).attempt(
                    robust.spec,
                    robust.history,
                    action,
                    "shock",
                    "robust1",
                    forged_admit,
                    time=0,
                    runtime_regime="fixture",
                ),
                "enforcement-decision authentication mismatch",
            ),
            "executor authenticates the enforcer decision, not only its verdict field",
        )
    )
    mutations.append(
        MutationResult(
            "F10-decision-replay",
            _caught(
                ExecutionError,
                lambda: MediatedExecutor(authority).attempt(
                    robust.spec,
                    robust.history,
                    action,
                    "shock",
                    "robust1",
                    admit,
                    time=0,
                    runtime_regime="fixture",
                ),
                "enforcement-decision replay detected",
            ),
            "authority-scoped replay state makes ADMIT one-shot across executors",
        )
    )
    mutations.append(
        MutationResult(
            "F10-reject-decision-replay",
            _caught(
                ExecutionError,
                lambda: MediatedExecutor(authority).attempt(
                    robust.spec,
                    robust.history,
                    action,
                    "shock",
                    "robust1",
                    reject,
                    time=0,
                    runtime_regime="fixture",
                ),
                "enforcement-decision replay detected",
            ),
            "authenticated non-ADMIT decisions are one-shot across executors",
        )
    )
    tampered_entry = replace(trace_ledger.entries[0], entry_commitment="00" * 32)
    tampered_ledger = replace(
        trace_ledger,
        entries=(tampered_entry,) + trace_ledger.entries[1:],
    )
    mutations.append(
        MutationResult(
            "F10-trace-lineage-mutation",
            _caught(
                ExecutionError, tampered_ledger.verify,
                "execution-trace chain commitment mismatch",
            ),
            "append-only trace lineage binds order, history continuity and trace bytes",
        )
    )
    mutations.append(
        MutationResult(
            "F16-certificate-recomputation",
            _caught(
                CertificateIntegrityError,
                lambda: engine.assert_snapshot(robust.spec, tampered_cert_snapshot),
                "all certificates",
            ),
            "certificate verifier recomputes sources, grounds, witnesses and verdict",
        )
    )
    unattested_history = History("forged-root")
    mutations.append(
        MutationResult(
            "F16-unattested-history-seal",
            _caught(
                SealIntegrityError,
                lambda: engine.create_seal(
                    robust.spec, unattested_history, robust.observation
                ),
                "root history is not the unique interpretation of the sealed observation",
            ),
            "seal create rejects history that is not Int(observation)",
        )
    )
    mutations.append(
        MutationResult(
            "F16-observation-preimage-check",
            _caught(
                SealIntegrityError,
                lambda: origin_seal.verify_observation(
                    replace(robust.observation, attributes=(("history_key", "unknown"),))
                ),
                "observation does not match the sealed observation commitment",
            ),
            "observation preimage must match the sealed observation commitment",
        )
    )
    # The seal is a commitment without a secret, so a full recompute is inside an
    # adversary's reach: rewrite the root history, then rebuild every binding that
    # depends on it. `verify` accepts the result — every equality it tests is one the
    # adversary satisfied by construction. Only `verify_observation` separates the two,
    # because the observation preimage is not the adversary's to choose. Pinned here so
    # the boundary is demonstrated rather than assumed, and so a future change that
    # silently narrows it turns this probe red.
    forged_history = History("attacker-chosen-root")
    forged_snapshot = replace(origin_seal.snapshot, history=forged_history)
    recomputed_forgery = replace(
        origin_seal,
        root_history=forged_history,
        snapshot=forged_snapshot,
        reservoir_commitment=forged_snapshot.digest,
        history_attribution=type(origin_seal)._attribution(
            origin_seal.observation_commitment,
            origin_seal.interpreter_commitment,
            forged_history,
        ),
    )
    recomputed_forgery = replace(
        recomputed_forgery,
        seal_commitment=commitment(
            {
                "origin_time": recomputed_forgery.origin_time,
                "horizon": recomputed_forgery.horizon,
                "root_history": recomputed_forgery.root_history,
                "observation_commitment": recomputed_forgery.observation_commitment,
                "interpreter_commitment": recomputed_forgery.interpreter_commitment,
                "history_attribution": recomputed_forgery.history_attribution,
                "reservoir_commitment": recomputed_forgery.reservoir_commitment,
                "spec_commitment": recomputed_forgery.spec_commitment,
                "provenance": recomputed_forgery.provenance,
                "scheme": recomputed_forgery.scheme,
            }
        ),
    )
    try:
        recomputed_forgery.verify()
        forgery_survives_verify = True
    except SealIntegrityError:
        forgery_survives_verify = False
    forgery_caught_by_preimage = _caught(
        SealIntegrityError,
        lambda: recomputed_forgery.verify_observation(robust.observation),
        "root history is not the unique interpretation of the supplied observation",
    )
    mutations.append(
        MutationResult(
            "F16-recomputed-seal-forgery",
            forgery_survives_verify and forgery_caught_by_preimage,
            "commitment consistency alone admits a fully recomputed seal; only the "
            "observation preimage separates it from the authentic one",
        )
    )

    drifted_interpreter = replace(
        robust.spec.interpreter,
        evaluator=lambda observation: History("drifted-root"),
    )
    drifted_spec = replace(robust.spec, interpreter=drifted_interpreter)
    drifted_seal = replace(origin_seal, spec=drifted_spec)
    try:
        drifted_seal.verify_observation(robust.observation)
        interpretation_drift_detected = False
        interpretation_drift_mechanism = "drifted evaluator escaped re-interpretation"
    except SealIntegrityError as exc:
        interpretation_drift_detected = (
            str(exc)
            == "root history is not the unique interpretation of the supplied observation"
        )
        interpretation_drift_mechanism = str(exc)
    mutations.append(
        MutationResult(
            "F16-interpretation-drift-check",
            interpretation_drift_detected,
            interpretation_drift_mechanism,
        )
    )

    checks.extend(
        (
            CheckResult(
                "scope-physical-retrocausality",
                Status.NOT_MACHINE_DECIDABLE,
                "absence of physical retrocausality beyond the declared finite dataflow",
                "requires external physical evidence",
            ),
            CheckResult(
                "scope-personal-identity",
                Status.NOT_MACHINE_DECIDABLE,
                "adequacy of the declared predicate as real personal identity",
                "requires constitutive and empirical evidence",
            ),
            CheckResult(
                "scope-consciousness-liveness",
                Status.NOT_MACHINE_DECIDABLE,
                "consciousness, life or IIC cycle reinitiation",
                "reservoir non-emptiness is intentionally not such a witness",
            ),
            CheckResult(
                "scope-host-nonbypassability",
                Status.NOT_MACHINE_DECIDABLE,
                "host-level non-bypassability outside the declared Python API",
                "requires OS capability and deployment-topology evidence",
            ),
            CheckResult(
                "scope-interpreter-evaluator-faithfulness",
                Status.NOT_MACHINE_DECIDABLE,
                "faithfulness of the live interpreter evaluator to its committed record",
                "commitments bind the interpreter record, not runtime evaluator behaviour",
            ),
        )
    )

    return ReferenceReport(
        schema="ncnc-reference-report-v6",
        checks=tuple(checks),
        mutations=tuple(mutations),
        limitations=(
            "finite exhaustive fixtures only",
            "HMAC demonstrates shared-secret integrity, not public non-repudiation",
            "declared commitments exclude uncommitted logical inputs, not hidden physical side channels",
            "algorithmic cost is exponential in horizon and branching in the worst case",
            "no claim of embodied or production instantiation",
        ),
    )


def render_text(report: ReferenceReport) -> str:
    lines = [
        "NCNC finite reference verification",
        f"schema: {report.schema}",
        f"successful: {str(report.successful).lower()}",
        f"report_sha256: {report.digest}",
        "",
        "Checks:",
    ]
    for item in report.checks:
        lines.append(f"- {item.check_id}: {item.status.value}")
    lines.extend(("", "Mutation teeth:"))
    for item in report.mutations:
        state = "DETECTED" if item.detected else "SURVIVED"
        lines.append(f"- {item.mutation_id}: {state}")
    lines.extend(("", "Limitations:"))
    lines.extend(f"- {item}" for item in report.limitations)
    return "\n".join(lines) + "\n"


def render_json(report: ReferenceReport, *, pretty: bool = True) -> str:
    data_json = canonical_json(
        {**report.canonical_data(), "report_sha256": report.digest}
    )
    if not pretty:
        return data_json + "\n"
    import json

    return (
        json.dumps(
            json.loads(data_json),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )


__all__ = [
    "CheckResult",
    "MutationResult",
    "ReferenceReport",
    "Status",
    "render_json",
    "render_text",
    "run_reference_verification",
]
