# Hostile Referee Report — Round 11 (full audit of artifacts the automated audit does NOT cover)

Scope of this round: everything `audit_numbers.py` does not check. The audit verifies that quoted numbers appear in the tex and match artifacts; it does not verify (i) numbers quoted with no artifact at all, (ii) claims about how computations were configured, (iii) content inside figure PDFs, (iv) whether "own-pipeline" table rows are actually derivable from the committed chains. This round attacked exactly those four blind spots, by direct inspection of every JSON artifact, every committed chain, every figure-generating script, and text extraction of every figure PDF.

**Verdict: MAJOR REVISION.** Five major findings, four minor. None of them is caught by the 310-check audit; all five majors are the same classes of error (retracted values, unsupported numbers, tex–artifact contradictions) that Rounds 3–10 were believed to have purged — they survived because they live in figures, in configuration claims, and in a table row whose provenance was never artifact-backed.

---

## MAJOR findings

### M1 — Figure 5 resurrects the retracted z_c = 0.42 inside the figure and contradicts its own caption

`make_fig5_gp.py` line 64 hardcodes the panel-(b) annotation

```
r"$f_{\rm DE}^{\max}\!\approx\!%.2f,\ z_c\!\approx\!0.42$" % f_pk
```

The committed `figs/fig5_gp_wz_reconstruction.pdf` therefore displays **"f_DE^max ≈ 1.01, z_c ≈ 0.42"**. Three independent failures:

1. **z_c = 0.42 ± 0.09 was retracted in Round 3** as derived-nowhere and replaced by 0.50 ± 0.08 (DESI DR2 + CMB). The Round-3 fix and audit section 3/17 guard the *tex*, but nothing guarded the *figure*: the retracted value has been sitting inside a figure PDF for eight rounds.
2. **The annotation mislabels the quantity.** The script itself computes the f_DE-peak redshift (`z_pk = zt[np.argmax(fmed)]` → **0.160**, printed at generation time) and then ignores it, writing the hardcoded 0.42 and calling it "z_c". The f_DE-density peak redshift is not the phantom-crossing redshift; conflating them is a physics error, not a typo.
3. **Figure–caption contradiction**, the same class as Round-9's fig6 failure: the tex caption correctly states "f_DE^max ≈ 1.01 at z ≈ 0.16", while the figure it caption says "z_c ≈ 0.42".

Fix: use the computed `z_pk` in the annotation and label it as the f_DE peak ("f_DE peak ≈ 1.01 at z ≈ 0.16"), never as z_c; regenerate the figure; extend the audit to scan figure PDFs for retracted strings.

### M2 — An unsupported number in Part VII-B: the CPL nested lnB "+4.28 on Union3" exists in no artifact

The nested-sampling paragraph quotes: "our CPL Bayes factors on the supernova compilations are systematically weaker than the published full-Planck PolyChord values (+0.26 vs. −0.66 ± 0.44 on Pantheon+, **+4.28 vs. +3.03 ± 0.44 on Union3**, +1.88 vs. +4.88 on DES-Y5)".

Artifact check: `nested_lnB.json` contains runs for `cpl_desi_cmb` (+2.365), `cpl_sn` (+0.262), `cpl_desy5` (+1.876) — **there is no `cpl_union3` entry anywhere in the file**, and "+4.28" appears in no JSON, no log, no script output in the repository. Two of the three quoted CPL comparisons are artifact-backed; the third is not. This is precisely the fabricated-number class that Rounds 3–7 eliminated from the rest of the manuscript. Fix: either run `cpl_union3` with the sampler and commit the result, or delete the +4.28 clause.

### M3 — "Two seeds per configuration" / "two seeds each" is false by the repository's own evidence

The tex asserts, twice:

- "an ellipsoidal nested sampler (... **two seeds per configuration**)"
- "All eight new chains (ΛCDM, CPL, and Mirage on Union3 and DES-Dovekie; **two seeds each**; 96,000 retained samples per chain)"

The repository says otherwise:

