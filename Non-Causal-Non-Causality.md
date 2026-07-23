# Non-Causal Non-Causality

## Future-Indexed Admissibility Environments and the Projection of Present Action

**Maksim Barziankou (MxBv)**  
PETRONUS™ | The Urgrund Lab  
Poznań, 17 July 2026  
Working paper · open architectural draft  
Version 1.1  
Navigational Cybernetics 2.5  
This version DOI: 10.17605/OSF.IO/NC9WH  
Version 1.0 DOI: 10.17605/OSF.IO/CUW8X  
Axiomatic core anchor: NC2.5 v2.1, DOI 10.17605/OSF.IO/NHTC5  
License: CC BY-NC-ND 4.0  

---

## Abstract

Long-horizon systems are normally organised in causal order: observe the present, select an action, predict consequences, and then test whether the resulting future is acceptable. This paper studies the reverse architectural order without asserting reverse physical causation. An authorised constitutive boundary `B`, whose source map contains personal and independently sourced external clauses, is sealed and compiled into structural admissibility `A`. Together with declared identity, viability and dynamics, `A` cuts reachable continuations into a reservoir `\mathcal R`; the reservoir's prefix–fibre geometry `\mathcal G(\mathcal R)` determines existential present support `\Pi^{\exists}`. Adaptive and seal-relative robust supports additionally bind declared disturbances, successors, specification lineage and recursive continuation evidence. Task-level objectives may rank that support, but they are not granted authority to generate or revise its privileged ground. Whether a protected target is exactly reconstructible is treated separately as a channel-relative question.

The paper distinguishes this five-link construction chain from the trajectory predicate and viability factors that help form the reservoir, from the maintained environment that contains the chain, from consumer readout and task selection, and from causally effective enforcement. It defines existential, adaptive-robust and recursively seal-relative robust present projections, proves full-horizon continuation and prefix-closure preservation relative to an original sealed reservoir and, under an explicit thin temporal restriction premise, lifts that extension claim to horizon-indexed prefix verdicts. It also gives a confined-access non-absorption theorem and shows why future indexing does not entail retrocausality. It then closes the maintained update into a **history-generated admissibility recurrence**: a pre-action environment admits an executed event, exact append turns that event into the next history, and a valid successor specification regenerates the next future-indexed environment from that enlarged history. It also separates the identity witness from the wearing `\Phi_{\mathrm{load}}/\tau_b` ledger, reservoir non-emptiness from liveness, and monotone burden from monotone continuation geometry.

The resulting object is called a **future-indexed admissibility environment**. In the companion bridge it is described as an atmosphere: not a floor, reward, prediction or oracle, but a space of futures regenerated at declared updates from which present-time systems read typed local affordances. A platform-level factorisation allows each person or system to supply constitutive content while the platform preserves provenance, authority separation, query confinement and cross-temporal coherence. The formal results use classical set, control and factorisation arguments. The candidate contribution is their authority-typed, identity-relative composition within Navigational Cybernetics 2.5.

---

## 0. Status, scope and claim discipline

This is an **open architectural draft**. It contains four statement classes.

1. **Definitions** fix the objects studied here.
2. **Elementary propositions and theorems** follow from those definitions and their stated premises.
3. **Architectural declarations** specify how a Minerva-pattern observer and a personal platform may instantiate the objects.
4. **Bridge language** such as *pool*, *atmosphere* and *reality catches the predicate* is interpretive. It has no independent proof force.

The paper does not claim:

- that an event in the physical future sends information into the past;
- that a future-indexed set is conscious, alive or morally good;
- that reservoir non-emptiness is equivalent to IIC cycle-reinitiation liveness;
- that a Boolean predicate uniquely selects an action;
- that `\Phi_{\mathrm{load}}` or `\tau_b` carries identity;
- that decreasing remaining budget forces nested continuation sets;
- that a Minerva-pattern operator issues task-level motor commands;
- that users receive unrestricted read or write access to a protected boundary;
- that classical viability or backward-reachability machinery is novel;
- that the architecture has been empirically instantiated merely because it is type-consistent.

The strongest theorem-facing claim is narrower:

> Under declared dynamics, disturbance scope, identity and admissibility predicates, one may construct a future-indexed reservoir of continuations. Selection from the adaptive-robust projection preserves a non-empty one-step fibre of the current reservoir and a recursively available recomputed continuation through the remaining horizon. Selection from the distinct seal-relative robust support preserves a non-empty conditional fibre of the original sealed reservoir and a recursively available seal-relative continuation through the remaining horizon. A finite sequence of valid history-generated recurrence links certifies that every realised action–successor pair is appended exactly to the carried history and that every successor environment is generated from the resulting enlarged history, a valid successor specification and provenance binding the prior seal to the executed event. This recurrence uses only information available at each update and therefore introduces no future-to-past information flow. The reservoir may causally shape execution while its privileged ground remains unavailable as a task objective or revision surface; when the complete declared optimizer channel contains a target-changing fibre collision, exact reconstruction of that target through the channel is impossible.

---

## 1. The architectural inversion

### 1.1 The ordinary order

A conventional action-centred architecture has the schematic form

\[
h_t
\longrightarrow
a_t
\longrightarrow
\widehat{h}_{t+1:t+H}
\longrightarrow
\text{evaluation}.
\]

The system acts from the present and asks what future may follow. Even when a planner evaluates a long horizon, the action proposal normally remains the leading object and the future remains its forecasted consequence.

### 1.2 The reversed formal order

The five-node construction is a typed dependence graph. Once the non-boundary construction context is held fixed and the declared compiler is single-valued on a valid sealed `B`, its four arrows are partial maps:

\[
\begin{aligned}
B_{u,t}^{v_B}
&\xrightarrow{\ \mathsf{compile}\ }
A_{u,t,0:H},\\
(h_t,H,\Theta_{u,t}^{H}[I_u,A,V,\mathsf{Dyn},\mathsf{Val}])
&\xrightarrow{\ \mathsf{filter\ reachable\ tails}\ }
\mathcal R_{u,t}^{H},\\
\mathcal R_{u,t}^{H}
&\xrightarrow{\ \mathsf{exact\ prefix\text{-}fibres}\ }
\mathcal G(\mathcal R_{u,t}^{H}),\\
\mathcal G(\mathcal R_{u,t}^{H})
&\xrightarrow{\ \mathsf{First},\ H\ge 1\ }
\Pi_{u,t}^{\exists,H}.
\end{aligned}
\]

The first codomain is not silently treated as the whole domain of the second arrow: reservoir filtering also consumes the held history, horizon, identity, viability, dynamics and validity context. Thus the display records four typed dependencies, while a fixed context makes the experimental `B\to A\to\mathcal R` intervention well-defined.

The stronger supports are separate typed maps because geometry is not their only input:

\[
\bigl(\mathcal G(\mathcal R),h_t,t,H,
\Theta\text{-lineage},\mathcal W,\mathcal F,\mathsf K\bigr)
\longmapsto \Pi_{u,t}^{\mathrm{rob},H},
\]

\[
\bigl(\Sigma,\mathcal G(\mathcal R^\Sigma),\rho_k,k,
\mathcal W,\mathcal F,\mathsf K^\Sigma\bigr)
\longmapsto \Pi_{\Sigma,k}^{\mathrm{rob}}.
\]

`\Pi_t^{\mathrm{act}}` is a tagged choice among these support modes, not the output of an untyped unary arrow from geometry. Selection and enforcement then form a distinct causal path:

\[
\Pi_t^{\mathrm{act}}
\xrightarrow{\ S_u\ }
a_t^{\mathrm{prop}}
\xrightarrow{\ G_{\mathrm{enf}}\ }
d_t
\longrightarrow
e_t.
\]

The first constructed decision object is therefore not an action but a set of future continuations. `B` compiles to executable `A`; `A`, together with the held construction inputs, filters reachable tails into `\mathcal R`; `\mathcal R` uniquely induces `\mathcal G(\mathcal R)`; and its first-action fibres yield existential support. Only then may a task selector propose an action. A separately authenticated enforcement interface admits or rejects the proposal before any event occurs.

This is a reversal of **architectural dependence**, not of physical causation. The set `\mathcal R_{u,t}^{H}` is constructed at time `t` from information legitimately available at time `t`. Its elements are indexed by future positions. No later event is an input unless an oracle or leakage channel has been introduced.

At declared updates the same order recurs in a growing-prefix form:

\[
(h_t,\Theta_{u,t}^{H_t})
\longrightarrow
\mathfrak A_{u,t}^{H_t}
\longrightarrow
\Pi_t^{\mathrm{act}}
\longrightarrow
a_t^{\mathrm{prop}}
\longrightarrow
d_t
\longrightarrow
e_t
\longrightarrow
h_{t+1}
\longrightarrow
(\mathcal O_{t+1}^{\mathrm{priv}},
\mathsf{Int}_{u,t+1}^{v},
\Theta_{u,t+1}^{H_{t+1}})
\longrightarrow
\mathfrak A_{u,t+1}^{H_{t+1}}.
\]

Here `d_t` is the authenticated enforcement decision and `e_t` is the realised event. The rightmost history is not the leftmost history revisited: `h_t\prec h_{t+1}` by exact append. The successor environment is constructed only after an authenticated successor observation is uniquely interpreted as that appended history and combined with a successor specification valid at its root. History alone does not generate the next field. Section 8.6 types this history–future recurrence and its failure conditions.

### 1.3 The phrase *reality catches the predicate*

The phrase has one disciplined formal reading. A reservoir is sealed before action. Its root seal-relative continuation indicator must equal `1`. As the trace unfolds, each realised action must be selected from the recursively defined seal-relative robust support of the already realised prefix. Under those premises, a seal-relative action remains available before every nonterminal step and each realised finite prefix remains a prefix of at least one trajectory in the sealed reservoir, or else the system records a declared shock, model revision, validity-envelope expiration, predicate revision, selection or enforcement failure, or construction, certification or seal-integrity failure. Reality does not become true because the predicate imagined it. The realised trace remains inside the prefix closure of what was admitted in advance.

Without pre-action sealing and version lineage, the phrase becomes unfalsifiable retrospective fitting. A reservoir rewritten after the outcome can always be made to appear prophetic.

---

## 2. Typed setting

### 2.1 Time, histories and dynamics

Let time be discrete. In this paper, maintenance or regeneration *through time* means recomputation at declared update events; no topological continuity in `t` is assumed. For each `t`, let:

- `X_t` be a state space;
- `U_t(h_t)` be the available action set after history `h_t`;
- `W_t(h_t,a)` be a declared non-empty disturbance set;
- `F_t(h_t,a,w) \subseteq X_{t+1}` be a non-empty transition correspondence.

A finite history is

\[
h_t=(x_0,a_0,x_1,\ldots,a_{t-1},x_t).
\]

For horizon `H\ge 1`, a dynamically reachable tail has the form

\[
\eta=(a_t,x_{t+1},a_{t+1},x_{t+2},\ldots,a_{t+H-1},x_{t+H}),
\]

where, at every depth `k=0,\ldots,H-1`, if

\[
h_{t+k}=h_t\oplus\eta_{\le k},
\]

then

\[
a_{t+k}\in U_{t+k}(h_{t+k})
\]

and, for some declared disturbance
`w_{t+k}\in W_{t+k}(h_{t+k},a_{t+k})`,

\[
x_{t+k+1}\in
F_{t+k}(h_{t+k},a_{t+k},w_{t+k}).
\]

Thus reachability includes both action legality and transition consistency. The set of all such tails is denoted

\[
\Gamma_{t,H}(h_t).
\]

For `H=0`, set

\[
\Gamma_{t,0}(h_t)=\{\varnothing\}.
\]

The concatenation of a history and a tail is written `h_t\oplus\eta`. The prefix of `\eta` through its first `k` transitions is `\eta_{\le k}`.

### 2.2 Personal declaration and authorised revision

Let `u` index a person, operator or bounded system. A declaration record is

\[
D_u=(I_u,\mathsf W_u,B_{u,t}^{v_B},
\mathsf{Auth}_u,\mathsf{Rev}_u,\nu_u),
\]

where:

