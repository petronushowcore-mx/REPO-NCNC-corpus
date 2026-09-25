# NC2.5 — Non-Causal Non-Causality

**Build the space of what is allowed, before choosing what to do. Not backward causation — forward responsibility.**

[![DOI](https://img.shields.io/badge/DOI-10.17605%2FOSF.IO%2FNC9WH-1f6feb)](https://doi.org/10.17605/OSF.IO/NC9WH)
[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-6e7781)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
[![Python 3, stdlib only](https://img.shields.io/badge/Python%203-stdlib--only-3776AB?logo=python&logoColor=white)](#verification-harness)
[![Checks](https://img.shields.io/badge/checks-145%2F145-2da44e)](#verification-harness)
[![NC2.5 anchor](https://img.shields.io/badge/NC2.5%20v2.1-10.17605%2FOSF.IO%2FNHTC5-0969da)](https://doi.org/10.17605/OSF.IO/NHTC5)

This repository contains the **Non-Causal Non-Causality** pair — the formal paper and its bridge essay — together with the pair map and the executable verification companion, as one citable unit of the NC2.5 (Navigational Cybernetics 2.5) corpus.

A long-lived system is normally organised in causal order: observe the present, choose an action, predict its consequences, then test whether the resulting future is acceptable. This pair studies the reverse architectural order without asserting reverse physical causation. An authorised constitutive boundary is compiled into executable structural admissibility; together with a declared identity predicate, viability and dynamics it cuts the reachable continuations into a reservoir; the reservoir's prefix–fibre geometry determines the set of actions admissible in the present. A task optimizer may rank that set, but it is not granted authority to generate or rewrite its ground. Whether a protected target is reconstructible is treated separately, as a channel-relative question.

> **Status (read first).** This is an **open architectural draft** with executable witnesses. Its theorems are conditional on stated premises which the companion enforces: prefix preservation is extension-based and is lifted to prefix-level joint verdicts only under an explicit thin temporal restriction premise; the three assurance modes (existential, adaptive-robust, recursively seal-relative) are typed separately and are not claimed to contain one another without an additional consistency premise; confined-access non-absorption is channel-relative and collision-based, not an absolute non-reconstructibility claim. The companion establishes claims only on its declared finite fixtures. It does **not** establish physical retrocausality, the adequacy of a declared predicate as real personal identity, consciousness, life or cycle reinitiation, nor host-level non-bypassability — these are reported by the instrument as not machine-decidable rather than left implicit.

**Author:** Maksim Barziankou (MxBv) — [LinkedIn](https://www.linkedin.com/in/maxbarzenkov)  
**Affiliation:** The Urgrund Laboratory  
**Website:** https://petronus.eu  
**License:** CC BY-NC-ND 4.0  
**Bundle DOI:** 10.17605/OSF.IO/NC9WH (version 1.1 — single deposit covering the formal paper + bridge essay + pair map + verification companion as one citable unit)  
**Version 1.0 DOI:** 10.17605/OSF.IO/CUW8X (prior version, deposited separately, retained as filed)  
**Axiomatic core anchor:** NC2.5 v2.1, DOI 10.17605/OSF.IO/NHTC5  
**Corpus:** one work in the 130+ work corpus of Navigational Cybernetics 2.5 (MxBv)  

## Contents

| Path | Role |
|---|---|
| `Non-Causal-Non-Causality.md` | The formal paper: typed setting, the reservoir and its three assurance modes, the thin temporal restriction premise, the confined-access non-absorption theorem, the history-generated admissibility recurrence, and the platform factorisation. |
| `Reality-Catches-the-Predicate.md` | The bridge essay: the same architecture in phenomenological and platform language. All its metaphors resolve to objects defined in the formal paper. |
| `00-PAIR-MAP.md` | Corpus dependency map, the load-bearing separations that may not be collapsed, and the required falsification surface. |
| `harness/` | The finite executable companion — standard library only. |
| `SHA256SUMS.txt`, `.asc`, `.ots` | Signed manifest and Bitcoin timestamp attesting the OSF deposit archive of this version. |
| `PETRONUS-Research-public-key.asc` | Public key for verifying the signatures. |
| `LICENSE` | CC BY-NC-ND 4.0. |

### Run it

Python 3, standard library only, no third-party dependencies. From `harness/`:

```
py -3 check_all.py --format text
```

**What a green run establishes.** A conforming run reports `successful: true` and
exits 0, covering the unit and mutation suites, the executable reference report and
the cross-artifact drift fence: each formal object is evaluated on finite fixtures,
and breaking the specific model fact a check names turns that check red.

**What it does not establish.** In the harness's own words: "The code establishes
claims only on its declared finite fixtures. It does not establish physical
retrocausality, the adequacy of a declared predicate as real personal identity,
consciousness" ([`harness/README.md`](harness/README.md), Scope boundary). The
enumeration makes the quantifiers visible; it does not make them true of anything
outside the fixtures.

---

## Verification harness

The companion is a finite reference instrument, standard library only, no third-party dependencies. It constructs and independently rechecks the complete admitted reservoir, keeps the three assurance modes separate, authenticates the path from evidence to execution, models confined access and bounded reconstruction, and emits a deterministic report.

From `harness/`:

```
py -3 check_all.py --format text
```

A conforming run reports `successful: true` and exit code 0, covering the unit and mutation suites, the executable reference report, the cross-artifact drift fence, the pinned artifacts, the package manifest and a standard-library-only import scan. The individual surfaces can also be run alone:

```
py -3 -m unittest discover -s tests
py -3 verify.py --format text
py -3 corpus_gate.py --format text
py -3 build_manifest.py --check
```

The reference report evaluates each formal object on finite fixtures and runs a mutation battery in which breaking the specific model fact a check names turns that check — and only that check — red. Five targets are reported as not machine-decidable rather than asserted: physical retrocausality beyond the declared dataflow, the adequacy of the declared predicate as real personal identity, consciousness/liveness, host-level non-bypassability, and interpreter-evaluator faithfulness.

## Provenance

The `SHA256SUMS.txt` manifest, its detached signature `SHA256SUMS.txt.asc`, and the Bitcoin timestamp `SHA256SUMS.txt.ots` attest the archived OSF deposit of this version (DOI 10.17605/OSF.IO/NC9WH). To verify:

```
gpg --import PETRONUS-Research-public-key.asc
gpg --verify SHA256SUMS.txt.asc SHA256SUMS.txt
```

A `Good signature from "PETRONUS Research <research@petronus.eu>"` line confirms authorship; the `.ots` stamp confirms the deposit date independently through the Bitcoin blockchain. The source code in this repository additionally self-verifies through the harness manifest (`harness/MANIFEST.sha256`) and the sealed reference report.

**Verifying the manifest.** `SHA256SUMS.txt` covers the OSF deposit archive `NCNC-v1.1.zip`, which is the citable artefact of this version, and its paths carry the archive's top folder `NCNC-v1.1/`. This repository is the working tree: three of the markdown files here carry a later typographic correction (a line break after the licence line), and the README is the repository's own rather than the archive's. Checked against this directory, with the `NCNC-v1.1/` prefix read as the repository root, the manifest therefore reports four differences (`00-PAIR-MAP.md`, `Non-Causal-Non-Causality.md`, `Reality-Catches-the-Predicate.md`, `README.md`) and one absent entry, `NCNC-v1.1.zip`, which is the deposit archive itself and is not committed here. No sentence of the works differs; verify the files against the OSF archive.