- `nested_lnB.json`: `n_seeds = 1` for all three CPL configurations (`cpl_desi_cmb`, `cpl_sn`, `cpl_desy5`), with `err = 0.0` — no seed half-range exists for them, even though the table caption says quoted lnB uncertainties are "given by the seed half-range".
- `verification/chains/`: `chain_lcdm_{union3,desy5}_s101.npy` and `chain_cpl_{union3,desy5}_s1.npy` — **one seed each**; only the Mirage chains have two (`_s71/_s72`).

"Eight new chains" is correct; "two seeds each" is true only for the two Mirage pairs. Fix: state the seed structure correctly (two seeds for Mirage, one for ΛCDM/CPL) and either run the missing seeds or scope the claim.

### M4 — The R̂ ≤ 1.001 claim is contradicted by its own cited artifact and is unverifiable for half the chains

The tex: "All eight new chains ... satisfy R̂ ≤ 1.001 (`verification/sn_extra_results.json`)."

Artifact check: `sn_extra_results.json` records R̂ **only for the two Mirage chain sets** — `mirage_union3.Rhat = [1.0005, 1.0003, 1.0011]` and `mirage_desy5.Rhat = [1.0004, 1.0005, 1.0]`. Two problems:

1. **1.0011 > 1.001**: the artifact's own maximum violates the quoted bound at face value.
2. **No R̂ is recorded anywhere** for the four ΛCDM/CPL Union3/Dovekie chains, so the claim is unverifiable for them, and `tab:convergence` covers only the original DESI DR2 + CMB chains.

Fix: compute and commit R̂ for all eight new chains (a small script over the committed chains suffices, e.g. split-R̂), state the true maximum (1.0011 → "R̂ ≤ 1.002" or "max R̂ = 1.0011"), and point the tex at the artifact that actually contains all of them.

### M5 — The "MCMC Pipeline (Base)" row of Table 5 uses an undefined symbol and cannot be reproduced from any committed artifact

`tab:cosmological_constraints` row: "MCMC Pipeline (Base), DESI DR2 + **Q_CMB** + Pantheon+: Ω_m = 0.3115 ± 0.0049, H0 = 67.42 ± 0.52, w0 = −0.846 ± 0.050, wa = −0.565 ± 0.204, r_d = 147.16 ± 0.28, Δχ² = −10.4".

1. **Q_CMB is never defined** anywhere in the 63-page manuscript (the Part III CMB likelihood is the (θ*, ω_b, ω_bc) compression; no symbol Q_CMB is introduced).
2. **No committed chain produces this row.** The Pantheon+ CPL chain `chain_cpl_sn_s1/s2` gives (H0, w0, wa) = (67.65 ± 0.59, −0.831 ± 0.053, −0.661 ± 0.196) — visibly different from the row (wa differs by ~0.5σ; H0 by 0.23) — and no committed chain contains r_d at all. `run_sn_joint.py` records these values only as hardcoded `"targets"` (i.e., inputs to compare against), not outputs.
3. **Internal Δχ² inconsistency**: the row says Δχ²_MAP = −10.4 for our pipeline on DESI DR2 + CMB + Pantheon+, while the `tab:model_comparison_full` caption says "our CPL Pantheon+ MAP gives Δχ²_MAP = −13.3" — same dataset, same claimed pipeline, two different values 2.9 apart, with no stated reason.

Fix: either (i) re-derive the row from a committed chain (and define Q_CMB if a different CMB compression was genuinely used, committing that chain), or (ii) replace the row with the actual current-pipeline values from `sn_joint_results.json` (67.65 ± 0.59, −0.831 ± 0.053, −0.661 ± 0.196, Δχ²_MAP = −13.3) and reconcile the two tables.

---

## MODERATE / MINOR findings

### M6 — The manuscript's own Union3/Dovekie posteriors are never quoted, and the abstract misattributes published values to "yields"

The repository contains and commits `chain_cpl_union3_s1.npy` and `chain_cpl_desy5_s1.npy`, whose posteriors are

- DES-Dovekie: (w0, wa, H0) = (−0.798 ± 0.055, −0.774 ± 0.212, 67.45 ± 0.54)
- Union3: (w0, wa, H0) = (−0.657 ± 0.085, −1.134 ± 0.278, 65.99 ± 0.83)

