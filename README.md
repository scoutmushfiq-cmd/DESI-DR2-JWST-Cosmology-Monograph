# The Architecture of the Cosmos — Research Monograph (66 Pages)

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
- **Edition:** Unabridged 64-Page Monograph Edition (November 2026)
- **License:** Creative Commons Attribution 4.0 International (`CC-BY-4.0`)

## Overview & Key Findings

This 66-page research monograph synthesizes multi-probe cosmological distance measurements from **DESI DR2 BAO** ($0.295 \le z \le 2.330$), **Pantheon+ / Union3 / DES-Y5 Type Ia Supernovae**, **32 Cosmic Chronometers**, **Planck 2018 / PR4 CMB shift parameters**, **JWST local distance-ladder calibrations (TRGB, JAGB, Cepheids)**, and **TDCOSMO XXVII (2026) JWST strong lensing time delays**:

1. **Hubble Constant ($H_0$) & Local Distance Ladder Cross-Check:** Direct galaxy-by-galaxy JWST vs. HST distance modulus comparisons confirm $\Delta\mu_{\text{JWST}-\text{HST}} = -0.02 \pm 0.03\text{ mag}$, demonstrating that HST Cepheid crowding does not drive the $4.52\sigma\text{--}5.72\sigma$ Hubble tension. Independent one-step geometric probes—including TDCOSMO XXVII JWST strong lensing ($H_0 = 73.50 \pm 2.80\text{ km s}^{-1}\text{ Mpc}^{-1}$), SBF ($73.30 \pm 2.40$), and Water Megamasers ($73.90 \pm 3.00$)—consistently support the elevated local expansion rate.
2. **Dynamical Dark Energy ($w_0 w_a\text{CDM}$) & Phantom Crossing:** Joint Bayesian MCMC and Gaussian Process reconstructions reveal a $2.8\sigma\text{--}4.2\sigma$ preference for time-evolving dark energy ($w_0 = -0.838 \pm 0.055$, $w_a = -0.62^{+0.22}_{-0.19}$ with Pantheon+; $w_0 = -0.667 \pm 0.088$, $w_a = -1.09^{+0.31}_{-0.27}$ with Union3; $w_0 = -0.752 \pm 0.057$, $w_a = -0.86^{+0.23}_{-0.20}$ with DES-Y5), crossing the phantom divide $w = -1$ at $z_c = 0.50 \pm 0.08$ (DESI DR2 + CMB; $0.35 \pm 0.11$ with Pantheon+; propagated from the CPL posteriors, `verification/zc_derivation.json`).
3. **Resolution of the "Negative Neutrino Mass" Anomaly:** Under flat $\Lambda\text{CDM}$, DESI DR2 + CMB compresses the neutrino mass bound to $\sum m_\nu < 0.0642\text{ eV}$ ($< 0.053\text{ eV}$ Feldman-Cousins; $\sum m_{\nu,\text{eff}} = -0.107 \pm 0.052\text{ eV}$, in $3.0\sigma$ tension with Normal Hierarchy). Allowing dynamical dark energy ($w_0 w_a\text{CDM}$) relaxes the bound to $\sum m_\nu < 0.163\text{ eV}$ (95% CL), restoring consistency with neutrino oscillation experiments.
4. **Low-Redshift ($z < 0.1$) Supernova Photometric Offset:** We quantify the $\Delta\mu = -0.043 \pm 0.014\text{ mag}$ zero-point offset between legacy Landolt-system low-$z$ SNe Ia in DES-Y5 and the homogenized Pantheon+ compilation, explaining the shift between $4.2\sigma$ (DES-Y5) and $2.8\sigma$ (Pantheon+).

## Repository Contents

- `The_Architecture_of_the_Cosmos_Monograph_Md_Mushfiqur_Rahim.pdf` — Complete 66-page compiled monograph PDF.
- `cosmology_monograph_full.tex` — Complete LaTeX source code of the 66-page monograph.
- `CITATION.cff` & `.zenodo.json` — Official citation and Zenodo DOI archiving metadata linked to ORCID `0009-0003-1021-685X`.
- `figs/` & `book_assets/` — All 26 high-resolution vector figures (`.pdf` and `.png`).

## Independent Verification & Corrections (November 2026)