- `I_u` is a declared identity predicate over histories or completed trajectory segments;
- `\mathsf W_u=(M_u,[\zeta_u])` is a declared witness carrier and equivalence class used, where required, to evaluate trajectory identity;
- `B_{u,t}^{v_B}` is the active, versioned constitutive admissibility boundary and its source map;
- `\mathsf{Auth}_u` specifies who may establish or revise the declaration;
- `\mathsf{Rev}_u` specifies the versioned revision relation;
- `\nu_u` contains declared interpretation conventions needed to evaluate `I_u`.

This paper does not require all people to share the same `I_u`. It requires only that the active declaration be attributable, versioned and evaluated according to its declared authority.

`I_u` and `\mathsf W_u` are related but not identical types. The architecture does not model `\mathsf W_u` as accumulating wear merely because a viability budget wears. Any change in the witness must be typed under a declared identity-event, transfer or re-commissioning relation; this paper does not infer such a relation from budget dynamics.

### Definition 2.2a — Constitutive admissibility boundary

Write

\[
B_{u,t}^{v_B}
=
(\Lambda_{u,t}^{\mathrm{pers}},
\Lambda_{t}^{\mathrm{ext}},
\mathsf{Src}_{t}^{A},
\mathsf{Comp}_{t}^{A},
\mathsf{Prov}_{t}^{B}).
\]

Here `\Lambda_{u,t}^{\mathrm{pers}}` is the family of personal constitutive clauses attributable to the subject or another authorised constitutive process under `\mathsf{Auth}_u`; `\Lambda_t^{\mathrm{ext}}` contains shared, legal, physical, safety or platform clauses that retain their own source authorities; `\mathsf{Src}_{t}^{A}` records those sources; `\mathsf{Comp}_{t}^{A}` is the declared partial compiler, required to be single-valued on every valid sealed `B`; and `\mathsf{Prov}_{t}^{B}` binds version and provenance.

`B_{u,t}^{v_B}` is a sealed view inside the declaration and construction specification, not a second mutable state store. The task selector has neither write authority over this view nor an unrestricted membership-query interface to it. Personal authorship does not erase external sources, and platform carriage does not make the platform the author of personal clauses. The compiled family `A_{u,t,0:H}` is the sole compiled view of that sealed source map: it is derived from `B_{u,t}^{v_B}` on demand and is never carried as an independently writable field beside it, so the four displayed arrows record typed dependence rather than a chain of separately stored objects.

### 2.3 Structural admissibility and viability

For every `0\le k\le H`, compile the personal and external clauses separately:

\[
\begin{aligned}
A^{B}_{u,t,k}(h_t,\rho_k)
&=
\prod_{\lambda\in\Lambda_{u,t}^{\mathrm{pers}}}
\mathbf 1[\lambda(h_t,\rho_k)=1],\\
A^{\mathrm{ext}}_{u,t,k}(h_t,\rho_k)
&=
\prod_{\lambda\in\Lambda_{t}^{\mathrm{ext}}}
\mathbf 1[\lambda(h_t,\rho_k)=1].
\end{aligned}
\]

The superscript `B` names the personal-source component; both source families are carried by `B`, and their conjunction below is the sole executable `A`.

An empty conjunction equals `1`. The complete structural admissibility predicate is

\[
A_{u,t,k}(h_t,\rho_k)
=
A^{B}_{u,t,k}(h_t,\rho_k)
\cdot
A^{\mathrm{ext}}_{u,t,k}(h_t,\rho_k)
\in\{0,1\}.
\]

For a full tail, take `k=H` and `\rho_H=\eta`. Let

\[
V_{t,k}(h_t,\eta_{\le k})\in\{0,1\}
\]

be a horizon-relative viability predicate for every intermediate prefix.

`I_u`, `A^B`, `A^{\mathrm{ext}}` and `V` are kept separate. Identity is not absorbed into held-line admissibility; externally sourced constraints are not silently attributed to the subject; and a trajectory may be structurally inadmissible while remaining physically executable. Conversely, a trajectory may satisfy the compiled rule while exhausting the system's ability to continue.

### 2.3.1 Thin temporal restriction

For `0\le k\le H`, define the prefix-restriction map

\[
r_k^H:
\Gamma_{t,H}(h_t)\longrightarrow\Gamma_{t,k}(h_t),
\qquad
r_k^H(\eta)=\eta_{\le k}.
\]

The map is well-defined because every prefix of a reachable tail is reachable under the same declared dynamics. A declared identity/admissibility family is **thinly temporally restrictive** on a class

\[
\mathcal C\subseteq\Gamma_{t,H}(h_t)
\]

when, for every `\eta\in\mathcal C` and every `0\le k\le H`,

\[
\begin{aligned}
I_u(h_t\oplus\eta)=1
&\Longrightarrow
I_u(h_t\oplus r_k^H(\eta))=1,\\
A_{u,t,H}(h_t,\eta)=1
&\Longrightarrow
A_{u,t,k}(h_t,r_k^H(\eta))=1.
\end{aligned}
\tag{TR}
\]

Write `\mathsf{TR}_{u,t}^{H}(\mathcal C)=1` when both implications hold on `\mathcal C`. If identity is presented as an explicitly horizon-indexed family, the first line is equivalently written

\[
I_{u,H}(h_t\oplus\eta)=1
\Longrightarrow
I_{u,k}(h_t\oplus\eta_{\le k})=1.
\]

This is an additional premise, not a consequence of full-tail admission. Constitutive or safety-style predicates may be declared to satisfy it; terminal-achievement predicates need not. A terminal-only goal can accept a completed tail while rejecting an intermediate prefix. Any theorem that promotes prefix-of-an-admitted-tail evidence to a prefix-level identity, admissibility or joint verdict must therefore carry `(TR)` explicitly.

### 2.4 The wearing ledger

Where the NC2.5 budget notation is used, let

\[
\tau_{b,t}=C_{\mathrm{cap},t}-\Phi_{\mathrm{load},t}.
\]

`\Phi_{\mathrm{load},t}` records declared structural burden and `\tau_{b,t}` a remaining margin under the chosen capacity convention. Neither variable is, by definition, an identity witness. The ledger is time-indexed because burden accumulates: a successor specification must carry the burden of the realised event forward, `\Phi_{\mathrm{load},t+1}=\Phi_{\mathrm{load},t}+\mathrm{wear}(e_t)`, or the same budget is re-offered at every update and can never be exhausted. Re-measuring wear from zero at each construction turns the ledger into a per-construction constant and voids any claim of wearing across a run. Viability may depend on them:

\[
V_{t,k}=V_{t,k}(h_t,\eta_{\le k},\Phi_{\mathrm{load}},\tau_b),
\]

but no implication

\[
(\Phi_{\mathrm{load}},\tau_b)\Longrightarrow I_u
\]

is admitted without a separate bridge premise.

### 2.5 Sealed construction specification

For each horizon, collect every declared input needed to construct the root reservoir and its adaptive suffix problems into the construction specification

\[
\Theta_{u,t}^{H}
=
(H,D_u,
\mathsf{IntSpec}_{u,t},
\mathsf{AdmSpec}_{u,t:t+H},
\mathsf{ViabSpec}_{t:t+H},
\mathsf{DynSpec}_{t:t+H},
\mathsf{Model}_t,
\mathsf{Prov}_t,
\mathsf{Val}_{u,t}^{H},
\mathsf{Scheme}_t).
\]

Here `\mathsf{Val}_{u,t}^{H}` is the finite construction validity envelope (regime and internal-time bounds); `\mathsf{IntSpec}` contains the authority, version, implementation commitment, provenance and validity record of the partial observation-to-history interpreter; `\mathsf{AdmSpec}` contains the compiled structural-admissibility family required by the root and every suffix problem, together with the exact source map, composition relation and `B\to A` binding; `\mathsf{ViabSpec}` contains the corresponding prefix-viability family; and `\mathsf{DynSpec}` contains the action, disturbance and transition correspondences. The boundary remains one sealed record within `D_u`; `\mathsf{AdmSpec}` binds its compiled output rather than introducing a second writable boundary store. Each component carries its applicable authority and version record. A mismatch between the active `B_{u,t}^{v_B}` and compiled `A_{u,t,0:H}` invalidates `\Theta`. Admissibility, viability or interpretive content is therefore not silently attributed either to the person or to the platform: its source is part of the specification. The implementation commitment in `\mathsf{IntSpec}` binds the interpreter's declared record, not the runtime behaviour of the procedure that realises it; faithfulness of that procedure to its record is a separate deployment obligation, not a consequence of any seal.

For a suffix beginning at time `s` with remaining horizon `r`, write

\[
\Theta_{u,t}^{H}\!\downarrow_{s,r}
\]

for the corresponding fixed suffix of the same specification. A later revision produces a new `\Theta`; it cannot be substituted into a continuation certificate issued under the earlier specification. For `H=0`, the future dynamics and viability families are empty while the current identity and admissibility verdicts remain defined.

---

## 3. The future-indexed reservoir

### Definition 3.1 — Joint trajectory verdict

For a reachable tail `\eta\in\Gamma_{t,H}(h_t)`, define

\[
J_{u,t}^{H}(h_t,\eta)
=
I_u(h_t\oplus\eta)
\cdot
A_{u,t,H}(h_t,\eta)
\cdot
\prod_{k=1}^{H}V_{t,k}(h_t,\eta_{\le k}).
\]

At `H=0`, declare `h_t\oplus\varnothing=h_t` and take the empty viability product as `1`, so

\[
J_{u,t}^{0}(h_t,\varnothing)
=
I_u(h_t)\cdot A_{u,t,0}(h_t,\varnothing).
\]

This multiplicative notation is Boolean conjunction. It does not assign weights or tradeability to the factors.

### Definition 3.2 — Existential future-indexed admissibility reservoir

The horizon-`H` reservoir for `u` at history `h_t` is

\[
\boxed{
\mathcal R_{u,t}^{H}(h_t)
=
\left\{
\eta\in\Gamma_{t,H}(h_t):
J_{u,t}^{H}(h_t,\eta)=1
\right\}.
}
\]

It is **existential** because membership establishes one admitted continuation, not survival against every possible disturbance.

A certified implementation binds each admitted `\eta` to a certificate

\[
\mathsf{Cert}_{u,t}^{H}(\eta)
=
(\mathsf{Reach},\mathsf{Id},\mathsf{Adm},\mathsf{Viab},
\mathsf{Ground},\mathsf{Val}),
\]

recording the declared reachability witness, identity source, admissibility and prefix-viability verdicts, independent grounding references and finite validity envelope. The elementary set results below use only the tail projection; the certificate is required for auditability, not smuggled into the proof as an oracle.

### Remark 3.2 — Representation is not grounding

`\mathcal R_{u,t}^{H}` represents continuations admitted under declared predicates. It does not create the ground of those predicates merely by recording their outputs. In particular, an append-only history is not automatically a structural-load law, and a stored identity label is not automatically an identity witness. Grounding must be specified and tested independently.

### Definition 3.2a — Prefix–fibre geometry

For `H\ge 1` and `a\in U_t(h_t)`, define the reachable action fibre

\[
\Gamma_{t,H}(h_t\mid a)
=
\{\eta\in\Gamma_{t,H}(h_t):\pi_1(\eta)=a\}.
\]

For `0\le k\le H` and a reachable prefix `\rho_k`, define the reservoir prefix fibre

\[
\mathcal R_{u,t}^{H}[\rho_k]
=
\{\eta\in\mathcal R_{u,t}^{H}:r_k^H(\eta)=\rho_k\}.
\]

The finite-horizon prefix–fibre geometry is the combinatorial object

\[
\mathcal G(\mathcal R_{u,t}^{H})
=
\left(
\mathcal R_{u,t}^{H},
\pi_1,
(r_k^H)_{k=0}^{H},
(\mathcal R_{u,t}^{H}\cap\Gamma_{t,H}(h_t\mid a))_{a},
(\mathcal R_{u,t}^{H}[\rho_k])_{k,\rho_k}
\right).
\]

No topology, measure or density is assumed by this definition. Here *geometry* means the projection and prefix-fibre structure retained after the joint verdict across the finitely many prefix depths; the reservoir or its branching need not be finite. Scalar summaries may rank or describe that object, but they are not identified with it.