These agree with the published Dovekie posterior to 0.09σ/0.26σ — an even stronger validation than the MAP comparison quoted in Part VII-B — yet they appear nowhere in the manuscript. Simultaneously, Executive-Summary bullet 3 says "Combining DESI DR2 BAO with Planck CMB and Type Ia supernovae **yields** w0 = −0.752 ± 0.057 ... for DES-Y5", and bullet 2 "shifts the inverse-distance-ladder H0 ... 66.74 ± 0.56 (with DES-Y5)" — both are the official DES-SN5YR (1829-SN, full-Planck BEAMS) transcriptions, not this work's Dovekie-based results. A referee will ask which value is "the" DES-Y5 result of this monograph. Fix: label the transcribed rows as such in the abstract, and quote the own-chain posteriors in Part VII-B next to the MAP validation.

### m1 — fig5 caption "w(0) = −0.98 ± 0.09" disagrees with its artifact

`gp_route_crossing.json` gives `w0_median = −0.9749` (→ −0.97) and records no dispersion; the ±0.09 is backed by nothing. Quote −0.97 with an artifact-backed uncertainty or drop the interval.

### m2 — fig2 is the only figure with no generator script in the repository

`figure_provenance.md` marks fig2 as "book-pipeline"; no script in the repo can regenerate or check it, and its two w0wa legend entries cannot be re-verified (text extraction is inconclusive about the minus signs because the figure's fonts drop glyphs). Commit a generator or visibly re-verify the legend signs.

### m3 — The ±0.02 nested uncertainty (Union3 Mirage) is a biased-low estimator

The quoted ±0.02 is the half-range of two seeds. The parameter-free nested-sampling error is ≈ sqrt(Ĥ/n_live); with Ĥ ~ O(lnB) ~ 7 and n_live = 128 this is ≈ 0.2 — ten times larger. "Seed-stable to 0.02 nats" is a fair statement; quoting ±0.02 as the uncertainty in the table is not. Quote both.

### m4 — Executive Summary overstates the GP crossing relative to the repository's own note

`gp_route_crossing.json` states the H(z)-route median crosses w = −1 near z ≈ 0.14 and is "consistent only at the level of the wide 68% band, not at the level of the median". The fig5 caption discloses this honestly; Executive-Summary bullet 4 ("independently confirm the phantom crossing") does not. Add the route caveat to the highlight.

---

## Verified clean in this round (no action)

- 81% Mirage recovery arithmetic: 12.4/15.29 = 81.1% ✓ (model_comparison.json CPL χ²_min 8.34 vs ΛCDM 23.63)
- 99.6% Dovekie recovery: 16.990/17.053 ✓; 94% Union3: 19.327/20.560 ✓
- Tension-significance arithmetic: 4.52σ, 5.53σ, 5.72σ all reproduce from the quoted H0 pairs ✓
- GP hyperparameters (σ_f = 305.09, ℓ_f = 3.885, −119.0 vs −904.6) ✓ vs `gp_hyperparameter_search.json`; z_t = 0.765 ± 0.083 ✓; GP q0 = −0.52 ± 0.13 ✓
- q0 = −0.365 ± 0.058 / j0 = −0.05 ± 0.37: derivation documented in `CORRECTIONS_FOR_MANUSCRIPT.md` (Eq. 22 exact, reproduces quoted to 0.7%) — provenance exists, though only in Markdown, not a machine-readable artifact
- All ‡ Mirage table rows vs `sn_extra_results.json` / `nested_lnB.json` ✓ (audit section 22)
- Dovekie posterior agreement 0.02σ/0.14σ ✓; sample arithmetic 1623+197 = 1820, 1635+194 = 1829 ✓
- No unresolved references; 63 pages compile cleanly

## Recommended fix order

M1 (figure regeneration + audit extension to figure PDFs) → M2 (run or delete +4.28) → M3/M4 (seed/R̂ truthing + small R̂ artifact) → M5 (Base-row re-derivation or replacement + Q_CMB definition) → M6/m1–m4 (wording and provenance labeling).