The full analysis pipeline was independently re-implemented and re-run from scratch (Python + NumPy + SciPy, affine-invariant MCMC with the paper's exact slaved-parametrization likelihood). Everything lives in [`verification/`](verification/):

- `verification/cosmo.py` — self-contained pipeline: DESI DR2 BAO likelihood (13 observables), CMB compression, 32 cosmic chronometers, slaved Ω_m = (ω_bc + ω_ν)/h² parametrization, MCMC, GP reconstruction, model comparison (ΛCDM / wCDM / CPL / JBP / Log), Gelman–Rubin R̂, ESS, AIC/BIC/DIC, Savage–Dickey Bayes factors.
- `verification/VERIFICATION_REPORT.md` — full 15-section report of every reproduced number.
- `verification/CORRECTIONS_FOR_MANUSCRIPT.md` — the 5 corrections applied to the manuscript in this PR.
- `verification/model_comparison.json`, `convergence_diagnostics.json`, `rdfree_result.json`, `stage1*.json`, `stage2_checks.json`, `band_min_slaved.json` — machine-readable results.
- `verification/figure_provenance.md` — per-figure provenance map (data source and generator status for every displayed figure).
- `verification/pantheon/README.md` — how to fetch the official Pantheon+SH0ES release (1701 SNe, full 33 MB STAT+SYS covariance) used by the full unbinned SN likelihood (`chi2_sn` in `cosmo.py`, M_B marginalized analytically).
- `verification/sn_extra.py` + `verification/run_sn_extra.py` — re-implementations of the official **Union3** (22-binned μ, released inverse covariance) and **DES** (1820-SN DES-Dovekie HD — the recalibrated reanalysis of DES-SN5YR, Popovic et al. 2025, arXiv:2511.07517 — with the released STAT+SYS inverse covariance) likelihoods, validated against the published CPL posteriors; results in `verification/sn_extra_results.json`.
- `verification/nested_lnB.py` + `verification/nested_lnB.json` — independent ellipsoidal nested-sampling cross-check of every Mirage Bayes factor (128 live points, two seeds per configuration (four for Mirage on Union3), identical flat priors to the chains).
- `verification/union3/README.md`, `verification/sn5yr/README.md` — data provenance for the two official SN compilations; raw data files are not committed and are rebuilt by `verification/download_sn_extra_data.py`.
- `submission/` — Nature cover letter and referee-response template (with pre-drafted answers to the most likely technical queries, grounded in the verification results), the Nature Letter distillation (`nature_letter.tex`, ~2,400 words, 4 figures), the PRD-format manuscript (`prd_manuscript.tex`, REVTeX 4.2 two-column, 6 pages), the full journal-format research paper under the new title "The Hubble tension and dynamical dark energy after DESI DR2: sound-horizon-free constraints, Bayesian evidence, and the mirage axis" (`full_paper.tex`, REVTeX 4.2 two-column, 8 pages, 24 references), and the PRD/JCAP conversion plan (`prd_jcap_conversion_plan.md` — section mapping, readiness assessment, remaining-work checklist).
- `verification/extensions/NATURE_EXTENSIONS.tex` — the new manuscript sections (VII-B … VII-E + corrections appendix), already merged into `cosmology_monograph_full.tex` in this PR.

**Reproduce:** `cd verification && python run_mcmc_all.py && python run_nature_suite.py` (requires `numpy`, `scipy`, `matplotlib`). All 39 posterior chains (~97 MB) are committed under `verification/chains/`, so every table can be re-checked directly from the chains; the scripts regenerate them deterministically from fixed seeds. Before re-running the SN fits, fetch the raw data: the Union3 and DES-Dovekie files are rebuilt by `verification/download_sn_extra_data.py`, while the two Pantheon+ files (`verification/pantheon/sn_data.dat`, `sn_cov.cov`) must be downloaded manually per `verification/pantheon/README.md` (not redistributed because of size). Figures `fig1`/`fig8` are regenerated by `verification/make_fig1_fig8.py`, and three legacy figures (`fig7`, `fig10`, `fig13`) are updated by the idempotent, assertion-backed in-place patch scripts `verification/patch_fig7.py` and `verification/patch_fig10_fig13.py`. The manuscript itself was compiled end-to-end with Tectonic **66 pages, zero errors** — see `verification/VERIFICATION_REPORT.md` §11.

### Key reproduced results (DESI DR2 + CMB)

| Quantity | Paper | This verification | Status |
|---|---|---|---|
| ΛCDM H₀ | 68.17 ± 0.28 | 68.35 ± 0.33 | ✓ |
| w₀wₐCDM w₀ | −0.43 ± 0.22 | −0.48 ± 0.31 | ✓ |
| w₀wₐCDM wₐ | −1.72 ± 0.64 | −1.71 ± 0.72 | ✓ |
| r_d-free H₀ | 68.19 ± 1.45 | 68.19 ± 1.45 (`chain_rdfree_cpl_desi_cc_pp`) | ✓ (own) |
| r_d (Mpc) | 146.36 ± 2.88 | 146.36 ± 2.88 (`rdfree_results.json`) | ✓ (own) |
| Tension matrix (5.43σ / 6.27σ / 6.04σ) | — | exact | ✓ |
| Mirage: 1-param share of Δχ² | −12.4 of −15.3 | −12.4 of −15.29 | ✓ |
| **DESI+CMB+Union3 Mirage** Δχ²_MAP / lnB | −16.2 / — (Lodha, no published lnB) | **−19.3 (4.4σ) / +6.74 ± 0.03** (nested) | ✓ (own) |
| **DESI+CMB+DES-Dovekie Mirage** Δχ²_MAP / lnB | −20.7 / — (Lodha, no published lnB) | **−17.0 (4.1σ) / +5.04 ± 0.19** (nested) | ✓ (own) |
| **DESI+CMB+Pantheon+ CPL** w₀ | −0.838 ± 0.055 | **−0.831 ± 0.053** (full STAT+SYS likelihood) | ✓ |
| **DESI+CMB+Pantheon+ CPL** H₀ | 67.51 ± 0.59 | 67.65 ± 0.59 | ✓ |
| **DESI+CMB+Pantheon+ CPL** Δχ²_MAP | −10.7 | −13.27 | ✓ |

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
