# Hostile Referee Report — Round 12

**Manuscript:** cosmology_monograph_full.tex (64 pp., commit `efb11fb`, audit 366/366)
**Scope of this round:** the Round-11 fixes themselves, the statistical conventions behind the quoted significances, and package-level consistency. The automated audit verifies that quoted numbers match artifacts; it does not verify that the *convention used to derive a quoted number* is the same convention used elsewhere in the same table, nor that claims of the form "all … chains satisfy …" enumerate the right set. That is where this round attacks.

**Verdict: MAJOR REVISION.** The Round-11 fixes introduced one statistically overstated significance column entry set, left the two newest chains outside the convergence claim that the new table rows implicitly rely on, and the manuscript's own declared σ-convention contradicts its own transcribed rows. One table row matches no committed chain — the exact failure class Round 11 was supposed to have eliminated.

---

## MAJOR findings

### M1 — The significance column silently mixes two σ-conventions, and the manuscript's declared convention contradicts its own rows

`tab:cosmological_constraints` last column quotes (Δχ²_MAP, Nσ). Compute both candidate conversions for every row:

| Row | Δχ² | quoted σ | 1-dof √Δχ² | 2-dof Gaussian-equivalent |
|---|---|---|---|---|
| Flat wCDM + PP (1 par) | −4.5 | 2.1 | 2.12 | 1.86 |
| ΛCDM+Ω_K (1 par) | −4.2 | 2.0 | 2.05 | 1.83 |
| CPL DESI+CMB+PP (2 par) | −10.7 | 2.8 | 3.27 | **2.82** |
| CPL DESI+CMB (2 par) | −12.5 | 3.1 | 3.54 | **3.10** |
| CPL Union3 (2 par) | −17.4 | 3.8 | 4.17 | **3.76** |
| CPL DES-Y5 (2 par) | −21.0 | 4.2 | 4.58 | **4.19** |
| **MCMC Pipeline Base (2 par, new)** | −13.3 | **3.6** | 3.65 | **3.22** |
| **MCMC Pipeline +TRGB (2 par, new)** | −12.9 | **3.6** | 3.59 | **3.16** |
| **MCMC Pipeline +SH0ES (2 par, new)** | −12.5 | **3.5** | 3.54 | **3.10** |
| Mirage Union3 (1 par) | −19.3 | 4.4 | 4.39 | 4.00 |
| Mirage DES-Dovekie (1 par) | −17.0 | 4.1 | 4.12 | 3.71 |

Three facts, mutually contradictory:

1. The 1-parameter rows (wCDM, Ω_K, Mirage) use the 1-dof √Δχ² conversion — correct as the two-sided Gaussian equivalent of a χ²₁ likelihood-ratio p-value.
2. The transcribed 2-parameter CPL rows use the 2-dof Gaussian-equivalent (p = e^{−Δχ²/2}) — presumably the published DESI DR2 convention.
3. The "Semantics of the goodness-of-fit and significance statements" paragraph (Part VII) **explicitly declares the 1-dof convention**: "a one-dimensional equivalent of the profile-likelihood interval". Under the manuscript's own declared rule, the transcribed CPL rows in the same column are wrong (−10.7 would be 3.3σ, not 2.8σ), and the three new Round-11 Pipeline rows (3.6σ/3.6σ/3.5σ) are "right" only by accident of being computed with the 1-dof rule that contradicts every neighboring CPL row.

Consequence: the paper's own strongest pipeline result (Base, −13.3) is presented as 3.6σ in a column where the like-for-like DESI comparison at −10.7 reads 2.8σ — an apparent +0.8σ strengthening of which ~0.4σ is pure convention mismatch. A referee who recomputes one row will conclude the column is not internally consistent, and the declared-semantics paragraph makes it worse, not better.

**Required fix:** adopt one stated rule — Gaussian-equivalent two-sided significance of the likelihood-ratio p-value with dof = number of added parameters — in the semantics paragraph and the table caption; correct the three new Pipeline rows to **3.2σ / 3.2σ / 3.1σ**; keep the Mirage 4.4σ/4.1σ (correct under the same per-dof rule); state that transcribed rows retain the published values.

