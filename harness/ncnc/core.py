"""Finite reference engine for future-indexed admissibility environments.

The module is intentionally standard-library only.  It implements the finite,
discrete objects in the companion paper and keeps four things separate:

* construction of reachable, admitted tails;
* existential, adaptive-robust and seal-relative present support;
* mode-specific evidence carried to enforcement; and
* versioned interpretation and sealing.

The code is a reference instrument, not a claim that the architecture has been
empirically instantiated in a physical system.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Callable, Iterable, Literal, Mapping, Protocol, TypeAlias


class NCNCError(Exception):
    """Base exception for the reference engine."""


class HorizonError(NCNCError):
    """Raised when an action-bearing object is requested outside its horizon."""


class SpecificationError(NCNCError):
    """Raised when a construction specification is malformed or stale."""


class InterpretationError(NCNCError):
    """Raised when a private observation cannot be mapped to one history."""


class SealIntegrityError(NCNCError):
    """Raised when a sealed object no longer matches its commitment."""


class CertificateIntegrityError(NCNCError):
    """Raised when recomputation falsifies a reservoir certificate or snapshot."""


def _canonical(value: Any) -> Any:
    """Convert an object into deterministic JSON-compatible data."""

    if hasattr(value, "canonical_data"):
        return _canonical(value.canonical_data())
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, Mapping):
        return {str(key): _canonical(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"No canonical representation for {type(value).__name__}")


def canonical_json(value: Any) -> str:
    """Return canonical UTF-8 JSON text used by every commitment."""

    return json.dumps(
        _canonical(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def commitment(value: Any) -> str:
    """Return a SHA-256 commitment to the canonical representation."""

    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True, order=True)
class Step:
    action: str
    next_state: str

    def canonical_data(self) -> dict[str, str]:
        return {"action": self.action, "next_state": self.next_state}


@dataclass(frozen=True, slots=True)
class History:
    initial_state: str
    steps: tuple[Step, ...] = ()

    @property
    def current_state(self) -> str:
        return self.steps[-1].next_state if self.steps else self.initial_state

    def append(self, action: str, next_state: str) -> "History":
        return History(self.initial_state, self.steps + (Step(action, next_state),))

    def extend(self, tail: "Tail") -> "History":
        result = self
        for step in tail.steps:
            result = result.append(step.action, step.next_state)
        return result

    def canonical_data(self) -> dict[str, Any]:
        return {"initial_state": self.initial_state, "steps": self.steps}

    @property
    def digest(self) -> str:
        return commitment(self)


@dataclass(frozen=True, slots=True, order=True)
class Tail:
    steps: tuple[Step, ...] = ()

    @classmethod
    def empty(cls) -> "Tail":
        return cls(())

    def prefix(self, length: int) -> "Tail":
        if length < 0 or length > len(self.steps):
            raise HorizonError(f"prefix length {length} outside 0..{len(self.steps)}")
        return Tail(self.steps[:length])

    def append(self, action: str, next_state: str) -> "Tail":
        return Tail(self.steps + (Step(action, next_state),))

    @property
    def first_action(self) -> str:
        if not self.steps:
            raise HorizonError("the terminal H=0 tail has no first action")
        return self.steps[0].action

    @property
    def digest(self) -> str:
        return commitment(self)

    def canonical_data(self) -> dict[str, Any]:
        return {"steps": self.steps}


@dataclass(frozen=True, slots=True)
class RuleRecord:
    rule_id: str
    version: str
    authority: str
    implementation_digest: str
    ground_refs: tuple[str, ...] = ()

    def canonical_data(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "version": self.version,
            "authority": self.authority,
            "implementation_digest": self.implementation_digest,
            "ground_refs": self.ground_refs,
        }


class BoundarySourceRole(str, Enum):
    SUBJECT = "subject"
    SHARED = "shared"
    PLATFORM = "platform"


@dataclass(frozen=True, slots=True)
class AdmissibilityCase:
    """Finite executable clause row keyed by current state and horizon."""

    current_state: str
    horizon: int
    allowed_action_paths: tuple[tuple[str, ...], ...] = ()
    allowed_state_paths: tuple[tuple[str, ...], ...] = ()

    def __post_init__(self) -> None:
        if not self.current_state:
            raise SpecificationError("admissibility cases require a current state")
        if self.horizon < 0:
            raise SpecificationError("admissibility case horizon must be non-negative")
        for name, paths in (
            ("action", self.allowed_action_paths),
            ("state", self.allowed_state_paths),
        ):
            if len(set(paths)) != len(paths):
                raise SpecificationError(
                    f"admissibility case {name} paths must be unique"
                )
            if any(len(path) != self.horizon for path in paths):
                raise SpecificationError(
                    f"admissibility case {name} path length must equal its horizon"
                )

    def admits(self, tail: Tail) -> bool:
        if len(tail.steps) != self.horizon:
            return False
        actions = tuple(step.action for step in tail.steps)
        states = tuple(step.next_state for step in tail.steps)
        return (
            not self.allowed_action_paths or actions in self.allowed_action_paths
        ) and (
            not self.allowed_state_paths or states in self.allowed_state_paths
        )

    def canonical_data(self) -> dict[str, Any]:
        return {
            "current_state": self.current_state,
            "horizon": self.horizon,
            "allowed_action_paths": self.allowed_action_paths,
            "allowed_state_paths": self.allowed_state_paths,
        }


@dataclass(frozen=True, slots=True)
class AdmissibilityClause:
    """Committed executable source clause; cases override the declared default."""

    clause_id: str
    version: str
    authority: str
    cases: tuple[AdmissibilityCase, ...] = ()
    default_allow: bool = True

    def __post_init__(self) -> None:
        if not self.clause_id or not self.version or not self.authority:
            raise SpecificationError(
                "admissibility clauses require id, authority and version"
            )
        keys = tuple((case.current_state, case.horizon) for case in self.cases)
        if len(set(keys)) != len(keys):
            raise SpecificationError(
                "admissibility clause state-horizon cases must be unique"
            )

    def __call__(
        self, time: int, horizon: int, history: History, tail: Tail
    ) -> bool:
        del time
        if len(tail.steps) != horizon:
            return False
        case = next(
            (
                item
                for item in self.cases
                if item.current_state == history.current_state
                and item.horizon == horizon
            ),
            None,
        )
        return self.default_allow if case is None else case.admits(tail)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "clause_id": self.clause_id,
            "version": self.version,
            "authority": self.authority,
            "cases": self.cases,
            "default_allow": self.default_allow,
        }


@dataclass(frozen=True, slots=True)
class BoundarySource:
    source_id: str
    role: BoundarySourceRole
    authority: str
    version: str
    clause: AdmissibilityClause

    def __post_init__(self) -> None:
        if not self.source_id or not self.authority or not self.version:
            raise SpecificationError("boundary sources require id, authority and version")
        if self.clause.clause_id != self.source_id:
            raise SpecificationError("boundary source id must match its executable clause id")
        if self.clause.authority != self.authority:
            raise SpecificationError(
                "boundary source authority must match its executable clause authority"
            )
        if self.clause.version != self.version:
            raise SpecificationError(
                "boundary source version must match its executable clause version"
            )

    def canonical_data(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "role": self.role,
            "authority": self.authority,
            "version": self.version,
            "clause": self.clause,
        }


@dataclass(frozen=True, slots=True)
class ConstitutiveBoundary:
    """Versioned executable source map compiled by conjunction into A."""

    subject_id: str
    sources: tuple[BoundarySource, ...]
    composition_relation: str
    version: str
    compiler_authority: str = "boundary-compiler"

    def __post_init__(self) -> None:
        if (
            not self.subject_id
            or not self.composition_relation
            or not self.version
            or not self.compiler_authority
        ):
            raise SpecificationError(
                "constitutive boundary requires subject, composition and version"
            )
        if not self.sources:
            raise SpecificationError("constitutive boundary requires at least one source")
        source_ids = tuple(source.source_id for source in self.sources)
        if len(set(source_ids)) != len(source_ids):
            raise SpecificationError("constitutive boundary source ids must be unique")
        if self.composition_relation != "source-separated-conjunction":
            raise SpecificationError(
                "unsupported constitutive boundary composition relation"
            )
        if not any(source.role is BoundarySourceRole.SUBJECT for source in self.sources):
            raise SpecificationError(
                "constitutive boundary requires an authorised subject source"
            )

    @property
    def compiled_admissibility(self) -> RuleRecord:
        return self.compile().record

    def compile(self) -> "AdmissibilityRule":
        sources = self.sources
        record = RuleRecord(
            rule_id=f"admissibility:{self.subject_id}:{self.version}",
            version=self.version,
            authority=self.compiler_authority,
            implementation_digest=commitment(
                _admissibility_material(self.composition_relation, sources)
            ),
            ground_refs=tuple(source.source_id for source in sources),
        )
        return AdmissibilityRule(record, sources, self.composition_relation)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "compiled_admissibility": self.compiled_admissibility,
            "sources": self.sources,
            "composition_relation": self.composition_relation,
            "version": self.version,
            "compiler_authority": self.compiler_authority,
        }


InterpreterEvaluator: TypeAlias = Callable[["PrivateObservation"], History]


def _admissibility_material(
    composition_relation: str, sources: tuple["BoundarySource", ...]
) -> dict[str, Any]:
    return {
        "composition_relation": composition_relation,
        "sources": tuple(
            (source.source_id, source.role, source.clause) for source in sources
        ),
    }


@dataclass(frozen=True, slots=True)
class WearLedger:
    """Declared structural-burden ledger; not an identity witness by definition."""

    phi_load: int
    capacity: int
    version: str
    authority: str

    def __post_init__(self) -> None:
        if self.capacity < 0 or self.phi_load < 0:
            raise SpecificationError("wear-ledger quantities must be non-negative")
        if self.phi_load > self.capacity:
            raise SpecificationError("wear-ledger load exceeds capacity")

    @property
    def tau_b(self) -> int:
        return self.capacity - self.phi_load

    def canonical_data(self) -> dict[str, Any]:
        return {
            "phi_load": self.phi_load,
            "capacity": self.capacity,
            "tau_b": self.tau_b,
            "version": self.version,
            "authority": self.authority,
        }


@dataclass(frozen=True, slots=True)
class IdentityCase:
    """Executable identity row; None fields are wildcards, first match wins."""

    initial_state: str | None = None
    history_length: int | None = None
    final_action: str | None = None
    verdict: bool = True

    def __post_init__(self) -> None:
        if self.history_length is not None and self.history_length < 0:
            raise SpecificationError("identity case history length must be non-negative")

    def matches(self, history: History) -> bool:
        if self.initial_state is not None and history.initial_state != self.initial_state:
            return False
        if self.history_length is not None and len(history.steps) != self.history_length:
            return False
        if self.final_action is not None:
            if not history.steps or history.steps[-1].action != self.final_action:
                return False
        return True

    def canonical_data(self) -> dict[str, Any]:
        return {
            "initial_state": self.initial_state,
            "history_length": self.history_length,
            "final_action": self.final_action,
            "verdict": self.verdict,
        }


@dataclass(frozen=True, slots=True)
class IdentityClause:
    """Committed executable identity predicate: ordered cases, first match wins."""

    clause_id: str
    version: str
    authority: str
    cases: tuple[IdentityCase, ...] = ()
    default_allow: bool = True

    def __post_init__(self) -> None:
        if not self.clause_id or not self.version or not self.authority:
            raise SpecificationError("identity clauses require id, authority and version")

    def __call__(self, history: History) -> bool:
        for case in self.cases:
            if case.matches(history):
                return case.verdict
        return self.default_allow

    def canonical_data(self) -> dict[str, Any]:
        return {
            "clause_id": self.clause_id,
            "version": self.version,
            "authority": self.authority,
            "cases": self.cases,
            "default_allow": self.default_allow,
        }


@dataclass(frozen=True, slots=True)
class ViabilityClause:
    """Committed executable prefix-viability predicate.

    Constraints are conjunctive: a prefix is viable when it visits no forbidden
    state AND, if a wear ledger is declared, accumulated wear stays within the
    remaining budget `phi_load + wear(prefix) <= capacity`. The ledger is part of
    the clause's canonical data, so budget participation is sealed, not ambient.
    """

    clause_id: str
    version: str
    authority: str
    forbidden_states: tuple[str, ...] = ()
    state_costs: tuple[tuple[str, int], ...] = ()
    step_cost: int = 0
    ledger: WearLedger | None = None

    def __post_init__(self) -> None:
        if not self.clause_id or not self.version or not self.authority:
            raise SpecificationError("viability clauses require id, authority and version")
        if len(set(self.forbidden_states)) != len(self.forbidden_states):
            raise SpecificationError("viability forbidden states must be unique")
        if self.step_cost < 0 or any(cost < 0 for _, cost in self.state_costs):
            raise SpecificationError("viability wear costs must be non-negative")
        if len({state for state, _ in self.state_costs}) != len(self.state_costs):
            raise SpecificationError("viability state costs must be keyed uniquely")
        if self.ledger is None and (self.state_costs or self.step_cost):
            raise SpecificationError("viability wear costs require a declared wear ledger")

    def wear(self, prefix: Tail) -> int:
        costs = dict(self.state_costs)
        return sum(
            costs.get(step.next_state, 0) + self.step_cost for step in prefix.steps
        )

    def charge(self, realised: Tail) -> "ViabilityClause":
        """Return the successor clause whose ledger has absorbed realised wear.

        Without this, a sealed ledger is a per-construction constant: every
        horizon-`H` verdict re-measures wear from zero, so an unbounded run of
        individually-admissible steps never exhausts the budget. Charging the
        executed prefix into `phi_load` is what makes the ledger a wearing
        resource across the history-generated recurrence rather than a
        parameter. An admitted step always fits by construction, so this cannot
        push the load past capacity; a later step that no longer fits is refused
        by the viability factor, which empties the successor reservoir.
        """

        if self.ledger is None:
            return self
        return replace(
            self,
            ledger=replace(
                self.ledger, phi_load=self.ledger.phi_load + self.wear(realised)
            ),
        )

    def __call__(self, time: int, prefix_length: int, history: History, prefix: Tail) -> bool:
        del time, prefix_length, history
        if any(step.next_state in self.forbidden_states for step in prefix.steps):
            return False
        if self.ledger is not None:
            if self.ledger.phi_load + self.wear(prefix) > self.ledger.capacity:
                return False
        return True

    def canonical_data(self) -> dict[str, Any]:
        return {
            "clause_id": self.clause_id,
            "version": self.version,
            "authority": self.authority,
            "forbidden_states": self.forbidden_states,
            "state_costs": self.state_costs,
            "step_cost": self.step_cost,
            "ledger": self.ledger,
        }


def _assert_rule_clause_binding(kind: str, record: RuleRecord, clause: Any) -> None:
    if record.implementation_digest != commitment(clause):
        raise SpecificationError(
            f"{kind} rule record does not commit to its executable clause"
        )
    if (
        record.rule_id != clause.clause_id
        or record.version != clause.version
        or record.authority != clause.authority
    ):
        raise SpecificationError(
            f"{kind} rule record does not match its executable clause"
        )


@dataclass(frozen=True, slots=True)
class IdentityRule:
    record: RuleRecord
    clause: IdentityClause

    def __post_init__(self) -> None:
        _assert_rule_clause_binding("identity", self.record, self.clause)

    def __call__(self, history: History) -> bool:
        return self.clause(history)

    def canonical_data(self) -> dict[str, Any]:
        return {"record": self.record, "clause": self.clause}


@dataclass(frozen=True, slots=True)
class AdmissibilityRule:
    """Conjunction of the boundary's source clauses; no free evaluator exists.

    The rule carries the exact sources it evaluates and refuses construction
    unless its record commits to them, so a caller cannot assemble an
    admissibility rule whose behaviour diverges from its committed record.
    """

    record: RuleRecord
    sources: tuple["BoundarySource", ...]
    composition_relation: str

    def __post_init__(self) -> None:
        if self.composition_relation != "source-separated-conjunction":
            raise SpecificationError(
                "unsupported admissibility composition relation"
            )
        expected = commitment(
            _admissibility_material(self.composition_relation, self.sources)
        )
        if self.record.implementation_digest != expected:
            raise SpecificationError(
                "admissibility rule record does not commit to its compiled sources"
            )
        if self.record.ground_refs != tuple(
            source.source_id for source in self.sources
        ):
            raise SpecificationError(
                "admissibility rule record does not reference its exact sources"
            )

    def __call__(self, time: int, horizon: int, history: History, tail: Tail) -> bool:
        return all(
            source.clause(time, horizon, history, tail) for source in self.sources
        )

    def canonical_data(self) -> Any:
        return self.record


@dataclass(frozen=True, slots=True)
class ViabilityRule:
    record: RuleRecord
    clause: ViabilityClause

    def __post_init__(self) -> None:
        _assert_rule_clause_binding("viability", self.record, self.clause)

    def __call__(self, time: int, prefix_length: int, history: History, prefix: Tail) -> bool:
        return self.clause(time, prefix_length, history, prefix)

    def canonical_data(self) -> dict[str, Any]:
        return {"record": self.record, "clause": self.clause}


def identity_rule_from_clause(
    clause: IdentityClause, ground_refs: tuple[str, ...] = ()
) -> IdentityRule:
    return IdentityRule(
        RuleRecord(
            rule_id=clause.clause_id,
            version=clause.version,
            authority=clause.authority,
            implementation_digest=commitment(clause),
            ground_refs=ground_refs,
        ),
        clause,
    )


def viability_rule_from_clause(
    clause: ViabilityClause, ground_refs: tuple[str, ...] = ()
) -> ViabilityRule:
    return ViabilityRule(
        RuleRecord(
            rule_id=clause.clause_id,
            version=clause.version,
            authority=clause.authority,
            implementation_digest=commitment(clause),
            ground_refs=ground_refs,
        ),
        clause,
    )


@dataclass(frozen=True, slots=True)
class PrivateObservation:
    observation_id: str
    observed_at: int
    attributes: tuple[tuple[str, str], ...]

    @classmethod
    def from_mapping(
        cls, observation_id: str, observed_at: int, attributes: Mapping[str, str]
    ) -> "PrivateObservation":
        return cls(observation_id, observed_at, tuple(sorted(attributes.items())))

    def get(self, key: str) -> str | None:
        return dict(self.attributes).get(key)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "observed_at": self.observed_at,
            "attributes": self.attributes,
        }

    @property
    def digest(self) -> str:
        return commitment(self)


@dataclass(frozen=True, slots=True)
class VersionedInterpreter:
    record: RuleRecord
    evaluator: InterpreterEvaluator = field(compare=False, repr=False)

    def interpret(self, observation: PrivateObservation) -> History:
        try:
            history = self.evaluator(observation)
        except InterpretationError:
            raise
        except Exception as exc:  # defensive boundary around an authority-bearing adapter
            raise InterpretationError(f"interpreter rejected observation: {exc}") from exc
        if not isinstance(history, History):
            raise InterpretationError("interpreter must return exactly one History")
        return history

    def canonical_data(self) -> Any:
        return self.record


@dataclass(frozen=True, slots=True)
class WitnessRecord:
    carrier_id: str
    equivalence_class: str
    version: str
    authority: str

    def canonical_data(self) -> dict[str, str]:
        return {
            "carrier_id": self.carrier_id,
            "equivalence_class": self.equivalence_class,
            "version": self.version,
            "authority": self.authority,
        }



@dataclass(frozen=True, slots=True)
class Declaration:
    subject_id: str
    identity: IdentityRule
    witness: WitnessRecord
    boundary: ConstitutiveBoundary
    declaration_authority: str
    revision_relation: str
    interpretation_convention: str
    version: str

    def __post_init__(self) -> None:
        if self.boundary.subject_id != self.subject_id:
            raise SpecificationError("boundary subject does not match declaration subject")
        if self.boundary.version != self.version:
            raise SpecificationError("boundary version does not match declaration version")
        if not any(
            source.role is BoundarySourceRole.SUBJECT
            and source.authority == self.declaration_authority
            for source in self.boundary.sources
        ):
            raise SpecificationError(
                "declaration authority does not bind an authorised subject source"
            )

    def canonical_data(self) -> dict[str, Any]:
        return {
            "subject_id": self.subject_id,
            "identity": self.identity,
            "witness": self.witness,
            "boundary": self.boundary,
            "declaration_authority": self.declaration_authority,
            "revision_relation": self.revision_relation,
            "interpretation_convention": self.interpretation_convention,
            "version": self.version,
        }


@dataclass(frozen=True, slots=True)
class ValidityEnvelope:
    not_before: int
    not_after: int
    regime: str
    version: str

    def __post_init__(self) -> None:
        if self.not_after < self.not_before:
            raise SpecificationError("validity envelope ends before it begins")

    def contains(self, time: int, regime: str) -> bool:
        return self.not_before <= time <= self.not_after and regime == self.regime

    def canonical_data(self) -> dict[str, Any]:
        return {
            "not_before": self.not_before,
            "not_after": self.not_after,
            "regime": self.regime,
            "version": self.version,
        }


@dataclass(frozen=True, slots=True)
class FiniteDynamics:
    dynamics_id: str
    version: str
    authority: str
    actions_by_state: tuple[tuple[str, tuple[str, ...]], ...]
    disturbances_by_state_action: tuple[tuple[str, str, tuple[str, ...]], ...]
    successors_by_key: tuple[tuple[str, str, str, tuple[str, ...]], ...]

    def __post_init__(self) -> None:
        self.validate()

    @classmethod
    def from_mappings(
        cls,
        dynamics_id: str,
        version: str,
        authority: str,
        actions: Mapping[str, Iterable[str]],
        disturbances: Mapping[tuple[str, str], Iterable[str]],
        successors: Mapping[tuple[str, str, str], Iterable[str]],
    ) -> "FiniteDynamics":
        return cls(
            dynamics_id=dynamics_id,
            version=version,
            authority=authority,
            actions_by_state=tuple(
                sorted((state, tuple(sorted(set(values)))) for state, values in actions.items())
            ),
            disturbances_by_state_action=tuple(
                sorted(
                    (state, action, tuple(sorted(set(values))))
                    for (state, action), values in disturbances.items()
                )
            ),
            successors_by_key=tuple(
                sorted(
                    (state, action, disturbance, tuple(sorted(set(values))))
                    for (state, action, disturbance), values in successors.items()
                )
            ),
        )

    def actions(self, history: History, time: int) -> tuple[str, ...]:
        del time
        return dict(self.actions_by_state).get(history.current_state, ())

    def disturbances(self, history: History, action: str, time: int) -> tuple[str, ...]:
        del time
        table = {(s, a): values for s, a, values in self.disturbances_by_state_action}
        return table.get((history.current_state, action), ())

    def successors(
        self, history: History, action: str, disturbance: str, time: int
    ) -> tuple[str, ...]:
        del time
        table = {
            (s, a, w): values for s, a, w, values in self.successors_by_key
        }
        return table.get((history.current_state, action, disturbance), ())

    def validate(self) -> None:
        action_keys = tuple(state for state, _ in self.actions_by_state)
        if len(set(action_keys)) != len(action_keys):
            raise SpecificationError("duplicate action declaration rows shadow one another")
        disturbance_keys = tuple(
            (state, action) for state, action, _ in self.disturbances_by_state_action
        )
        if len(set(disturbance_keys)) != len(disturbance_keys):
            raise SpecificationError(
                "duplicate disturbance declaration rows shadow one another"
            )
        successor_keys = tuple(
            (state, action, disturbance)
            for state, action, disturbance, _ in self.successors_by_key
        )
        if len(set(successor_keys)) != len(successor_keys):
            raise SpecificationError("duplicate successor declaration rows shadow one another")
        for label, rows in (
            ("action", tuple(values for _, values in self.actions_by_state)),
            (
                "disturbance",
                tuple(values for _, _, values in self.disturbances_by_state_action),
            ),
            (
                "successor",
                tuple(values for _, _, _, values in self.successors_by_key),
            ),
        ):
            for values in rows:
                if len(set(values)) != len(values):
                    raise SpecificationError(
                        f"duplicate entries inside a {label} declaration row"
                    )
        declared_pairs = {
            (state, action)
            for state, actions in self.actions_by_state
            for action in actions
        }
        for state, action, _ in self.disturbances_by_state_action:
            if (state, action) not in declared_pairs:
                raise SpecificationError(
                    f"orphan disturbance row for undeclared pair ({state!r}, {action!r})"
                )
        declared_triples = {
            (state, action, disturbance)
            for state, action, values in self.disturbances_by_state_action
            for disturbance in values
        }
        for state, action, disturbance, _ in self.successors_by_key:
            if (state, action, disturbance) not in declared_triples:
                raise SpecificationError(
                    "orphan successor row for undeclared triple "
                    f"({state!r}, {action!r}, {disturbance!r})"
                )
        for state, actions in self.actions_by_state:
            if not actions:
                raise SpecificationError(f"state {state!r} has an empty action declaration")
            for action in actions:
                ws = self.disturbances(History(state), action, 0)
                if not ws:
                    raise SpecificationError(
                        f"({state!r}, {action!r}) has an empty disturbance declaration"
                    )
                for disturbance in ws:
                    xs = self.successors(History(state), action, disturbance, 0)
                    if not xs:
                        raise SpecificationError(
                            f"({state!r}, {action!r}, {disturbance!r}) has no successor"
                        )

    def canonical_data(self) -> dict[str, Any]:
        return {
            "dynamics_id": self.dynamics_id,
            "version": self.version,
            "authority": self.authority,
            "actions_by_state": self.actions_by_state,
            "disturbances_by_state_action": self.disturbances_by_state_action,
            "successors_by_key": self.successors_by_key,
        }


@dataclass(frozen=True, slots=True)
class ConstructionSpec:
    spec_id: str
    root_time: int
    horizon: int
    declaration: Declaration
    viability: ViabilityRule
    dynamics: FiniteDynamics
    interpreter: VersionedInterpreter
    model_id: str
    model_version: str
    provenance: tuple[str, ...]
    validity: ValidityEnvelope
    scheme: str = "sha256-canonical-json-v1"

    def __post_init__(self) -> None:
        if self.horizon < 0:
            raise SpecificationError("horizon must be non-negative")
        if self.validity.not_after < self.root_time:
            raise SpecificationError("validity expires before the root time")

    @property
    def admissibility(self) -> AdmissibilityRule:
        return self.declaration.boundary.compile()

    @property
    def digest(self) -> str:
        return commitment(self)

    def validate_suffix(self, time: int, remaining: int) -> None:
        if remaining < 0:
            raise HorizonError("remaining horizon must be non-negative")
        elapsed = time - self.root_time
        if elapsed < 0 or elapsed + remaining > self.horizon:
            raise HorizonError(
                f"suffix (time={time}, remaining={remaining}) is outside root horizon "
                f"[{self.root_time}, {self.root_time + self.horizon}]"
            )

    def assert_valid(self, time: int, regime: str | None = None) -> None:
        chosen = self.validity.regime if regime is None else regime
        if not self.validity.contains(time, chosen):
            raise SpecificationError("construction specification is outside its validity envelope")

    def canonical_data(self) -> dict[str, Any]:
        return {
            "spec_id": self.spec_id,
            "root_time": self.root_time,
            "horizon": self.horizon,
            "declaration": self.declaration,
            "admissibility": self.admissibility,
            "viability": self.viability,
            "dynamics": self.dynamics,
            "interpreter": self.interpreter,
            "model_id": self.model_id,
            "model_version": self.model_version,
            "provenance": self.provenance,
            "validity": self.validity,
            "scheme": self.scheme,
        }


@dataclass(frozen=True, slots=True)
class JointVerdict:
    identity: bool
    admissibility: bool
    viability: tuple[bool, ...]

    @property
    def admitted(self) -> bool:
        return self.identity and self.admissibility and all(self.viability)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "identity": self.identity,
            "admissibility": self.admissibility,
            "viability": self.viability,
            "admitted": self.admitted,
        }


@dataclass(frozen=True, slots=True)
class Certificate:
    tail: Tail
    reachability_witnesses: tuple[tuple[str, ...], ...]
    verdict: JointVerdict
    identity_source: RuleRecord
    admissibility_source: RuleRecord
    viability_source: RuleRecord
    ground_refs: tuple[str, ...]
    validity: ValidityEnvelope
    spec_commitment: str

    @property
    def digest(self) -> str:
        return commitment(self)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "tail": self.tail,
            "reachability_witnesses": self.reachability_witnesses,
            "verdict": self.verdict,
            "identity_source": self.identity_source,
            "admissibility_source": self.admissibility_source,
            "viability_source": self.viability_source,
            "ground_refs": self.ground_refs,
            "validity": self.validity,
            "spec_commitment": self.spec_commitment,
        }


@dataclass(frozen=True, slots=True)
class CertificateAudit:
    certificate_digest: str
    shape_binding: bool
    spec_binding: bool
    source_binding: bool
    ground_binding: bool
    validity_binding: bool
    tail_reachable: bool
    witness_exactness: bool
    verdict_exactness: bool
    admitted: bool
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return all(
            (
                self.shape_binding,
                self.spec_binding,
                self.source_binding,
                self.ground_binding,
                self.validity_binding,
                self.tail_reachable,
                self.witness_exactness,
                self.verdict_exactness,
                self.admitted,
            )
        ) and not self.errors

    def canonical_data(self) -> dict[str, Any]:
        return {
            "certificate_digest": self.certificate_digest,
            "shape_binding": self.shape_binding,
            "spec_binding": self.spec_binding,
            "source_binding": self.source_binding,
            "ground_binding": self.ground_binding,
            "validity_binding": self.validity_binding,
            "tail_reachable": self.tail_reachable,
            "witness_exactness": self.witness_exactness,
            "verdict_exactness": self.verdict_exactness,
            "admitted": self.admitted,
            "errors": self.errors,
            "valid": self.valid,
        }


@dataclass(frozen=True, slots=True)
class ReservoirSnapshot:
    time: int
    remaining: int
    history: History
    spec_commitment: str
    tails: tuple[Tail, ...]
    certificates: tuple[Certificate, ...]

    @property
    def digest(self) -> str:
        return commitment(self)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "time": self.time,
            "remaining": self.remaining,
            "history": self.history,
            "spec_commitment": self.spec_commitment,
            "tails": self.tails,
            "certificates": self.certificates,
        }


@dataclass(frozen=True, slots=True)
class PrefixFibre:
    prefix: Tail
    tails: tuple[Tail, ...]

    def __post_init__(self) -> None:
        if any(
            len(tail.steps) < len(self.prefix.steps)
            or tail.steps[: len(self.prefix.steps)] != self.prefix.steps
            for tail in self.tails
        ):
            raise SpecificationError("prefix fibre contains a tail outside its prefix")

    def canonical_data(self) -> dict[str, Any]:
        return {"prefix": self.prefix, "tails": self.tails}


@dataclass(frozen=True, slots=True)
class PrefixFibreGeometry:
    """Canonical prefix-indexed fibre family derived from one reservoir."""

    time: int
    remaining: int
    history: History
    spec_commitment: str
    reservoir_commitment: str
    fibres: tuple[PrefixFibre, ...]

    def __post_init__(self) -> None:
        if self.remaining < 0:
            raise SpecificationError("prefix-fibre geometry requires H>=0")
        roots = tuple(item for item in self.fibres if item.prefix == Tail.empty())
        if len(roots) != 1:
            raise SpecificationError(
                "prefix-fibre geometry requires exactly one empty-prefix fibre"
            )
        root_tails = roots[0].tails
        if any(len(tail.steps) != self.remaining for tail in root_tails):
            raise SpecificationError(
                "prefix-fibre root tails must have the declared remaining horizon"
            )
        prefixes = {Tail.empty()}
        for tail in root_tails:
            prefixes.update(
                tail.prefix(length) for length in range(1, self.remaining + 1)
            )
        expected = tuple(
            PrefixFibre(
                prefix,
                tuple(
                    tail
                    for tail in root_tails
                    if tail.steps[: len(prefix.steps)] == prefix.steps
                ),
            )
            for prefix in sorted(prefixes)
        )
        if self.fibres != expected:
            raise SpecificationError(
                "prefix-fibre geometry is not the exact geometry of its root fibre"
            )

    @property
    def digest(self) -> str:
        return commitment(self)

    @property
    def first_actions(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                {
                    item.prefix.first_action
                    for item in self.fibres
                    if len(item.prefix.steps) == 1 and item.tails
                }
            )
        )

    def fibre(self, prefix: Tail) -> tuple[Tail, ...]:
        item = next((item for item in self.fibres if item.prefix == prefix), None)
        return () if item is None else item.tails

    def canonical_data(self) -> dict[str, Any]:
        return {
            "time": self.time,
            "remaining": self.remaining,
            "history": self.history,
            "spec_commitment": self.spec_commitment,
            "reservoir_commitment": self.reservoir_commitment,
            "fibres": self.fibres,
        }


@dataclass(frozen=True, slots=True)
class SnapshotAudit:
    snapshot_digest: str
    suffix_binding: bool
    metadata_binding: bool
    ordered_unique: bool
    pairing_exact: bool
    admitted_tail_set_exact: bool
    certificate_audits: tuple[CertificateAudit, ...]
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return (
            self.suffix_binding
            and self.metadata_binding
            and self.ordered_unique
            and self.pairing_exact
            and self.admitted_tail_set_exact
            and all(audit.valid for audit in self.certificate_audits)
            and not self.errors
        )

    def canonical_data(self) -> dict[str, Any]:
        return {
            "snapshot_digest": self.snapshot_digest,
            "suffix_binding": self.suffix_binding,
            "metadata_binding": self.metadata_binding,
            "ordered_unique": self.ordered_unique,
            "pairing_exact": self.pairing_exact,
            "admitted_tail_set_exact": self.admitted_tail_set_exact,
            "certificate_audits": self.certificate_audits,
            "errors": self.errors,
            "valid": self.valid,
        }


@dataclass(frozen=True, slots=True)
class BranchEvidence:
    disturbance: str
    successor: str
    current_fibre: tuple[str, ...]
    recursive_continuation: bool
    child_support_digest: str | None

    @property
    def valid(self) -> bool:
        return bool(self.current_fibre) and self.recursive_continuation

    def canonical_data(self) -> dict[str, Any]:
        return {
            "disturbance": self.disturbance,
            "successor": self.successor,
            "current_fibre": self.current_fibre,
            "recursive_continuation": self.recursive_continuation,
            "child_support_digest": self.child_support_digest,
            "valid": self.valid,
        }


@dataclass(frozen=True, slots=True)
class ActionEvidence:
    action: str
    branches: tuple[BranchEvidence, ...]

    @property
    def valid(self) -> bool:
        return bool(self.branches) and all(branch.valid for branch in self.branches)

    def canonical_data(self) -> dict[str, Any]:
        return {"action": self.action, "branches": self.branches, "valid": self.valid}


@dataclass(frozen=True, slots=True)
class AdaptiveSupport:
    time: int
    remaining: int
    history: History
    spec_commitment: str
    current_reservoir: str
    current_geometry: str
    actions: tuple[str, ...]
    evidence: tuple[ActionEvidence, ...]

    @property
    def digest(self) -> str:
        return commitment(self)

    def evidence_for(self, action: str) -> ActionEvidence | None:
        return next((item for item in self.evidence if item.action == action), None)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "time": self.time,
            "remaining": self.remaining,
            "history": self.history,
            "spec_commitment": self.spec_commitment,
            "current_reservoir": self.current_reservoir,
            "current_geometry": self.current_geometry,
            "actions": self.actions,
            "evidence": self.evidence,
        }


@dataclass(frozen=True, slots=True)
class SealRecord:
    origin_time: int
    horizon: int
    root_history: History
    spec: ConstructionSpec = field(compare=False, repr=False)
    snapshot: ReservoirSnapshot
    observation_commitment: str
    interpreter_commitment: str
    history_attribution: str
    reservoir_commitment: str
    spec_commitment: str
    provenance: tuple[str, ...]
    scheme: str
    seal_commitment: str

    @staticmethod
    def _attribution(
        observation_commitment: str,
        interpreter_commitment: str,
        history: History,
    ) -> str:
        return commitment(
            {
                "observation_commitment": observation_commitment,
                "interpreter_commitment": interpreter_commitment,
                "history": history,
            }
        )

    @classmethod
    def create(
        cls,
        spec: ConstructionSpec,
        history: History,
        snapshot: ReservoirSnapshot,
        observation: PrivateObservation,
    ) -> "SealRecord":
        if observation.observed_at != spec.root_time:
            raise SealIntegrityError(
                "sealed observation time does not match the construction root time"
            )
        try:
            interpreted = spec.interpreter.interpret(observation)
        except InterpretationError as exc:
            raise SealIntegrityError(
                f"sealed observation is not uniquely interpretable: {exc}"
            ) from exc
        if interpreted != history:
            raise SealIntegrityError(
                "root history is not the unique interpretation of the sealed observation"
            )
        if snapshot.time != spec.root_time or snapshot.remaining != spec.horizon:
            raise SealIntegrityError("root seal must bind the root reservoir")
        if snapshot.history != history or snapshot.spec_commitment != spec.digest:
            raise SealIntegrityError("snapshot does not match the root history/specification")
        observation_commitment = observation.digest
        interpreter_commitment = commitment(spec.interpreter.record)
        history_attribution = cls._attribution(
            observation_commitment, interpreter_commitment, history
        )
        payload = {
            "origin_time": spec.root_time,
            "horizon": spec.horizon,
            "root_history": history,
            "observation_commitment": observation_commitment,
            "interpreter_commitment": interpreter_commitment,
            "history_attribution": history_attribution,
            "reservoir_commitment": snapshot.digest,
            "spec_commitment": spec.digest,
            "provenance": spec.provenance,
            "scheme": spec.scheme,
        }
        return cls(
            origin_time=spec.root_time,
            horizon=spec.horizon,
            root_history=history,
            spec=spec,
            snapshot=snapshot,
            observation_commitment=observation_commitment,
            interpreter_commitment=interpreter_commitment,
            history_attribution=history_attribution,
            reservoir_commitment=snapshot.digest,
            spec_commitment=spec.digest,
            provenance=spec.provenance,
            scheme=spec.scheme,
            seal_commitment=commitment(payload),
        )

    def _payload(self) -> dict[str, Any]:
        return {
            "origin_time": self.origin_time,
            "horizon": self.horizon,
            "root_history": self.root_history,
            "observation_commitment": self.observation_commitment,
            "interpreter_commitment": self.interpreter_commitment,
            "history_attribution": self.history_attribution,
            "reservoir_commitment": self.reservoir_commitment,
            "spec_commitment": self.spec_commitment,
            "provenance": self.provenance,
            "scheme": self.scheme,
        }

    def verify(self) -> None:
        """Check that every sealed field is mutually consistent — fixity, NOT authorship.

        This is a commitment scheme with no secret and no signature, so it answers "are
        these fields consistent with each other?" and cannot answer "did the legitimate
        generator produce them?". An adversary who rewrites a field AND recomputes every
        binding that depends on it — history attribution, snapshot, reservoir commitment,
        seal commitment — produces a seal this method accepts, because every equality it
        tests is one the adversary can satisfy by construction.

        The boundary is real and is pinned by the `F16-recomputed-seal-forgery` mutation:
        an authentic seal is separated from a fully recomputed one only by
        `verify_observation`, which re-derives the root history from the observation
        preimage the adversary does not control, or by comparison against an
        out-of-band authenticated reference. Callers holding the preimage MUST use
        `verify_observation`; `verify` alone is not tamper-evidence.
        """

        if self.spec.digest != self.spec_commitment:
            raise SealIntegrityError("construction specification no longer matches the seal")
        expected_interpreter = commitment(self.spec.interpreter.record)
        if self.interpreter_commitment != expected_interpreter:
            raise SealIntegrityError(
                "interpreter commitment no longer matches the sealed specification"
            )
        expected_attribution = self._attribution(
            self.observation_commitment,
            self.interpreter_commitment,
            self.root_history,
        )
        if self.history_attribution != expected_attribution:
            raise SealIntegrityError(
                "history attribution no longer binds observation, interpreter and root history"
            )
        if self.snapshot.digest != self.reservoir_commitment:
            raise SealIntegrityError("reservoir snapshot no longer matches the seal")
        if self.snapshot.spec_commitment != self.spec_commitment:
            raise SealIntegrityError("snapshot specification commitment no longer matches the seal")
        if self.snapshot.history != self.root_history:
            raise SealIntegrityError("root history no longer matches the sealed snapshot history")
        if self.snapshot.time != self.origin_time:
            raise SealIntegrityError("snapshot time no longer matches the seal origin time")
        if self.snapshot.remaining != self.horizon:
            raise SealIntegrityError("snapshot remaining horizon no longer matches the seal horizon")
        if commitment(self._payload()) != self.seal_commitment:
            raise SealIntegrityError("seal commitment mismatch")

    def verify_observation(self, observation: PrivateObservation) -> None:
        """Re-check Def. 3.5 history attribution against a concrete observation preimage."""

        self.verify()
        if observation.digest != self.observation_commitment:
            raise SealIntegrityError("observation does not match the sealed observation commitment")
        try:
            interpreted = self.spec.interpreter.interpret(observation)
        except InterpretationError as exc:
            raise SealIntegrityError(
                f"sealed observation is not uniquely interpretable: {exc}"
            ) from exc
        if interpreted != self.root_history:
            raise SealIntegrityError(
                "root history is not the unique interpretation of the supplied observation"
            )

    def canonical_data(self) -> dict[str, Any]:
        return {**self._payload(), "seal_commitment": self.seal_commitment}


@dataclass(frozen=True, slots=True)
class SealBranchEvidence:
    disturbance: str
    successor: str
    conditional_fibre: tuple[str, ...]
    recursive_continuation: bool
    child_support_digest: str | None

    @property
    def valid(self) -> bool:
        return bool(self.conditional_fibre) and self.recursive_continuation

    def canonical_data(self) -> dict[str, Any]:
        return {
            "disturbance": self.disturbance,
            "successor": self.successor,
            "conditional_fibre": self.conditional_fibre,
            "recursive_continuation": self.recursive_continuation,
            "child_support_digest": self.child_support_digest,
            "valid": self.valid,
        }


@dataclass(frozen=True, slots=True)
class SealActionEvidence:
    action: str
    branches: tuple[SealBranchEvidence, ...]

    @property
    def valid(self) -> bool:
        return bool(self.branches) and all(branch.valid for branch in self.branches)

    def canonical_data(self) -> dict[str, Any]:
        return {"action": self.action, "branches": self.branches, "valid": self.valid}


@dataclass(frozen=True, slots=True)
class SealRelativeSupport:
    origin_seal: str
    origin_geometry: str
    prefix: Tail
    prefix_index: int
    remaining: int
    current_history: History
    actions: tuple[str, ...]
    evidence: tuple[SealActionEvidence, ...]

    @property
    def digest(self) -> str:
        return commitment(self)

    def evidence_for(self, action: str) -> SealActionEvidence | None:
        return next((item for item in self.evidence if item.action == action), None)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "origin_seal": self.origin_seal,
            "origin_geometry": self.origin_geometry,
            "prefix": self.prefix,
            "prefix_index": self.prefix_index,
            "remaining": self.remaining,
            "current_history": self.current_history,
            "actions": self.actions,
            "evidence": self.evidence,
        }


class AssuranceMode(str, Enum):
    EXISTENTIAL = "existential"
    ADAPTIVE_ROBUST = "adaptive-robust"
    SEAL_RELATIVE = "seal-relative"


class AssuranceContext(Protocol):
    mode: AssuranceMode
    history: History
    time: int
    remaining: int
    validity: ValidityEnvelope
    runtime_regime: str
    actions: tuple[str, ...]

    @property
    def digest(self) -> str: ...

    def canonical_data(self) -> dict[str, Any]: ...


@dataclass(frozen=True, slots=True)
class ExistentialAssurance:
    mode: AssuranceMode
    history: History
    time: int
    remaining: int
    validity: ValidityEnvelope
    runtime_regime: str
    spec_commitment: str
    reservoir_commitment: str
    geometry_commitment: str
    actions: tuple[str, ...]
    action_tail_witnesses: tuple[tuple[str, tuple[str, ...]], ...]

    @property
    def digest(self) -> str:
        return commitment(self)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "history": self.history,
            "time": self.time,
            "remaining": self.remaining,
            "validity": self.validity,
            "runtime_regime": self.runtime_regime,
            "spec_commitment": self.spec_commitment,
            "reservoir_commitment": self.reservoir_commitment,
            "geometry_commitment": self.geometry_commitment,
            "actions": self.actions,
            "action_tail_witnesses": self.action_tail_witnesses,
        }


@dataclass(frozen=True, slots=True)
class AdaptiveAssurance:
    mode: AssuranceMode
    history: History
    time: int
    remaining: int
    validity: ValidityEnvelope
    runtime_regime: str
    root_spec_commitment: str
    suffix_offset: int
    current_reservoir_commitment: str
    current_geometry_commitment: str
    actions: tuple[str, ...]
    support: AdaptiveSupport

    @property
    def digest(self) -> str:
        return commitment(self)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "history": self.history,
            "time": self.time,
            "remaining": self.remaining,
            "validity": self.validity,
            "runtime_regime": self.runtime_regime,
            "root_spec_commitment": self.root_spec_commitment,
            "suffix_offset": self.suffix_offset,
            "current_reservoir_commitment": self.current_reservoir_commitment,
            "current_geometry_commitment": self.current_geometry_commitment,
            "actions": self.actions,
            "support": self.support,
        }


@dataclass(frozen=True, slots=True)
class SealRelativeAssurance:
    mode: AssuranceMode
    history: History
    time: int
    remaining: int
    validity: ValidityEnvelope
    runtime_regime: str
    origin_seal: str
    origin_spec_commitment: str
    origin_geometry_commitment: str
    prefix: Tail
    prefix_index: int
    actions: tuple[str, ...]
    support: SealRelativeSupport

    @property
    def digest(self) -> str:
        return commitment(self)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "history": self.history,
            "time": self.time,
            "remaining": self.remaining,
            "validity": self.validity,
            "runtime_regime": self.runtime_regime,
            "origin_seal": self.origin_seal,
            "origin_spec_commitment": self.origin_spec_commitment,
            "origin_geometry_commitment": self.origin_geometry_commitment,
            "prefix": self.prefix,
            "prefix_index": self.prefix_index,
            "actions": self.actions,
            "support": self.support,
        }


Assurance: TypeAlias = ExistentialAssurance | AdaptiveAssurance | SealRelativeAssurance


class ReservoirEngine:
    """Exhaustive engine for finite construction specifications."""

    def __init__(self) -> None:
        self._reachable_cache: dict[tuple[Any, ...], tuple[Tail, ...]] = {}
        self._reservoir_cache: dict[tuple[Any, ...], ReservoirSnapshot] = {}
        self._geometry_cache: dict[str, PrefixFibreGeometry] = {}
        self._adaptive_cache: dict[tuple[Any, ...], AdaptiveSupport] = {}
        self._seal_relative_cache: dict[tuple[str, str], SealRelativeSupport] = {}
        # Shared-process trust roots (same standing as the HMAC secret): the
        # engine remembers exactly which specifications and seals it has itself
        # processed, so authorities can recompute assurance evidence instead of
        # trusting hand-built artifacts. This is not a distributed-registry claim.
        self._spec_registry: dict[str, ConstructionSpec] = {}
        self._seal_registry: dict[str, SealRecord] = {}

    def register_spec(self, spec: ConstructionSpec) -> None:
        self._spec_registry.setdefault(spec.digest, spec)

    def spec_for(self, spec_commitment: str) -> ConstructionSpec:
        spec = self._spec_registry.get(spec_commitment)
        if spec is None:
            raise SpecificationError(
                "unknown construction-specification commitment for this engine"
            )
        return spec

    def register_seal(self, seal: SealRecord) -> None:
        self._seal_registry.setdefault(seal.seal_commitment, seal)

    def seal_for(self, seal_commitment: str) -> SealRecord:
        seal = self._seal_registry.get(seal_commitment)
        if seal is None:
            raise SpecificationError("unknown seal commitment for this engine")
        return seal

    @staticmethod
    def _key(spec: ConstructionSpec, history: History, time: int, remaining: int) -> tuple[Any, ...]:
        return (id(spec), spec.digest, history.digest, time, remaining)

    def reachable_tails(
        self, spec: ConstructionSpec, history: History, time: int, remaining: int
    ) -> tuple[Tail, ...]:
        spec.validate_suffix(time, remaining)
        key = self._key(spec, history, time, remaining)
        cached = self._reachable_cache.get(key)
        if cached is not None:
            return cached
        if remaining == 0:
            result = (Tail.empty(),)
        else:
            tails: set[Tail] = set()
            for action in spec.dynamics.actions(history, time):
                next_states: set[str] = set()
                for disturbance in spec.dynamics.disturbances(history, action, time):
                    next_states.update(
                        spec.dynamics.successors(history, action, disturbance, time)
                    )
                for next_state in sorted(next_states):
                    successor_history = history.append(action, next_state)
                    for suffix in self.reachable_tails(
                        spec, successor_history, time + 1, remaining - 1
                    ):
                        tails.add(Tail((Step(action, next_state),) + suffix.steps))
            result = tuple(sorted(tails))
        self._reachable_cache[key] = result
        return result

    def joint_verdict(
        self,
        spec: ConstructionSpec,
        history: History,
        time: int,
        remaining: int,
        tail: Tail,
    ) -> JointVerdict:
        spec.validate_suffix(time, remaining)
        if len(tail.steps) != remaining:
            raise HorizonError("tail length does not match remaining horizon")
        full_history = history.extend(tail)
        identity = spec.declaration.identity(full_history)
        admissibility = spec.admissibility(time, remaining, history, tail)
        viability = tuple(
            spec.viability(time, k, history, tail.prefix(k))
            for k in range(1, remaining + 1)
        )
        return JointVerdict(identity, admissibility, viability)

    def thin_temporal_restriction_failures(
        self,
        spec: ConstructionSpec,
        history: History,
        time: int,
        remaining: int,
    ) -> tuple[tuple[str, int, str], ...]:
        """Return admitted-tail prefixes that violate the optional restriction premise."""

        snapshot = self.reservoir(spec, history, time, remaining)
        failures: list[tuple[str, int, str]] = []
        for tail in snapshot.tails:
            for k in range(remaining + 1):
                prefix = tail.prefix(k)
                if not spec.declaration.identity(history.extend(prefix)):
                    failures.append((tail.digest, k, "identity"))
                if not spec.admissibility(time, k, history, prefix):
                    failures.append((tail.digest, k, "admissibility"))
        return tuple(failures)

    def _reachability_witnesses(
        self, spec: ConstructionSpec, history: History, time: int, tail: Tail
    ) -> tuple[tuple[str, ...], ...]:
        if not tail.steps:
            return ((),)
        step = tail.steps[0]
        suffix = Tail(tail.steps[1:])
        witnesses: set[tuple[str, ...]] = set()
        for disturbance in spec.dynamics.disturbances(history, step.action, time):
            if step.next_state not in spec.dynamics.successors(
                history, step.action, disturbance, time
            ):
                continue
            successor_history = history.append(step.action, step.next_state)
            for rest in self._reachability_witnesses(
                spec, successor_history, time + 1, suffix
            ):
                witnesses.add((disturbance,) + rest)
        return tuple(sorted(witnesses))

    def reservoir(
        self, spec: ConstructionSpec, history: History, time: int, remaining: int
    ) -> ReservoirSnapshot:
        spec.validate_suffix(time, remaining)
        spec.assert_valid(time)
        self.register_spec(spec)
        key = self._key(spec, history, time, remaining)
        cached = self._reservoir_cache.get(key)
        if cached is not None:
            return cached
        tails: list[Tail] = []
        certificates: list[Certificate] = []
        for tail in self.reachable_tails(spec, history, time, remaining):
            verdict = self.joint_verdict(spec, history, time, remaining, tail)
            if not verdict.admitted:
                continue
            witnesses = self._reachability_witnesses(spec, history, time, tail)
            if not witnesses:
                raise SpecificationError("reachable tail has no reachability witness")
            tails.append(tail)
            records = (
                spec.declaration.identity.record,
                spec.admissibility.record,
                spec.viability.record,
            )
            ground_refs = tuple(
                sorted({ref for record in records for ref in record.ground_refs})
            )
            certificates.append(
                Certificate(
                    tail=tail,
                    reachability_witnesses=witnesses,
                    verdict=verdict,
                    identity_source=records[0],
                    admissibility_source=records[1],
                    viability_source=records[2],
                    ground_refs=ground_refs,
                    validity=spec.validity,
                    spec_commitment=spec.digest,
                )
            )
        ordered = sorted(zip(tails, certificates), key=lambda pair: pair[0])
        snapshot = ReservoirSnapshot(
            time=time,
            remaining=remaining,
            history=history,
            spec_commitment=spec.digest,
            tails=tuple(pair[0] for pair in ordered),
            certificates=tuple(pair[1] for pair in ordered),
        )
        self._reservoir_cache[key] = snapshot
        return snapshot

    def audit_certificate(
        self,
        spec: ConstructionSpec,
        history: History,
        time: int,
        remaining: int,
        certificate: Certificate,
    ) -> CertificateAudit:
        """Recompute every load-bearing factor of one finite certificate."""

        errors: list[str] = []
        shape_binding = len(certificate.tail.steps) == remaining
        spec_binding = certificate.spec_commitment == spec.digest
        expected_sources = (
            spec.declaration.identity.record,
            spec.admissibility.record,
            spec.viability.record,
        )
        source_binding = (
            certificate.identity_source,
            certificate.admissibility_source,
            certificate.viability_source,
        ) == expected_sources
        expected_ground = tuple(
            sorted({ref for record in expected_sources for ref in record.ground_refs})
        )
        ground_binding = certificate.ground_refs == expected_ground
        validity_binding = certificate.validity == spec.validity
        tail_reachable = False
        witness_exactness = False
        verdict_exactness = False
        admitted = False

        try:
            spec.validate_suffix(time, remaining)
            spec.assert_valid(time)
        except (SpecificationError, HorizonError) as exc:
            errors.append(str(exc))
        else:
            if shape_binding:
                tail_reachable = certificate.tail in self.reachable_tails(
                    spec, history, time, remaining
                )
                if tail_reachable:
                    expected_witnesses = self._reachability_witnesses(
                        spec, history, time, certificate.tail
                    )
                    witness_exactness = (
                        certificate.reachability_witnesses == expected_witnesses
                        and bool(expected_witnesses)
                    )
                    expected_verdict = self.joint_verdict(
                        spec, history, time, remaining, certificate.tail
                    )
                    verdict_exactness = certificate.verdict == expected_verdict
                    admitted = expected_verdict.admitted and certificate.verdict.admitted

        flags = {
            "shape binding": shape_binding,
            "specification binding": spec_binding,
            "source binding": source_binding,
            "ground-reference binding": ground_binding,
            "validity binding": validity_binding,
            "tail reachability": tail_reachable,
            "witness exactness": witness_exactness,
            "verdict exactness": verdict_exactness,
            "admitted verdict": admitted,
        }
        errors.extend(name for name, passed in flags.items() if not passed)
        return CertificateAudit(
            certificate_digest=certificate.digest,
            shape_binding=shape_binding,
            spec_binding=spec_binding,
            source_binding=source_binding,
            ground_binding=ground_binding,
            validity_binding=validity_binding,
            tail_reachable=tail_reachable,
            witness_exactness=witness_exactness,
            verdict_exactness=verdict_exactness,
            admitted=admitted,
            errors=tuple(errors),
        )

    def assert_certificate(
        self,
        spec: ConstructionSpec,
        history: History,
        time: int,
        remaining: int,
        certificate: Certificate,
    ) -> CertificateAudit:
        audit = self.audit_certificate(spec, history, time, remaining, certificate)
        if not audit.valid:
            raise CertificateIntegrityError("; ".join(audit.errors))
        return audit

    def audit_snapshot(
        self, spec: ConstructionSpec, snapshot: ReservoirSnapshot
    ) -> SnapshotAudit:
        """Recompute the admitted tail-set and every paired certificate."""

        errors: list[str] = []
        try:
            spec.validate_suffix(snapshot.time, snapshot.remaining)
            spec.assert_valid(snapshot.time)
            suffix_binding = True
        except (SpecificationError, HorizonError) as exc:
            suffix_binding = False
            errors.append(str(exc))
        metadata_binding = snapshot.spec_commitment == spec.digest
        ordered_unique = snapshot.tails == tuple(sorted(set(snapshot.tails)))
        pairing_exact = (
            len(snapshot.tails) == len(snapshot.certificates)
            and tuple(cert.tail for cert in snapshot.certificates) == snapshot.tails
        )
        expected_tails: tuple[Tail, ...] = ()
        if suffix_binding:
            expected_tails = tuple(
                tail
                for tail in self.reachable_tails(
                    spec,
                    snapshot.history,
                    snapshot.time,
                    snapshot.remaining,
                )
                if self.joint_verdict(
                    spec,
                    snapshot.history,
                    snapshot.time,
                    snapshot.remaining,
                    tail,
                ).admitted
            )
        admitted_tail_set_exact = suffix_binding and snapshot.tails == expected_tails
        certificate_audits = tuple(
            self.audit_certificate(
                spec,
                snapshot.history,
                snapshot.time,
                snapshot.remaining,
                certificate,
            )
            for certificate in snapshot.certificates
        )
        flags = {
            "suffix binding": suffix_binding,
            "metadata binding": metadata_binding,
            "ordered unique tails": ordered_unique,
            "tail-certificate pairing": pairing_exact,
            "complete admitted tail-set": admitted_tail_set_exact,
            "all certificates": all(audit.valid for audit in certificate_audits),
        }
        errors.extend(name for name, passed in flags.items() if not passed)
        return SnapshotAudit(
            snapshot_digest=snapshot.digest,
            suffix_binding=suffix_binding,
            metadata_binding=metadata_binding,
            ordered_unique=ordered_unique,
            pairing_exact=pairing_exact,
            admitted_tail_set_exact=admitted_tail_set_exact,
            certificate_audits=certificate_audits,
            errors=tuple(errors),
        )

    def assert_snapshot(
        self, spec: ConstructionSpec, snapshot: ReservoirSnapshot
    ) -> SnapshotAudit:
        audit = self.audit_snapshot(spec, snapshot)
        if not audit.valid:
            raise CertificateIntegrityError("; ".join(audit.errors))
        return audit

    def geometry_from_snapshot(
        self, snapshot: ReservoirSnapshot
    ) -> PrefixFibreGeometry:
        cached = self._geometry_cache.get(snapshot.digest)
        if cached is not None:
            return cached
        prefixes = {Tail.empty()}
        for tail in snapshot.tails:
            prefixes.update(
                tail.prefix(length) for length in range(1, snapshot.remaining + 1)
            )
        geometry = PrefixFibreGeometry(
            time=snapshot.time,
            remaining=snapshot.remaining,
            history=snapshot.history,
            spec_commitment=snapshot.spec_commitment,
            reservoir_commitment=snapshot.digest,
            fibres=tuple(
                PrefixFibre(
                    prefix,
                    tuple(
                        tail
                        for tail in snapshot.tails
                        if tail.steps[: len(prefix.steps)] == prefix.steps
                    ),
                )
                for prefix in sorted(prefixes)
            ),
        )
        self._geometry_cache[snapshot.digest] = geometry
        return geometry

    def assert_geometry(
        self, snapshot: ReservoirSnapshot, geometry: PrefixFibreGeometry
    ) -> None:
        if geometry.reservoir_commitment != snapshot.digest:
            raise CertificateIntegrityError(
                "geometry reservoir commitment does not match its snapshot"
            )
        if (
            geometry.time,
            geometry.remaining,
            geometry.history,
            geometry.spec_commitment,
        ) != (
            snapshot.time,
            snapshot.remaining,
            snapshot.history,
            snapshot.spec_commitment,
        ):
            raise CertificateIntegrityError(
                "geometry suffix metadata does not match its snapshot"
            )
        expected = self.geometry_from_snapshot(snapshot)
        if geometry != expected:
            raise CertificateIntegrityError(
                "geometry fibres do not match the exact snapshot prefix fibres"
            )

    def geometry(
        self, spec: ConstructionSpec, history: History, time: int, remaining: int
    ) -> PrefixFibreGeometry:
        snapshot = self.reservoir(spec, history, time, remaining)
        geometry = self.geometry_from_snapshot(snapshot)
        self.assert_geometry(snapshot, geometry)
        return geometry

    @staticmethod
    def existential_support(geometry: PrefixFibreGeometry) -> tuple[str, ...]:
        if geometry.remaining < 1:
            raise HorizonError("present support is undefined at terminal horizon H=0")
        return geometry.first_actions

    def continuation_indicator(
        self, spec: ConstructionSpec, history: History, time: int, remaining: int
    ) -> bool:
        if remaining == 0:
            return bool(self.reservoir(spec, history, time, 0).tails)
        support = self.adaptive_support(spec, history, time, remaining)
        return bool(support.actions)

    def adaptive_support(
        self, spec: ConstructionSpec, history: History, time: int, remaining: int
    ) -> AdaptiveSupport:
        if remaining < 1:
            raise HorizonError("adaptive present support is undefined at H=0")
        spec.validate_suffix(time, remaining)
        key = self._key(spec, history, time, remaining)
        cached = self._adaptive_cache.get(key)
        if cached is not None:
            return cached
        snapshot = self.reservoir(spec, history, time, remaining)
        geometry = self.geometry_from_snapshot(snapshot)
        self.assert_geometry(snapshot, geometry)
        candidate_actions = self.existential_support(geometry)
        evidence: list[ActionEvidence] = []
        admitted: list[str] = []
        for action in candidate_actions:
            branches: list[BranchEvidence] = []
            for disturbance in spec.dynamics.disturbances(history, action, time):
                for successor in spec.dynamics.successors(
                    history, action, disturbance, time
                ):
                    current_fibre = geometry.fibre(
                        Tail((Step(action, successor),))
                    )
                    successor_history = history.append(action, successor)
                    child_support_digest: str | None = None
                    if remaining - 1 == 0:
                        recursive = bool(
                            self.reservoir(spec, successor_history, time + 1, 0).tails
                        )
                    else:
                        child = self.adaptive_support(
                            spec, successor_history, time + 1, remaining - 1
                        )
                        recursive = bool(child.actions)
                        child_support_digest = child.digest
                    branches.append(
                        BranchEvidence(
                            disturbance=disturbance,
                            successor=successor,
                            current_fibre=tuple(tail.digest for tail in current_fibre),
                            recursive_continuation=recursive,
                            child_support_digest=child_support_digest,
                        )
                    )
            action_evidence = ActionEvidence(action, tuple(branches))
            evidence.append(action_evidence)
            if action_evidence.valid:
                admitted.append(action)
        result = AdaptiveSupport(
            time=time,
            remaining=remaining,
            history=history,
            spec_commitment=spec.digest,
            current_reservoir=snapshot.digest,
            current_geometry=geometry.digest,
            actions=tuple(admitted),
            evidence=tuple(evidence),
        )
        self._adaptive_cache[key] = result
        return result

    def create_seal(
        self,
        spec: ConstructionSpec,
        history: History,
        observation: PrivateObservation,
    ) -> SealRecord:
        snapshot = self.reservoir(spec, history, spec.root_time, spec.horizon)
        seal = SealRecord.create(spec, history, snapshot, observation)
        self.register_seal(seal)
        return seal

    def seal_continuation_indicator(self, seal: SealRecord, prefix: Tail) -> bool:
        # Evaluate K^Sigma at a prefix inside the original sealed reservoir.

        seal.verify()
        self.assert_snapshot(seal.spec, seal.snapshot)
        k = len(prefix.steps)
        if k < 0 or k > seal.horizon:
            raise HorizonError("seal-relative continuation indicator requires 0 <= k <= H")
        geometry = self.geometry_from_snapshot(seal.snapshot)
        self.assert_geometry(seal.snapshot, geometry)
        if not geometry.fibre(prefix):
            return False
        if k == seal.horizon:
            return True
        return bool(self.seal_relative_support(seal, prefix).actions)

    def seal_relative_support(
        self, seal: SealRecord, prefix: Tail
    ) -> SealRelativeSupport:
        seal.verify()
        self.assert_snapshot(seal.spec, seal.snapshot)
        self.register_seal(seal)
        k = len(prefix.steps)
        if k < 0 or k >= seal.horizon:
            raise HorizonError(
                "seal-relative present support exists only for 0 <= k < H"
            )
        geometry = self.geometry_from_snapshot(seal.snapshot)
        self.assert_geometry(seal.snapshot, geometry)
        if not geometry.fibre(prefix):
            raise SealIntegrityError("realised prefix is outside the sealed reservoir")
        cache_key = (seal.seal_commitment, prefix.digest)
        cached = self._seal_relative_cache.get(cache_key)
        if cached is not None:
            return cached
        spec = seal.spec
        history = seal.root_history.extend(prefix)
        time = seal.origin_time + k
        evidence: list[SealActionEvidence] = []
        admitted: list[str] = []
        for action in spec.dynamics.actions(history, time):
            branches: list[SealBranchEvidence] = []
            for disturbance in spec.dynamics.disturbances(history, action, time):
                for successor in spec.dynamics.successors(
                    history, action, disturbance, time
                ):
                    extended = prefix.append(action, successor)
                    fibre = geometry.fibre(extended)
                    recursive = False
                    child_support_digest: str | None = None
                    if fibre:
                        if k + 1 == seal.horizon:
                            recursive = True
                        else:
                            child = self.seal_relative_support(seal, extended)
                            recursive = bool(child.actions)
                            child_support_digest = child.digest
                    branches.append(
                        SealBranchEvidence(
                            disturbance=disturbance,
                            successor=successor,
                            conditional_fibre=tuple(tail.digest for tail in fibre),
                            recursive_continuation=recursive,
                            child_support_digest=child_support_digest,
                        )
                    )
            action_evidence = SealActionEvidence(action, tuple(branches))
            evidence.append(action_evidence)
            if action_evidence.valid:
                admitted.append(action)
        result = SealRelativeSupport(
            origin_seal=seal.seal_commitment,
            origin_geometry=geometry.digest,
            prefix=prefix,
            prefix_index=k,
            remaining=seal.horizon - k,
            current_history=history,
            actions=tuple(admitted),
            evidence=tuple(evidence),
        )
        self._seal_relative_cache[cache_key] = result
        return result

    def assurance_context(
        self,
        mode: AssuranceMode,
        spec: ConstructionSpec,
        history: History,
        time: int,
        remaining: int,
        *,
        runtime_regime: str,
        seal: SealRecord | None = None,
        prefix: Tail | None = None,
    ) -> Assurance:
        if remaining < 1:
            raise HorizonError("an assurance context carrying an action requires H>=1")
        spec.assert_valid(time, runtime_regime)
        if mode is AssuranceMode.EXISTENTIAL:
            snapshot = self.reservoir(spec, history, time, remaining)
            geometry = self.geometry_from_snapshot(snapshot)
            self.assert_geometry(snapshot, geometry)
            actions = self.existential_support(geometry)
            witnesses = tuple(
                (
                    action,
                    tuple(tail.digest for tail in snapshot.tails if tail.first_action == action),
                )
                for action in actions
            )
            return ExistentialAssurance(
                mode=mode,
                history=history,
                time=time,
                remaining=remaining,
                validity=spec.validity,
                runtime_regime=runtime_regime,
                spec_commitment=spec.digest,
                reservoir_commitment=snapshot.digest,
                geometry_commitment=geometry.digest,
                actions=actions,
                action_tail_witnesses=witnesses,
            )
        if mode is AssuranceMode.ADAPTIVE_ROBUST:
            support = self.adaptive_support(spec, history, time, remaining)
            return AdaptiveAssurance(
                mode=mode,
                history=history,
                time=time,
                remaining=remaining,
                validity=spec.validity,
                runtime_regime=runtime_regime,
                root_spec_commitment=spec.digest,
                suffix_offset=time - spec.root_time,
                current_reservoir_commitment=support.current_reservoir,
                current_geometry_commitment=support.current_geometry,
                actions=support.actions,
                support=support,
            )
        if mode is AssuranceMode.SEAL_RELATIVE:
            if seal is None or prefix is None:
                raise SpecificationError("seal-relative assurance requires origin seal and prefix")
            if spec.digest != seal.spec_commitment:
                raise SealIntegrityError("a fresh specification cannot replace the origin seal")
            support = self.seal_relative_support(seal, prefix)
            if support.current_history != history:
                raise SealIntegrityError("history does not equal origin history plus sealed prefix")
            if support.remaining != remaining or time != seal.origin_time + support.prefix_index:
                raise HorizonError("seal-relative time/remaining horizon mismatch")
            return SealRelativeAssurance(
                mode=mode,
                history=history,
                time=time,
                remaining=remaining,
                validity=spec.validity,
                runtime_regime=runtime_regime,
                origin_seal=seal.seal_commitment,
                origin_spec_commitment=seal.spec_commitment,
                origin_geometry_commitment=support.origin_geometry,
                prefix=prefix,
                prefix_index=support.prefix_index,
                actions=support.actions,
                support=support,
            )
        raise SpecificationError(f"unknown assurance mode {mode!r}")


@dataclass(frozen=True, slots=True)
class MinervaOutput:
    history: History
    reservoir: ReservoirSnapshot
    seal: SealRecord
    generator_input_commitment: str


class MinervaOperator:
    """Project-declared interpreter + generator, without selector authority."""

    def __init__(self, engine: ReservoirEngine) -> None:
        self.engine = engine

    @staticmethod
    def input_commitment(
        observation: PrivateObservation, spec: ConstructionSpec
    ) -> str:
        # Commit the complete declared logical input interface; not host isolation.

        return commitment(
            {
                "observation_commitment": observation.digest,
                "interpreter_commitment": commitment(spec.interpreter.record),
                "spec_commitment": spec.digest,
            }
        )

    def generate(
        self, observation: PrivateObservation, spec: ConstructionSpec
    ) -> MinervaOutput:
        if observation.observed_at != spec.root_time:
            raise InterpretationError("observation time does not match specification root")
        history = spec.interpreter.interpret(observation)
        reservoir = self.engine.reservoir(
            spec, history, spec.root_time, spec.horizon
        )
        self.engine.assert_snapshot(spec, reservoir)
        seal = self.engine.create_seal(spec, history, observation)
        return MinervaOutput(
            history,
            reservoir,
            seal,
            self.input_commitment(observation, spec),
        )


__all__ = [
    "AdmissibilityCase",
    "AdmissibilityClause",
    "ActionEvidence",
    "AdaptiveAssurance",
    "AdaptiveSupport",
    "AdmissibilityRule",
    "Assurance",
    "AssuranceContext",
    "AssuranceMode",
    "BranchEvidence",
    "BoundarySource",
    "BoundarySourceRole",
    "Certificate",
    "CertificateAudit",
    "CertificateIntegrityError",
    "ConstructionSpec",
    "ConstitutiveBoundary",
    "Declaration",
    "FiniteDynamics",
    "History",
    "HorizonError",
    "IdentityCase",
    "IdentityClause",
    "IdentityRule",
    "InterpretationError",
    "JointVerdict",
    "MinervaOperator",
    "MinervaOutput",
    "NCNCError",
    "PrivateObservation",
    "PrefixFibre",
    "PrefixFibreGeometry",
    "ReservoirEngine",
    "ReservoirSnapshot",
    "RuleRecord",
    "SnapshotAudit",
    "SealActionEvidence",
    "SealBranchEvidence",
    "SealIntegrityError",
    "SealRecord",
    "SealRelativeAssurance",
    "SealRelativeSupport",
    "SpecificationError",
    "Step",
    "Tail",
    "ValidityEnvelope",
    "VersionedInterpreter",
    "ViabilityClause",
    "ViabilityRule",
    "WearLedger",
    "WitnessRecord",
    "canonical_json",
    "commitment",
    "identity_rule_from_clause",
    "viability_rule_from_clause",
]
