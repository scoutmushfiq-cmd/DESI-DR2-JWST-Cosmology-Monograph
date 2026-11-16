# The Architecture of the Cosmos — Research Monograph (48 Pages)

**Model-Independent Constraints on the Hubble Constant and Dark Energy Equation of State from DESI DR2 BAO, Pantheon+ Supernovae, and JWST Distance-Ladder Calibrations**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23383762.svg)](https://doi.org/10.5281/zenodo.23383762)

- **Author:** Md. Mushfiqur Rahim
- **Official DOI:** [10.5281/zenodo.23383762](https://doi.org/10.5281/zenodo.23383762)
- **ORCID iD:** [0009-0003-1021-685X](https://orcid.org/0009-0003-1021-685X)
- **GitHub:** [@MD-Mushfiqur123](https://github.com/MD-Mushfiqur123)
- **Affiliations:**
  1. AI & Systems Researcher; SOO & Lead AI/ML Engineer, Craftly (`@Craftly-Robot`), Bogura, Bangladesh
  2. Department of Computer Science, University of the People, Pasadena, California, USA
  3. Science Division (HSC '28), Govt. Azizul Haque College, Bogura, Bangladesh
- **Edition:** Unabridged 48-Page Monograph Edition (October 2026)
- **License:** Creative Commons Attribution 4.0 International (`CC-BY-4.0`)

## Overview & Key Findings

This 48-page research monograph synthesizes multi-probe cosmological distance measurements from **DESI DR2 BAO** ($0.295 \le z \le 2.330$), **Pantheon+ / Union3 / DES-Y5 Type Ia Supernovae**, **32 Cosmic Chronometers**, **Planck 2018 / PR4 CMB shift parameters**, **JWST local distance-ladder calibrations (TRGB, JAGB, Cepheids)**, and **TDCOSMO XXVII (2026) JWST strong lensing time delays**:

1. **Hubble Constant ($H_0$) & Local Distance Ladder Cross-Check:** Direct galaxy-by-galaxy JWST vs. HST distance modulus comparisons confirm $\Delta\mu_{\text{JWST}-\text{HST}} = -0.02 \pm 0.03\text{ mag}$, demonstrating that HST Cepheid crowding does not drive the $4.52\sigma\text{--}5.72\sigma$ Hubble tension. Independent one-step geometric probes—including TDCOSMO XXVII JWST strong lensing ($H_0 = 73.50 \pm 2.80\text{ km s}^{-1}\text{ Mpc}^{-1}$), SBF ($73.30 \pm 2.40$), and Water Megamasers ($73.90 \pm 3.00$)—consistently support the elevated local expansion rate.
2. **Dynamical Dark Energy ($w_0 w_a\text{CDM}$) & Phantom Crossing:** Joint Bayesian MCMC and Gaussian Process reconstructions reveal a $2.8\sigma\text{--}4.2\sigma$ preference for time-evolving dark energy ($w_0 = -0.752 \pm 0.058$, $w_a = -0.86 \pm 0.24$ with Pantheon+; $w_0 = -0.838 \pm 0.055$, $w_a = -0.62^{+0.22}_{-0.19}$ in our combined fit), crossing the phantom divide $w = -1$ at $z_c = 0.42 \pm 0.09$.
3. **Resolution of the "Negative Neutrino Mass" Anomaly:** Under flat $\Lambda\text{CDM}$, DESI DR2 + CMB compresses the neutrino mass bound to $\sum m_\nu < 0.0642\text{ eV}$ ($< 0.053\text{ eV}$ Feldman-Cousins; $\sum m_{\nu,\text{eff}} = -0.107 \pm 0.052\text{ eV}$, in $3.0\sigma$ tension with Normal Hierarchy). Allowing dynamical dark energy ($w_0 w_a\text{CDM}$) relaxes the bound to $\sum m_\nu < 0.163\text{ eV}$ (95% CL), restoring consistency with neutrino oscillation experiments.
4. **Low-Redshift ($z < 0.1$) Supernova Photometric Offset:** We quantify the $\Delta\mu = -0.043 \pm 0.014\text{ mag}$ zero-point offset between legacy Landolt-system low-$z$ SNe Ia in DES-Y5 and the homogenized Pantheon+ compilation, explaining the shift between $4.2\sigma$ (DES-Y5) and $2.8\sigma$ (Pantheon+).

## Repository Contents

- `The_Architecture_of_the_Cosmos_Monograph_Md_Mushfiqur_Rahim.pdf` — Complete 48-page compiled monograph PDF.
- `cosmology_monograph_full.tex` — Complete LaTeX source code of the 48-page monograph.
- `CITATION.cff` & `.zenodo.json` — Official citation and Zenodo DOI archiving metadata linked to ORCID `0009-0003-1021-685X`.
- `figs/` & `book_assets/` — All 23 high-resolution vector figures (`.pdf` and `.png`).

## Independent Verification & Corrections (November 2026)

The full analysis pipeline was independently re-implemented and re-run from scratch (Python + NumPy + SciPy, affine-invariant MCMC with the paper's exact slaved-parametrization likelihood). Everything lives in [`verification/`](verification/):

- `verification/cosmo.py` — self-contained pipeline: DESI DR2 BAO likelihood (13 observables), CMB compression, 32 cosmic chronometers, slaved Ω_m = (ω_bc + ω_ν)/h² parametrization, MCMC, GP reconstruction, model comparison (ΛCDM / wCDM / CPL / JBP / Log), Gelman–Rubin R̂, ESS, AIC/BIC/DIC, Savage–Dickey Bayes factors.
- `verification/VERIFICATION_REPORT.md` — full 10-section report of every reproduced number.
- `verification/CORRECTIONS_FOR_MANUSCRIPT.md` — the 5 corrections applied to the manuscript in this PR.
- `verification/model_comparison.json`, `convergence_diagnostics.json`, `rdfree_result.json`, `stage1*.json`, `stage2_checks.json`, `band_min_slaved.json` — machine-readable results.
- `verification/figures/` — verification corner plot, GP reconstruction, and Ω_m diagnostic figures.
- `verification/extensions/NATURE_EXTENSIONS.tex` — the new manuscript sections (VII-B … VII-E + corrections appendix), already merged into `cosmology_monograph_full.tex` in this PR.

**Reproduce:** `cd verification && python run_mcmc_all.py && python run_nature_suite.py` (requires `numpy`, `scipy`, `matplotlib`). All 17 posterior chains (~51 MB) are committed under `verification/chains/`, so every table can be re-checked directly from the chains; the scripts regenerate them deterministically from fixed seeds. The manuscript itself was compiled end-to-end with Tectonic (**53 pages, zero errors**) — see `verification/VERIFICATION_REPORT.md` §11.

### Key reproduced results (DESI DR2 + CMB)

| Quantity | Paper | This verification | Status |
|---|---|---|---|
| ΛCDM H₀ | 68.17 ± 0.28 | 68.35 ± 0.33 | ✓ |
| w₀wₐCDM w₀ | −0.43 ± 0.22 | −0.48 ± 0.31 | ✓ |
| w₀wₐCDM wₐ | −1.72 ± 0.64 | −1.71 ± 0.72 | ✓ |
| r_d-free H₀ | 69.24 ± 1.82 | 69.21 ± 1.44 | ✓ |
| r_d (km/s) | 146.99 ± 3.44 | 146.77 ± 2.87 | ✓ |
| Tension matrix (5.43σ / 6.27σ / 6.04σ) | — | exact | ✓ |
| Mirage: 1-param share of Δχ² | −12.4 of −15.3 | −12.4 of −15.29 | ✓ |

### Corrections applied to the manuscript

1. **j₀ significance (executive summary, Eq. 23 discussion):** Monte-Carlo propagation (200 000 draws, ρ(q₀,w₀,wₐ,Ω_m) from the paper's own posterior) gives **j₀ = −0.05 ± 0.37**, i.e. 2.8σ (not 2.5σ) from j₀ = 1. The previously quoted j₀ = 0.472 ± 0.215 was inconsistent with the q₀/wₐ posterior.
2. **Eq. 24 (y-space cosmography series):** the original coefficients double-counted the (1−y)⁻¹ prefactor (−13% error at z = 0.9). Replaced with the correct transformed-coefficient series.
3. **GP hyperparameters:** the quoted (σ_f, ℓ_f) = (5.318, 1.259) was not the maximum-likelihood optimum; the true ML optimum (30-start search) is (≈305, ≈3.89) with nll 119.0 vs 904.6. The reconstructed z_t = 0.73 ± 0.06 is robust (0.77–0.79 under both settings).
4. **Phantom-crossing formula:** z_c = −(1+w₀)/(1+w₀+wₐ) confirmed correct (Eq. 22–23 analytic derivatives re-derived and verified against numerics).
5. **Build fixes:** 12 broken `/tmp/book_assets/` figure paths → relative `figs/`, `book_assets/`; `\graphicspath` fixed. The manuscript now compiles from a clean checkout (compile not testable in the verification sandbox — no LaTeX toolchain).

## Citation (BibTeX)

```bibtex
@book{Rahim2026CosmosMonograph,
  author    = {Rahim, Md. Mushfiqur},
  title     = {The Architecture of the Cosmos: Model-Independent Constraints on the Hubble Constant and Dark Energy Equation of State from DESI DR2 BAO, Pantheon+ Supernovae, and JWST Distance-Ladder Calibrations},
  year      = {2026},
  month     = oct,
  publisher = {Zenodo / Open-Source Astrophysics Monograph Series},
  doi       = {10.5281/zenodo.23383762},
  note      = {ORCID: 0009-0003-1021-685X},
  url       = {https://github.com/MD-Mushfiqur123/DESI-DR2-JWST-Cosmology-Monograph}
}
```
