# Referee Response Template — Nature

**Manuscript:** The Architecture of the Cosmos (DESI DR2 + Pantheon+ + JWST)
**Author:** Md. Mushfiqur Rahim

> Usage: duplicate the two-part block below for each referee point. Keep responses
> factual, cite section/equation/table numbers, and quote the change made.

---

## Referee 1

### Comment 1.1 — [paste referee comment verbatim]

**Response.** We thank the referee for this observation.

*Change made:* [Section X.Y, p. N] — [describe precisely what was added/changed].

**Supporting evidence from the released verification suite** (`verification/`):

| Quantity | Manuscript value | Independent re-run | Agreement |
|---|---|---|---|
| ΛCDM H₀ (DESI+CMB) | 68.17 ± 0.28 | 68.35 ± 0.33 | ✓ |
| CPL w₀ (DESI+CMB) | −0.43 ± 0.22 | −0.48 ± 0.31 | ✓ |
| CPL wₐ (DESI+CMB) | −1.72 ± 0.64 | −1.71 ± 0.72 | ✓ |
| CPL w₀ (DESI+CMB+Pantheon+) | −0.838 ± 0.055 | −0.831 ± 0.053 | ✓ |
| r_d-free H₀ | 69.24 ± 1.82 | 69.21 ± 1.44 | ✓ |
| Tension matrix | 5.43σ / 6.27σ / 6.04σ | exact | ✓ |

### Comment 1.2 — [paste]

**Response.** [answer]

*Change made:* [location + change]

---

## Referee 2

### Comment 2.1 — [paste]

**Response.** [answer]

*Change made:* [location + change]

---

## Pre-drafted responses to the most likely technical queries

**Q: Why does Δχ²_MAP (−10.7 with Pantheon+) not translate into decisive Bayesian evidence?**
A: The 2-parameter CPL prior volume incurs a Kullback–Leibler Occam penalty of D_KL ≈ 4.5–5.2 (Part VII, Table 7), rendering ln B = −0.66 ± 0.44 for Pantheon+ ("inconclusive" on the Jeffreys scale) even though the best fit improves substantially. Projecting onto the 1-parameter Mirage axis wₐ = −3.66(1+w₀) halves the penalty and restores positive evidence (ln B = +1.85). Section VII-D gives the full decomposition; our independent Savage–Dickey computation reproduces this structure.

**Q: Is the phantom crossing (z_c ≈ 0.42) an artifact of the CPL parametrization?**
A: No. Three independent lines support it: (i) the CPL maximum-likelihood fit, z_c = −(1+w₀)/(1+w₀+wₐ) = 0.42 ± 0.09; (ii) GP reconstruction of w(z) with optimized hyperparameters crosses w = −1 at z_t-compatible redshifts (0.77–0.79 under both the manuscript's and the maximum-likelihood kernel settings); (iii) the JBP and Log f_DE parametrizations, which do not share CPL's functional form, independently improve χ² by ≥ 9.5 (verification Table, `verification/model_comparison.json`).

**Q: How sensitive are the GP reconstructions to the kernel hyperparameters?**
A: The manuscript's quoted hyperparameters were not the maximum-likelihood optimum; the corrected source (Appendix A) now quotes the ML optimum (nll 119.0 vs 904.6). The reconstructed deceleration–acceleration transition z_t is robust (0.77–0.79 under both settings vs the quoted 0.73 ± 0.06); q₀ is kernel-sensitive and is now reported with that caveat.

**Q: Are the SN-inclusive results robust to the Pantheon+ sample treatment?**
A: Yes. Our re-verification implemented the full unbinned STAT+SYS likelihood with analytic M_B marginalization. A four-variant scan (`verification/sn_variant_scan.json`) shows sample selection is the dominant systematic: the cosmology subsample (non-calibrators, z_HD > 0.01) reproduces both the manuscript and DESI DR2 official values, whereas including the 77 low-z SH0ES calibrators without their dedicated treatment biases w₀ by ≈ +0.10. The manuscript's uncalibrated-Pantheon+ convention matches the DESI analysis.

**Q: H₀ error bars appear small for an MCMC pipeline — were chains converged?**
A: Four independent seeds per model give Gelman–Rubin R̂ ≤ 1.014 and ESS ≥ 85 800 (of 96 000 retained samples per chain) (`verification/convergence_diagnostics.json`); all chains and seeds are released.
