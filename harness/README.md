# Non-Causal Non-Causality — Executable Companion

This directory contains the finite, standard-library reference instrument paired with **Non-Causal Non-Causality: Future-Indexed Admissibility Environments and the Projection of Present Action** and its bridge, **Reality Catches the Predicate**.

It is deliberately stronger than a toy projection demo. The instrument constructs and independently rechecks the complete admitted reservoir, keeps three assurance modes separate, authenticates the path from evidence to execution, models confined access and bounded reconstruction, and emits a deterministic report.

## What it implements

- Immutable histories and finite action–disturbance–successor dynamics, validated at construction against duplicate shadowing rows and orphan disturbance or successor rows.
- A single source-attributed, subject- and version-bound constitutive boundary inside the declaration, with explicit personal/shared/platform source roles and composition provenance.
- Identity and prefix-viability predicates as committed executable clause tables whose rule records bind their exact content; the interpreter is the only committed callable.
- A wear/budget ledger sealed inside the viability clause, so declared burden genuinely participates in reservoir construction while remaining distinct from identity; the realised step is charged into the successor specification at every recurrence update, so the budget wears across the run instead of resetting at each construction. Equal-ledger and equal-identity countermodels, an exhausted-ledger coupling probe and an accumulation probe cover it.
- A complete, versioned construction specification whose active admissibility is derived solely by compiling that boundary, while also binding identity, viability, dynamics, interpreter, model, provenance and validity.
- A versioned partial observation-to-history interpreter that fails on ambiguity.
- Exhaustive reachable-tail enumeration and joint-verdict filtering.
- A first-class `PrefixFibreGeometry` derived exactly from every reservoir, checked against the complete prefix family and used as the sole input to existential projection.
- An explicit thin temporal restriction audit over every admitted tail and prefix, with independent terminal-only identity and horizon-sensitive admissibility mutations proving that full-tail admission alone is insufficient.
- Replayable certificates for every admitted tail, plus independent certificate and complete-snapshot recomputation.
- Existential, adaptive-robust and recursively original-seal-relative supports, including the terminal `K^Sigma` base and child-support evidence.
- Explicit terminal semantics at `H=0` and action-bearing support only for `H>=1`.
- Mode-tagged assurance contexts with distinct evidence payloads, the declared validity envelope and an explicitly supplied runtime regime.
- HMAC-authenticated, expiring admission tokens bound to action, history, context, mode, time, runtime regime and versions; token lifetime cannot exceed the assurance envelope. The token authority is anchored to one reservoir engine and recomputes every presented assurance context before signing or accepting it, so a hand-built or foreign-geometry context fails closed. That anchor bounds which contexts can be certified, not who may author a specification: like the shared secret itself, it is process-trust-relative.
- Authenticated one-shot enforcement decisions bound to history, construction specification, execution time and runtime regime, with authority-scoped replay rejection for every verdict.
- A mediated executor and append-only, mutation-detecting execution-trace lineage.
- A history-generated admissibility recurrence certificate that independently rechecks the active assurance support and authenticated `ADMIT` decision, then binds both declared generator-input commitments, the pre-action seal, exact history append, successor interpretation, provenance-linked successor specification and successor seal.
- A sealed empty-active-support handler, including the case where the reservoir is non-empty but robust support is empty.
- Exact channel-fibre collision search for confined-access non-absorption.
- A budgeted membership oracle and greedy version-space reconstruction attack.
- An authorised boundary intervention that holds the reachable carrier, identity and viability fixed while swapping the whole admitted `L`/`R` action fibre; equal reservoir cardinality with different existential support is reported separately.
- Deterministic finite-fixture reporting and mutation teeth.
- A static cross-artifact drift fence tying the formal paper, bridge, pair map and executable API together.
- A reproducible SHA-256 package manifest covering every distributable harness file.

## Run

From this directory:

```powershell
py -3 check_all.py --format text
```

The verification surfaces can also be run independently:

```powershell
py -3 -m unittest discover -s tests
py -3 verify.py --format text
py -3 corpus_gate.py --format text
py -3 build_manifest.py --check
```

