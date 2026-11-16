# Hostile Referee Report — Round 13

**Manuscript:** *The Architecture of the Cosmos* (`cosmology_monograph_full.tex`, 65 pp., commit `35734cd` + working tree)
**Referee stance:** adversarial; every number in the newly touched rows, every regenerated figure, and every figure that no previous round audited (fig2, fig3, fig7, fig10–13) was checked against the committed chains and artifacts.
**Verdict: MAJOR REVISION** — the Round-12 fix pass itself introduced one numerical error, and the legacy figure set (which Round 11/12 audits never opened) contains three confirmed figure–table contradictions of exactly the class this manuscript claims to have eliminated.

---

## MAJOR findings

### M1 — The Sound-Horizon-Free Ωm uncertainty introduced in Round 12 is miscomputed (wrong estimator, inconsistent with the rows above it)

`run_round12_fixes.py` propagates the Ωm error by quadrature **assuming H0–ω_bc independence**:

```
Om_s = sqrt((2*Om/H0*H0s)**2 + (wbc_s/h2)**2)
```

The committed chain says otherwise. Direct per-draw computation on `chain_rdfree_cpl_desi_cc_pp.npy` (96,000 samples):

| Quantity | tex / `rdfree_results.json` | chain-direct | discrepancy |
|---|---|---|---|
| Ωm (CPL, r_d free) | 0.3048 ± **0.0188** | 0.3050 ± **0.0132** | σ overestimated by **42%** |
| Ωm (ΛCDM, r_d free) | 0.3045 ± **0.0175** | 0.3044 ± **0.0077** | σ overestimated by **factor 2.3** |

