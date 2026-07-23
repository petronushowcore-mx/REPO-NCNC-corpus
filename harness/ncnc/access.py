"""Channel-relative non-absorption and bounded-query reconstruction tools."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Callable, Iterable, Sequence

from .core import NCNCError, canonical_json, commitment


class QueryBudgetExceeded(NCNCError):
    """Raised when an adaptive membership attack exceeds its sealed budget."""


@dataclass(frozen=True, slots=True)
class ChannelCase:
    case_id: str
    optimizer_observation: Any
    privileged_target: Any

    def canonical_data(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "optimizer_observation": self.optimizer_observation,
            "privileged_target": self.privileged_target,
        }


@dataclass(frozen=True, slots=True)
class FibreCollision:
    observation_commitment: str
    left_case: str
    right_case: str
    left_target: Any
    right_target: Any

    def canonical_data(self) -> dict[str, Any]:
        return {
            "observation_commitment": self.observation_commitment,
            "left_case": self.left_case,
            "right_case": self.right_case,
            "left_target": self.left_target,
            "right_target": self.right_target,
        }


def find_fibre_collisions(cases: Iterable[ChannelCase]) -> tuple[FibreCollision, ...]:
    """Find target-changing fibres of the complete declared optimizer channel."""

    groups: dict[str, list[ChannelCase]] = {}
    for case in cases:
        key = commitment(case.optimizer_observation)
        groups.setdefault(key, []).append(case)
    collisions: list[FibreCollision] = []
    for observation_digest, group in sorted(groups.items()):
        ordered = sorted(group, key=lambda item: item.case_id)
        for index, left in enumerate(ordered):
            for right in ordered[index + 1 :]:
                if canonical_json(left.privileged_target) == canonical_json(
                    right.privileged_target
                ):
                    continue
                collisions.append(
                    FibreCollision(
                        observation_commitment=observation_digest,
                        left_case=left.case_id,
                        right_case=right.case_id,
                        left_target=left.privileged_target,
                        right_target=right.privileged_target,
                    )
                )
    return tuple(collisions)


def exact_factorisation_map(cases: Iterable[ChannelCase]) -> dict[str, Any] | None:
    """Return O->target map when it exists; otherwise return None."""

    result: dict[str, Any] = {}
    for case in cases:
        key = canonical_json(case.optimizer_observation)
        if key in result and canonical_json(result[key]) != canonical_json(
            case.privileged_target
        ):
            return None
        result[key] = case.privileged_target
    return result


@dataclass(frozen=True, slots=True)
class BoundaryHypothesis:
    name: str
    domain: tuple[str, ...]
    admitted: frozenset[str]

    def __post_init__(self) -> None:
        if len(set(self.domain)) != len(self.domain):
            raise ValueError("boundary domain points must be unique")
        if not self.admitted.issubset(set(self.domain)):
            raise ValueError("boundary admits a point outside its declared domain")

    def answer(self, point: str) -> bool:
        if point not in self.domain:
            raise KeyError(point)
        return point in self.admitted

    def canonical_data(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "domain": self.domain,
            "admitted": tuple(sorted(self.admitted)),
        }


@dataclass(frozen=True, slots=True)
class QueryEvent:
    index: int
    point: str
    answer: bool

    def canonical_data(self) -> dict[str, Any]:
        return {"index": self.index, "point": self.point, "answer": self.answer}


class MembershipOracle:
    """Budgeted membership surface used only by the adversarial instrument."""

    def __init__(self, boundary: BoundaryHypothesis, budget: int) -> None:
        if budget < 0:
            raise ValueError("query budget must be non-negative")
        self.boundary = boundary
        self.budget = budget
        self._events: list[QueryEvent] = []

    @property
    def events(self) -> tuple[QueryEvent, ...]:
        return tuple(self._events)

    @property
    def remaining(self) -> int:
        return self.budget - len(self._events)

    def query(self, point: str) -> bool:
        if self.remaining <= 0:
            raise QueryBudgetExceeded("sealed membership-query budget exhausted")
        answer = self.boundary.answer(point)
        self._events.append(QueryEvent(len(self._events) + 1, point, answer))
        return answer


@dataclass(frozen=True, slots=True)
class AttackResult:
    initial_hypotheses: int
    remaining_hypotheses: tuple[str, ...]
    events: tuple[QueryEvent, ...]
    exact_reconstruction: bool
    leakage_bits: float
    budget_exhausted: bool

    def canonical_data(self) -> dict[str, Any]:
        return {
            "initial_hypotheses": self.initial_hypotheses,
            "remaining_hypotheses": self.remaining_hypotheses,
            "events": self.events,
            "exact_reconstruction": self.exact_reconstruction,
            "leakage_bits": round(self.leakage_bits, 12),
            "budget_exhausted": self.budget_exhausted,
        }


class GreedyVersionSpaceAttack:
    """Choose membership queries that most evenly split the version space."""

    @staticmethod
    def _choose_point(
        candidates: Sequence[BoundaryHypothesis], queried: set[str]
    ) -> str | None:
        if not candidates:
            return None
        domain = candidates[0].domain
        if any(candidate.domain != domain for candidate in candidates):
            raise ValueError("all boundary hypotheses must share one ordered domain")
        scored: list[tuple[int, str]] = []
        for point in domain:
            if point in queried:
                continue
            yes = sum(candidate.answer(point) for candidate in candidates)
            no = len(candidates) - yes
            if yes == 0 or no == 0:
                continue
            scored.append((min(yes, no), point))
        if not scored:
            return None
        return sorted(scored, key=lambda item: (-item[0], item[1]))[0][1]

    def run(
        self,
        hypotheses: Sequence[BoundaryHypothesis],
        oracle: MembershipOracle,
    ) -> AttackResult:
        if not hypotheses:
            raise ValueError("at least one hypothesis is required")
        names = tuple(item.name for item in hypotheses)
        if len(set(names)) != len(names):
            raise ValueError("boundary hypothesis names must be unique")
        domain = hypotheses[0].domain
        if any(candidate.domain != domain for candidate in hypotheses):
            raise ValueError("all boundary hypotheses must share one ordered domain")
        if oracle.boundary not in hypotheses:
            raise ValueError("actual boundary must be in the declared version space")
        candidates = list(hypotheses)
        queried: set[str] = set()
        while len(candidates) > 1 and oracle.remaining > 0:
            point = self._choose_point(candidates, queried)
            if point is None:
                break
            answer = oracle.query(point)
            queried.add(point)
            candidates = [item for item in candidates if item.answer(point) == answer]
        remaining = tuple(sorted(item.name for item in candidates))
        leakage = math.log2(len(hypotheses) / len(candidates)) if candidates else math.inf
        return AttackResult(
            initial_hypotheses=len(hypotheses),
            remaining_hypotheses=remaining,
            events=oracle.events,
            exact_reconstruction=len(candidates) == 1,
            leakage_bits=leakage,
            budget_exhausted=oracle.remaining == 0 and len(candidates) > 1,
        )


@dataclass(frozen=True, slots=True)
class LeakagePolicy:
    maximum_queries: int
    maximum_bits: float

    def __post_init__(self) -> None:
        if self.maximum_queries < 0:
            raise ValueError("maximum query leakage must be non-negative")
        if self.maximum_bits < 0 or math.isnan(self.maximum_bits):
            raise ValueError("maximum bit leakage must be non-negative and not NaN")

    def accepts(self, result: AttackResult) -> bool:
        return (
            len(result.events) <= self.maximum_queries
            and result.leakage_bits <= self.maximum_bits
            and not result.exact_reconstruction
        )


__all__ = [
    "AttackResult",
    "BoundaryHypothesis",
    "ChannelCase",
    "FibreCollision",
    "GreedyVersionSpaceAttack",
    "LeakagePolicy",
    "MembershipOracle",
    "QueryBudgetExceeded",
    "QueryEvent",
    "exact_factorisation_map",
    "find_fibre_collisions",
]
