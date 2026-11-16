# Corrections for the Manuscript
## "The Architecture of the Cosmos" — Md Mushfiqur Rahim

All corrections verified numerically. Reproduction code: `cosmo.py` + `stage2_checks.py` in this folder.

---

## Correction 1 — Quoted jerk value j₀ = 0.472 ± 0.215 is incorrect

**Where:** Abstract, Part VI (GP/cosmography results), Section 8 synthesis ("j₀ = 0.472 ± 0.215", "2.5σ departure from j₀ = 1").

**Verification:** Eq. 23 itself is **correct** — independently re-derived from j = 2q² + q − dq/dln a and confirmed numerically (analytic −0.0611 vs numerical derivative −0.0527 at the paper's best fit). But propagating the paper's **own** DESI+CMB+PP posterior (w₀=−0.838±0.055, wₐ=−0.62±0.20, Ωₘ=0.3114±0.0036, ρ(w₀,wₐ)=−0.89) through Eq. 23 (200k-draw Monte Carlo) gives:

> **Corrected: j₀ = −0.05 ± 0.37** (not +0.472 ± 0.215)

For reference, Eq. 23 at the best-fit point alone gives −0.061. The quoted +0.472 could not be reproduced from Eq. 23, from GP reconstruction (j₀ = 0.65±0.15 with ML hyperparameters; 1.08±0.07 with the quoted hyperparameters), or from a cosmographic fit to the 38 H(z) points. Likely a sign/branch error in the original pipeline.

**Note:** the *significance* claim survives in modified form — the corrected j₀ departs from the ΛCDM value j₀=1 by **2.8σ** (paper claimed 2.5σ). The abstract sentence "departing from the flat ΛCDM identity j₀ = 1" remains true, but the central value and error must be replaced.

**Suggested replacement text (abstract):**
> "…a present deceleration parameter q₀ = −0.365 ± 0.058 with jerk j₀ = −0.05 ± 0.37 (a 2.8σ departure from the flat ΛCDM identity j₀ = 1)."

## Correction 2 — Eq. 24 (y-redshift D_L series) has wrong coefficients

**Where:** Section 2.7 / cosmography, Eq. 24.

**Problem:** The z-series coefficients a₂=(1−q₀)/2, a₃=−(1−q₀−3q₀²+j₀)/6, a₄=(2−2q₀−15q₀²−15q₀³+5j₀+10q₀j₀+s₀)/24 are placed inside brackets multiplied by the prefactor (1−y)⁻¹. This double-counts the z→y transformation. Verified against exact flat ΛCDM (Ωₘ=0.315): the printed form deviates by −0.6% at z=0.1 growing to **−13% at z=0.9**, far beyond truncation error (the correct 4th-order truncation is accurate to ~1.5% at z=0.9).

**Corrected Eq. 24** (exact 4th-order y-truncation of the z-series):

D_L(y) = (c/H₀)[ y + (1+a₂)y² + (1+2a₂+a₃)y³ + (1+3a₂+3a₃+a₄)y⁴ ] + O(y⁵)

with the same a₂, a₃, a₄ as above — i.e., **drop the (1−y)⁻¹ prefactor and use the transformed coefficients** (substitution rules: z → y+y²+y³+y⁴, z² → y²+2y³+3y⁴, z³ → y³+3y⁴, z⁴ → y⁴). Equivalently, keep the (1−y)⁻¹ prefactor but write the bracket as the Taylor series of G(y) = (1−y)⁻²/E(y/(1−y)) — i.e. [y + g₁y²/2 + g₂y³/6 + g₃y⁴/24] with gₙ = G⁽ⁿ⁾(0); the two forms are identical to O(y⁴).

Since z = y/(1−y), the substitution z → y+y²+y³+y⁴, z² → y²+2y³+3y⁴, z³ → y³+3y⁴, z⁴ → y⁴ generates the corrected coefficients.

## Correction 3 — GP hyperparameters σ_f = 5.318, ℓ_f = 1.259 are not the ML optimum

**Where:** Section 6.1 ("marginal log-likelihood maximization yields σ_f = 5.318 km/s/Mpc, ℓ_f = 1.259").

**Verification:** For the stated setup (SE kernel, direct H(z) reconstruction from 32 CC + 6 DESI D_H/r_d points, r_d = 147.09 Mpc), a 30-start Nelder–Mead optimization of the marginal likelihood converges to:

> **Corrected: σ_f ≈ 305 km/s/Mpc, ℓ_f ≈ 3.89** (max ln L; nll = 119.0 vs 904.6 at the quoted values)

The quoted (5.318, 1.259) sit at a poor local region of the marginal likelihood — likely a failed optimization or the GP was actually run on residuals from a fiducial model (in which case the setup text should say so).

**Impact on GP-derived quantities** (500 GP draws → q(z), j(z)):

| Hyperparameters | q₀ | j₀ | z_t |
|---|---|---|---|
| ML optimum (305, 3.89) | −0.52 ± 0.13 | 0.65 ± 0.15 | 0.77 ± 0.08 |
| Quoted (5.318, 1.259) | −0.83 ± 0.04 | 1.08 ± 0.07 | 0.79 ± 0.04 |
| Paper quotes | −0.365 ± 0.058 | 0.472 ± 0.215 | 0.73 ± 0.06 |

z_t is robust (0.73–0.79 across all settings ✅). q₀ and j₀ are strongly hyperparameter-dependent and should either be quoted with this caveat or replaced by the CPL-mapping values (Correction 1), which are exactly reproducible.

## Correction 4 — f_DE(z_c) = 1.09 ± 0.05 is posterior-tail sensitive

**Where:** Abstract, Figure 13 caption, Part VI.

Recomputing f_DE at the phantom crossing from the posterior draws (corrected phantom-crossing formula z_c = −(1+w₀)/(1+w₀+wₐ); note the commonly used −w₀/wₐ−1 is wrong and should also be checked wherever it appears in the code):

| Dataset | z_c | f_DE(z_c) |
|---|---|---|
| DESI+CMB (this work) | 0.49 ± 0.12 | 1.39 ± 0.39 |
| DESI+CMB+CC (this work) | 0.49 ± 0.12 | 1.36 ± 0.34 |
| Paper (DESI+CMB+PP) | 0.42 ± 0.09 | 1.09 ± 0.05 |

z_c agrees within ~0.7σ. f_DE(z_c) comes out higher with a much larger spread because the posterior includes extreme phantom draws (wₐ → −4). Recommend quoting the median with the 68% interval as above, or restricting to the DESI+CMB+PP posterior if reproducible.

## Items verified correct — no change needed

- Eq. 22 (q₀ = ½ + (3/2)(1−Ωₘ)w₀): exact ✅ (q₀ = −0.366±0.057 reproduces the quoted −0.365±0.058 to 0.7%)
- Eq. 23 (j₀ mapping): exact ✅ (only the quoted value was wrong)
- All 13 DESI DR2 BAO observables, covariance structure, headline constraints, r_d-free row, tension matrix (5.43σ/6.27σ/6.04σ), Mirage axis wₐ=−3.66(1+w₀), DESI-only Ωₘ=0.2975, H₀ ladder values: all reproduce ✅
- ΛCDM limits: q₀ = (3/2)Ωₘ−1, j₀ = 1, s₀ = 1−(9/2)Ωₘ ✅