### M2 — "All eight new MCMC chains … maximum 1.0022": the two chains the new table rows depend on are outside the claim, and one of them exceeds the quoted maximum

The Round-11 fixes added `chain_cpl_pp_cc_trgb.npy` and `chain_cpl_pp_cc_shoes.npy`; the +TRGB/+SH0ES rows of `tab:cosmological_constraints` are now derived from them. Yet the split-R̂ sentence in Part VII-B still enumerates "all eight new MCMC chains (ΛCDM, CPL, and Mirage on Union3 and DES-Dovekie)" — the two pipeline chains are new, are CPL, and are on none of the listed datasets. Computing the identical 8-segment Gelman–Rubin statistic on them (same code path as `rhat_new_chains.py`):

- `chain_cpl_pp_cc_trgb.npy`: max split-R̂ = **1.00371** (wa)
- `chain_cpl_pp_cc_shoes.npy`: max split-R̂ = 1.00237

So (a) the enumeration "all eight" is false — ten new chains exist; (b) extending the claim to all ten makes the quoted maximum 1.0022 wrong (it is 1.0037); (c) the audit's own threshold (`max_rhat <= 1.003`) would fail on the extended artifact. The convergence itself is fine (≤ 1.004 ≪ 1.01), but as written the sentence is false and the +TRGB row rests on a chain with no recorded diagnostic.

**Required fix:** extend `rhat_new_chains.py` to the ten chains; tex → "all ten new MCMC chains … maximum 1.0037"; audit threshold → 1.005; keep the walker-level Mirage statement.

### M3 — The Sound-Horizon-Free row matches no committed chain and no artifact, and the table caption misattributes two of the "bottom five rows"

Row 5 of the pipeline block (L704): Ωm 0.2929 ± 0.0304, H0 69.24 ± 1.82, w0 −0.900 ± 0.052, wa −0.042 ± 0.454, r_d = 146.99 ± 3.44. Audit:

- The only committed r_d-free chain is `chain_rdfree_lcdm_desi_cc.npy` — **ΛCDM** (H0 69.21 ± 1.44, r_d 146.77 ± 2.87; no w0/wa exist in it). The row quotes CPL (w0, wa) values that exist in no committed chain and no JSON artifact.
- Even the overlapping quantities disagree beyond rounding: H0 σ 1.82 vs 1.44; r_d 146.99 ± 3.44 vs 146.77 ± 2.87.
- The caption attributes the "bottom five rows" to "our Affine-Invariant Ensemble MCMC pipeline" — but row 4 (Pivoted CPL) is transcribed from Carloni et al. (2026) and row 5 matches nothing committed. This is precisely the Round-11 M5 failure class (row matching no chain), surviving one round later in the same table.
- Propagation: the unverifiable (69.24 ± 1.82) is also the input to the Sound-Horizon-Free row of `tab:tension_matrix` (L834), whose caption claims it is "computed … from our pipeline outputs".

**Required fix (either):** (a) run and commit `chain_rdfree_cpl_desi_cc.npy` (DESI DR2 + CMB + Pantheon+ + CC, r_d free, CPL), replace the row with chain-derived values and its Δχ², and update the tension-matrix row; or (b) relabel the row's provenance explicitly (original book-pipeline value; our ΛCDM r_d-free chain reproduces H0 and r_d within 0.2σ but with narrower intervals; the CPL w0/wa were never reproduced) and correct both captions ("bottom three rows" + separately attributed rows).

### M4 — The submission package contradicts the Round-11 manuscript

- `submission/referee_response_template.md` (Comment on dark energy): quotes the superseded **"+6.75 ± 0.02"** (now +6.74 ± 0.03) and still says "official Union3 and **DES-SN5YR** likelihoods" — the Round-10 relabeling (DES-Dovekie distance release) never reached the template.
- `README.md` verification-list entry: "**two seeds per configuration**" (now four for Mirage on Union3).
- `README.md` results table: "**+6.75 ± 0.02**" for the Union3 Mirage row.

The Round-8 systemic fix (package-consistency section of the audit) guards the package against *previously* superseded values; these three sites were re-superseded by Round 11 and are guarded by nothing. **Required fix:** update the three sites and add audit checks pinning the current values in the template and README.

