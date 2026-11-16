# Cover Letter — Nature submission

**Manuscript title:** The Architecture of the Cosmos: Model-Independent Constraints on the Hubble Constant and Dark Energy from DESI DR2, Pantheon+, and JWST

**Author:** Md. Mushfiqur Rahim (ORCID: 0009-0003-1021-685X)

Dear Editors,

We submit for your consideration a 62-page research monograph that addresses the two defining anomalies of modern cosmology — the Hubble constant tension and the evidence for evolving dark energy — through a single, fully reproducible Bayesian pipeline built on the most precise late-time probes currently available.

**Why this manuscript matters now.** The DESI DR2 BAO measurements (arXiv:2503.14738) have made the case for dynamical dark energy the central question in cosmology. Our work provides, in one place: (i) an inverse-distance-ladder determination H₀ = 68.17 ± 0.28 km s⁻¹ Mpc⁻¹ from DESI DR2 + compressed Planck CMB within flat ΛCDM; (ii) a 2.8σ–4.2σ case for evolving dark energy (w₀ = −0.838 ± 0.055, wₐ = −0.62⁺⁰·²²₋₀.₁₉ with Pantheon+) with a phantom divide crossing at z_c = 0.35 ± 0.11 with Pantheon+ (0.50 ± 0.08 for DESI DR2 + CMB alone); (iii) a resolution of the "negative neutrino mass" anomaly (∑m_ν < 0.0642 eV in ΛCDM, relaxed to < 0.163 eV in w₀wₐCDM); and (iv) a galaxy-by-galaxy JWST–HST distance cross-check (Δμ = −0.02 ± 0.03 mag) demonstrating that the CCHP–SH0ES divergence stems from small-sample host selection, not Cepheid crowding.

**What sets this work apart.**

1. *Complete reproducibility.* Every number in the paper is reproduced by a self-contained Python pipeline (affine-invariant ensemble MCMC, slaved Ω_m parametrization, full Pantheon+ STAT+SYS covariance) that ships with the manuscript, including all posterior chains, convergence diagnostics (Gelman–Rubin R̂ ≤ 1.014, ESS ≥ 85 811), and machine-readable results. An independent re-verification pass confirmed all headline posteriors, the 5.43σ/6.27σ/6.04σ tension matrix, the Mirage dark-energy decomposition (1-parameter Mirage captures Δχ² = −12.4 of the −15.3 total), and the full DESI+CMB+Pantheon+ joint fit (w₀ = −0.831 ± 0.053 versus the official −0.838 ± 0.055).

2. *Model-comparison rigor beyond Δχ².* We complement frequentist preferences with AIC/BIC/DIC and Savage–Dickey nested Bayes factors across five dark-energy parametrizations (ΛCDM, wCDM, CPL, JBP, Log f_DE), quantifying the Kullback–Leibler Occam penalty that separates "the data prefer w(z) evolution" from "the evidence supports it" — resolving the apparent frequentist–Bayesian paradox through the Mirage degeneracy axis.

3. *Honest systematics treatment.* The manuscript quantifies the low-redshift photometric offset between legacy Landolt-system SNe in DES-Y5 and Pantheon+ (Δμ = −0.043 ± 0.014 mag), explains the 4.2σ-versus-2.8σ discrepancy between SN compilations, and includes an explicit limitations section.

**Fit to Nature.** The manuscript speaks directly to your readership's intense interest in the DESI DR2 dark-energy results and the JWST-era Hubble tension, and it delivers the methodological transparency (full pipeline, chains, and diagnostics released alongside publication) that standards for high-impact cosmological claims increasingly demand.

All data analysed are public (DESI DR2, Pantheon+, Union3, DES-Y5, Planck 2018, JWST/CCHP and SH0ES tables). The author declares no competing interests. The manuscript is not under consideration elsewhere.

Sincerely,
Md. Mushfiqur Rahim