The H0–ω_bc posterior anticorrelation (the dominant covariance term in the slaved parametrization) is simply dropped. Worse, this makes the new row methodologically inconsistent with the three MCMC Pipeline rows directly above it, whose Ωm errors are chain-direct and reproduce exactly (verified: +TRGB chain gives 0.3107 ± 0.0059, matching the tex to all digits). One table, two undisclosed estimators for the same derived parameter. The audit (`audit_numbers.py` Round-12 section) currently **enforces the wrong value** — the identical failure mode Round-12 finding m3 flagged, recreated one round later. The H0, w0, wa, r_d cells and the Δχ² = −4.684 → 1.7σ conversion are correct; only the Ωm error (and the artifact's `Om` fields) are wrong.

### M2 — fig7 panel (a) contains three independent defects and no generator script

Vector-coordinate extraction from `figs/fig7_ede_horndeski_degeneracy.pdf` (marker positions mapped through the axis-tick calibration):

1. **The Sound-Horizon-Free marker is plotted at (r_d, H0) = (146.99, 69.25)** — the superseded values. The table, abstract, fig1, and fig8 now say (146.36, 68.19). This is the *same* figure–table contradiction class as Round-11 M1 (fig5) and Round-12's fig1/fig8 finds, surviving in the one panel whose entire purpose is to display this point.
2. **The hyperbola label reads "H₀r_d = 10027 ± 65 km s⁻¹"** while the fig7 caption and `h0rd_check.json` (err_quadrature 44.8, err_montecarlo 44.9) say **±45**. The figure contradicts its own caption in the same panel.
3. **The legend quotes "Early Dark Energy (f_EDE = 0.092 ± 0.024)"** — this value appears nowhere in the manuscript (which says f_EDE ≈ 0.09–0.13 and quotes 0.126 ± 0.021 from P-ACT-LBSM) nor in any artifact. Unbacked number in a figure legend.

No generator script exists for fig7 (`book-pipeline` provenance), so none of these can be reproduced or fixed by rerunning anything.

### M3 — fig8's severity semantics contradict its own caption and the tex tension table

The fig8 caption says: *"Values exceeding 3σ (severe tension) are highlighted in bold."* The regenerated figure (faithful to the original) contains **no bolding at all**; it annotates cells with severity words on an undeclared threshold scheme (SEVERE ≥ 4σ, MOD. ≥ 2σ), under which **3.08σ** (Union3-w₀wₐ vs SH0ES 4-anchor) is labeled "MOD." — while the tex tension table's own rule (and bolding) treats > 3σ as severe. Two severity conventions for the same quantity, on facing pages, with the caption describing a third (bold) that exists in neither.

---

## Minor findings

- **m1 — fig13 vs table (H0pe):** the figure plots "75.40 ± 6.80"; the tex table row says "75.40⁺⁸·¹⁰₋₅.₅₀". The figure invented a symmetric error from an asymmetric one.
- **m2 — fig10 unbacked uncertainty:** "SH0ES Restricted to Same N = 11 Hosts (71.20 ± 1.85)". The 71.20 center is backed (`tab:jwst_hst_comparison` column H₀^HST,sub), but **±1.85 appears in no table, artifact, or cited source**.
- **m3 — fig11 forecast numbers have no provenance:** the caption asserts ">6.2σ" for DESI Y5 + Euclid + LSST and panel (b) plots 5.4σ (2028F) and 6.8σ (2030F). No forecast computation exists anywhere in `verification/` (no script, no artifact). These are illustrations, but the manuscript presents them with two-decimal precision and no derivation.
- **m4 — fig1 caption overgeneralizes:** "Thick and thin error bars denote 68% (1σ) and 95% (2σ) credible intervals" — only the two SH0ES rows carry 2σ bars; the other sixteen rows are 1σ-only (true of the original figure as well; the Round-12 regeneration is confirmed faithful).
- **m5 — fig2 panel (b) ambiguity + recurring missing generator:** the legend says residuals are against "Pantheon+ Best-Fit Flat ΛCDM (Ωm = 0.334, H0 = 73.04)" while the caption's Δμ(z) = μ_obs − μ_ΛCDM does not state which ΛCDM — a reader will assume the Planck-anchored fit of panel (a). fig2 also still has no generator script (deferred since Round 9; signs visually verified only).

---

## Verified clean (evidence-backed)

- rdfree CPL chain means/stds match the tex row for H0, w0, wa, r_d to all quoted digits; `sn_set=None` → Pantheon+, so the row label "DESI DR2 + CC + Pantheon+ (r_d free)" is correct.
- Caption's sampler config (48 walkers, 2,500 steps, 500 burn → 96,000) matches `run_round12_fixes.py` and both chain shapes.
- Pipeline-row Ωm errors are chain-direct and reproduce exactly (0.3114 ± 0.0061 / 0.3107 ± 0.0059 / 0.2992 ± 0.0052 vs 2-seed tex values).
- split-R̂: 12 chain entries + 2 cross-seed checks, max 1.00371 = quoted 1.0037; 8 × 12,000 = 96,000 segments consistent.
- fig3 contour labels (3.1σ/2.8σ/3.8σ/4.2σ) match the tex table; Mirage axis −3.66(1+w₀) correct.
- fig13: 73.49 ± 0.93, 73.50 ± 2.80, 73.30 ± 2.40, 73.90 ± 3.00, 70.80 ± 4.20 all backed by tex/registry.
- fig12: all seven 95% limits (<0.120/<0.072/<0.064/<0.053/<0.117/<0.139/<0.163) and the −0.107 ± 0.052 eV peak (3.0σ) backed.
- fig10 mean Δμ = −0.02 ± 0.03 mag matches the abstract.
- h₀r_d = 10027 ± 45 in the tex matches `h0rd_check.json` (the ±65 exists only inside the figure).
- Tension-matrix recomputation formula verified against three pre-existing rows before acceptance.
- Δχ² = −4.684 → 1.7σ at 2 dof verified with scipy (`norm.isf(chi2.sf(4.684, 2)/2) = 1.664`).

---

## Recommended fix order

1. **M1:** recompute Ωm (and its error) chain-direct for both rdfree configurations; update the tex row (0.3050 ± 0.0132), `rdfree_results.json`, `VERIFICATION_REPORT.md`, and the audit's Round-12 section in the same pass.
2. **M2:** write a released generator `make_fig7.py` (the fig1/fig8 pattern, with an unchanged-cell assertion); move the SHF marker to (146.36, 68.19); relabel the hyperbola ±45; replace or artifact-back the f_EDE legend value.
3. **M3:** align fig8's severity words with the tex table's 3σ rule (or reword both captions to the actual 2σ/4σ scheme — pick one convention and state it).
4. **m1–m5:** fig13 asymmetric bar, fig10 ±1.85 provenance, fig11 forecast caveat or derivation artifact, fig1 caption wording, fig2 caption wording (+ generator if time permits).
5. Extend `audit_numbers.py` accordingly (including PDF-text checks for fig7/fig8/fig10/fig11/fig13, mirroring the fig5 precedent).
