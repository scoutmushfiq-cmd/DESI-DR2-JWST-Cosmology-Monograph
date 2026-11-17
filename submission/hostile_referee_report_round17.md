# Hostile Referee Report — Round 17

**Scope:** the submission package around the manuscript — README, cover letter, `.zenodo.json`, `figure_provenance.md`, and the VERIFICATION_REPORT's committed-artifacts section — checked against the actual repository state.

**Verdict: MINOR REVISION.** Three findings, all package-staleness; the manuscript itself is untouched by this round.

---

## Findings

### M1 — VERIFICATION_REPORT §12 is a stale Round-1 snapshot that contradicts the repo and names the deleted orphan

§12 ("Committed artifacts") still says "all 17 posterior chains (`chain_*.npy`, ~51 MB)" — the repository commits **39 chains (~97 MB)** — and its historical sandbox list names `rdfree_result.json` (singular), the orphan artifact `git rm`-oved in Round 14, plus sandbox-era PNG figures superseded by the released `figs/*.pdf` set. A reader reconciling §12 against the repo finds three contradictions. Fixed: a Round-17 update note states the current counts (39 chains, ~97 MB), names the generators and patch scripts released since, and records the orphan's Round-14 removal.

### m1 — the cover letter presents the published 68.17 ± 0.28 as an own determination

Cover-letter point (i): "an inverse-distance-ladder determination H0 = 68.17 ± 0.28 ... from DESI DR2 + compressed Planck CMB" — the same misattribution class fixed in the tex in Rounds 15–16 (the official DESI DR2 value; our chain gives 68.35 ± 0.33). Fixed: the bullet now states the reproduction explicitly, quotes our chain value with the 0.4σ agreement, and adds the work's own sound-horizon-free determination (68.19 ± 1.45, r_d = 146.36 ± 2.88) — which is both accurate and the stronger claim.

### m2 — cover-letter convergence claims were not artifact-checked

"R̂ ≤ 1.014, ESS ≥ 85 811, split-R̂ maximum 1.0037" were never enforced by the audit. Verified now: 85,811 is the minimum per-chain ESS in `convergence_diagnostics.json` (`ess_cpl_per_chain`), 1.014 the wa walker-level R̂, 1.0037 the twelve-chain split-R̂ maximum; audit checks added for all three plus the chain-count (39) and README/§12 consistency.

## Verified-clean in this pass

- `.zenodo.json`: 65-page description, correct title/creator/ORCID/license/keywords.
- `figure_provenance.md`: all 15 `figs/` assets covered (12 PDFs + associated files), including the Round-14 patch-script mentions.
- README reproduce paragraph: current (39 chains, ~97 MB, generator + patch scripts named).
- Referee-response template: current values only (Round-14 cleanup held).