Machine-readable output. `check_all.py` pins the expected report, the expected gate, the pinned bundle's recomputable fields and the package manifest, so the artifacts must be regenerated in dependency order — report and gate first, manifest next, then repeated bundle passes with a manifest write after each, until the stored bundle itself reports `successful: true`:

```powershell
py -3 verify.py --format json --output expected-report.json
py -3 corpus_gate.py --format json --output expected-corpus-gate.json
py -3 build_manifest.py --write
py -3 check_all.py --format json --output expected-bundle.json
py -3 build_manifest.py --write
py -3 check_all.py --format json --output expected-bundle.json
py -3 build_manifest.py --write
py -3 check_all.py --format json --output expected-bundle.json
py -3 build_manifest.py --write
py -3 build_manifest.py --check
```

This fixed-point order supersedes the earlier fixed-count recipes. Because the bundle pins its own recomputable fields, each pass reads the file the previous pass wrote: after a report or gate digest changes, the first pass legitimately records the previous pin as stale, and later passes carry that recorded failure forward until one pass finally reads a file that already agrees with it. The number of passes needed is therefore not fixed — do not count them. Repeat the pass-plus-manifest pair until the stored `expected-bundle.json` itself contains `"successful": true`, then seal with a final manifest write. Reading the terminal output of a bare `check_all.py` run is not sufficient: that run can be green while the file it read was written by a red pass. The bundle pin intentionally covers only recomputable fields — the two digests and the stored `manifest_ok` flag — because pinning the stored test or success literals would make this fixed point non-convergent. Run the listed commands in order even when an intermediate bundle pass returns a non-zero status. `check_all.py --output` refuses to write into the harness tree except to `expected-bundle.json` and manifest-excluded paths, so a stray in-tree output cannot silently falsify the manifest it has just certified.

The implementation has no third-party dependencies, and the bundle enforces that claim with an AST import scan of every distributable Python file against the standard-library module list.

## Layout

| Path | Role |
|---|---|
| `ncnc/core.py` | Typed histories, rules, specification, reservoir engine, certificates, seals and assurance contexts |
| `ncnc/control.py` | Selector, admission authority, enforcer, mediated executor, trace lineage and history-generated recurrence certificate |
| `ncnc/access.py` | Confined-channel fibres, membership oracle and reconstruction attack |
| `ncnc/scenarios.py` | Deterministic finite countermodels and witness fixtures |
| `ncnc/report.py` | Canonical executable report and mutation results |
| `check_all.py` | One-command tests + executable report + corpus contract |
| `verify.py` | Command-line verifier |
| `corpus_gate.py` | Cross-artifact definition and mirror contract |
| `build_manifest.py` | Deterministic package manifest writer and verifier |
| `MANIFEST.sha256` | SHA-256 inventory of distributable harness files |
| `tests/` | Unit, mutation and contract-gate tests |
| `VERIFICATION-MAP.md` | Formal object and failure-mode mapping to executable surfaces |

## Scope boundary

The code establishes claims only on its declared finite fixtures. It does not establish physical retrocausality, the adequacy of a declared predicate as real personal identity, consciousness, life or IIC cycle reinitiation. The boundary fixture establishes `B\xrightarrow{\mathsf{compile}}A`; under held history, horizon, identity, viability and dynamics it establishes the resulting change in `\mathcal R`; it derives exact `\mathcal G(\mathcal R)`; and it projects `\mathcal G(\mathcal R)\xrightarrow{\mathsf{First}}\Pi^{\exists}`. The equal-cardinality collision does not show that every scalar encoding fails. Full-tail admission is promoted to a prefix-level joint verdict only when the explicit thin temporal restriction audit passes; the extension-based base theorem remains separate. HMAC demonstrates shared-secret artifact integrity, not public non-repudiation. Generator-input commitments exclude undeclared logical inputs from the certified interface; they do not prove the absence of hidden physical side channels. Python-level mediation does not prove host-level non-bypassability; both claims require deployment, capability and operating-system evidence.

Worst-case enumeration cost is exponential in horizon and branching. That is intentional: the reference instrument makes the quantifiers visible rather than hiding them behind sampling.