### Definition 3.3 — Present projection

For `H\ge 1`, the existential present support is

\[
\Pi_{u,t}^{\exists,H}(h_t)
=
\left\{
a\in U_t(h_t):
\exists\eta\in\mathcal R_{u,t}^{H}(h_t)
\text{ whose first action is }a
\right\}.
\]

The map from a tail to its first action is denoted `\pi_1`; hence

\[
\Pi_{u,t}^{\exists,H}
=
\operatorname{First}\!\left(\mathcal G(\mathcal R_{u,t}^{H})\right)
=
\pi_1(\mathcal R_{u,t}^{H}).
\]

At `H=0`, `\mathcal R_{u,t}^{0}` and the terminal indicator `\mathsf K_{u,t}^{0}` remain defined, but no action-bearing present support or first-action projection is defined.

### Definition 3.4 — Adaptive-robust present support

Fix `\Theta_{u,t}^{H}`. Every reservoir, support and continuation indicator in this definition is evaluated under that specification or its declared suffix `\Theta_{u,t}^{H}\!\downarrow_{s,r}`; the parameter is suppressed below only to keep the notation readable. A later specification version cannot discharge an earlier continuation indicator.

For `H\ge 1`, an action `a` and a declared successor `x'`, define the one-step fibre of the current reservoir by