---

## Minor findings

- **m1 — Undefined "our MCMC Run 2" (Part V narrative, L719):** no "Run 1"/"Run 2" is defined anywhere in the manuscript. Replace with the concrete pointer (the +SH0ES chain / `pipeline_rows_results.json`).
- **m2 — No provenance pointer for the three MCMC Pipeline rows:** the table caption gives no artifact for the rows most likely to be scrutinized (chains, `pipeline_rows_results.json`, `sn_map_dchi2.json`). Every other own-computed row class has one.
- **m3 — The fix machinery embeds the M1 error:** `audit_numbers.py` now *enforces* "−12.9 (3.6σ)" and "−12.5 (3.5σ)", and the Round-11 section of `VERIFICATION_REPORT.md` records the same values. If M1 is fixed without touching these, the audit will reject the correction. Both must be updated in the same pass.
- **m4 — Cover letter advertises the weakest convergence number:** "R̂ ≤ 1.014, ESS ≥ 85 811" (the old 4-seed DESI+CMB diagnostics; artifact-backed) is the first convergence claim a Nature editor reads, while the manuscript's current headline criterion is split-R̂ ≤ 1.0037 on all ten new chains. Not wrong — but quote the stronger current criterion alongside the old one.

---

## Verified clean this round (no action)

- ΔDIC = −11.26 (semantics paragraph) = model_comparison.json CPL 16.44 − ΛCDM 27.70 exactly.
- Prior-volume robustness "+2.71 → +2.60 (V = 13.5 → 15)" = savage_dickey_canonical.json (2.7059, 2.6005).
- Mirage CPL-recovery percentages: 12.4/15.29 = 81.1%, −19.33/−20.6 = 94.0%, −16.99/−17.06 = 99.6% — the quoted "81–99.6%" range is exact.
- Own-vs-published Dovekie agreement 0.06σ (w0), 0.18σ (wa): recomputed from the committed chain and the published posterior — exact.
- SH0ES residual offsets 4.3σ (Carloni binned) / 3.5σ (our unbinned run): single-parameter H0 offsets, √ convention appropriate, arithmetic exact (4.53/1.059; 4.04/1.164).
- SD-vs-nested Union3 agreement "0.6σ": (8.71 − 6.74)/√(3.03² + 0.46²) = 0.64 — exact.
- √(Ĥ/n_live) quotes: 0.4606 (Mirage-Union3), 0.358–2.554 (CPL) → "≈ 0.46" and "0.36–2.6" — exact.
- +TRGB/+SH0ES row values vs `pipeline_rows_results.json`: all roundings correct; Ωm propagation formula correct; Δχ² monotonicity (Base −13.3 → +TRGB −12.9 → +SH0ES −12.5) sensible.
- fig4: legend, caption, and committed chains mutually consistent; TRGB prior 68.81 ± 2.22 = `H0_LADDER["CCHP JWST TRGB"]` actually used.
- `convergence_diagnostics.json`: R̂ ≤ 1.014 (max 1.0139) and ESS ≥ 85 811 (min 85 811) — template/cover-letter claims backed.
- Abstract bullets 2–3 attribution (official vs own-chain), Executive-Summary GP caveat, absence of "68.64", "Q_{CMB}", "+6.75", "z_c = 0.42" in the tex — all confirmed.
- Package page/chain counts: 64 pages everywhere; 37 chains; ~92 MB.

## Recommended fix order

1. M1 (σ-convention: semantics paragraph + caption + three rows → 3.2/3.2/3.1, Mirage unchanged) — touches the headline number.
2. M2 (extend split-R̂ artifact to ten chains; tex maximum 1.0037; audit threshold).
3. M3 (Sound-Horizon-Free row: new committed CPL r_d-free chain preferred; else relabel + fix both captions and the tension-matrix provenance).
4. M4 (template + README staleness; add package audit pins).
5. m1–m4 in the same pass (m3 is mandatory with M1).
6. Recompile, page-count sync if needed, extend the audit (target ≥ 380 checks), ALL PASS, commit.
