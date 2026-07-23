"""Deterministic finite fixtures exercising the paper's load-bearing distinctions."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping

from .access import BoundaryHypothesis, ChannelCase
from .core import (
    AdmissibilityCase,
    AdmissibilityClause,
    BoundarySource,
    BoundarySourceRole,
    ConstructionSpec,
    ConstitutiveBoundary,
    Declaration,
    FiniteDynamics,
    History,
    IdentityCase,
    IdentityClause,
    IdentityRule,
    PrivateObservation,
    ReservoirEngine,
    RuleRecord,
    Step,
    Tail,
    ValidityEnvelope,
    VersionedInterpreter,
    ViabilityClause,
    ViabilityRule,
    WearLedger,
    WitnessRecord,
    commitment,
    identity_rule_from_clause,
    viability_rule_from_clause,
)


@dataclass(frozen=True, slots=True)
class Scenario:
    name: str
    description: str
    spec: ConstructionSpec
    observation: PrivateObservation
    history: History


@dataclass(frozen=True, slots=True)
class DivergenceScenario:
    scenario: Scenario
    realised_prefix: Tail
    expected_adaptive: tuple[str, ...]
    expected_seal_relative: tuple[str, ...]


def _record(
    rule_id: str,
    *,
    authority: str = "fixture-authority",
    version: str = "1",
    ground_refs: tuple[str, ...] = ("fixture-ground-v1",),
    implementation_material: Any | None = None,
) -> RuleRecord:
    material = rule_id if implementation_material is None else implementation_material
    return RuleRecord(
        rule_id=rule_id,
        version=version,
        authority=authority,
        implementation_digest=commitment(material),
        ground_refs=ground_refs,
    )


def _interpreter(
    histories: Mapping[str, History], *, name: str
) -> VersionedInterpreter:
    frozen = tuple(sorted((key, value) for key, value in histories.items()))
    frozen_histories = dict(frozen)

    def interpret(observation: PrivateObservation) -> History:
        key = observation.get("history_key")
        if key is None or key not in frozen_histories:
            raise ValueError("unknown or ambiguous history key")
        return frozen_histories[key]

    return VersionedInterpreter(
        _record(
            f"interpreter:{name}",
            authority="observation-authority",
            implementation_material=frozen,
        ),
        interpret,
    )


FIXTURE_GROUND = ("fixture-ground-v1",)


def _identity_clause(
    clause_id: str,
    *,
    cases: tuple[IdentityCase, ...] = (),
    default_allow: bool = True,
    authority: str = "personal-authority",
    version: str = "1",
) -> IdentityClause:
    return IdentityClause(clause_id, version, authority, cases, default_allow)


def _identity_rule(clause: IdentityClause) -> IdentityRule:
    return identity_rule_from_clause(clause, ground_refs=FIXTURE_GROUND)


def _always_identity(name: str = "identity:always") -> IdentityRule:
    return _identity_rule(_identity_clause(name))


def _viability_clause(
    clause_id: str,
    *,
    forbidden_states: tuple[str, ...] = (),
    state_costs: tuple[tuple[str, int], ...] = (),
    step_cost: int = 0,
    ledger: WearLedger | None = None,
    authority: str = "fixture-authority",
    version: str = "1",
) -> ViabilityClause:
    return ViabilityClause(
        clause_id,
        version,
        authority,
        forbidden_states=forbidden_states,
        state_costs=state_costs,
        step_cost=step_cost,
        ledger=ledger,
    )


def _viability_rule(clause: ViabilityClause) -> ViabilityRule:
    return viability_rule_from_clause(clause, ground_refs=FIXTURE_GROUND)


def _wear_ledger(*, phi_load: int, capacity: int) -> WearLedger:
    return WearLedger(
        phi_load=phi_load,
        capacity=capacity,
        version="1",
        authority="budget-authority",
    )


def _boundary_source(
    *,
    source_id: str,
    role: BoundarySourceRole,
    authority: str,
    version: str,
    cases: tuple[AdmissibilityCase, ...] = (),
    default_allow: bool = True,
) -> BoundarySource:
    return BoundarySource(
        source_id=source_id,
        role=role,
        authority=authority,
        version=version,
        clause=AdmissibilityClause(
            source_id, version, authority, cases, default_allow
        ),
    )


def _always_viable(name: str = "viability:always") -> ViabilityRule:
    return _viability_rule(_viability_clause(name))


def _make_spec(
    *,
    spec_id: str,
    horizon: int,
    dynamics: FiniteDynamics,
    histories: Mapping[str, History],
    identity: IdentityRule | None = None,
    boundary_sources: tuple[BoundarySource, ...] | None = None,
    boundary_version: str = "1",
    viability: ViabilityRule | None = None,
    root_time: int = 0,
) -> ConstructionSpec:
    chosen_identity = identity or _always_identity(f"identity:{spec_id}")
    sources = boundary_sources or (
        _boundary_source(
            source_id=f"source:{spec_id}:subject",
            role=BoundarySourceRole.SUBJECT,
            authority="personal-authority",
            version=boundary_version,
        ),
    )
    boundary = ConstitutiveBoundary(
        subject_id="subject-u",
        sources=sources,
        composition_relation="source-separated-conjunction",
        version=boundary_version,
    )
    declaration = Declaration(
        subject_id="subject-u",
        identity=chosen_identity,
        witness=WitnessRecord(
            carrier_id=f"witness:{spec_id}",
            equivalence_class="declared-trajectory-class",
            version="1",
            authority="personal-authority",
        ),
        boundary=boundary,
        declaration_authority="personal-authority",
        revision_relation="authorised-version-successor",
        interpretation_convention="fixture-history-semantics-v1",
        version=boundary_version,
    )
    return ConstructionSpec(
        spec_id=spec_id,
        root_time=root_time,
        horizon=horizon,
        declaration=declaration,
        viability=viability or _always_viable(f"viability:{spec_id}"),
        dynamics=dynamics,
        interpreter=_interpreter(histories, name=spec_id),
        model_id=f"finite-model:{spec_id}",
        model_version="1",
        provenance=("fixture-source", f"scenario:{spec_id}"),
        validity=ValidityEnvelope(root_time, root_time + horizon + 5, "fixture", "1"),
    )



def _observation(name: str, time: int, history_key: str) -> PrivateObservation:
    return PrivateObservation.from_mapping(
        f"observation:{name}", time, {"history_key": history_key}
    )


def robust_branching_scenario() -> Scenario:
    """Two-step fixture with one existentially safe but non-robust action."""

    history = History("s0")
    dynamics = FiniteDynamics.from_mappings(
        "robust-branching",
        "1",
        "dynamics-authority",
        actions={
            "s0": ("a", "b"),
            "good1": ("continue",),
            "robust1": ("continue",),
            "bad1": ("continue",),
        },
        disturbances={
            ("s0", "a"): ("calm", "shock"),
            ("s0", "b"): ("calm", "shock"),
            ("good1", "continue"): ("calm", "shock"),
            ("robust1", "continue"): ("calm", "shock"),
            ("bad1", "continue"): ("calm", "shock"),
        },
        successors={
            ("s0", "a", "calm"): ("good1",),
            ("s0", "a", "shock"): ("bad1",),
            ("s0", "b", "calm"): ("good1",),
            ("s0", "b", "shock"): ("robust1",),
            ("good1", "continue", "calm"): ("terminal",),
            ("good1", "continue", "shock"): ("terminal",),
            ("robust1", "continue", "calm"): ("terminal",),
            ("robust1", "continue", "shock"): ("terminal",),
            ("bad1", "continue", "calm"): ("terminal",),
            ("bad1", "continue", "shock"): ("terminal",),
        },
    )

    spec = _make_spec(
        spec_id="robust-branching",
        horizon=2,
        dynamics=dynamics,
        histories={"root": history},
        viability=_viability_rule(
            _viability_clause("viability:no-bad1", forbidden_states=("bad1",))
        ),
    )
    return Scenario(
        "robust-branching",
        "a is existential but b alone survives every declared branch recursively",
        spec,
        _observation("robust-branching", 0, "root"),
        history,
    )


def recurrence_update_inputs(
    scenario: Scenario,
    post_history: History,
    provenance_link: str,
) -> tuple[ConstructionSpec, PrivateObservation]:
    """Build the successor-root fixture used by the recurrence certificate."""

    if scenario.spec.horizon < 1:
        raise ValueError("recurrence update requires a positive prior horizon")
    next_time = scenario.spec.root_time + 1
    next_horizon = scenario.spec.horizon - 1
    history_key = f"history-at-{next_time}"
    # The successor specification absorbs the wear of the realised step. Copying
    # the prior clause unchanged would reset the budget at every update, so an
    # unbounded run of individually-admissible steps could never exhaust it.
    realised = (
        Tail((post_history.steps[-1],)) if post_history.steps else Tail.empty()
    )
    charged = scenario.spec.viability.clause.charge(realised)
    next_spec = replace(
        scenario.spec,
        spec_id=f"{scenario.spec.spec_id}:update:{next_time}",
        root_time=next_time,
        horizon=next_horizon,
        viability=viability_rule_from_clause(
            charged, ground_refs=scenario.spec.viability.record.ground_refs
        ),
        interpreter=_interpreter(
            {history_key: post_history},
            name=f"{scenario.spec.spec_id}:update:{next_time}",
        ),
        provenance=scenario.spec.provenance + (provenance_link,),
        validity=ValidityEnvelope(
            next_time,
            next_time + next_horizon + 5,
            scenario.spec.validity.regime,
            "update-1",
        ),
    )
    observation = _observation(
        f"{scenario.name}:update:{next_time}", next_time, history_key
    )
    return next_spec, observation


def empty_active_support_scenario() -> Scenario:
    """Reservoir non-empty while adaptive and seal-relative supports are empty."""

    history = History("s0")
    dynamics = FiniteDynamics.from_mappings(
        "empty-active-support",
        "1",
        "dynamics-authority",
        actions={"s0": ("a",)},
        disturbances={("s0", "a"): ("calm", "shock")},
        successors={
            ("s0", "a", "calm"): ("good",),
            ("s0", "a", "shock"): ("bad",),
        },
    )

    spec = _make_spec(
        spec_id="empty-active-support",
        horizon=1,
        dynamics=dynamics,
        histories={"root": history},
        viability=_viability_rule(
            _viability_clause("viability:no-bad", forbidden_states=("bad",))
        ),
    )
    return Scenario(
        "empty-active-support",
        "one favourable tail keeps R non-empty, but shock empties the robust fibre",
        spec,
        _observation("empty-active-support", 0, "root"),
        history,
    )



def seal_recursive_gap_scenario() -> Scenario:
    """A shallow original-seal fibre exists while recursive K^Sigma is zero."""

    history = History("root")
    dynamics = FiniteDynamics.from_mappings(
        "seal-recursive-gap",
        "1",
        "dynamics-authority",
        actions={"root": ("enter",), "mid": ("continue",)},
        disturbances={
            ("root", "enter"): ("nominal",),
            ("mid", "continue"): ("calm", "shock"),
        },
        successors={
            ("root", "enter", "nominal"): ("mid",),
            ("mid", "continue", "calm"): ("good",),
            ("mid", "continue", "shock"): ("bad",),
        },
    )

    spec = _make_spec(
        spec_id="seal-recursive-gap",
        horizon=2,
        dynamics=dynamics,
        histories={"root": history},
        viability=_viability_rule(
            _viability_clause(
                "viability:seal-recursive-gap", forbidden_states=("bad",)
            )
        ),
    )
    return Scenario(
        "seal-recursive-gap",
        "the one-step sealed fibre survives but no robust sealed suffix exists",
        spec,
        _observation("seal-recursive-gap", 0, "root"),
        history,
    )


def seal_recomputation_divergence_scenario() -> DivergenceScenario:
    """Adaptive suffix admits novel while the original seal contains only old."""

    history = History("root")
    dynamics = FiniteDynamics.from_mappings(
        "seal-divergence",
        "1",
        "dynamics-authority",
        actions={"root": ("enter",), "mid": ("novel", "old")},
        disturbances={
            ("root", "enter"): ("nominal",),
            ("mid", "novel"): ("nominal",),
            ("mid", "old"): ("nominal",),
        },
        successors={
            ("root", "enter", "nominal"): ("mid",),
            ("mid", "novel", "nominal"): ("terminal",),
            ("mid", "old", "nominal"): ("terminal",),
        },
    )

    source = _boundary_source(
        source_id="source:seal-divergence:subject",
        role=BoundarySourceRole.SUBJECT,
        authority="personal-authority",
        version="1",
        cases=(
            AdmissibilityCase(
                "root", 2, allowed_action_paths=(("enter", "old"),)
            ),
            AdmissibilityCase(
                "mid", 1, allowed_action_paths=(("novel",),)
            ),
        ),
    )

    spec = _make_spec(
        spec_id="seal-divergence",
        horizon=2,
        dynamics=dynamics,
        histories={"root": history},
        boundary_sources=(source,),
    )
    base = Scenario(
        "seal-divergence",
        "recomputed suffix and original sealed conditional fibre diverge",
        spec,
        _observation("seal-divergence", 0, "root"),
        history,
    )
    return DivergenceScenario(
        base,
        Tail((Step("enter", "mid"),)),
        expected_adaptive=("novel",),
        expected_seal_relative=("old",),
    )


def predicate_intervention_specs() -> tuple[Scenario, Scenario]:
    """Two identity predicates disagree on tails with A=V=1."""

    history = History("shared")
    dynamics = FiniteDynamics.from_mappings(
        "predicate-intervention",
        "1",
        "dynamics-authority",
        actions={"shared": ("L", "R")},
        disturbances={
            ("shared", "L"): ("nominal",),
            ("shared", "R"): ("nominal",),
        },
        successors={
            ("shared", "L", "nominal"): ("terminal",),
            ("shared", "R", "nominal"): ("terminal",),
        },
    )

    def admits(name: str, action: str) -> IdentityRule:
        return _identity_rule(
            _identity_clause(
                name,
                cases=(IdentityCase(final_action=action, verdict=True),),
                default_allow=False,
            )
        )

    left_identity = admits("identity:only-L", "L")
    right_identity = admits("identity:only-R", "R")
    left_spec = _make_spec(
        spec_id="predicate-left",
        horizon=1,
        dynamics=dynamics,
        histories={"root": history},
        identity=left_identity,
    )
    right_spec = _make_spec(
        spec_id="predicate-right",
        horizon=1,
        dynamics=dynamics,
        histories={"root": history},
        identity=right_identity,
    )
    return (
        Scenario(
            "predicate-left",
            "authorised declaration admits only L",
            left_spec,
            _observation("predicate-left", 0, "root"),
            history,
        ),
        Scenario(
            "predicate-right",
            "authorised declaration admits only R",
            right_spec,
            _observation("predicate-right", 0, "root"),
            history,
        ),
    )



def boundary_intervention_specs() -> tuple[Scenario, Scenario]:
    """An authorised B-to-A revision swaps a whole present action fibre."""

    history = History("shared")
    dynamics = FiniteDynamics.from_mappings(
        "boundary-intervention",
        "1",
        "dynamics-authority",
        actions={"shared": ("L", "R")},
        disturbances={
            ("shared", "L"): ("nominal",),
            ("shared", "R"): ("nominal",),
        },
        successors={
            ("shared", "L", "nominal"): ("blocked", "terminal"),
            ("shared", "R", "nominal"): ("blocked", "terminal"),
        },
    )

    left_subject = _boundary_source(
        source_id="personal-boundary",
        role=BoundarySourceRole.SUBJECT,
        authority="personal-authority",
        version="1",
        cases=(
            AdmissibilityCase(
                "shared", 1, allowed_action_paths=(("L",),)
            ),
        ),
    )
    right_subject = _boundary_source(
        source_id="personal-boundary",
        role=BoundarySourceRole.SUBJECT,
        authority="personal-authority",
        version="2",
        cases=(
            AdmissibilityCase(
                "shared", 1, allowed_action_paths=(("R",),)
            ),
        ),
    )
    shared_terminal = _boundary_source(
        source_id="shared-terminal-boundary",
        role=BoundarySourceRole.SHARED,
        authority="shared-boundary-authority",
        version="1",
        cases=(
            AdmissibilityCase(
                "shared", 1, allowed_state_paths=(("terminal",),)
            ),
        ),
    )
    left_spec = _make_spec(
        spec_id="boundary-intervention",
        horizon=1,
        dynamics=dynamics,
        histories={"root": history},
        boundary_sources=(left_subject, shared_terminal),
        boundary_version="1",
    )
    right_spec = _make_spec(
        spec_id="boundary-intervention",
        horizon=1,
        dynamics=dynamics,
        histories={"root": history},
        boundary_sources=(right_subject, shared_terminal),
        boundary_version="2",
    )
    shared_observation = _observation("boundary-intervention", 0, "root")
    return (
        Scenario(
            "boundary-left",
            "boundary version 1 compiles admissibility of the whole L fibre",
            left_spec,
            shared_observation,
            history,
        ),
        Scenario(
            "boundary-right",
            "authorised boundary version 2 compiles admissibility of the whole R fibre",
            right_spec,
            shared_observation,
            history,
        ),
    )


def empty_reservoir_scenario() -> Scenario:
    """Active support and reservoir are both empty under the declared identity."""

    history = History("s0")
    dynamics = FiniteDynamics.from_mappings(
        "empty-reservoir",
        "1",
        "dynamics-authority",
        actions={"s0": ("a",)},
        disturbances={("s0", "a"): ("nominal",)},
        successors={("s0", "a", "nominal"): ("terminal",)},
    )

    identity = _identity_rule(
        _identity_clause("identity:never", default_allow=False)
    )
    spec = _make_spec(
        spec_id="empty-reservoir",
        horizon=1,
        dynamics=dynamics,
        histories={"root": history},
        identity=identity,
    )
    return Scenario(
        "empty-reservoir",
        "no admitted tail remains, so active support is empty because R is empty",
        spec,
        _observation("empty-reservoir", 0, "root"),
        history,
    )


def wear_accumulation_scenario() -> Scenario:
    """Two steps each fit the sealed budget, but their sum does not."""

    history = History("live")
    dynamics = FiniteDynamics.from_mappings(
        "wear-accumulation",
        "1",
        "dynamics-authority",
        actions={"live": ("step",)},
        disturbances={("live", "step"): ("nominal",)},
        successors={("live", "step", "nominal"): ("live",)},
    )
    spec = _make_spec(
        spec_id="wear-accumulation",
        horizon=1,
        dynamics=dynamics,
        histories={"root": history},
        viability=_viability_rule(
            _viability_clause(
                "viability:wear-accumulation",
                step_cost=2,
                ledger=_wear_ledger(phi_load=0, capacity=3),
            )
        ),
    )
    return Scenario(
        "wear-accumulation",
        "one step costs 2 of a capacity-3 budget, so the second step must be refused",
        spec,
        _observation("wear-accumulation", 0, "root"),
        history,
    )


@dataclass(frozen=True, slots=True)
class BudgetGeometryComparison:
    current: Scenario
    later: Scenario
    tau_current: int
    tau_later: int


def hidden_lineage_scenarios() -> tuple[Scenario, Scenario]:
    """Same visible snapshot and equal sealed budget, different privileged reservoirs."""

    left_history = History("origin-left", (Step("arrive", "shared"),))
    right_history = History("origin-right", (Step("arrive", "shared"),))
    histories = {"left": left_history, "right": right_history}
    dynamics = FiniteDynamics.from_mappings(
        "hidden-lineage",
        "1",
        "dynamics-authority",
        actions={"shared": ("L", "R")},
        disturbances={
            ("shared", "L"): ("nominal",),
            ("shared", "R"): ("nominal",),
        },
        successors={
            ("shared", "L", "nominal"): ("terminal",),
            ("shared", "R", "nominal"): ("terminal",),
        },
    )
    identity = _identity_rule(
        _identity_clause(
            "identity:hidden-lineage",
            cases=(
                IdentityCase(
                    initial_state="origin-left", final_action="L", verdict=True
                ),
                IdentityCase(initial_state="origin-left", verdict=False),
                IdentityCase(
                    initial_state="origin-right", final_action="R", verdict=True
                ),
                IdentityCase(initial_state="origin-right", verdict=False),
            ),
            default_allow=False,
        )
    )
    # One specification, hence one sealed budget-bearing viability clause: the
    # wear ledger is equal by construction while the admitted reservoirs differ.
    spec = _make_spec(
        spec_id="hidden-lineage",
        horizon=1,
        dynamics=dynamics,
        histories=histories,
        identity=identity,
        viability=_viability_rule(
            _viability_clause(
                "viability:hidden-lineage-budget",
                step_cost=1,
                ledger=_wear_ledger(phi_load=2, capacity=7),
            )
        ),
    )
    left = Scenario(
        "hidden-lineage-left",
        "left lineage admits L under the equal sealed wear ledger",
        spec,
        _observation("hidden-lineage-left", 0, "left"),
        left_history,
    )
    right = Scenario(
        "hidden-lineage-right",
        "right lineage admits R under the equal sealed wear ledger",
        spec,
        _observation("hidden-lineage-right", 0, "right"),
        right_history,
    )
    return left, right


def equal_identity_different_budget_scenarios() -> tuple[Scenario, Scenario]:
    """Equal identity verdicts while distinct sealed ledgers cut viability differently."""

    history = History("shared")
    dynamics = FiniteDynamics.from_mappings(
        "equal-identity-budget",
        "1",
        "dynamics-authority",
        actions={"shared": ("rest", "strain")},
        disturbances={
            ("shared", "rest"): ("nominal",),
            ("shared", "strain"): ("nominal",),
        },
        successors={
            ("shared", "rest", "nominal"): ("calm",),
            ("shared", "strain", "nominal"): ("worn",),
        },
    )
    identity = _identity_rule(
        _identity_clause("identity:always-shared", default_allow=True)
    )

    def budget_spec(spec_id: str, phi_load: int) -> ConstructionSpec:
        return _make_spec(
            spec_id=spec_id,
            horizon=1,
            dynamics=dynamics,
            histories={"root": history},
            identity=identity,
            viability=_viability_rule(
                _viability_clause(
                    f"viability:{spec_id}",
                    state_costs=(("worn", 5),),
                    ledger=_wear_ledger(phi_load=phi_load, capacity=10),
                )
            ),
        )

    low = Scenario(
        "equal-identity-budget-low-wear",
        "low sealed wear admits both the rest and strain continuations",
        budget_spec("equal-identity-budget-low-wear", 1),
        _observation("equal-identity-budget-low-wear", 0, "root"),
        history,
    )
    high = Scenario(
        "equal-identity-budget-high-wear",
        "high sealed wear cuts the strain continuation while identity is unchanged",
        budget_spec("equal-identity-budget-high-wear", 6),
        _observation("equal-identity-budget-high-wear", 0, "root"),
        history,
    )
    return low, high


def budget_geometry_comparison() -> BudgetGeometryComparison:
    """Later reservoir expands even though the sealed remaining budget falls."""

    current_history = History("closed")
    later_history = History("open")
    dynamics = FiniteDynamics.from_mappings(
        "budget-geometry",
        "1",
        "dynamics-authority",
        actions={"closed": ("hold",), "open": ("explore", "hold")},
        disturbances={
            ("closed", "hold"): ("nominal",),
            ("open", "hold"): ("nominal",),
            ("open", "explore"): ("nominal",),
        },
        successors={
            ("closed", "hold", "nominal"): ("terminal",),
            ("open", "hold", "nominal"): ("terminal",),
            ("open", "explore", "nominal"): ("terminal",),
        },
    )
    current_ledger = _wear_ledger(phi_load=2, capacity=7)
    later_ledger = _wear_ledger(phi_load=3, capacity=7)
    current_spec = _make_spec(
        spec_id="budget-geometry-current",
        horizon=1,
        dynamics=dynamics,
        histories={"current": current_history},
        root_time=0,
        viability=_viability_rule(
            _viability_clause(
                "viability:budget-geometry-current",
                step_cost=1,
                ledger=current_ledger,
            )
        ),
    )
    later_spec = _make_spec(
        spec_id="budget-geometry-later",
        horizon=1,
        dynamics=dynamics,
        histories={"later": later_history},
        root_time=1,
        viability=_viability_rule(
            _viability_clause(
                "viability:budget-geometry-later",
                step_cost=1,
                ledger=later_ledger,
            )
        ),
    )
    current = Scenario(
        "budget-geometry-current",
        "closed environment under the larger sealed remaining budget",
        current_spec,
        _observation("budget-geometry-current", 0, "current"),
        current_history,
    )
    later = Scenario(
        "budget-geometry-later",
        "new environmental branch opens under the lower sealed remaining budget",
        later_spec,
        _observation("budget-geometry-later", 1, "later"),
        later_history,
    )
    return BudgetGeometryComparison(
        current,
        later,
        tau_current=current_ledger.tau_b,
        tau_later=later_ledger.tau_b,
    )


def non_absorption_cases() -> tuple[ChannelCase, ChannelCase]:
    """Computed coarse-channel collision induced by an authorised B-to-A revision."""

    engine = ReservoirEngine()

    def derive(scenario: Scenario) -> ChannelCase:
        remaining = scenario.spec.horizon
        reachable = engine.reachable_tails(
            scenario.spec, scenario.history, 0, remaining
        )
        reservoir = engine.reservoir(
            scenario.spec, scenario.history, 0, remaining
        )
        geometry = engine.geometry(
            scenario.spec, scenario.history, 0, remaining
        )
        support = engine.existential_support(geometry)
        if len(support) != 1:
            raise ValueError("boundary intervention must induce singleton support")
        observation = {
            "visible_state": scenario.history.current_state,
            "reachable_cardinality": len(reachable),
            "reservoir_cardinality": len(reservoir.tails),
            "geometry_profile": tuple(
                (len(item.prefix.steps), len(item.tails))
                for item in geometry.fibres
            ),
            "support_cardinality": len(support),
            "urgency": "normal",
            "rejection_shape": "constant",
            "timing_bucket": "constant",
            "queries": (),
        }
        return ChannelCase(
            scenario.name,
            observation,
            {"admitted_action": support[0]},
        )

    return tuple(derive(scenario) for scenario in boundary_intervention_specs())


def boundary_hypotheses() -> tuple[BoundaryHypothesis, ...]:
    domain = ("p0", "p1", "p2", "p3")
    return tuple(
        BoundaryHypothesis(f"B{mask:02d}", domain, frozenset(
            point for index, point in enumerate(domain) if mask & (1 << index)
        ))
        for mask in range(16)
    )


__all__ = [
    "BudgetGeometryComparison",
    "DivergenceScenario",
    "Scenario",
    "boundary_intervention_specs",
    "boundary_hypotheses",
    "budget_geometry_comparison",
    "empty_active_support_scenario",
    "empty_reservoir_scenario",
    "equal_identity_different_budget_scenarios",
    "hidden_lineage_scenarios",
    "non_absorption_cases",
    "predicate_intervention_specs",
    "recurrence_update_inputs",
    "robust_branching_scenario",
    "seal_recomputation_divergence_scenario",
    "seal_recursive_gap_scenario",
    "wear_accumulation_scenario",
]
