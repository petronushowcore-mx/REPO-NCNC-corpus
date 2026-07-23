# Executable Verification Map

This map states what each executable surface checks. A runtime witness, a static cross-artifact fence and an external empirical claim are different evidence types; the map does not collapse them.

## Formal objects

| Formal object | Implementation | Principal tests/report checks |
|---|---|---|
| `Theta` construction specification | `ConstructionSpec` | specification and seal mutation tests |
| Executable identity and viability predicates | `IdentityCase`, `IdentityClause`, `ViabilityClause`, `IdentityRule`/`ViabilityRule` record-to-clause binding | clause well-formedness guards, record/clause commitment binding, `T3-predicate-intervention`, `F18` identity mutation |
| Wear / budget ledger | `WearLedger` sealed inside `ViabilityClause`; `ViabilityClause.charge` absorbs realised wear into the successor specification | `P6.1-two-ledgers`, `P6.2-nonmonotone-geometry`, `F7-budget-viability-coupling`, `F7-wear-accumulation` |
| Declared finite dynamics | `FiniteDynamics` construction-time validation | duplicate-row shadowing and orphan-row rejection tests |
| `B → A` compilation | `AdmissibilityCase`, `AdmissibilityClause`, `BoundarySource`, `ConstitutiveBoundary.compile`, computed `ConstructionSpec.admissibility` | clause/source id-authority-version guards, source conjunction, `D2.2a-boundary-compilation` |
| Held construction inputs plus `A → \mathcal R` | `ConstructionSpec`, `ReservoirEngine.reachable_tails`, `joint_verdict`, `reservoir` | history, horizon, identity, compiled admissibility, viability and dynamics tests; `D3.2-reservoir`, `P4.1a-T14-boundary-fibre` |
| `\mathcal R → \mathcal G(\mathcal R)` | `PrefixFibreGeometry`, `geometry_from_snapshot`, `assert_geometry` | exact prefix-family tests, `D3.2a-prefix-fibre-geometry`, `F16-geometry-fibre-tamper` |
| `\mathcal G(\mathcal R) → \Pi^{\exists}` | `existential_support` | exact first-action image and terminal-domain tests, `D3.3-P4.1`, `P6.2a-cardinality-collision` |
| Versioned partial interpreter and declared generator inputs | `VersionedInterpreter`, `MinervaOperator.generate`, `generator_input_commitment` | ambiguity failure, seal-binding and generator-input mutation tests |
| Seal history attribution (Def. 3.5) | `SealRecord.create` interpretation check, `SealRecord.verify_observation` | `F16-unattested-history-seal`, `F16-observation-preimage-check` (commitment arm), `F16-interpretation-drift-check` (re-interpretation arm) and unattested-history mutation tests |
| Reachable set `Gamma` | `ReservoirEngine.reachable_tails` | horizon and reachability tests |
| Joint verdict `J` | `ReservoirEngine.joint_verdict` | conjunction and terminal-product tests |
| Thin temporal restriction (§2.3.1, Corollary 4.6a) | `ReservoirEngine.thin_temporal_restriction_failures` | `T13-thin-temporal-restriction`, terminal-only `F18-prefix-verdict-inflation` and horizon-sensitive `F18-prefix-admissibility-inflation` mutations |

| Membership certificate | `Certificate`, `CertificateAudit` | certificate recomputation and mutation tests |
| Complete admitted-set audit | `SnapshotAudit` | omission, pairing and full-set tests |

| Adaptive-robust support | `adaptive_support`, `ActionEvidence`; geometry plus history, fixed specification lineage, disturbances, successors and recursive child support | `D3.4-T2`, changed-spec/current-fibre/recursive-child tests |
| Recursive original-seal-relative support | `seal_relative_support`, `seal_continuation_indicator`, `SealBranchEvidence`; original seal geometry plus realised prefix, disturbances, successors and recursive `K^Sigma` | `D4.5-KSigma-recursion`, `T1-T4.6`, prefix/geometry/time mismatch tests and two-way divergence fixture |
| Tagged assurance context | three assurance dataclasses | mode-specific evidence, validity-envelope and current-runtime-regime tests |
| `O_enf` artifact channel | `TokenAuthority` anchored to one `ReservoirEngine`; `recompute_context` | signature, expiry, mode, action, context, runtime-regime and version mutations; `F10-handcrafted-assurance`, `F10-forged-self-consistent-geometry`, `F10-unregistered-spec`. The anchor refuses contexts the engine cannot reproduce; it does not authenticate who authored a specification, so it is process-trust-relative in exactly the sense of the shared HMAC secret. The field-level equality checks on this channel are cheap pre-filters whose force is inherited from that recomputation, which is what the forged-context mutations actually pin. |
| `G_enf` decision boundary | `Enforcer` | authority-scoped token replay, decision-version, validity-expiry and regime-change tests |
| Mediated execution | `MediatedExecutor` | verdict intervention, forged-decision, regime-change and cross-executor one-shot tests for every verdict |
| Execution lineage | `TraceLedger` | chain integrity and discontinuity tests |
| History-generated admissibility recurrence | `HistoryFutureRecurrence` | `D8.6-P8.7-T12`, active-support, authenticated-decision, exact-append, prior-observation, declared-generator-input, successor-provenance, successor-seal and link-commitment checks and mutations |