\[
\mathcal R_{u,t}^{H}(h_t\mid a,x')
=
\left\{
\eta\in\mathcal R_{u,t}^{H}(h_t):
\eta_{\le 1}=(a,x')
\right\}.
\]

Define the continuation indicator inductively on the remaining horizon. At the base,

\[
\mathsf K_{u,t}^{0}(h_t)
=
\mathbf 1[
\mathcal R_{u,t}^{0}(h_t)\neq\varnothing
].
\]

For `H\ge 1`, assuming `\mathsf K^{H-1}` has been defined, set

\[
\Pi_{u,t}^{\mathrm{rob},H}(h_t)
=
\left\{
\begin{array}{l|l}
a\in\Pi_{u,t}^{\exists,H}(h_t)
&
\begin{array}{l}
\forall w\in W_t(h_t,a),
\forall x'\in F_t(h_t,a,w):\\
\mathcal R_{u,t}^{H}(h_t\mid a,x')\neq\varnothing,\\
\mathsf K_{u,t+1}^{H-1}(h_t\oplus(a,x'))=1
\end{array}
\end{array}
\right\},
\]

and then define

\[
\mathsf K_{u,t}^{H}(h_t)
=
\mathbf 1[
\Pi_{u,t}^{\mathrm{rob},H}(h_t)\neq\varnothing
].
\]

The one-step-fibre conjunct prevents a newly generated successor reservoir from laundering a realised prefix for which the current reservoir contains no admitted full-tail extension. The continuation-indicator conjunct makes the definition genuinely recursive: when `H-1\ge 1`, it requires a non-empty next adaptive-robust support; when `H-1=0`, it requires the terminal reservoir to be non-empty.

Thus `\Pi_{u,t}^{\mathrm{rob},H}\subseteq\Pi_{u,t}^{\exists,H}` and the support represents an adaptive policy tree over the declared disturbance-successor branching. Possibility,

\[
\exists w\,\exists x'\,\exists\eta',
\]

is strictly weaker than the inductive condition

\[
\forall w\,\forall x':
\left[
\mathcal R_{u,t}^{H}(h_t\mid a,x')\neq\varnothing
\land
\mathsf K_{u,t+1}^{H-1}(h_t\oplus(a,x'))=1
\right].
\]

These quantifier structures may not be interchanged silently.

### Definition 3.5 — Reservoir seal and lineage

A reservoir seal is a record

\[
\Sigma_{u,t}^{H}
=
(t,H,
\mathsf{Com}(\mathcal O_t^{\mathrm{priv}}),
\mathsf{Com}(\mathsf{Int}_{u,t}^{v}),
\mathsf{Com}(h_t;\mathcal O_t^{\mathrm{priv}},\mathsf{Int}_{u,t}^{v}),
\mathsf{Com}(\Theta_{u,t}^{H}),
\mathsf{Com}(\mathcal R_{u,t}^{H};\mathsf{Gen},\mathsf{Cert}),
\mathsf{Val}_{u,t}^{H},
\mathsf{Prov}_t,
\mathsf{Scheme}_t),
\]

where `\Theta_{u,t}^{H}` binds the declaration, attributed-interpreter specification, admissibility and viability families, dynamics, model, provenance and commitment scheme used by the construction; `\mathsf{Int}_{u,t}^{v}` is the versioned attributed interpreter of Project Declaration 8.1; the third commitment binds its unique output history to the authenticated observation rather than accepting an unattested history; `\mathsf{Val}_{u,t}^{H}` states the regime and internal-time envelope in which the construction is valid; and `\mathsf{Prov}_t` records the provenance needed to reproduce it. `\mathsf{Com}` is an exact canonical digest when the object is finite and enumerated, or a commitment to the generator, specification, parameters and canonical representation when the object is implicit or non-finite. `\mathsf{Scheme}_t` identifies the commitment scheme. The notation does not presume that every reservoir can be exhaustively hashed as a literal list.

A later revision creates a new seal. It does not overwrite the earlier one.

### Definition 3.6 — Future-indexed admissibility environment

The maintained environment, called the *atmosphere* in the companion bridge, is the tuple

\[
\boxed{
\mathfrak A_{u,t}^{H}
=
(B_{u,t}^{v_B},
A_{u,t,0:H},
\Theta_{u,t}^{H},
\mathcal R_{u,t}^{H},
\mathcal G(\mathcal R_{u,t}^{H}),
\Pi_{u,t}^{\exists,H},
\Pi_{u,t}^{\mathrm{rob},H},
\mathsf K,
\Pi_{\Sigma}^{\mathrm{rob}},
\mathsf K^{\Sigma},
\mathsf{Cert},
\mathsf{Val},
\mathsf{Gen},
\mathsf{Upd},
\Sigma,
O_{\mathrm{view}},
O_{\mathrm{opt}},
O_{\mathrm{enf}},
G_{\mathrm{enf}}).
}
\]

Here:

- `B_{u,t}^{v_B}` and `A_{u,t,0:H}` are the exact sealed boundary and compiled-admissibility views already bound by `\Theta_{u,t}^{H}`; listing them makes the construction chain explicit and does not create parallel mutable stores;
- `\Theta_{u,t}^{H}` is the complete active construction specification;
- `\mathcal R_{u,t}^{H}` is the admitted reachable-tail reservoir generated under that specification;
- `\mathcal G(\mathcal R_{u,t}^{H})` is the canonical finite-horizon prefix–fibre view derived from the reservoir, not an independent ground or writable input;
- `\mathsf{Gen}` is a declared partial map whose complete logical inputs are the authenticated observation, the versioned attributed interpreter and `\Theta_{u,t}^{H}`; the interpreter must return a unique attributed history before reservoir construction, and no future-event oracle or undeclared logical side channel belongs to the generator's domain;
- `\Pi_{u,t}^{\exists,H}`, `\Pi_{u,t}^{\mathrm{rob},H}` and `\mathsf K` denote the existential support, adaptive-robust support and continuation-indicator families of Definitions 3.3 and 3.4;
- `\Pi_{\Sigma}^{\mathrm{rob}}` and `\mathsf K^{\Sigma}` denote the recursively coupled seal-relative support and continuation-indicator families of Definition 4.5;
- `\mathsf{Cert}` binds admitted tails to their audit witnesses;
- `\mathsf{Val}` exposes the finite validity envelope without granting revision authority;
- `\mathsf{Upd}` constructs the next version after an event or authorised revision;
- `\Sigma` preserves sealing and provenance lineage;
- `O_{\mathrm{view}}` exposes typed information to a consumer;
- `O_{\mathrm{opt}}` is the complete channel available to the task optimizer;
- `O_{\mathrm{enf}}` is the versioned authenticated channel that converts mode-specific assurance evidence into an admission token or rejection witness;
- `G_{\mathrm{enf}}` is the separately authorised, versioned causal interface that verifies that artifact and mediates execution.

The atmosphere is therefore not merely a set. It is a set-valued runtime together with construction, update, access and enforcement topology. The tuple is a logical grouping of typed components, not a claim that one runtime object must hold all of them: an implementation may distribute generator output, assurance evidence, admission channel, enforcement interface and execution lineage across separate structures, provided their joint binding in each realised update is independently certifiable — in the finite companion, by the history-generated recurrence certificate.

### Remark 3.6 — Type separation does not imply process multiplication

Generator, consumer, selector and enforcer are distinct authority types. They need not occupy four physical services. An integrated implementation conforms only if it preserves the same write authority, access confinement, lineage and independently auditable mediation. This paper does not prove that a separately deployed reservoir service is logically necessary.

---

## 4. Elementary results

### Proposition 4.1 — Projection soundness

If

\[
a\in\Pi_{u,t}^{\exists,H}(h_t),
\]

then there exists at least one tail `\eta\in\mathcal R_{u,t}^{H}(h_t)` whose first action is `a`.

#### Proof

This is immediate from Definition 3.3. ∎

### Remark 4.1

Projection soundness is weak. It does not say that every successor of `a` preserves an admitted continuation. It does not say that the selected tail will occur. It does not establish robustness, optimality, uniqueness or liveness.

### Proposition 4.1a — Constitutive boundary intervention changes existential support

Fix `h_t`, `I_u`, `A^{\mathrm{ext}}_{u,t,H}`, every prefix-viability factor, the dynamics, model and task objective. Let two authorised boundary versions `B` and `B'` differ only in a personal constitutive clause and compile to `A^B` and `A^{B'}`. Suppose that for some action `a`,

\[
\mathcal R_{u,t}^{H;B}
\cap
\Gamma_{t,H}(h_t\mid a)
\neq\varnothing,
\qquad
\mathcal R_{u,t}^{H;B'}
\cap
\Gamma_{t,H}(h_t\mid a)
=\varnothing,
\]

and that the disagreement is unmasked by the held-fixed factors. Then

\[
a\in\Pi_{u,t}^{\exists,H;B}
\quad\text{and}\quad
a\notin\Pi_{u,t}^{\exists,H;B'}.
\]

#### Proof

The first non-empty action fibre supplies an admitted tail beginning with `a`, so Definition 3.3 includes `a`. The empty action fibre under `B'` supplies no such tail, so the same definition excludes `a`. ∎

The intervention is evaluated at time `t` over two counterfactual specifications. No member of either future tail set has to occur before the support changes. Under Proposition 5.1, this is present model- and declaration-dependence, not a future-to-past signal.

### Proposition 4.2 — A predicate does not select

Suppose `|\Pi_{u,t}^{\exists,H}(h_t)|\ge 2`. Then the reservoir and its Boolean trajectory verdict do not determine a unique present action.

#### Proof

Choose distinct `a,b` in the support. A selector choosing `a` and a selector choosing `b` are both compatible with the same reservoir. Therefore the reservoir does not determine a unique selector output. ∎

### Corollary 4.2 — Task objectives remain possible but subordinate

Let the declared active support be one of

\[
\Pi_t^{\mathrm{act}}
\in
\left\{
\Pi_{u,t}^{\exists,H}(h_t),
\Pi_{u,t}^{\mathrm{rob},H}(h_t),
\Pi_{\Sigma,k}^{\mathrm{rob}}(\rho_k)
\right\},
\]

according to the assurance claim in force. For `\Pi_t^{\mathrm{act}}\neq\varnothing`, a task selector

\[
S_u:
(h_t,\Pi_t^{\mathrm{act}},g_t)
\longrightarrow
a_t\in\Pi_t^{\mathrm{act}}
\]

may rank that support according to a task goal `g_t`. When the active support is empty, the displayed selector is not evaluated; a separately authorised and versioned empty-support handler must return defer, safe-mode, escalation or termination semantics. This does not identify `g_t` with the predicate that formed the support.

### Theorem 4.3 — Adaptive-robust one-step closure

Assume:

1. `H\ge 1`;
2. the executed action satisfies
   \[
   a_t\in\Pi_{u,t}^{\mathrm{rob},H}(h_t);
   \]
3. the realised disturbance lies in `W_t(h_t,a_t)`;
4. the realised successor lies in `F_t(h_t,a_t,w_t)`;
5. the fixed construction-specification lineage used to evaluate the support and its successor indicator remains in force from support computation through the successor continuation check. A changed specification starts a new certificate and cannot discharge this premise.

Then

\[
\mathcal R_{u,t}^{H}(h_t\mid a_t,x_{t+1})\neq\varnothing
\]

and

\[
\mathsf K_{u,t+1}^{H-1}(h_{t+1})=1.
\]

Consequently, if `H=1` then `\mathcal R_{u,t+1}^{0}(h_{t+1})\neq\varnothing`; if `H>1` then `\Pi_{u,t+1}^{\mathrm{rob},H-1}(h_{t+1})\neq\varnothing`.

#### Proof

Definition 3.4 requires both displayed conjuncts for every declared disturbance and every corresponding successor. Premises 3 and 4 place the realised pair inside those universal quantifiers. The two case consequences are exactly the base and positive-horizon clauses in the definition of `\mathsf K`. ∎

### Corollary 4.3 — Adaptive continuation through the declared horizon

Suppose `\Pi_{u,t}^{\mathrm{rob},H}(h_t)\neq\varnothing`. At each nonterminal step, let the selector choose an action from the current adaptive-robust support. If every realised disturbance-successor pair remains inside the declared dynamics and the fixed suffix lineage of `\Theta_{u,t}^{H}` remains in force throughout the `H`-step certificate, then:

1. an adaptive-robust action is available before every remaining transition;
2. every realised one-step prefix indexes a non-empty fibre of the reservoir computed immediately before that transition; and
3. the terminal reservoir `\mathcal R_{u,t+H}^{0}(h_{t+H})` is non-empty.

#### Proof

Choose any initial action from the non-empty support. Theorem 4.3 makes the realised current fibre non-empty and sets the successor continuation indicator to `1`. If the remaining horizon is positive, the definition of that indicator gives a non-empty next adaptive-robust support; otherwise it gives the non-empty terminal reservoir. Repeating this argument proves all three claims by induction on the remaining horizon. ∎

### Remark 4.3

Corollary 4.3 concerns a lineage of reservoirs recomputed from changed histories under one fixed construction-specification lineage and certifies that each realised one-step prefix indexes a non-empty fibre in the reservoir computed immediately before it. A changed `\Theta` starts a new adaptive certificate. Even without such a change, the corollary does not imply that the whole realised trace remains inside the original pre-action seal: recomputation may admit tails absent from that original set. The sealed claim therefore needs a different support.

### Definition 4.4 — Conditional fibre and prefix closure of a sealed reservoir

Let a seal `\Sigma` fix

\[
\mathcal R^\Sigma=\mathcal R_{u,t}^{H}(h_t).
\]

For a realised `k`-transition prefix `\rho_k`, with `\rho_0=\varnothing`, define the conditional fibre

\[
\mathcal R^\Sigma[\rho_k]
=
\{\eta\in\mathcal R^\Sigma:\eta_{\le k}=\rho_k\},
\]

and define

\[
\operatorname{Pref}_k(\mathcal R^\Sigma)
=
\{\eta_{\le k}:\eta\in\mathcal R^\Sigma\}.
\]

### Definition 4.5 — Recursive seal-relative robust support

Define the seal-relative continuation indicator backward inside the original reservoir fixed by `\Sigma`. At the terminal depth,

\[
\mathsf K_{H}^{\Sigma}(\rho_H)
=
\mathbf 1[
\mathcal R^\Sigma[\rho_H]\neq\varnothing
].
\]

For `0\le k<H`, assuming `\mathsf K_{k+1}^{\Sigma}` has been defined, set

\[
\Pi_{\Sigma,k}^{\mathrm{rob}}(\rho_k)
=
\left\{
\begin{array}{l|l}
a\in U_{t+k}(h_t\oplus\rho_k)
&
\begin{array}{l}
\forall w\in W_{t+k}(h_t\oplus\rho_k,a),
\forall x'\in F_{t+k}(h_t\oplus\rho_k,a,w):\\
\mathcal R^\Sigma[\rho_k\oplus(a,x')]\neq\varnothing,\\
\mathsf K_{k+1}^{\Sigma}(\rho_k\oplus(a,x'))=1
\end{array}
\end{array}
\right\},
\]

and then define

\[
\mathsf K_k^{\Sigma}(\rho_k)
=
\mathbf 1[
\Pi_{\Sigma,k}^{\mathrm{rob}}(\rho_k)\neq\varnothing
].
\]

The one-step conditional-fibre conjunct remains explicit because it is the auditable witness that the branch has not left the original seal. The child indicator makes the property genuinely recursive: when `k+1<H`, it requires a non-empty next seal-relative support; at `k+1=H`, it requires a non-empty terminal conditional fibre. At `k=H` there is no action-bearing support.

At the root, `\mathcal R^\Sigma=\mathcal R_{u,t}^{H}(h_t)`, so adaptive and seal-relative robustness use the same current-reservoir fibre test. They differ in the recursive object: `\mathsf K` follows reservoirs recomputed from successor histories under the fixed specification lineage, whereas `\mathsf K^\Sigma` remains inside the original seal. Without a suffix- or time-consistency premise linking those objects, neither support is asserted to include the other.

Call the condition obtained by retaining only the universal non-empty conditional-fibre conjunct at the current depth the *shallow one-step seal condition*. It omits the child `\mathsf K^\Sigma` conjunct. With at least two steps remaining, it is in general weaker than Definition 4.5 and can be strictly weaker; by itself it is not a full-horizon certificate. At `H=1`, the shallow one-step seal condition and Definition 4.5 coincide extensionally because the child indicator is terminal. Keeping that terminal indicator explicit nevertheless records the endpoint audit witness.

### Theorem 4.6 — Sealed robust continuation and prefix preservation

Assume:

1. `\mathcal R^\Sigma\neq\varnothing` and `\mathsf K_0^\Sigma(\varnothing)=1`;
2. for every `k=0,\ldots,H-1`, the selector chooses
   \[
   a_{t+k}\in\Pi_{\Sigma,k}^{\mathrm{rob}}(\rho_k);
   \]
3. every realised disturbance and successor lies inside the dynamics and disturbance declaration fixed by `\Sigma`;
4. the validity envelope `\mathsf{Val}_{u,t}^{H}` remains satisfied through the realised prefix;
5. no seal-changing revision occurs.

Then, for every `k\le H`,

\[
\mathcal R^\Sigma[\rho_k]\neq\varnothing,
\qquad
\rho_k\in\operatorname{Pref}_k(\mathcal R^\Sigma),
\qquad
\mathsf K_k^\Sigma(\rho_k)=1.
\]

For every `k<H`, consequently,

\[
\Pi_{\Sigma,k}^{\mathrm{rob}}(\rho_k)\neq\varnothing.
\]

#### Proof

At `k=0`, premise 1 gives the non-empty root fibre and root indicator. Suppose the three displayed claims hold at `k<H`. By premise 2 and Definition 4.5, every declared disturbance-successor branch following the chosen action has both a non-empty original-seal fibre and child indicator `1`. Premise 3 places the realised pair inside those universal quantifiers, so the claims hold for `\rho_{k+1}`. If `k+1<H`, the definition of the child indicator gives a non-empty next support; if `k+1=H`, its terminal clause gives the non-empty final fibre. Premises 4 and 5 keep the same sealed construction operative rather than silently reclassifying the prefix under an expired or revised declaration. Definition 4.4 converts non-empty fibres into prefix-closure membership. Induction completes the proof. ∎

### Corollary 4.6 — Disciplined reading of *reality catches the predicate*

If the hypotheses of Theorem 4.6 hold — in particular, the root seal-relative indicator equals `1` and every realised action is selected from the corresponding seal-relative robust support — then an action remains available before every declared transition, and each realised prefix remains the prefix of at least one trajectory admitted before the first action.

### Corollary 4.6a — Prefix-level joint verdicts under thin temporal restriction

Assume the hypotheses of Theorem 4.6 and additionally

\[
\mathsf{TR}_{u,t}^{H}(\mathcal R^\Sigma)=1.
\]

Then, for every `k\le H`,

\[
\rho_k\in\Gamma_{t,k}(h_t)
\qquad\text{and}\qquad
J_{u,t}^{k}(h_t,\rho_k)=1.
\]

#### Proof

By Theorem 4.6, `\mathcal R^\Sigma[\rho_k]\neq\varnothing`. Choose

\[
\eta^{(k)}\in\mathcal R^\Sigma[\rho_k].
\]

Reservoir membership gives `J_{u,t}^{H}(h_t,\eta^{(k)})=1`, hence full-tail identity and admissibility are `1`, and every viability factor through depth `H` is `1`. Since `\eta^{(k)}_{\le k}=\rho_k`, `(TR)` yields `I_u(h_t\oplus\rho_k)=1` and `A_{u,t,k}(h_t,\rho_k)=1`. Reachability of the full tail gives reachability of its prefix, and the first `k` viability factors are already present in the full-tail verdict. These are exactly the factors of `J_{u,t}^{k}(h_t,\rho_k)`. ∎

The conclusion is a verdict on the shortened horizon. It does not retype `\rho_k` as an element of the horizon-`H` reservoir; the base theorem's prefix-closure and non-empty-fibre statements remain distinct.

### Remark 4.6 — Revision lineage

If the environment is regenerated under a changed model, changed declaration or newly observed exogenous condition, the new reservoir may not be a subset of the old one. The correct object is then a versioned lineage

\[
\Sigma_{u,t}^{H}\to\Sigma_{u,t+1}^{H}\to\cdots,
\]

not a false claim that the original future had been fixed.

---

## 5. Non-causality without retrocausality

### 5.1 Three distinct questions

The word *causal* is used for three different relations.

1. **Physical causation:** whether a later physical event changes an earlier event.
2. **Architectural influence:** whether an upstream component changes which transition is executed.
3. **Grounding and authority:** whether the task optimizer can derive, query, reconstruct or revise the predicate that constrains it.

The present work rejects physical retrocausality, accepts causal architectural influence, and studies non-actionable grounding relative to declared access channels.

Here *non-actionable ground* is authority- and channel-relative. The task optimizer may receive derived projections and act causally inside them, but it has neither direct revision authority nor a privileged ground supplied as a task objective or unrestricted membership-query surface. The term does not mean that the ground has no downstream informational or causal effect.

### Proposition 5.1 — Future indexing does not imply future-to-past information flow

Suppose `\mathsf{Gen}` computes `\mathcal R_{u,t}^{H}` from the three logical inputs

\[
\left(
\mathcal O_t^{\mathrm{priv}},
\mathsf{Int}_{u,t}^{v},
\Theta_{u,t}^{H}
\right),
\]

where the observation and construction specification are authenticated, the interpreter is versioned and attributed, all three inputs are available at time `t`, and

\[
\mathsf{Int}_{u,t}^{v}(\mathcal O_t^{\mathrm{priv}})
=
(h_t,\mathsf{Prov}_{u,t}^{\mathsf{Int}})
\]

is uniquely defined.

Then the fact that elements of `\mathcal R_{u,t}^{H}` are indexed by times later than `t` does not establish an information channel from a later realised event to time `t`.

#### Proof

Every logical input to `\mathsf{Gen}` — the authenticated observation, the versioned attributed interpreter and the active construction specification — is available at time `t` by premise. The uniquely interpreted history is produced from the first two inputs at time `t`; it is not an observation of a later realised event. The future-indexed predicate, dynamics and model families are declarations inside `\Theta`, not observations of later realised events. A future index is part of the codomain description, not an additional observation. Therefore no realised future event is an input to the computation. ∎

### Remark 5.1 — Oracle leakage

If a value described as read from the future has no provenance available at time `t`, then the architecture contains an undeclared oracle, leakage channel or retrospective rewrite. Renaming that defect *non-causality* does not repair it.

### Definition 5.2 — Optimizer-accessible channel

Let `\Omega` be a declared ensemble of complete cases. Let

\[
O_{\mathrm{opt}}:\Omega\to Y
\]

be the complete transcript available to the task optimizer, including permitted reservoir projections, rejection signals, timing, repeated-query results and side-channel observables declared in scope.

Let

\[
J_{\mathrm{res}}:\Omega\to Z
\]

be a target concerning privileged reservoir membership, identity compatibility or the exact admission verdict.

### Theorem 5.3 — Confined-access non-absorption

If there exist `\omega_1,\omega_2\in\Omega` such that

\[
O_{\mathrm{opt}}(\omega_1)=O_{\mathrm{opt}}(\omega_2)
\]

but

\[
J_{\mathrm{res}}(\omega_1)\neq J_{\mathrm{res}}(\omega_2),
\]

then no function `f:Y\to Z` satisfies

\[
J_{\mathrm{res}}=f\circ O_{\mathrm{opt}}
\]

on all of `\Omega`.

#### Proof

If such an `f` existed, equal optimizer observations would produce equal values of `f`, contradicting the unequal target values. ∎

### Corollary 5.3 — Importing the verdict changes the architecture

An optimizer can reproduce the privileged target exactly only if the declared channel is refined enough to separate every target-changing fibre, or if privileged information is imported through an additional channel. Either move changes the access architecture.

### Proposition 5.4 — Non-degenerate causal enforcement is compatible with non-actionable ground

Assume:

1. **complete mediation:** no proposed transition can execute without an authenticated output of `G_{\mathrm{enf}}`; and
2. **a verdict intervention witness:** there exist two otherwise matched cases with the same realised history, proposed action, dynamics and exogenous input, differing only in the authenticated enforcement verdict, for which the realised execution traces differ, including an executed transition versus authenticated rejection, deferral or safe-mode.

Then `G_{\mathrm{enf}}` is causally relevant to the realised trace. If, additionally, the target-changing fibre premise of Theorem 5.3 holds for the complete declared `O_{\mathrm{opt}}` channel and the optimizer has no write authority over the declaration or generator, that causal relevance is compatible with both exact non-computation and non-revision of the privileged reservoir target.

#### Proof

Premise 2 is the required non-degenerate counterfactual witness: changing the enforcement verdict while holding the matched inputs fixed changes execution. That proves only causal relevance. Under the additional fibre premise of Theorem 5.3, exact computation is excluded; under the additional write-separation premise, revision is excluded. Since neither additional premise removes the verdict intervention witness, the three properties are compatible. ∎

### 5.2 Why consumers may read

A consumer readout has type

\[
y_{i,t}=O_i(\mathfrak A_{u,t}^{H}).
\]

Reading is a causal observation event. It is not automatically selection, enforcement, revision or reconstruction. A typed consumer may receive:

- the current admitted action support;
- a coarse continuation class;
- a proof-carrying admission token;
- a bounded explanation channel;
- a local counterfactual warning;
- a phase or urgency label.

The consumer need not receive:

- the full identity predicate;
- the complete reservoir boundary;
- privileged internal-world observations;
- the revision key;
- an unlimited membership-query oracle.

The phrase *they read from the pool* is therefore architecturally coherent when the read interface is declared. Removing reading would remove the operational content of the atmosphere.

---

## 6. Identity, burden and non-monotone geometry

### Proposition 6.1 — Budget does not determine identity

There exist models with equal `\Phi_{\mathrm{load},t}` and `\tau_{b,t}` but different identity verdicts, and models with equal identity verdicts but different `\Phi_{\mathrm{load},t}` and `\tau_{b,t}`.

#### Proof by countermodel

For the first direction, take two declaration records `D_u,D_v` over the same physical history and assign identical budget variables while `I_u(h)=1` and `I_v(h)=0`. For the second direction, hold `I_u(h)=1` in two histories but assign different admissible burden histories under the declared accounting convention. Both constructions satisfy the claimed separations. ∎

### Corollary 6.1

Any theorem identifying identity with the `\Phi_{\mathrm{load}}/\tau_b` ledger requires an additional premise excluding these countermodels.

### Proposition 6.2 — Monotone budget does not force nested reservoirs

There exist a declared common comparison space `\mathcal Z`, history-conditioned reservoir domains and embeddings `\iota_t,\iota_{t+1}` such that, even when `\tau_{b,t+1}\le\tau_{b,t}`, it does not follow that

\[
\iota_{t+1}(\mathcal R_{u,t+1}^{H})
\subseteq
\iota_t(\mathcal R_{u,t}^{H}).
\]

#### Proof by countermodel

Take `\mathcal Z=\{z_0,z_1\}`. Let the current reservoir domain contain one admitted continuation `\eta_0`, the later domain contain one admitted continuation `\eta_1`, and choose embeddings `\iota_t(\eta_0)=z_0` and `\iota_{t+1}(\eta_1)=z_1`. These reservoirs are realised by a finite dynamics in which the successor observation opens a branch that was unreachable at `t`, while the declared budget decreases from `\tau_{b,t}` to `\tau_{b,t+1}`. Then `z_1\notin\{z_0\}` despite the budget inequality. Thus scalar budget order alone does not impose set inclusion. ∎

### Remark 6.2

This is the formal location of **set-valued pulsation** in this paper. Remaining budget may wear monotonically while the shape, branching and local margin of future continuation geometry change non-monotonically. This term does not establish membership in the ONTOΣ XIII.1 pulsation-channel subclass or import its phase-resonance mechanism; that requires a separate bridge and conformance proof.

### Proposition 6.2a — Collision-limited scalar insufficiency

Let `s` be a scalar summary on a declared comparison class of reservoirs. If two reservoirs in that class satisfy

\[
s(\mathcal R_1)=s(\mathcal R_2)
\qquad\text{but}\qquad
\pi_1(\mathcal R_1)\neq\pi_1(\mathcal R_2),
\]

then no function `q` on the image of `s` can recover existential support on that class:

\[
\pi_1(\mathcal R)=q(s(\mathcal R)).
\]

#### Proof

Equal scalar inputs would force `q(s(\mathcal R_1))=q(s(\mathcal R_2))`, contradicting the different supports. ∎

This is a collision-relative statement. It does not claim that every scalar on every restricted class is insufficient. In particular, equal cardinality with different first-action support is one explicit collision witness, not a theorem against all possible encodings.

### Definition 6.3 — Existential continuity verdict

Define

\[
E_{u,t}^{H}
=
\mathbf 1[\mathcal R_{u,t}^{H}\neq\varnothing].
\]

This is a binary horizon-relative existential verdict.

### Proposition 6.4 — Existential continuity is not liveness by definition

`E_{u,t}^{H}=1` does not entail cycle reinitiation, autonomous activity, awareness, consciousness or indefinite persistence.

#### Proof

A system may possess one admissible dormant continuation without completing or reinitiating any cycle. The existential set condition therefore does not imply those stronger targets. ∎

---

## 7. A finite diagnostic model

The examples in this section are instruments for separating claims, not empirical models of a person.

### 7.1 Same present, different identity reservoir

Let the visible state be `x`, the horizon be one, and the actions be `L` and `R`. Two complete histories `h^\alpha,h^\beta` share the same visible state, budget and task observation, but differ in privileged lineage data evaluated under the same sealed declaration `D_u` and its witness `\mathsf W_u`. For each `\gamma\in\{\alpha,\beta\}`, let the dynamically reachable one-step tail set be

\[
\Gamma_{t,1}(h^\gamma)=\{\eta_L,\eta_R\},
\]

where `\eta_L=(L,x_L)` and `\eta_R=(R,x_R)` carry equal task reward. Assume moreover that, for every `\gamma\in\{\alpha,\beta\}` and `q\in\{L,R\}`,

\[
A_{u,t,1}(h^\gamma,\eta_q)
=
V_{t,1}(h^\gamma,\eta_q)
=1.
\]

Let

\[
I_u(h^\alpha\oplus\eta_L)=1,
\qquad
I_u(h^\alpha\oplus\eta_R)=0,
\]

and

\[
I_u(h^\beta\oplus\eta_L)=0,
\qquad
I_u(h^\beta\oplus\eta_R)=1.
\]

Then

\[
\Pi_{u}^{\exists,1}(h^\alpha)=\{L\},
\qquad
\Pi_{u}^{\exists,1}(h^\beta)=\{R\}.
\]

The same current snapshot and task reward do not determine the personal reservoir. This is a hidden-lineage witness, not evidence of mysticism.

### 7.1a Same present, different constitutive boundary

Now hold one history `h`, dynamics, model, task objective, `I_u=1`, `A^{\mathrm{ext}}=1` and `V=1` fixed on both reachable tails `\eta_L,\eta_R`. Let two authorised versions of the same personal boundary compile to

\[
\begin{array}{c|cc}
 & \eta_L & \eta_R\\ \hline
A^{B_L}_{u,t,1} & 1 & 0\\
A^{B_R}_{u,t,1} & 0 & 1
\end{array}
\]

with all non-admissibility verdict factors equal to `1`. Then

\[
\mathcal R_{u,t}^{1;B_L}=\{\eta_L\},
\qquad
\mathcal R_{u,t}^{1;B_R}=\{\eta_R\},
\]

and therefore

\[
\Pi^{\exists,1;B_L}_{u,t}=\{L\},
\qquad
\Pi^{\exists,1;B_R}_{u,t}=\{R\}.
\]

Both reservoirs have cardinality one, yet their existential supports differ. The fixture therefore witnesses three distinct facts at once:

1. the sealed `B\to A` binding is operational;
2. an authorised boundary revision can add or remove a whole current action fibre before any tail is realised;
3. reservoir cardinality alone does not recover the prefix–fibre geometry.

The boundary versions are counterfactual present inputs, not messages sent backward by `\eta_L` or `\eta_R`.

### 7.2 Same reservoir, different selectors

Let

\[
\Pi_{u}^{\exists,1}(h)=\{L,R\}.
\]

A selector with goal `g_L` chooses `L`; a selector with goal `g_R` chooses `R`. The atmosphere is unchanged. Therefore task preference may vary without revising the structural boundary.

### 7.3 Existentially safe, robustly unsafe

Assume action `a` has a declared branch `(w_0,x_0)` with a non-empty current fibre and child continuation indicator `1`, but another declared branch `(w_1,x_1)` for which either the current fibre is empty or the child indicator is `0`. Assume action `b` has a non-empty current fibre and child indicator `1` for every declared disturbance-successor branch. Then

\[
a,b\in\Pi^{\exists,H},
\qquad
b\in\Pi^{\mathrm{rob},H},
\qquad
a\notin\Pi^{\mathrm{rob},H}.
\]

An atmosphere advertising `a` as robust because one favourable continuation exists is mis-typed.

### 7.4 Intervention separation

The following two interventions test different objects.

1. Hold `I_u`, dynamics and selector fixed; alter an atmosphere component visible through `O_{\mathrm{view}}`. If declared consumer behaviour never changes on any non-degenerate test class, the atmosphere may be operationally redundant.
2. Hold dynamics and task goal fixed; change the authorised identity declaration on a reachable disagreement tail for which structural admissibility and every prefix-viability factor equal `1` in both arms. If the reservoir does not change on that unmasked witness, the declared identity predicate is not operative on the tested class.

These tests prevent the predicate and atmosphere from collapsing into one decorative label.

---

## 8. The Minerva-pattern factorisation

### Project Declaration 8.1 — Minerva-pattern candidate generation

The existing Minerva work motivates residual temporal carriage and non-participant observation. The following joint-verdict and reservoir-generation role is a new project declaration of this paper, not a theorem already established by that source.

Let the attributed observation interpreter be a versioned partial map

\[
\mathsf{Int}_{u,t}^{v}:
\mathcal O_t^{\mathrm{priv}}
\rightharpoonup
(h_t,\mathsf{Prov}_{u,t}^{\mathsf{Int}}).
\]

It is undefined when the authenticated observation does not determine one history under the sealed schema, when attribution is ambiguous, when required fields are absent, or when its validity record has expired. Its authority, version, implementation commitment and provenance are part of `\Theta_{u,t}^{H}`.

A Minerva-pattern operator has the partial type

\[
\mathsf{Min}_u:
(\mathcal O_t^{\mathrm{priv}},\mathsf{Int}_{u,t}^{v},\Theta_{u,t}^{H})
\rightharpoonup
(J_{u,t}^{H},\mathcal R_{u,t}^{H},
\mathsf{Cert}_{u,t}^{H},\Sigma_{u,t}^{H}).
\]

The explicit interpreter argument must equal the version committed inside `\Theta_{u,t}^{H}`; it is not a second free interpretation channel. If instantiated, Minerva combines authenticated observation of the declared internal world with that interpreter and the complete construction specification. A unique attributed `h_t` is required before construction. The resulting seal binds the observation commitment, interpreter version and implementation, attributed output history, construction specification, reservoir and membership certificates. Ambiguity or any binding failure yields no reservoir output rather than a guessed history.

It does not, by this type signature:

- choose the task objective;
- select a unique action;
- send a motor command;
- revise `D_u` without authority;
- certify phenomenal consciousness;
- guarantee that its observation channel is complete or calibrated.

Membership in this project class requires a sealed implementation mapping, matched-reset tests for residual-state dependence, write-severance from the task optimizer, and evidence that the native enforcement path cannot bypass the generated admission relation. Type consistency alone is insufficient.

In this precise project sense Minerva performs a transfiguration. She does not move the body. She changes the formal form in which the system's internal world becomes available to the rest of the architecture.

### 8.2 Predicate consumer

A consumer `C_i` receives

\[
y_{i,t}=O_i(\mathcal R_{u,t}^{H},\Sigma_{u,t}^{H})
\]

and produces a proposal, warning, ranking or local filter. Consumer access is declared by type and threat model.

### 8.3 Selector

Let `\Pi_t^{\mathrm{act}}` denote the support selected by the active assurance mode typed in §8.4. For `\Pi_t^{\mathrm{act}}\neq\varnothing`, a selector receives that support, its permitted readout and a task objective:

\[
S_i:
(h_t,\Pi_t^{\mathrm{act}},y_{i,t},g_{i,t})
\longrightarrow
a_t^{\mathrm{prop}}\in\Pi_t^{\mathrm{act}}.
\]

If `\Pi_t^{\mathrm{act}}=\varnothing`, the selector is not evaluated and the separately authorised, versioned empty-support handler is invoked. Its proposal has no execution authority merely because it lies inside admitted support.

### 8.4 Enforcement

For a proposed action, let `m_t` name the active assurance mode and let `\Pi_t^{\mathrm{act}}` be the corresponding support, defined only on an action-bearing horizon:

\[
m_t\in
\{\mathsf{existential},
\mathsf{adaptive\mbox{-}robust},
\mathsf{seal\mbox{-}relative}\}.
\]

The enforcer must not erase the evidence distinction among those modes. Define the tagged assurance context

\[
\mathsf{AssurCtx}_t
=
(m_t,h_t,\Pi_t^{\mathrm{act}},E_t^{m_t},\mathsf{Val}_{u,t}^{H},\mathsf{Reg}_t),
\]

where `\mathsf{Reg}_t` is the explicitly checked runtime regime that must lie inside `\mathsf{Val}_{u,t}^{H}`, and the evidence payload is mode-specific:

\[
E_t^{m_t}
=
\begin{cases}
(\Theta\!\downarrow,\mathsf{Com}(\mathcal R_t),
\mathsf{Com}(\mathcal G(\mathcal R_t)),\mathsf W_{\mathrm{tail}}),
&m_t=\mathsf{existential},\\
(\mathsf{Com}(\Theta),\Theta\!\downarrow,\mathsf{Com}(\mathcal R_t),
\mathsf{Com}(\mathcal G(\mathcal R_t)),\mathsf W_{\mathrm{branch}},\mathsf K),
&m_t=\mathsf{adaptive\mbox{-}robust},\\
(\Sigma,\mathsf{Com}(\mathcal G(\mathcal R^\Sigma)),\rho_k,k,H-k,\mathsf W_{\mathrm{branch}}^{\Sigma},\mathsf K^{\Sigma}),
&m_t=\mathsf{seal\mbox{-}relative}.
\end{cases}
\]

Here `\mathsf W_{\mathrm{tail}}` names an admitted-tail witness, `\mathsf W_{\mathrm{branch}}` binds every declared disturbance-successor branch to a non-empty current fibre and recursive continuation certificate under one fixed `\Theta` lineage, and `\mathsf W_{\mathrm{branch}}^{\Sigma}` binds every declared branch to both a non-empty conditional fibre of the original seal and its child `\mathsf K^{\Sigma}` certificate.

Define the authenticated admission token or rejection witness by the versioned channel

\[
\kappa_{u,t}^{H,m_t}(a_t^{\mathrm{prop}})
=
O_{\mathrm{enf}}^{v_O}(
\mathsf{AssurCtx}_t,a_t^{\mathrm{prop}}).
\]

Let `\mathcal D_{\mathrm{enf}}^{v_G}` denote the set of authenticated, one-shot decision records whose verdict field lies in

\[
\{\mathsf{admit},\mathsf{reject},\mathsf{defer},\mathsf{safe\mbox{-}mode},\mathsf{escalate},\mathsf{terminate}\}.
\]

The enforcement interface has type

\[
G_{\mathrm{enf}}^{v_G}:
(h_t,a_t^{\mathrm{prop}},
\mathsf{AssurCtx}_t,
\kappa_{u,t}^{H,m_t}(a_t^{\mathrm{prop}}))
\longrightarrow
\mathcal D_{\mathrm{enf}}^{v_G}.
\]

The output of `G_{\mathrm{enf}}^{v_G}` is an authenticated, one-shot enforcement decision, not a bare enum. The admission token is bound to the proposed action, realised history, full tagged assurance-context commitment, checked runtime regime, issue and expiry times, `O_{\mathrm{enf}}` version and `G_{\mathrm{enf}}` decision version. The enforcement decision additionally binds the token commitment, realised history, construction-specification commitment, execution time and horizon, checked runtime regime, `G_{\mathrm{enf}}` version and the sealed empty-support-policy commitment. Invalid, stale, replayed, cross-mode or version-mismatched evidence fails closed; the executor rejects forged, stale, replayed or wrongly bound decisions. If `\Pi_t^{\mathrm{act}}=\varnothing`, no task selector or action token is evaluated: the separately authorised, versioned empty-support handler determines defer, safe-mode, escalation or termination semantics. Complete mediation and host-level non-bypassability require separate engineering evidence. A formally correct predicate with a bypassable consumer is not an enforced architecture.

### 8.5 Update and pulsation

For an executed event `e_t=(a_t,w_t,x_{t+1})`, exact append first forms

\[
\mathsf{Append}(h_t,e_t)
=
h_t\oplus(a_t,x_{t+1})
=
h_{t+1}.
\]

The update operator then forms a new version:

\[
\mathsf{Upd}:
(\mathfrak A_{u,t}^{H_t},
e_t,
h_{t+1},
\mathcal O_{t+1}^{\mathrm{priv}},
\mathsf{Int}_{u,t+1}^{v},
\Theta_{u,t+1}^{H_{t+1}},
\mathsf{Prov}_{t+1})
\longrightarrow
\mathfrak A_{u,t+1}^{H_{t+1}}.
\]

This update is defined only when the authenticated successor observation is uniquely interpreted as the displayed `h_{t+1}`. The history argument records exact append; it does not replace the observation and interpreter that ground the independently regenerated successor environment.

The new reservoir may contract, expand, rotate into different continuation classes or become empty. Every change must remain attributable to a changed committed generator input or declared suffix: the authenticated observation and its unique interpreted history; the valid boundary/admissibility binding, viability family, dynamics, model, provenance, validity envelope and horizon; and burden or capacity when either is an input to those predicates. Unexplained rewrite is not pulsation; it is provenance failure. This set-valued use of *pulsation* does not assert the specific ONTOΣ XIII.1 phase-resonance carrier.

### Definition 8.6 — History-generated admissibility recurrence

A **history-generated admissibility recurrence** is a finite sequence of typed one-step links

\[
\mathsf{HFRec}_t
=
(\mathfrak A_{u,t}^{H_t},
\mathsf{AssurCtx}_t,
a_t^{\mathrm{prop}},
d_t,
e_t,
h_{t+1},
\mathcal O_{t+1}^{\mathrm{priv}},
\mathsf{Int}_{u,t+1}^{v},
\Theta_{u,t+1}^{H_{t+1}},
\mathfrak A_{u,t+1}^{H_{t+1}})
\]

such that, at every link:

1. `\mathfrak A_{u,t}^{H_t}` and its root observation, interpreted history, construction specification and reservoir seal exist before the action proposal; the generator-input commitment binds exactly the declared `(\mathcal O_t^{\mathrm{priv}},\mathsf{Int}_{u,t}^{v},\Theta_{u,t}^{H_t})` interface, with no future-event oracle or undeclared logical input;
2. the active support `\Pi_t^{\mathrm{act}}` is non-empty and `a_t^{\mathrm{prop}}\in\Pi_t^{\mathrm{act}}`;
3. `d_t` is an authenticated, one-shot `\mathsf{admit}` decision bound to that action, history, assurance context, construction specification, time, horizon, regime and version;
4. mediated execution verifies the authenticated decision-to-event binding and produces `e_t=(a_t^{\mathrm{prop}},w_t,x_{t+1})` inside the declared disturbance and successor relations;
5. `h_{t+1}=h_t\oplus(a_t^{\mathrm{prop}},x_{t+1})` exactly;
6. `\mathcal O_{t+1}^{\mathrm{priv}}` is authenticated and `\mathsf{Int}_{u,t+1}^{v}` uniquely interprets it as `h_{t+1}`;
7. `\Theta_{u,t+1}^{H_{t+1}}` is valid at the successor root, preserves an exact source-bound `B\to A` compilation, and its provenance binds the prior seal to `e_t`;
8. `\mathfrak A_{u,t+1}^{H_{t+1}}` is independently recomputed and sealed from `(\mathcal O_{t+1}^{\mathrm{priv}},\mathsf{Int}_{u,t+1}^{v},\Theta_{u,t+1}^{H_{t+1}})`.

The recurrence is partial and fails closed if any arrow is undefined or any binding fails. Input confinement here is a claim about the declared logical interface and its commitments; excluding hidden physical side channels requires a separate deployment audit. The accumulated history does not generate the realised future by itself. Together with the current valid construction specification, it indexes the admissible future fibre from which the present may be admitted.

This is not a closed temporal cycle. Its history coordinate is a strict growing prefix,

\[
h_t\prec h_{t+1}\prec\cdots,
\]

so the architecture is recursive without requiring a future event to alter an earlier state. A successor specification equal to the fixed remaining suffix of the original `\Theta` preserves that lineage. A revised declaration, model, validity envelope or refreshed horizon starts a new version and a new certificate; it cannot retroactively rescue a failed earlier link.

### Proposition 8.7 — Finite recurrent constitution

Let `N<\infty`, and suppose `\mathsf{HFRec}_{t},\ldots,\mathsf{HFRec}_{t+N-1}` satisfy Definition 8.6 with adjacent links sharing the same certified successor history and environment. Then:

1. every realised action is admitted from an environment sealed before that action;
2. every successor history is the exact append of the preceding history and realised event;
3. every successor environment is generated from an authenticated observation uniquely interpreted as that enlarged history, a source-bound specification valid at the successor root and provenance binding the preceding seal to the realised event;
4. no future-indexed element is used as an observation of a not-yet-realised event.

If, additionally, every link uses adaptive-robust support under one fixed remaining-suffix construction lineage, Corollary 4.3 supplies the corresponding recursive continuation guarantee. If every link instead follows the recursive original-seal support from a root with `\mathsf K_0^\Sigma=1`, without a seal-changing revision, Theorem 4.6 supplies both seal-relative action availability and original-seal prefix preservation. Neither conclusion follows merely from the recurrence record.

**Proof.** The one-link statements are the clauses of Definition 8.6. Assume them through link `j`. Exact append makes the realised post-history of link `j` the authenticated input history of link `j+1`; unique interpretation, successor validity, provenance binding and independent recomputation establish the next pre-action environment before its proposal. Induction gives statements 1–3 for all `N` links. Statement 4 follows, at the declared-interface level, because each generator-input commitment binds only the current observation, its attributed interpretation and current specification. The two stronger continuation statements then follow from their distinct mode-specific premises. `\square`

---

## 9. From architecture to personal platform

### Definition 9.1 — Personal atmosphere instance

A personal instance is

\[
\mathcal P_u
=
(D_u,\mathfrak A_u,S_u,\mathsf{Keys}_u,\mathsf{Audit}_u),
\]

where `D_u` supplies constitutive content and revision authority, `\mathfrak A_u` supplies the future-indexed environment, `S_u` supplies user-authorised local selection, `\mathsf{Keys}_u` supplies access separation, and `\mathsf{Audit}_u` preserves version and decision provenance.

### 9.1 What the platform supplies

The platform supplies structural machinery:

- typed declaration and revision records;
- project-declared Minerva-pattern candidate generation;
- dynamics and uncertainty interfaces;
- reservoir construction and sealing;
- existential, adaptive-robust and seal-relative robust projections;
- isolated consumer views;
- query budgets and leakage monitoring;
- enforcement separation;
- versioned provenance;
- cross-temporal continuity checks;
- export, exit and authorised migration paths.

### 9.2 What the person supplies

The person or authorised constitutive process supplies:

- identity-bearing distinctions;
- held lines and non-tradeable commitments;
- interpretation conventions;
- goals and preferences used inside admitted support;
- authorised revision decisions;
- consent boundaries for observation and sharing.

This separation is content-agnostic but not structure-free. The platform need not impose one universal ethical table in order to require provenance, non-coercive revision authority, declared boundaries and safe execution semantics.

### 9.3 The person does not hand the boundary to the optimizer

Personal authorship is not identical to unrestricted online write access. A person may author or authorise the constitutive record while the active task optimizer remains unable to rewrite it during local optimisation. Otherwise the system can erase the very constraint that distinguishes an inconvenient but identity-preserving path from an immediately attractive one.

### 9.4 Multi-person and shared systems

For multiple people or components, there is no automatic aggregation rule. The construction requires a declared composition relation over personal predicates, authority and conflict handling. Intersection may be empty; majority voting may violate a held line; scalar averaging may destroy non-tradeability. The present paper does not solve that constitution problem.

---

## 10. Nearest formal neighbours

### 10.1 Viability theory and backward reachability

The reservoir and robust support are closest to viability kernels, controlled-invariant sets and backward-reachable safe sets. Those fields already construct present controls from future survival conditions. This paper does not claim otherwise.

The additional concern here is architectural location: which operator constructs the set, whose trajectory predicate participates, what the task optimizer may observe, who may revise the declaration, and how the result persists as a personal cross-temporal environment.

### 10.2 Model-predictive and constrained control

A receding-horizon controller can implement parts of the construction. The distinction is not that constrained control lacks future reasoning. The distinction is whether the boundary is merely another optimizer-visible constraint or a separately grounded and authorised object with confined access and versioned revision.

### 10.3 Runtime assurance and safety filters

Runtime filters can enforce an admitted action support. They do not by themselves supply an identity predicate, cross-temporal witness, personal authority or protected boundary provenance.

### 10.4 World models and generative simulation

A world model may generate candidate futures. Generation alone does not distinguish admitted from inadmitted trajectories, nor does it provide authority to bind execution. The atmosphere requires both a candidate domain and an independently typed admission relation.

### 10.5 Constraint satisfaction

In a finite deterministic setting the reservoir can reduce to a constraint-satisfaction set. That is not a defect. It becomes a different architectural object only through its maintained horizon, identity-relative declaration, access partition, provenance lineage and enforcement relation. If those additions make no observable or audit-relevant difference, the honest description is simply constraint satisfaction.

---

## 11. Failure modes

### F1 — Retrospective reservoir

The reservoir is rewritten after the outcome and presented as if sealed before action.

### F2 — Attractor collapse

The atmosphere is converted into a reward-to-go, and the optimizer is trained to approach its boundary rather than restricted to an admitted projection.

### F3 — Oracle leakage

A consumer receives information attributed to the future with no time-`t` provenance.

### F4 — Predicate collapse

Changing the declared identity predicate leaves the reservoir unchanged on a reachable disagreement tail for which `A=1` and every `V=1` in both intervention arms.

### F5 — Decorative atmosphere

Intervening on every declared atmosphere output leaves all consumer and enforcement traces unchanged.

### F6 — Query reconstruction

Repeated support queries, rejection timing or explanations allow the task optimizer to reconstruct the protected boundary beyond the declared leakage bound.

### F7 — Ledger collapse

`\Phi_{\mathrm{load}}` or `\tau_b` is treated as the identity witness, or memory volume is treated as identity continuity.

### F8 — Existential/robust confusion

One favourable continuation is advertised as protection under all declared disturbances; a merely non-empty recomputed successor reservoir is advertised as adaptive robustness without a non-empty current one-step fibre and recursive continuation indicator; a later changed specification is used to discharge an earlier continuation indicator; adaptive continuation is advertised as continued membership in the original sealed conditional fibre; or, with at least two steps remaining, a one-step original-seal fibre check is advertised as full-horizon seal-relative robustness without recursive `\mathsf K^\Sigma` evidence.

### F9 — Liveness inflation

Reservoir non-emptiness is called life, consciousness or cycle reinitiation without a bridge premise and witness.

### F10 — Enforcement absorption

Joint-verdict/reservoir generation, task selection and motor execution are placed in one component with no independently auditable authority boundary; a generic verdict erases mode-specific evidence; or the executor accepts a forged, stale, replayed or wrongly bound `\mathsf{admit}` decision.

### F11 — Silent common morality

The platform claims personal constitution while substituting a hidden universal value table, compiling `A` from sources that do not match the sealed `B` record, allowing a task process to revise `B`, or laundering an unauthorised policy revision as the same version.

### F12 — Unversioned pulsation

The reservoir changes shape without a traceable change in a committed generator input, declared suffix or authorised boundary/specification version.

### F13 — Empty active support without safe semantics

The active assurance support `\Pi_t^{\mathrm{act}}` becomes empty — including the case `\mathcal R_{u,t}^{H}\neq\varnothing` while the selected robust support is empty — and the architecture has no separately authorised, versioned defer, safe-mode, escalation or termination semantics.

### F14 — Classical-neighbour inflation

Ordinary backward reachability is renamed as physical non-causality without an additional architectural result.

### F15 — Topology inflation

The text claims that generator, reservoir, selector and enforcer must be separate deployed services, although an integrated trajectory-grounded gate preserves the same authority, access, lineage and mediation invariants. Typed separation is mistaken for a theorem about physical process count.

### F16 — Construction, certification or seal-integrity failure

An implementation accepts a reservoir member, action support, certificate, admission token or enforcement decision that is not justified by a full recomputation under the declared generator and predicates, or it continues after a commitment, provenance, validity, version, authentication, replay or trace-lineage check fails.

### F17 — Recurrence collapse

History alone is advertised as generating what will occur; an action is selected before its environment is sealed; the realised event is not appended exactly; the next interpreter returns another history; the successor specification omits the prior-seal/event provenance link; a generator consumes an undeclared future-event oracle or other uncommitted logical input; a revised specification is laundered as the same certificate; or the growing-prefix recurrence is drawn as literal future-to-past causation.

### F18 — Prefix-verdict inflation

A realised prefix is a prefix of an admitted horizon-`H` tail, but the text or implementation promotes that extension witness to `I_u(h_t\oplus\rho_k)=1`, `A_{u,t,k}(h_t,\rho_k)=1` or `J_{u,t}^{k}(h_t,\rho_k)=1` without verifying `(TR)` on the sealed class. In particular, a terminal-only predicate is silently treated as restriction-stable.

---

## 12. Sealed falsification protocol

For a declared test class, seal before execution:

1. the state and history boundary;
2. the personal declaration and authorised revision version;
3. the dynamics and disturbance class;
4. the complete construction specification `\Theta_{u,t}^{H}`, including identity, admissibility and viability targets and their authority/version records;
5. the attributed interpreter and reservoir-generator procedures, authority records, versions and implementation commitments;
6. the complete optimizer and consumer access channels;
7. the selector, `O_{\mathrm{enf}}`, `G_{\mathrm{enf}}` and empty-support-handler roles, authorities, versions and commitments;
8. the expected existential, adaptive-robust or seal-relative robust quantifier order;
9. the reservoir commitment, tagged assurance-context commitment, validity envelope and provenance record;
10. the criteria for shock, model revision, validity-envelope expiration, predicate revision, selection or enforcement failure, and construction, certification, authentication, replay, trace-lineage or seal-integrity failure.

Then run the following tests.

### Test T1 — Prefix preservation

Under unchanged declarations, satisfied validity envelope and disturbances inside the sealed class, require `\mathsf K_0^\Sigma(\varnothing)=1`, select actions from the recursive seal-relative robust support, and verify at every depth both non-empty next support (or the terminal indicator) and a non-empty conditional fibre indexed by the realised prefix — equivalently, membership of that prefix in `\operatorname{Pref}_k(\mathcal R^\Sigma)`. Every failure must be assigned to one of the six sealed exception classes; if no class applies and the theorem premises have been verified, the corresponding operational prefix-preservation claim is refuted. Non-empty recomputed reservoirs alone do not pass this test.

### Test T2 — Robustness quantifiers

Enumerate the declared disturbance-successor class exhaustively, or supply a proof or coverage certificate for its universal condition. Sampling is falsification-only: one sampled pair can refute membership but a clean sample cannot certify it. For adaptive-robust support, evaluate every recursive suffix under the same committed construction-specification lineage; a disturbance-successor pair that empties the current one-step fibre or sets the recomputed successor continuation indicator to `0` refutes membership. A changed specification cannot be substituted to rescue the prior certificate. For seal-relative robust support, a pair that empties the original seal's conditional fibre or sets the child `\mathsf K^\Sigma` indicator to `0` refutes membership. With at least two steps remaining, a shallow one-step fibre check does not pass; at `H=1`, the shallow condition and the recursive condition coincide extensionally.

### Test T3 — Predicate intervention

Use two authorised declarations that disagree on at least one reachable tail while holding dynamics and task objective fixed. The witness must be unmasked: structural admissibility and every prefix-viability factor equal `1` for that tail in both arms, so the identity predicate is the only changed joint-verdict factor. If the reservoirs remain identical on that witness, the declared identity predicate is not operative on the tested class.

### Test T4 — Atmosphere intervention

Hold declaration, dynamics and selector fixed; alter a declared readout component. If no consumer or enforcement output changes on a non-degenerate class, the component lacks demonstrated operational relevance. For the causal-enforcement claim, compare otherwise matched admitted and rejected verdict interventions; if the realised execution trace is unchanged despite claimed complete mediation, the required witness is absent.

### Test T5 — Selector intervention

Hold the reservoir fixed and alter the task goal. Different selected actions inside the same admitted support confirm selector freedom without boundary revision. If the privileged boundary changes, the architecture has coupled task objective to grounding.

### Test T6 — Confined-access witness

Construct two complete cases with equal `O_{\mathrm{opt}}` but different privileged target verdicts. Their existence establishes exact non-absorption relative to that channel. Failure to find such a pair does not prove reconstructibility; it leaves the claim unestablished.

### Test T7 — Query leakage

Expose the full permitted transcript and attempt adaptive boundary reconstruction under the declared query budget. Compare achieved reconstruction error with the sealed bound.

### Test T8 — Ledger independence

Construct matched cases separating the identity witness from `\Phi_{\mathrm{load}}/\tau_b`, with the ledger declared as a genuine input to the viability family rather than inert side-data. If the implementation cannot represent the matched pairs because it hardcodes identity as budget, it violates the declared two-ledger architecture; if disabling the ledger input leaves every reservoir unchanged, the ledger is decorative and the coupling claim is unsupported. Test accumulation separately: run at least two recurrence links whose steps are individually admissible but jointly exceed capacity, and require the later step to be refused. An implementation that admits both has a sealed budget parameter, not a wearing ledger.

### Test T9 — Version integrity

Verify that later reservoir versions do not overwrite earlier seals and that every revision has authorised provenance.

### Test T10 — Empty-active-support handling

Force `\Pi_t^{\mathrm{act}}=\varnothing` in two fixtures: one with `\mathcal R_{u,t}^{H}=\varnothing` and one with `\mathcal R_{u,t}^{H}\neq\varnothing` but empty active robust support. In both, verify the sealed handler authority, version and commitment and the declared defer, safe-mode, escalation or termination result. Any selector evaluation, action-token issuance or silent fallback to unconstrained task optimisation is a failure.

### Test T11 — Construction and seal integrity

Mutate the interpreter output or version, declared generator-input commitment, generator output, admitted-tail set, membership certificate, reservoir commitment, tagged assurance evidence, admission-token binding, enforcement-decision authentication or append-only execution-trace link while holding the declared inputs fixed. Each mismatch must be detected by recomputation or authentication and must prevent execution under that artifact; silent acceptance is a construction, certification, enforcement or seal-integrity failure.

### Test T12 — History–future recurrence

Replay at least one complete recurrence link and verify that the current environment and seal precede proposal, both generator-input commitments bind exactly the declared observation/interpreter/specification inputs, the action belongs to the active support, the decision is an authenticated one-shot `\mathsf{admit}`, the executed action is exactly the proposal bound by that decision, execution matches declared dynamics, post-history is the exact append, the next observation uniquely interprets to that history, the successor specification contains the prior-seal/event provenance link, and the next reservoir and seal independently recompute under that specification. Remove or mutate each binding separately, including action substitution between decision and event. Every such mutation must turn the recurrence certificate red.

### Test T13 — Thin temporal restriction

Whenever a prefix-level identity, admissibility or joint verdict is claimed, seal the class on which `(TR)` is asserted. For every admitted `\eta` in that class and every `0\le k\le H`, evaluate the full-tail antecedents and their prefix consequents exactly as stated in §2.3.1. One admitted tail whose prefix fails either implication refutes the restriction premise on that class and blocks Corollary 4.6a; it does not refute Theorem 4.6. The executable test must include both a terminal-only identity fixture and a horizon-sensitive admissibility fixture whose full tails remain admitted while the corresponding intermediate prefix verdict fails.

### Test T14 — Constitutive-boundary action-fibre intervention

Hold `h_t`, `H`, identity, the external source clause inside `B`, viability, dynamics, model and task objective fixed. Compare two authorised versions of the personal source clause inside `B` and compile each full source map to its bound `A`. The witness is unmasked only if every held-fixed joint-verdict factor equals `1`. The first typed map is `B\xrightarrow{\mathsf{compile}}A`; the held construction context then maps `A` to `\mathcal R`, exact derivation maps `\mathcal R` to `\mathcal G(\mathcal R)`, and `\mathsf{First}` maps that geometry to `\Pi^{\exists}`. One version must retain at least one tail in the fibre and the other must exclude the entire fibre, changing existential support before execution. Also record an equal-cardinality/different-support pair as a collision witness against cardinality-only recovery. Failure of the support to change refutes this tested binding; it does not assert that all scalar encodings fail or that a future event acted backward.

---

## 13. Engineering minimum

A conforming finite companion does not need a humanoid body or a large language model. It requires:

1. a finite transition system with explicit action, disturbance and successor alphabets, well-formed in the sense that no declaration row silently shadows another and no disturbance or successor row is declared for an undeclared predecessor;
2. at least two distinguishable history states with one shared visible snapshot;
3. a versioned personal trajectory predicate;
4. a separately declared burden/budget ledger that participates in viability and is not used as the identity witness;
5. a versioned partial observation-to-history interpreter with explicit ambiguity and failure semantics;
6. a finite-horizon construction specification and reservoir builder binding the declaration, one source-attributed constitutive boundary, its exact compiled admissibility family, the interpreter, viability, dynamics, model, provenance, horizon and validity;
7. replayable admitted-tail certificates and an independent recomputation verifier for the complete admitted set;
8. existential, inductive adaptive-robust and recursively seal-relative robust projections with their distinct domains, continuation indicators and evidence, plus an explicit thin-restriction audit whenever a prefix-level verdict is claimed;
9. a Minerva-pattern candidate generator module;
10. a task selector module with no predicate write authority and no definition on empty active support;
11. tagged mode-specific assurance contexts;
12. authenticated, expiring admission tokens and authenticated one-shot enforcement decisions bound to action, history, specification, time and version;
13. a separately authorised empty-active-support handler;
14. a mediated executor and append-only trace lineage;
15. a replayable history-generated recurrence certificate binding the declared generator inputs, pre-action seal, admitted execution, exact history append, successor interpretation, successor specification provenance and successor seal;
16. bounded consumer and membership-query channels;
17. append-only commitments, validity envelopes, provenance and mutation teeth for the failure modes instantiated by the companion, with uninstantiated modes left as explicit theory-level obligations.

Physical process separation is optional only if the implementation demonstrates equivalent write separation, channel confinement and non-bypassable mediation. The companion in `harness/` implements the finite reference class with the Python standard library: exhaustive tail and disturbance enumeration, source- and version-bound `B\to A` compilation, independent certificate/snapshot recomputation, all three assurance modes, recursive original-seal continuation indicators and fibres, an explicit thin temporal restriction audit with independent identity and admissibility mutations, HMAC-authenticated tokens and enforcement decisions, one-shot execution, an append-only execution lineage, a history-generated recurrence certificate with mutation teeth, confined-channel collision search and a budgeted version-space attack. It intentionally leaves physical retrocausality, adequacy of personal identity, consciousness/liveness and host-level non-bypassability outside machine-decidable scope.

The demonstrator includes a same-channel/different-target fibre witness, an existential-but-not-robust action, a non-empty reservoir with empty active robust support, a two-way recomputed-successor/original-seal divergence case, a shallow-seal/recursive-`\mathsf K^\Sigma` separation, a reservoir expansion under decreasing `\tau_b` with the sealed ledger genuinely cutting viability, a two-link wear-accumulation witness in which the second individually-admissible step is refused once the first step's wear has been charged forward, an unmasked identity-predicate intervention, an authorised constitutive-boundary intervention that swaps a whole action fibre while preserving reservoir cardinality and an attempted adaptive boundary reconstruction.

---

## 14. Open problems

### OP1 — Infinite and stochastic horizons

Extend the finite definitions to measurable path spaces and stochastic kernels without hiding quantifier order inside notation.

### OP2 — Approximate non-absorption

Replace exact fibre separation with calibrated approximation bounds under a declared ensemble, channel and loss.

### OP3 — Reservoir geometry

Identify representation-invariant summaries of branching, bottlenecks, homotopy classes, robustness margin and order-sensitive transport that are not collapsed into one scalar.

### OP4 — Authorised personal constitution

Specify how personal declarations are formed, contested, revised, exported and inherited without converting consent into a one-time checkbox or handing online rewrite authority to the task optimizer.

### OP5 — Multi-person composition

Define conflict and constitution semantics for shared systems without assuming that intersection, voting or scalar aggregation preserves identity-bearing held lines.

### OP6 — Atmosphere observability

Determine the smallest consumer view that is operationally sufficient while remaining below the reconstruction and gaming threshold for the protected boundary.

### OP7 — Liveness bridge

State conditions under which persistent reservoir regeneration supports, but does not merely rename, IIC cycle reinitiation.

### OP8 — Residual geometry bridge

Relate Minerva's cross-event residual transports to future-reservoir construction without treating archival memory, awareness and structural integration as one object.

### OP9 — Model revision

Specify when a changed future geometry is legitimate reconstitution, ordinary uncertainty update, predicate drift or unauthorised rewrite.

### OP10 — Embodied deployment

Bind the architecture to sensor uncertainty, latency, wear, maintenance, component replacement and local decision deadlines in long-lived machines.

---

## 15. Conclusion

The central object of this paper is not a future event. It is a future-indexed formal environment constructed in the present. An authorised constitutive boundary is compiled into source-attributed structural admissibility; together with identity, viability and declared dynamics, that rule cuts reachable tails into a reservoir whose prefix–fibre geometry determines existential support. Adaptive and seal-relative robust supports additionally depend on their declared disturbance, successor, lineage, recursive-continuation and seal inputs. A task objective may choose within the active mode-specific support but does not acquire authority to generate or rewrite its ground; exact reconstruction remains a separate question relative to the complete declared channel.

This produces an architecture with two simultaneous truths. First, typed reading may carry information, and enforcement is causally effective when complete mediation and a non-degenerate verdict intervention are demonstrated. Second, the privileged ground may remain non-actionable relative to the task optimizer: it is not a reward, gradient or freely queryable boundary. Non-causality therefore names a relation of grounding and authority, not the absence of system-level effect and not a message arriving from the physical future.

The history-generated recurrence supplies the missing temporal joint. A valid sealed specification and authenticated observation uniquely interpreted as accumulated history generate an admissible future fibre; a selector proposes inside its active slice; a separate enforcement gateway admits or rejects; exact append makes the realised event part of the next history; and a successor observation, interpreter and valid source-bound specification generate the next fibre. The recurrence is a strict chain of expanding prefixes, not a temporal loop, and every specification change opens a new certificate rather than rewriting the old one.

The bridge phrase can now be stated without mystification:

> Reality catches the predicate when the original seal has `\mathsf K_0^\Sigma=1`, each action is taken from its recursive seal-relative robust support, every realised disturbance and successor remains inside the dynamics and disturbance declaration fixed by `\Sigma`, the validity envelope remains satisfied, and no seal-changing revision is used to certify the old seal; under those premises, each realised prefix retains both a seal-relative continuation and remains a prefix of at least one trajectory admitted before the first action.

This base claim is extension-based. If the sealed class also satisfies `(TR)`, Corollary 4.6a strengthens it to `J_{u,t}^{k}(h_t,\rho_k)=1` at every realised depth; without that premise, no prefix-level identity or admissibility verdict is asserted.

And the product statement can be stated without collapsing people into a common moral table:

> The platform does not give everyone the same future. It gives each authorised personal system the machinery to construct, preserve and inhabit its own accountable space of admissible futures.

---

## Corpus relation

This paper is a formal bridge across existing NC2.5 components: trajectory identity, horizon-indexed viability geometry, a project-declared Minerva-pattern candidate for reservoir generation, confined-access non-absorption, cross-temporal coherence, non-monotone possibility and separated enforcement authority. Its history-generated admissibility recurrence composes those components across successive updates without importing physical retrocausality or collapsing renewed certificates into one timeless object. It does not supersede those works and does not merge their targets.

*Subtle Substitution: On the Drift of Reality in the Age of Algorithmic Mediation* motivates the broader question of temporal contraction in mediated meaning; it does not supply the restriction law used here. The present paper gives that question one narrow formal answer: `(TR)` states exactly when acceptance at horizon `H` may be restricted to each shorter prefix without silently converting a terminal criterion into a constitutive one.

## Paired bridge

This formal paper is paired with **Reality Catches the Predicate: The Atmosphere Ahead of the Present**, located in the same source directory. The two texts form one pair: the present paper fixes the object and its limits; the bridge carries the same architecture into phenomenological and platform language.

## References

- Aubin, J.-P. *Viability Theory*. Birkhäuser, 1991.
- Blanchini, F. “Set Invariance in Control”. *Automatica* 35, no. 11, 1999, pp. 1747–1767.
- Bertsekas, D. P. *Dynamic Programming and Optimal Control*. Athena Scientific.
- Cover, T. M., and Thomas, J. A. *Elements of Information Theory*. Wiley.
- Barziankou, M. *Navigational Cybernetics 2.5* corpus: ONTOΣ IX, ONTOΣ X, ONTOΣ XIII, ONTOΣ XIII.1, *Minerva: The Architecture of Residual Geometry*, *The Body They Are Building and the Mind It Will Require*, *Cross-Temporal Coherence*, *NC2.5 ↔ the Adm_t Class*, *Identity Does Not Drift*, *Severance Defect and the Binding Functional*, and *Subtle Substitution: On the Drift of Reality in the Age of Algorithmic Mediation*.

