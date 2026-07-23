"""Selection, authenticated admission and mediated finite execution.

Mediation here is Python-level: host-level non-bypassability is explicitly out
of scope and is reported as NOT_MACHINE_DECIDABLE by the reference report.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import hmac
from hashlib import sha256
from threading import Lock
from typing import Any, Mapping

from .core import (
    AdaptiveAssurance,
    Assurance,
    AssuranceMode,
    CertificateIntegrityError,
    ConstructionSpec,
    ExistentialAssurance,
    History,
    MinervaOperator,
    MinervaOutput,
    NCNCError,
    PrivateObservation,
    ReservoirEngine,
    SealIntegrityError,
    SealRelativeAssurance,
    SpecificationError,
    canonical_json,
    commitment,
)


class EmptySupportError(NCNCError):
    """Raised when a task selector is called on an empty active support."""


class TokenError(NCNCError):
    """Raised when admission evidence is missing, stale or inauthentic."""


class ExecutionError(NCNCError):
    """Raised when an admitted transition does not match declared dynamics."""


class RecurrenceError(NCNCError):
    """Raised when a history-future recurrence link loses a binding."""


class EmptyDisposition(str, Enum):
    DEFER = "defer"
    SAFE_MODE = "safe-mode"
    ESCALATE = "escalate"
    TERMINATE = "terminate"


class EnforcementVerdict(str, Enum):
    ADMIT = "admit"
    REJECT = "reject"
    DEFER = "defer"
    SAFE_MODE = "safe-mode"
    ESCALATE = "escalate"
    TERMINATE = "terminate"


@dataclass(frozen=True, slots=True)
class EmptySupportPolicy:
    policy_id: str
    version: str
    authority: str
    disposition: EmptyDisposition
    rationale: str

    @property
    def digest(self) -> str:
        return commitment(self)

    def canonical_data(self) -> dict[str, str]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "authority": self.authority,
            "disposition": self.disposition.value,
            "rationale": self.rationale,
        }


class TaskSelector:
    """Ranks only inside an already constructed non-empty support."""

    def select(self, context: Assurance, scores: Mapping[str, float]) -> str:
        if not context.actions:
            raise EmptySupportError(
                "selector is partial: empty active support must use its sealed handler"
            )
        missing = [action for action in context.actions if action not in scores]
        if missing:
            raise ValueError(f"missing task scores for {missing}")
        return sorted(context.actions, key=lambda action: (-scores[action], action))[0]


def _validate_context_validity(
    context: Assurance, runtime_regime: str | None = None
) -> None:
    active_regime = context.runtime_regime if runtime_regime is None else runtime_regime
    if active_regime != context.runtime_regime:
        raise TokenError("runtime regime does not match assurance context")
    if not context.validity.contains(context.time, active_regime):
        raise TokenError("assurance context is outside its validity envelope")


def _validate_action_evidence(context: Assurance, action: str) -> None:
    _validate_context_validity(context)
    if action not in context.actions:
        raise TokenError("proposed action is outside the active support")
    if isinstance(context, ExistentialAssurance):
        witnesses = dict(context.action_tail_witnesses).get(action, ())
        if not witnesses:
            raise TokenError("existential action lacks a tail witness")
        return
    if isinstance(context, AdaptiveAssurance):
        if context.actions != context.support.actions:
            raise TokenError("adaptive context/action list mismatch")
        evidence = context.support.evidence_for(action)
        if evidence is None or not evidence.valid:
            raise TokenError("adaptive action lacks valid branch evidence")
        if context.root_spec_commitment != context.support.spec_commitment:
            raise TokenError("adaptive support changed specification lineage")
        if context.current_reservoir_commitment != context.support.current_reservoir:
            raise TokenError("adaptive current-reservoir evidence mismatch")
        if context.current_geometry_commitment != context.support.current_geometry:
            raise TokenError("adaptive current-geometry evidence mismatch")
        return
    if isinstance(context, SealRelativeAssurance):
        if context.actions != context.support.actions:
            raise TokenError("seal-relative context/action list mismatch")
        if context.origin_seal != context.support.origin_seal:
            raise TokenError("seal-relative context changed the origin seal")
        if context.origin_geometry_commitment != context.support.origin_geometry:
            raise TokenError("seal-relative origin-geometry evidence mismatch")
        if context.prefix != context.support.prefix:
            raise TokenError("seal-relative context changed the realised prefix")
        if context.prefix_index != context.support.prefix_index:
            raise TokenError("seal-relative prefix index mismatch")
        evidence = context.support.evidence_for(action)
        if evidence is None or not evidence.valid:
            raise TokenError("seal-relative action lacks conditional-fibre and recursive K^Sigma evidence")
        return
    raise TokenError("unknown assurance-context type")


def _context_spec_commitment(context: Assurance) -> str:
    if isinstance(context, ExistentialAssurance):
        return context.spec_commitment
    if isinstance(context, AdaptiveAssurance):
        return context.root_spec_commitment
    if isinstance(context, SealRelativeAssurance):
        return context.origin_spec_commitment
    raise TokenError("unknown assurance-context type")


@dataclass(frozen=True, slots=True)
class TokenPayload:
    issuer: str
    action: str
    mode: AssuranceMode
    history_commitment: str
    context_commitment: str
    time: int
    remaining: int
    runtime_regime: str
    issued_at: int
    expires_at: int
    decision_version: str
    enforcement_channel_version: str

    def canonical_data(self) -> dict[str, Any]:
        return {
            "issuer": self.issuer,
            "action": self.action,
            "mode": self.mode,
            "history_commitment": self.history_commitment,
            "context_commitment": self.context_commitment,
            "time": self.time,
            "remaining": self.remaining,
            "runtime_regime": self.runtime_regime,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "decision_version": self.decision_version,
            "enforcement_channel_version": self.enforcement_channel_version,
        }


@dataclass(frozen=True, slots=True)
class AdmissionToken:
    payload: TokenPayload
    signature: str

    @property
    def digest(self) -> str:
        return commitment(self)

    def canonical_data(self) -> dict[str, Any]:
        return {"payload": self.payload, "signature": self.signature}


class TokenAuthority:
    """Issues HMAC-authenticated tokens bound to the complete assurance context.

    The authority is anchored to one reservoir engine: every presented assurance
    context is recomputed through that engine before signing or accepting it, so
    a hand-built context that is merely self-consistent cannot be certified.
    """

    def __init__(
        self,
        issuer: str,
        secret: bytes,
        *,
        engine: ReservoirEngine,
        channel_version: str = "O_enf-v1",
    ) -> None:
        if len(secret) < 32:
            raise ValueError("reference HMAC secret must contain at least 32 bytes")
        self.issuer = issuer
        self._secret = bytes(secret)
        self.engine = engine
        self.channel_version = channel_version
        self._consumed_tokens: set[str] = set()
        self._consumed_decisions: set[str] = set()
        self._token_lock = Lock()
        self._decision_lock = Lock()

    def recompute_context(self, context: Assurance) -> None:
        """Fail closed unless the engine independently reproduces this context."""

        try:
            spec = self.engine.spec_for(_context_spec_commitment(context))
        except SpecificationError as exc:
            raise TokenError(
                f"assurance specification is not registered with the engine: {exc}"
            ) from exc
        kwargs: dict[str, Any] = {}
        if isinstance(context, SealRelativeAssurance):
            try:
                kwargs["seal"] = self.engine.seal_for(context.origin_seal)
            except SpecificationError as exc:
                raise TokenError(
                    f"assurance seal is not registered with the engine: {exc}"
                ) from exc
            kwargs["prefix"] = context.prefix
        try:
            expected = self.engine.assurance_context(
                context.mode,
                spec,
                context.history,
                context.time,
                context.remaining,
                runtime_regime=context.runtime_regime,
                **kwargs,
            )
        except NCNCError as exc:
            raise TokenError(
                f"assurance context does not recompute from the engine: {exc}"
            ) from exc
        if expected != context:
            raise TokenError("assurance context does not recompute from the engine")

    def _mac(self, domain: bytes, value: Any) -> str:
        message = domain + b"\x00" + canonical_json(value).encode("utf-8")
        return hmac.new(self._secret, message, sha256).hexdigest()

    def _sign(self, payload: TokenPayload) -> str:
        return self._mac(b"ncnc-admission-token-v1", payload)

    def sign_decision(self, unsigned_data: Mapping[str, Any]) -> str:
        return self._mac(b"ncnc-enforcement-decision-v1", unsigned_data)

    def verify_decision(self, decision: "EnforcementDecision") -> None:
        expected = self.sign_decision(decision.unsigned_data())
        if not hmac.compare_digest(expected, decision.authorization_tag):
            raise TokenError("enforcement-decision authentication mismatch")
        if decision.issuer != self.issuer:
            raise TokenError("unexpected enforcement-decision issuer")
        if decision.enforcement_channel_version != self.channel_version:
            raise TokenError("enforcement-decision channel version mismatch")

    def consume_token(self, token_digest: str) -> None:
        with self._token_lock:
            if token_digest in self._consumed_tokens:
                raise TokenError("admission-token replay detected")
            self._consumed_tokens.add(token_digest)

    def consume_decision(self, decision_digest: str) -> None:
        with self._decision_lock:
            if decision_digest in self._consumed_decisions:
                raise TokenError("enforcement-decision replay detected")
            self._consumed_decisions.add(decision_digest)

    def issue(
        self,
        context: Assurance,
        action: str,
        *,
        issued_at: int,
        expires_at: int,
        decision_version: str,
    ) -> AdmissionToken:
        if expires_at < issued_at:
            raise TokenError("token expiry precedes issuance")
        _validate_action_evidence(context, action)
        self.recompute_context(context)
        if issued_at < context.validity.not_before:
            raise TokenError("token issuance precedes assurance validity envelope")
        if expires_at > context.validity.not_after:
            raise TokenError("token expiry exceeds assurance validity envelope")
        payload = TokenPayload(
            issuer=self.issuer,
            action=action,
            mode=context.mode,
            history_commitment=context.history.digest,
            context_commitment=context.digest,
            time=context.time,
            remaining=context.remaining,
            runtime_regime=context.runtime_regime,
            issued_at=issued_at,
            expires_at=expires_at,
            decision_version=decision_version,
            enforcement_channel_version=self.channel_version,
        )
        return AdmissionToken(payload, self._sign(payload))

    def verify(
        self,
        token: AdmissionToken,
        context: Assurance,
        action: str,
        *,
        now: int,
        runtime_regime: str,
    ) -> None:
        expected = self._sign(token.payload)
        if not hmac.compare_digest(expected, token.signature):
            raise TokenError("admission-token signature mismatch")
        payload = token.payload
        if payload.issuer != self.issuer:
            raise TokenError("unexpected token issuer")
        if payload.enforcement_channel_version != self.channel_version:
            raise TokenError("enforcement-channel version mismatch")
        if payload.action != action:
            raise TokenError("token is bound to another action")
        if payload.mode is not context.mode:
            raise TokenError("token is bound to another assurance mode")
        if payload.history_commitment != context.history.digest:
            raise TokenError("token is bound to another realised history")
        if payload.context_commitment != context.digest:
            raise TokenError("token is bound to another assurance context")
        if payload.time != context.time or payload.remaining != context.remaining:
            raise TokenError("token time/horizon binding mismatch")
        if payload.runtime_regime != context.runtime_regime:
            raise TokenError("token is bound to another runtime regime")
        _validate_context_validity(context, runtime_regime)
        if not context.validity.contains(now, runtime_regime):
            raise TokenError("assurance validity envelope does not cover enforcement time")
        if not (payload.issued_at <= now <= payload.expires_at):
            raise TokenError("token is not valid at the enforcement time")
        _validate_action_evidence(context, action)
        self.recompute_context(context)


@dataclass(frozen=True, slots=True)
class EnforcementDecision:
    verdict: EnforcementVerdict
    reason: str
    action: str | None
    context_commitment: str
    token_commitment: str | None
    decision_version: str
    empty_handler_commitment: str
    issuer: str
    enforcement_channel_version: str
    history_commitment: str
    spec_commitment: str
    time: int
    remaining: int
    runtime_regime: str
    authorization_tag: str

    def unsigned_data(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "reason": self.reason,
            "action": self.action,
            "context_commitment": self.context_commitment,
            "token_commitment": self.token_commitment,
            "decision_version": self.decision_version,
            "empty_handler_commitment": self.empty_handler_commitment,
            "issuer": self.issuer,
            "enforcement_channel_version": self.enforcement_channel_version,
            "history_commitment": self.history_commitment,
            "spec_commitment": self.spec_commitment,
            "time": self.time,
            "remaining": self.remaining,
            "runtime_regime": self.runtime_regime,
        }

    @property
    def digest(self) -> str:
        return commitment(self)

    def canonical_data(self) -> dict[str, Any]:
        return {**self.unsigned_data(), "authorization_tag": self.authorization_tag}


class Enforcer:
    """Fail-closed decision boundary; it does not choose the task objective."""

    def __init__(
        self,
        authority: TokenAuthority,
        empty_support_policy: EmptySupportPolicy,
        *,
        decision_version: str = "G_enf-v1",
    ) -> None:
        self.authority = authority
        self.empty_support_policy = empty_support_policy
        self.decision_version = decision_version

    def _build_decision(
        self,
        context: Assurance,
        runtime_regime: str,
        verdict: EnforcementVerdict,
        reason: str,
        action: str | None,
        token: AdmissionToken | None,
    ) -> EnforcementDecision:
        unsigned = EnforcementDecision(
            verdict=verdict,
            reason=reason,
            action=action,
            context_commitment=context.digest,
            token_commitment=token.digest if token else None,
            decision_version=self.decision_version,
            empty_handler_commitment=self.empty_support_policy.digest,
            issuer=self.authority.issuer,
            enforcement_channel_version=self.authority.channel_version,
            history_commitment=context.history.digest,
            spec_commitment=_context_spec_commitment(context),
            time=context.time,
            remaining=context.remaining,
            runtime_regime=runtime_regime,
            authorization_tag="",
        )
        return replace(
            unsigned,
            authorization_tag=self.authority.sign_decision(unsigned.unsigned_data()),
        )

    def _empty_decision(
        self, context: Assurance, runtime_regime: str
    ) -> EnforcementDecision:
        mapping = {
            EmptyDisposition.DEFER: EnforcementVerdict.DEFER,
            EmptyDisposition.SAFE_MODE: EnforcementVerdict.SAFE_MODE,
            EmptyDisposition.ESCALATE: EnforcementVerdict.ESCALATE,
            EmptyDisposition.TERMINATE: EnforcementVerdict.TERMINATE,
        }
        return self._build_decision(
            context,
            runtime_regime,
            mapping[self.empty_support_policy.disposition],
            "sealed empty-active-support policy",
            None,
            None,
        )

    def decide(
        self,
        context: Assurance,
        action: str | None,
        token: AdmissionToken | None,
        *,
        now: int,
        runtime_regime: str,
    ) -> EnforcementDecision:
        try:
            _validate_context_validity(context, runtime_regime)
            if not context.validity.contains(now, runtime_regime):
                raise TokenError(
                    "assurance validity envelope does not cover enforcement time"
                )
        except TokenError as exc:
            return self._build_decision(
                context,
                runtime_regime,
                EnforcementVerdict.REJECT,
                str(exc),
                action,
                token,
            )
        if not context.actions:
            return self._empty_decision(context, runtime_regime)
        if action is None or token is None:
            return self._build_decision(
                context,
                runtime_regime,
                EnforcementVerdict.REJECT,
                "missing action or authenticated admission token",
                action,
                token,
            )
        try:
            self.authority.verify(
                token,
                context,
                action,
                now=now,
                runtime_regime=runtime_regime,
            )
            if token.payload.decision_version != self.decision_version:
                raise TokenError("enforcement decision version mismatch")
            self.authority.consume_token(token.digest)
        except TokenError as exc:
            return self._build_decision(
                context,
                runtime_regime,
                EnforcementVerdict.REJECT,
                str(exc),
                action,
                token,
            )
        return self._build_decision(
            context,
            runtime_regime,
            EnforcementVerdict.ADMIT,
            "authenticated action-bound assurance evidence",
            action,
            token,
        )


@dataclass(frozen=True, slots=True)
class ExecutionTrace:
    time: int
    pre_history: History
    action: str
    disturbance: str
    successor: str
    enforcement_decision: str
    decision_commitment: str
    decision_version: str
    context_commitment: str
    token_commitment: str | None
    runtime_regime: str
    executed: bool
    post_history: History

    @property
    def digest(self) -> str:
        return commitment(self)

    def canonical_data(self) -> dict[str, Any]:
        return {
            "time": self.time,
            "pre_history": self.pre_history,
            "action": self.action,
            "disturbance": self.disturbance,
            "successor": self.successor,
            "enforcement_decision": self.enforcement_decision,
            "decision_commitment": self.decision_commitment,
            "decision_version": self.decision_version,
            "context_commitment": self.context_commitment,
            "token_commitment": self.token_commitment,
            "runtime_regime": self.runtime_regime,
            "executed": self.executed,
            "post_history": self.post_history,
        }


@dataclass(frozen=True, slots=True)
class HistoryFutureRecurrence:
    """One certified history в†’ future fibre в†’ event в†’ history update link."""

    prior_spec_commitment: str
    prior_seal_commitment: str
    prior_history_commitment: str
    prior_observation_commitment: str
    prior_generator_input_commitment: str
    assurance_context_commitment: str
    enforcement_decision_commitment: str
    execution_trace_commitment: str
    next_spec_commitment: str
    next_observation_commitment: str
    next_generator_input_commitment: str
    next_history_commitment: str
    next_reservoir_commitment: str
    next_seal_commitment: str
    provenance_link: str
    next_runtime_regime: str
    link_commitment: str

    @staticmethod
    def provenance_token(
        prior_seal_commitment: str, execution_trace_commitment: str
    ) -> str:
        return "history-future:" + commitment(
            {
                "prior_seal_commitment": prior_seal_commitment,
                "execution_trace_commitment": execution_trace_commitment,
            }
        )

    @staticmethod
    def _bindings(
        prior_spec: ConstructionSpec,
        prior_output: MinervaOutput,
        prior_observation: PrivateObservation,
        assurance_context: Assurance,
        enforcement_decision: EnforcementDecision,
        trace: ExecutionTrace,
        next_spec: ConstructionSpec,
        next_output: MinervaOutput,
        next_observation: PrivateObservation,
        next_runtime_regime: str,
    ) -> dict[str, str]:
        return {
            "prior_spec_commitment": prior_spec.digest,
            "prior_seal_commitment": prior_output.seal.seal_commitment,
            "prior_history_commitment": prior_output.history.digest,
            "prior_observation_commitment": prior_observation.digest,
            "prior_generator_input_commitment": prior_output.generator_input_commitment,
            "assurance_context_commitment": assurance_context.digest,
            "enforcement_decision_commitment": enforcement_decision.digest,
            "execution_trace_commitment": trace.digest,
            "next_spec_commitment": next_spec.digest,
            "next_observation_commitment": next_observation.digest,
            "next_generator_input_commitment": next_output.generator_input_commitment,
            "next_history_commitment": next_output.history.digest,
            "next_reservoir_commitment": next_output.reservoir.digest,
            "next_seal_commitment": next_output.seal.seal_commitment,
            "provenance_link": HistoryFutureRecurrence.provenance_token(
                prior_output.seal.seal_commitment, trace.digest
            ),
            "next_runtime_regime": next_runtime_regime,
        }

    @staticmethod
    def _validate_operational_link(
        engine: ReservoirEngine,
        prior_spec: ConstructionSpec,
        prior_output: MinervaOutput,
        prior_observation: PrivateObservation,
        assurance_context: Assurance,
        enforcement_decision: EnforcementDecision,
        authority: TokenAuthority,
        trace: ExecutionTrace,
        next_spec: ConstructionSpec,
        next_output: MinervaOutput,
        next_observation: PrivateObservation,
        next_runtime_regime: str,
    ) -> None:
        if trace.time != prior_spec.root_time:
            raise RecurrenceError("recurrence trace is not rooted at the prior specification")
        try:
            prior_spec.assert_valid(trace.time, trace.runtime_regime)
        except SpecificationError as exc:
            raise RecurrenceError(f"recurrence prior specification is invalid: {exc}") from exc
        if prior_output.seal.spec_commitment != prior_spec.digest:
            raise RecurrenceError("recurrence prior specification commitment mismatch")
        try:
            prior_output.seal.verify_observation(prior_observation)
        except SealIntegrityError as exc:
            raise RecurrenceError(f"recurrence prior observation/seal mismatch: {exc}") from exc
        if prior_output.generator_input_commitment != MinervaOperator.input_commitment(
            prior_observation, prior_spec
        ):
            raise RecurrenceError("recurrence prior generator input commitment mismatch")
        try:
            engine.assert_snapshot(prior_spec, prior_output.reservoir)
        except CertificateIntegrityError as exc:
            raise RecurrenceError(f"recurrence prior reservoir recomputation failed: {exc}") from exc
        if (
            prior_output.history != prior_output.seal.root_history
            or prior_output.reservoir != prior_output.seal.snapshot
        ):
            raise RecurrenceError("recurrence prior output is detached from its seal")

        try:
            _validate_action_evidence(assurance_context, trace.action)
        except TokenError as exc:
            raise RecurrenceError(
                f"recurrence assurance context rejects the action: {exc}"
            ) from exc
        if (
            assurance_context.history != prior_output.history
            or _context_spec_commitment(assurance_context) != prior_spec.digest
            or assurance_context.time != trace.time
            or assurance_context.remaining != prior_spec.horizon
            or assurance_context.runtime_regime != trace.runtime_regime
        ):
            raise RecurrenceError(
                "recurrence assurance context does not bind the prior environment"
            )
        try:
            authority.verify_decision(enforcement_decision)
        except TokenError as exc:
            raise RecurrenceError(
                f"recurrence enforcement decision authentication mismatch: {exc}"
            ) from exc
        if (
            enforcement_decision.verdict is not EnforcementVerdict.ADMIT
            or enforcement_decision.action != trace.action
            or enforcement_decision.token_commitment is None
            or enforcement_decision.context_commitment != assurance_context.digest
            or enforcement_decision.history_commitment != prior_output.history.digest
            or enforcement_decision.spec_commitment != prior_spec.digest
            or enforcement_decision.time != trace.time
            or enforcement_decision.remaining != assurance_context.remaining
            or enforcement_decision.runtime_regime != trace.runtime_regime
        ):
            raise RecurrenceError(
                "recurrence enforcement decision does not bind the admitted step"
            )
        if (
            trace.decision_commitment != enforcement_decision.digest
            or trace.decision_version != enforcement_decision.decision_version
            or trace.context_commitment != assurance_context.digest
            or trace.token_commitment != enforcement_decision.token_commitment
            or trace.enforcement_decision != enforcement_decision.verdict.value
            or trace.runtime_regime != enforcement_decision.runtime_regime
        ):
            raise RecurrenceError(
                "recurrence execution trace does not bind the authenticated decision"
            )
        if trace.pre_history != prior_output.history:
            raise RecurrenceError("recurrence trace does not start from the sealed history")
        if not trace.executed:
            raise RecurrenceError("recurrence requires an executed ADMIT trace")
        expected_post = trace.pre_history.append(trace.action, trace.successor)
        if trace.post_history != expected_post:
            raise RecurrenceError("recurrence post-history is not the exact append")
        if trace.disturbance not in prior_spec.dynamics.disturbances(
            trace.pre_history, trace.action, trace.time
        ) or trace.successor not in prior_spec.dynamics.successors(
            trace.pre_history, trace.action, trace.disturbance, trace.time
        ):
            raise RecurrenceError("recurrence trace lies outside declared dynamics")
        if next_spec.root_time != trace.time + 1:
            raise RecurrenceError("recurrence next root is not the successor time")
        if next_observation.observed_at != next_spec.root_time:
            raise RecurrenceError("recurrence next observation time does not match the next root")
        provenance_link = HistoryFutureRecurrence.provenance_token(
            prior_output.seal.seal_commitment, trace.digest
        )
        if provenance_link not in next_spec.provenance:
            raise RecurrenceError(
                "recurrence provenance link is absent from the next specification"
            )
        try:
            next_spec.assert_valid(next_spec.root_time, next_runtime_regime)
        except SpecificationError as exc:
            raise RecurrenceError(f"recurrence next specification is invalid: {exc}") from exc
        if next_output.seal.spec_commitment != next_spec.digest:
            raise RecurrenceError("recurrence next specification commitment mismatch")
        try:
            next_output.seal.verify_observation(next_observation)
        except SealIntegrityError as exc:
            raise RecurrenceError(f"recurrence next observation/seal mismatch: {exc}") from exc
        if next_output.generator_input_commitment != MinervaOperator.input_commitment(
            next_observation, next_spec
        ):
            raise RecurrenceError("recurrence next generator input commitment mismatch")
        try:
            engine.assert_snapshot(next_spec, next_output.reservoir)
        except CertificateIntegrityError as exc:
            raise RecurrenceError(f"recurrence next reservoir recomputation failed: {exc}") from exc
        if (
            next_output.history != next_output.seal.root_history
            or next_output.reservoir != next_output.seal.snapshot
        ):
            raise RecurrenceError("recurrence next output is detached from its seal")
        if next_output.history != trace.post_history:
            raise RecurrenceError(
                "recurrence next history does not equal the realised post-history"
            )

    @classmethod
    def create(
        cls,
        engine: ReservoirEngine,
        prior_spec: ConstructionSpec,
        prior_output: MinervaOutput,
        prior_observation: PrivateObservation,
        assurance_context: Assurance,
        enforcement_decision: EnforcementDecision,
        authority: TokenAuthority,
        trace: ExecutionTrace,
        next_spec: ConstructionSpec,
        next_output: MinervaOutput,
        next_observation: PrivateObservation,
        *,
        next_runtime_regime: str,
    ) -> "HistoryFutureRecurrence":
        cls._validate_operational_link(
            engine,
            prior_spec,
            prior_output,
            prior_observation,
            assurance_context,
            enforcement_decision,
            authority,
            trace,
            next_spec,
            next_output,
            next_observation,
            next_runtime_regime,
        )
        bindings = cls._bindings(
            prior_spec,
            prior_output,
            prior_observation,
            assurance_context,
            enforcement_decision,
            trace,
            next_spec,
            next_output,
            next_observation,
            next_runtime_regime,
        )
        record = cls(**bindings, link_commitment=commitment(bindings))
        record.verify(
            engine,
            prior_spec,
            prior_output,
            prior_observation,
            assurance_context,
            enforcement_decision,
            authority,
            trace,
            next_spec,
            next_output,
            next_observation,
            next_runtime_regime=next_runtime_regime,
        )
        return record

    @classmethod
    def advance(
        cls,
        engine: ReservoirEngine,
        prior_spec: ConstructionSpec,
        prior_output: MinervaOutput,
        prior_observation: PrivateObservation,
        assurance_context: Assurance,
        enforcement_decision: EnforcementDecision,
        authority: TokenAuthority,
        trace: ExecutionTrace,
        next_spec: ConstructionSpec,
        next_observation: PrivateObservation,
        *,
        next_runtime_regime: str,
    ) -> tuple["HistoryFutureRecurrence", MinervaOutput]:
        next_output = MinervaOperator(engine).generate(next_observation, next_spec)
        return (
            cls.create(
                engine,
                prior_spec,
                prior_output,
                prior_observation,
                assurance_context,
                enforcement_decision,
                authority,
                trace,
                next_spec,
                next_output,
                next_observation,
                next_runtime_regime=next_runtime_regime,
            ),
            next_output,
        )

    def verify(
        self,
        engine: ReservoirEngine,
        prior_spec: ConstructionSpec,
        prior_output: MinervaOutput,
        prior_observation: PrivateObservation,
        assurance_context: Assurance,
        enforcement_decision: EnforcementDecision,
        authority: TokenAuthority,
        trace: ExecutionTrace,
        next_spec: ConstructionSpec,
        next_output: MinervaOutput,
        next_observation: PrivateObservation,
        *,
        next_runtime_regime: str,
    ) -> None:
        self._validate_operational_link(
            engine,
            prior_spec,
            prior_output,
            prior_observation,
            assurance_context,
            enforcement_decision,
            authority,
            trace,
            next_spec,
            next_output,
            next_observation,
            next_runtime_regime,
        )
        expected = self._bindings(
            prior_spec,
            prior_output,
            prior_observation,
            assurance_context,
            enforcement_decision,
            trace,
            next_spec,
            next_output,
            next_observation,
            next_runtime_regime,
        )
        if self._payload() != expected:
            raise RecurrenceError("recurrence certificate field binding mismatch")
        if self.link_commitment != commitment(expected):
            raise RecurrenceError("recurrence link commitment mismatch")

    def _payload(self) -> dict[str, str]:
        return {
            "prior_spec_commitment": self.prior_spec_commitment,
            "prior_seal_commitment": self.prior_seal_commitment,
            "prior_history_commitment": self.prior_history_commitment,
            "prior_observation_commitment": self.prior_observation_commitment,
            "prior_generator_input_commitment": self.prior_generator_input_commitment,
            "assurance_context_commitment": self.assurance_context_commitment,
            "enforcement_decision_commitment": self.enforcement_decision_commitment,
            "execution_trace_commitment": self.execution_trace_commitment,
            "next_spec_commitment": self.next_spec_commitment,
            "next_observation_commitment": self.next_observation_commitment,
            "next_generator_input_commitment": self.next_generator_input_commitment,
            "next_history_commitment": self.next_history_commitment,
            "next_reservoir_commitment": self.next_reservoir_commitment,
            "next_seal_commitment": self.next_seal_commitment,
            "provenance_link": self.provenance_link,
            "next_runtime_regime": self.next_runtime_regime,
        }

    def canonical_data(self) -> dict[str, str]:
        return {**self._payload(), "link_commitment": self.link_commitment}


@dataclass(frozen=True, slots=True)
class TraceEntry:
    index: int
    previous_commitment: str
    trace: ExecutionTrace
    entry_commitment: str

    @classmethod
    def create(
        cls, index: int, previous_commitment: str, trace: ExecutionTrace
    ) -> "TraceEntry":
        payload = {
            "index": index,
            "previous_commitment": previous_commitment,
            "trace": trace,
        }
        return cls(index, previous_commitment, trace, commitment(payload))

    def verify(self) -> None:
        expected = commitment(
            {
                "index": self.index,
                "previous_commitment": self.previous_commitment,
                "trace": self.trace,
            }
        )
        if expected != self.entry_commitment:
            raise ExecutionError("execution-trace chain commitment mismatch")

    def canonical_data(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "previous_commitment": self.previous_commitment,
            "trace": self.trace,
            "entry_commitment": self.entry_commitment,
        }


@dataclass(frozen=True, slots=True)
class TraceLedger:
    entries: tuple[TraceEntry, ...] = ()

    @property
    def digest(self) -> str:
        return commitment(self)

    def append(self, trace: ExecutionTrace) -> "TraceLedger":
        if self.entries and self.entries[-1].trace.post_history != trace.pre_history:
            raise ExecutionError("execution trace is discontinuous with the ledger head")
        previous = self.entries[-1].entry_commitment if self.entries else "0" * 64
        entry = TraceEntry.create(len(self.entries), previous, trace)
        return TraceLedger(self.entries + (entry,))

    def verify(self) -> None:
        previous = "0" * 64
        prior_history: History | None = None
        for expected_index, entry in enumerate(self.entries):
            entry.verify()
            if entry.index != expected_index or entry.previous_commitment != previous:
                raise ExecutionError("execution-trace chain order mismatch")
            if prior_history is not None and entry.trace.pre_history != prior_history:
                raise ExecutionError("execution-trace history continuity mismatch")
            previous = entry.entry_commitment
            prior_history = entry.trace.post_history

    def canonical_data(self) -> dict[str, Any]:
        return {"entries": self.entries}


class MediatedExecutor:
    """Executes only authenticated one-shot decisions bound to state and specification."""

    def __init__(self, authority: TokenAuthority) -> None:
        self.authority = authority

    def _verify_binding(
        self,
        spec: ConstructionSpec,
        history: History,
        action: str,
        decision: EnforcementDecision,
        time: int,
        runtime_regime: str,
    ) -> None:
        try:
            self.authority.verify_decision(decision)
        except TokenError as exc:
            raise ExecutionError(str(exc)) from exc
        if decision.history_commitment != history.digest:
            raise ExecutionError("enforcement decision is bound to another history")
        if decision.spec_commitment != spec.digest:
            raise ExecutionError("enforcement decision is bound to another specification")
        if decision.time != time:
            raise ExecutionError("enforcement decision is bound to another time")
        if decision.runtime_regime != runtime_regime:
            raise ExecutionError("enforcement decision is bound to another runtime regime")
        try:
            spec.assert_valid(time, runtime_regime)
        except SpecificationError as exc:
            raise ExecutionError(str(exc)) from exc
        expected_remaining = spec.horizon - (time - spec.root_time)
        if expected_remaining < 0 or decision.remaining != expected_remaining:
            raise ExecutionError("enforcement decision horizon binding mismatch")
        if decision.action is not None and decision.action != action:
            raise ExecutionError("enforcement decision is bound to another action")

    @staticmethod
    def _trace(
        time: int,
        history: History,
        action: str,
        disturbance: str,
        successor: str,
        decision: EnforcementDecision,
        executed: bool,
        post_history: History,
    ) -> ExecutionTrace:
        return ExecutionTrace(
            time=time,
            pre_history=history,
            action=action,
            disturbance=disturbance,
            successor=successor,
            enforcement_decision=decision.verdict.value,
            decision_commitment=decision.digest,
            decision_version=decision.decision_version,
            context_commitment=decision.context_commitment,
            token_commitment=decision.token_commitment,
            runtime_regime=decision.runtime_regime,
            executed=executed,
            post_history=post_history,
        )

    def attempt(
        self,
        spec: ConstructionSpec,
        history: History,
        action: str,
        disturbance: str,
        successor: str,
        decision: EnforcementDecision,
        *,
        time: int,
        runtime_regime: str,
    ) -> ExecutionTrace:
        self._verify_binding(
            spec, history, action, decision, time, runtime_regime
        )
        try:
            self.authority.consume_decision(decision.digest)
        except TokenError as exc:
            raise ExecutionError(str(exc)) from exc
        if decision.verdict is not EnforcementVerdict.ADMIT:
            return self._trace(
                time,
                history,
                action,
                disturbance,
                successor,
                decision,
                False,
                history,
            )
        if decision.action != action or decision.token_commitment is None:
            raise ExecutionError("ADMIT decision lacks an action-bound token commitment")
        if disturbance not in spec.dynamics.disturbances(history, action, time):
            raise ExecutionError("disturbance lies outside declared dynamics")
        if successor not in spec.dynamics.successors(
            history, action, disturbance, time
        ):
            raise ExecutionError("successor lies outside declared dynamics")
        return self._trace(
            time,
            history,
            action,
            disturbance,
            successor,
            decision,
            True,
            history.append(action, successor),
        )

def causal_intervention_witness(
    admitted: ExecutionTrace, blocked: ExecutionTrace
) -> bool:
    """Check the matched verdict-intervention condition from Proposition 5.4."""

    matched = (
        admitted.pre_history == blocked.pre_history
        and admitted.action == blocked.action
        and admitted.disturbance == blocked.disturbance
        and admitted.successor == blocked.successor
    )
    return matched and admitted.executed != blocked.executed


__all__ = [
    "AdmissionToken",
    "EmptyDisposition",
    "EmptySupportError",
    "EmptySupportPolicy",
    "EnforcementDecision",
    "EnforcementVerdict",
    "Enforcer",
    "ExecutionError",
    "ExecutionTrace",
    "HistoryFutureRecurrence",
    "MediatedExecutor",
    "RecurrenceError",
    "TraceEntry",
    "TraceLedger",
    "TaskSelector",
    "TokenAuthority",
    "TokenError",
    "TokenPayload",
    "causal_intervention_witness",
]