| Confined optimizer channel | `ChannelCase`, fibre collision search | `T5.3-T6` |
| Query leakage bound | membership oracle and version-space attack over an abstract declared hypothesis class | `T7-query-budget`. This is a channel-and-budget lemma on that abstract class; it makes no claim that the constitutive boundary of this companion is or is not reconstructible. |

## Failure modes

| Failure mode | Executable witness or fence |
|---|---|
| F1 retrospective reservoir | seal and snapshot mutation detection |
| F2 attractor collapse | fixed-reservoir selector intervention with changed goals |
| F3 oracle leakage | target-changing channel fibre plus bounded-query attack |
| F4 predicate collapse | unmasked identity-predicate intervention |
| F5 decorative atmosphere | matched enforcement-verdict intervention changes execution |
| F6 query reconstruction | query-budget overrun and residual version space |
| F7 ledger collapse | sealed `WearLedger` inside the viability clause: equal-ledger/different-reservoir and equal-identity/different-ledger fixtures, plus an exhausted-ledger coupling probe showing the budget genuinely cuts viability |
| F8 existential/robust confusion | existential-only action, adaptive recursive evidence, shallow-seal/recursive-`K^Sigma` separation and adaptive/original-seal two-way divergence |
| F9 liveness inflation | explicit non-machine-decidable scope boundary; no liveness field is inferred from reservoir non-emptiness |
| F10 enforcement absorption | authenticated decision, forged-ADMIT rejection, replay rejection and mediated execution |
| F11 silent common morality | boundary source, subject and version are bound to the exact compiled admissibility record; source-map or `B/A` mismatch fails construction |
| F12 unversioned pulsation | changed reservoir bytes invalidate the original seal, and every successor change remains tied to committed generator inputs or a declared specification version |
| F13 empty support without safe semantics | empty-reservoir and non-empty-reservoir/empty-active-support fixtures both invoke sealed handler before selection |
| F14 classical-neighbour inflation | corpus gate preserves the no-physical-retrocausality scope fence |
| F15 topology inflation | corpus gate preserves typed-separation-without-process-count inflation |
| F16 construction/certification/seal failure | complete certificate, snapshot, token, decision and trace-lineage mutation suite |
| F17 recurrence collapse | pre-action seal, declared generator-input commitments, assurance-context, authenticated-decision, action-substitution, exact-append, successor-interpretation, provenance and recurrence-link commitment mutation suite |
| F18 prefix-verdict inflation | thin temporal restriction audit plus independent identity and admissibility mutations that admit full tails and reject their one-step prefixes; T14 independently tests boundary-to-action-fibre dependence |

## Artifact drift fence

`check_all.py` additionally verifies the pinned artifacts on every run: the fresh reference-report digest must equal `expected-report.json`, the fresh gate digest must equal `expected-corpus-gate.json`, and `MANIFEST.sha256` must match the current package bytes. A stale pin or stale manifest fails the bundle. `ArtifactPinTests` exercises every failure arm of this fence on isolated fixtures — missing report pin, missing gate pin, report-digest mismatch, gate-digest mismatch, `successful: false` in either pin, and a stale manifest — plus a passing fixture and a self-consistency check on the pinned `expected-bundle.json`. `OutputRefusalTests` covers the companion refusal of unmanaged in-tree `--output` writes.

## Atmosphere instance

The atmosphere tuple of Definition 3.6 is a logical grouping, not a single runtime class: its components are distributed across `MinervaOutput` (history, reservoir, seal, generator-input commitment), the assurance dataclasses (mode-specific evidence, geometry commitments, validity), `TokenAuthority` (`O_enf`), `Enforcer` (`G_enf`), the sealed empty-support policy and `TraceLedger` (execution lineage). Their joint binding in one runtime state is certified by the history-generated recurrence certificate, not by a wrapper type.

The audit distinguishes two verdicts the executable surfaces must not collapse: membership of a realised prefix in the prefix closure of the sealed reservoir (Theorem 4.6) and a prefix-level joint verdict (Corollary 4.6a). Only the second requires an empty thin-restriction failure set, and the report keeps them as separate results rather than one certificate.

## Deliberate limits

The executable report labels five targets `NOT_MACHINE_DECIDABLE`: physical retrocausality beyond declared dataflow, adequacy of personal identity, consciousness/liveness, host-level non-bypassability and interpreter-evaluator faithfulness (the seal commitments bind the interpreter's versioned record, not the runtime behaviour of its evaluator). Identity, admissibility and viability are executable committed data in this companion, so the interpreter is the only committed callable to which the faithfulness label applies. These labels are part of the result, not failed tests and not implied achievements.
