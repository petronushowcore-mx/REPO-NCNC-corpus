#!/usr/bin/env python3
"""Static cross-artifact contract gate for the NCNC paper pair and harness."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping


PAIR_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True, slots=True)
class GateCheck:
    check_id: str
    passed: bool
    detail: str

    def as_dict(self) -> dict[str, object]:
        return {
            "check_id": self.check_id,
            "passed": self.passed,
            "detail": self.detail,
        }


@dataclass(frozen=True, slots=True)
class GateReport:
    schema: str
    checks: tuple[GateCheck, ...]

    @property
    def successful(self) -> bool:
        return all(check.passed for check in self.checks)

    def payload(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "checks": [check.as_dict() for check in self.checks],
            "successful": self.successful,
        }

    @property
    def digest(self) -> str:
        encoded = json.dumps(
            self.payload(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return sha256(encoded).hexdigest()


def load_surfaces(root: Path = PAIR_ROOT) -> dict[str, str]:
    paths = {
        "formal": root / "Non-Causal-Non-Causality.md",
        "bridge": root / "Reality-Catches-the-Predicate.md",
        "map": root / "00-PAIR-MAP.md",
        "readme": root / "harness" / "README.md",
        "verification_map": root / "harness" / "VERIFICATION-MAP.md",
        "core": root / "harness" / "ncnc" / "core.py",
        "control": root / "harness" / "ncnc" / "control.py",
        "access": root / "harness" / "ncnc" / "access.py",
        "report": root / "harness" / "ncnc" / "report.py",
        "scenarios": root / "harness" / "ncnc" / "scenarios.py",
        "manifest_builder": root / "harness" / "build_manifest.py",
        # The bundle producer was outside the fence: every artifact the bundle pins was
        # watched, but the code that decides what the bundle asserts was not, so its
        # guards could be weakened without a single gate check moving.
        "bundle_builder": root / "harness" / "check_all.py",
    }
    return {name: path.read_text(encoding="utf-8") for name, path in paths.items()}


def evaluate_surfaces(surfaces: Mapping[str, str]) -> GateReport:
    checks: list[GateCheck] = []

    def require(check_id: str, surface: str, needles: tuple[str, ...]) -> None:
        text = surfaces[surface]
        missing = tuple(needle for needle in needles if needle not in text)
        checks.append(
            GateCheck(
                check_id,
                not missing,
                "present" if not missing else "missing: " + " | ".join(missing),
            )
        )

    def forbid(check_id: str, surface_names: tuple[str, ...], needles: tuple[str, ...]) -> None:
        hits = tuple(
            f"{surface}:{needle}"
            for surface in surface_names
            for needle in needles
            if needle in surfaces[surface]
        )
        checks.append(
            GateCheck(
                check_id,
                not hits,
                "absent" if not hits else "forbidden: " + " | ".join(hits),
            )
        )

    def forbid_control_characters(
        check_id: str, surface_names: tuple[str, ...]
    ) -> None:
        hits = tuple(
            f"{surface}:U+{ord(char):04X}"
            for surface in surface_names
            for char in surfaces[surface]
            if ord(char) < 32 and char not in "\n\r\t"
        )
        checks.append(
            GateCheck(
                check_id,
                not hits,
                "absent" if not hits else "forbidden control characters: " + " | ".join(hits),
            )
        )

    formal_five_link = "\n".join(
        (
            r"(B_{u,t}^{v_B},",
            r"A_{u,t,0:H},",
            r"\Theta_{u,t}^{H},",
            r"\mathcal R_{u,t}^{H},",
            r"\mathcal G(\mathcal R_{u,t}^{H}),",
        )
    )
    map_five_link = "\n".join(
        (
            r"(B_{u,t}^{v_B},",
            r"A_{u,t,0:H},",
            r"\Theta_{u,t}^{H},",
            r"\mathcal{R}_{u,t}^{H},",
            r"\mathcal G(\mathcal R_{u,t}^{H}),",
        )
    )
    formal_compile = "\n".join(
        (
            r"B_{u,t}^{v_B}",
            r"&\xrightarrow{\ \mathsf{compile}\ }",
            r"A_{u,t,0:H},\\",
        )
    )
    formal_reservoir = "\n".join(
        (
            r"(h_t,H,\Theta_{u,t}^{H}[I_u,A,V,\mathsf{Dyn},\mathsf{Val}])",
            r"&\xrightarrow{\ \mathsf{filter\ reachable\ tails}\ }",
            r"\mathcal R_{u,t}^{H},\\",
        )
    )
    formal_geometry = "\n".join(
        (
            r"\mathcal R_{u,t}^{H}",
            r"&\xrightarrow{\ \mathsf{exact\ prefix\text{-}fibres}\ }",
            r"\mathcal G(\mathcal R_{u,t}^{H}),\\",
        )
    )
    formal_projection = "\n".join(
        (
            r"\mathcal G(\mathcal R_{u,t}^{H})",
            r"&\xrightarrow{\ \mathsf{First},\ H\ge 1\ }",
            r"\Pi_{u,t}^{\exists,H}.",
        )
    )
    five_link_requirements = (
        ("formal", formal_five_link),
        ("formal", formal_compile),
        ("formal", formal_reservoir),
        ("formal", formal_geometry),
        ("formal", formal_projection),
        (
            "bridge",
            "Boundary → executable admissibility → admitted tails → exact "
            "prefix–fibre geometry → existential support.",
        ),
        ("map", map_five_link),
        (
            "map",
            r"| `B → A` | `\mathsf{compile}(B)` |",
        ),
        (
            "map",
            r"| `\mathcal R → \mathcal G(\mathcal R)` | exact prefix–fibre derivation |",
        ),
        (
            "readme",
            r"`B\xrightarrow{\mathsf{compile}}A`",
        ),
        (
            "readme",
            r"`\mathcal G(\mathcal R)\xrightarrow{\mathsf{First}}\Pi^{\exists}`",
        ),
        (
            "verification_map",
            r"| `\mathcal R → \mathcal G(\mathcal R)` | `PrefixFibreGeometry`, "
            r"`geometry_from_snapshot`, `assert_geometry` |",
        ),
        (
            "verification_map",
            r"| `\mathcal G(\mathcal R) → \Pi^{\exists}` | `existential_support` |",
        ),
        (
            "report",
            "an authorised B revision creates a different admissible region, "
            "which changes R, G(R) and existential support before execution",
        ),
    )
    five_link_missing = tuple(
        f"{surface}:{needle}"
        for surface, needle in five_link_requirements
        if needle not in surfaces[surface]
    )
    checks.append(
        GateCheck(
            "five-link-architecture-contract",
            not five_link_missing,
            "present"
            if not five_link_missing
            else "missing: " + " | ".join(five_link_missing),
        )
    )

    require(
        "formal-object-contract",
        "formal",
        (
            r"\mathsf{Int}_{u,t}^{v}",
            r"\mathsf{AssurCtx}_t",
            r"\mathsf{Val}_{u,t}^{H}",
            r"O_{\mathrm{enf}}",
            r"G_{\mathrm{enf}}^{v_G}",
            r"\Pi_t^{\mathrm{act}}=\varnothing",
            r"\mathsf K_k^{\Sigma}",
            r"\mathsf K,",
            r"\mathsf{Int}_{u,t}^{v},",
            "the interpreter is versioned and attributed, all three inputs are available at time `t`",
            "At `H=1`, the shallow one-step seal condition and Definition 4.5 coincide extensionally",
            "every realised disturbance and successor remains inside the dynamics and disturbance declaration fixed by `\\Sigma`",
            "Recursive seal-relative robust support",
        ),
    )
    require(
        "formal-thin-restriction-contract",
        "formal",
        (
            "### 2.3.1 Thin temporal restriction",
            r"\mathsf{TR}_{u,t}^{H}",
            "### Corollary 4.6a — Prefix-level joint verdicts under thin temporal restriction",
            "### F18 — Prefix-verdict inflation",
            "### Test T13 — Thin temporal restriction",
        ),
    )
    require(
        "formal-boundary-fibre-contract",
        "formal",
        (
            "### Definition 2.2a — Constitutive admissibility boundary",
            "### Definition 3.2a — Prefix–fibre geometry",
            "### Proposition 4.1a — Constitutive boundary intervention changes existential support",
            "### Proposition 6.2a — Collision-limited scalar insufficiency",
            "### Test T14 — Constitutive-boundary action-fibre intervention",
            "No topology, measure or density is assumed by this definition",
            r"A_{u,t,k}(h_t,\rho_k)",
        ),
    )
    require(
        "formal-recurrence-contract",
        "formal",
        (
            "### Definition 8.6 — History-generated admissibility recurrence",
            "### Proposition 8.7 — Finite recurrent constitution",
            "### F17 — Recurrence collapse",
            "### Test T12 — History–future recurrence",
        ),
    )
    require(
        "formal-domain-contract",
        "formal",
        (
            r"For `H\ge 1`, the existential present support",
            r"For `0\le k<H`",
            r"a_{t+k}\in U_{t+k}(h_{t+k})",
            "no action-bearing present support or first-action projection is defined",
        ),
    )
    require(
        "formal-unmasked-intervention",
        "formal",
        (
            "structural admissibility and every prefix-viability factor equal `1`",
            "`A=1` and every `V=1`",
        ),
    )
    require(
        "formal-active-support-handler",
        "formal",
        (
            "### F13 — Empty active support without safe semantics",
            "### Test T10 — Empty-active-support handling",
            "separately authorised, versioned empty-support handler",
        ),
    )
    require(
        "bridge-mirror-contract",
        "bridge",
        (
            "versioned, attributed interpreter",
            "active support is empty",
            "separately authenticated enforcement channel",
            "growing-prefix recurrence",
            "thin temporal restriction",
            "Three claims must remain separate",
            "whole reachable fibre",
            "successor observation, interpreter and source-bound specification",
        ),
    )
    require(
        "pair-map-code-contract",
        "map",
        (
            "`harness/` now contains",
            "**Observation / interpretation.**",
            "**Assurance evidence / enforcement verdict.**",
            "**Reservoir non-emptiness / active-support non-emptiness.**",
            "**History-generated admissibility recurrence / physical retrocausality.**",
            "**Constitutive boundary / compiled admissibility.**",
            "**Unrealised future tail / present action fibre.**",
            r"\mathsf K,",
            r"\mathsf K^{\Sigma},",
            "**Prefix of an admitted tail / prefix-level joint verdict.**",
            "terminal-only counterexample",
            "equal-cardinality reservoirs with different first-action supports",
        ),
    )
    require(
        "scope-no-retrocausal-inflation",
        "formal",
        (
            "Future indexing does not imply future-to-past information flow",
            "Ordinary backward reachability is renamed as physical non-causality",
        ),
    )
    require(
        "scope-no-topology-inflation",
        "formal",
        (
            "They need not occupy four physical services",
            "Typed separation is mistaken for a theorem about physical process count",
        ),
    )
    require(
        "readme-entrypoint-contract",
        "readme",
        (
            "`check_all.py`",
            "`verify.py`",
            "`corpus_gate.py`",
            "`build_manifest.py`",
            "`MANIFEST.sha256`",
            "`VERIFICATION-MAP.md`",
        ),
    )
    require(
        "readme-thin-restriction-contract",
        "readme",
        (
            "thin temporal restriction audit",
            "terminal-only identity",
            "horizon-sensitive admissibility",
        ),
    )
    require(
        "harness-manifest-contract",
        "manifest_builder",
        (
            'MANIFEST_NAME = "MANIFEST.sha256"',
            "def manifest_entries(",
            "def manifest_text(",
            "def check_manifest(",
        ),
    )
    require(
        "harness-bundle-contract",
        "bundle_builder",
        (
            "def verify_pinned_artifacts(",
            "def refuse_self_poisoning_output(",
            "def scan_third_party_imports(",
            'errors.append("expected-report.json report_sha256 mismatch")',
            'errors.append("expected-corpus-gate.json report_sha256 mismatch")',
            'errors.append("expected-bundle.json bundle_sha256 mismatch")',
            'errors.append("expected-bundle.json reference_report sha256 mismatch")',
            'errors.append("MANIFEST.sha256 does not match current package bytes")',
            '"successful": not errors,',
            '"stdlib_only"',
        ),
    )
    require(
        "verification-map-enforcement-contract",
        "verification_map",
        (
            "`O_enf` artifact channel",
            "`G_enf` decision boundary",
            "Mediated execution",
            "validity-envelope and current-runtime-regime tests",
            "F16 construction/certification/seal failure",
            "empty-reservoir and non-empty-reservoir/empty-active-support",
            "PrefixFibreGeometry",
            "D3.2a-prefix-fibre-geometry",
            "F16-geometry-fibre-tamper",
            "History-generated admissibility recurrence",
            "F17 recurrence collapse",
            "Thin temporal restriction",
            "F18 prefix-verdict inflation",
            "`B → A` compilation",
            "P4.1a-T14-boundary-fibre",
            "P6.2a-cardinality-collision",
            "WearLedger",
            "F7-budget-viability-coupling",
            "F7-wear-accumulation",
            "recompute_context",
            "## Atmosphere instance",
        ),
    )
    require(
        "harness-certificate-contract",
        "core",
        (
            "class CertificateAudit:",
            "class SnapshotAudit:",
            "def audit_certificate(",
            "def audit_snapshot(",
            "class AdaptiveAssurance:",
            "class SealRelativeAssurance:",
            "class WearLedger:",
            "validity: ValidityEnvelope",
            "runtime_regime: str",
            "spec.assert_valid(time, runtime_regime)",
            "snapshot.history != self.root_history",
            "snapshot.remaining != self.horizon",
            "history_attribution",
            "def verify_observation(",
            "root history is not the unique interpretation of the sealed observation",
            "root history is not the unique interpretation of the supplied observation",
            "def thin_temporal_restriction_failures(",
        ),
    )
    require(
        "harness-clause-contract",
        "core",
        (
            "class IdentityCase:",
            "class IdentityClause:",
            "class ViabilityClause:",
            "def identity_rule_from_clause(",
            "def viability_rule_from_clause(",
            "def charge(self, realised: Tail)",
            "admissibility rule record does not commit to its compiled sources",
            "rule record does not commit to its executable clause",
            "viability wear costs require a declared wear ledger",
            "self.ledger.phi_load + self.wear(prefix) > self.ledger.capacity",
        ),
    )
    require(
        "harness-dynamics-contract",
        "core",
        (
            "duplicate action declaration rows shadow one another",
            "duplicate disturbance declaration rows shadow one another",
            "duplicate successor declaration rows shadow one another",
            "orphan disturbance row for undeclared pair",
            "orphan successor row for undeclared triple",
        ),
    )
    require(
        "harness-boundary-contract",
        "core",
        (
            "class AdmissibilityCase:",
            "class AdmissibilityClause:",
            "class BoundarySourceRole(str, Enum):",
            "class BoundarySource:",
            "boundary source id must match its executable clause id",
            "boundary source authority must match its executable clause authority",
            "boundary source version must match its executable clause version",
            "class ConstitutiveBoundary:",
            "def compile(self) -> \"AdmissibilityRule\":",
            "source.clause(time, horizon, history, tail) for source in self.sources",
            "def admissibility(self) -> AdmissibilityRule:",
            "return self.declaration.boundary.compile()",
        ),
    )
    require(
        "harness-geometry-contract",
        "core",
        (
            "class PrefixFibreGeometry:",
            "def geometry_from_snapshot(",
            "tail.prefix(length) for length in range(1, snapshot.remaining + 1)",
            "def assert_geometry(",
            "geometry fibres do not match the exact snapshot prefix fibres",
            "def existential_support(geometry: PrefixFibreGeometry)",
        ),
    )
    require(
        "harness-boundary-scenario-contract",
        "scenarios",
        (
            "def boundary_intervention_specs(",
            'source_id="personal-boundary"',
            'source_id="shared-terminal-boundary"',
            'allowed_action_paths=(("L",),)',
            'allowed_action_paths=(("R",),)',
            'allowed_state_paths=(("terminal",),)',
            "boundary_sources=(left_subject, shared_terminal)",
            "boundary_sources=(right_subject, shared_terminal)",
            "def non_absorption_cases(",
            "geometry = engine.geometry(",
            "support = engine.existential_support(geometry)",
        ),
    )
    require(
        "harness-ledger-scenario-contract",
        "scenarios",
        (
            "def hidden_lineage_scenarios(",
            "def equal_identity_different_budget_scenarios(",
            "def budget_geometry_comparison(",
            "def wear_accumulation_scenario(",
            "charged = scenario.spec.viability.clause.charge(realised)",
            "ledger=_wear_ledger(",
            'state_costs=(("worn", 5),)',
        ),
    )
    require(
        "harness-enforcement-contract",
        "control",
        (
            "class TokenAuthority:",
            "class Enforcer:",
            "class MediatedExecutor:",
            "class TraceLedger:",
            "enforcement-decision replay detected",
            "runtime regime does not match assurance context",
            "token expiry exceeds assurance validity envelope",
            "decision.runtime_regime",
            "def consume_token(",
            "def consume_decision(",
            "engine: ReservoirEngine",
            "def recompute_context(",
            "assurance context does not recompute from the engine",
            "adaptive current-geometry evidence mismatch",
            "seal-relative origin-geometry evidence mismatch",
        ),
    )
    require(
        "harness-k-sigma-contract",
        "core",
        (
            "def seal_continuation_indicator(",
            "recursive_continuation: bool",
            "child_support_digest: str | None",
            "self._seal_relative_cache",
            "generator_input_commitment: str",
        ),
    )
    require(
        "harness-recurrence-contract",
        "control",
        (
            "class HistoryFutureRecurrence:",
            "recurrence enforcement decision authentication mismatch",
            "recurrence post-history is not the exact append",
            "recurrence provenance link is absent from the next specification",
            "recurrence next history does not equal the realised post-history",
            "recurrence link commitment mismatch",
            "recurrence prior generator input commitment mismatch",
            "recurrence next generator input commitment mismatch",
        ),
    )
    require(
        "harness-access-contract",
        "access",
        (
            "def find_fibre_collisions(",
            "class MembershipOracle:",
            "class GreedyVersionSpaceAttack:",
            "class LeakagePolicy:",
        ),
    )
    require(
        "harness-report-contract",
        "report",
        (
            'schema="ncnc-reference-report-v6"',
            "D8.6-P8.7-T12",
            "D2.2a-boundary-compilation",
            "D3.2a-prefix-fibre-geometry",
            "D3.3-P4.1",
            "P4.1a-T14-boundary-fibre",
            "P6.2a-cardinality-collision",
            "F16-geometry-fibre-tamper",
            "F11-boundary-version-mismatch",
            "F17-history-append",
            "F17-action-substitution",
            "F17-successor-provenance",
            "F17-decision-authentication",
            "F17-link-commitment",
            "F17-generator-input",
            "F8-unsealed-prefix-support",
            "D4.5-KSigma-recursion",
            "scope-host-nonbypassability",
            "F10-forged-admit-decision",
            "F10-reject-decision-replay",
            "F10-handcrafted-assurance",
            "F10-forged-self-consistent-geometry",
            "F10-unregistered-spec",
            "F16-certificate-recomputation",
            "F16-unattested-history-seal",
            "F7-budget-viability-coupling",
            "P6.1-two-ledgers",
            "P6.2-nonmonotone-geometry",
            "empty_reservoir_scenario",
            "T13-thin-temporal-restriction",
            "F18-prefix-verdict-inflation",
            "F18-prefix-admissibility-inflation",
        ),
    )
    forbid(
        "stale-language-residue",
        ("formal", "bridge", "map", "readme", "verification_map"),
        (
            "Code: not yet created",
            "### Test T10 — Empty-reservoir handling",
            "The reservoir becomes empty and the architecture has no declared",
        ),
    )
    forbid(
        "logical-quote-punctuation",
        ("formal", "bridge", "map", "readme", "verification_map"),
        ('."', ',"'),
    )
    forbid_control_characters(
        "public-control-characters",
        ("formal", "bridge", "map", "readme", "verification_map"),
    )
    return GateReport("ncnc-corpus-gate-v6", tuple(checks))


def run_gate(root: Path = PAIR_ROOT) -> GateReport:
    return evaluate_surfaces(load_surfaces(root))


def render_text(report: GateReport) -> str:
    lines = [
        "NCNC cross-artifact contract gate",
        f"schema: {report.schema}",
        f"successful: {str(report.successful).lower()}",
        f"report_sha256: {report.digest}",
        "",
    ]
    lines.extend(
        f"- {check.check_id}: {'PASS' if check.passed else 'FAIL'} - {check.detail}"
        for check in report.checks
    )
    return "\n".join(lines) + "\n"


def render_json(report: GateReport) -> str:
    payload = {**report.payload(), "report_sha256": report.digest}
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check cross-artifact NCNC definitions, mirrors and executable surfaces."
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = run_gate()
    rendered = render_json(report) if args.format == "json" else render_text(report)
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    return 0 if report.successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
