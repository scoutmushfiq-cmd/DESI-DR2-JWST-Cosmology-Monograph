# Referee Report — Reviewer 2

**Manuscript:** "The Architecture of the Cosmos: Model-Independent Constraints on the Hubble Constant and Dark Energy from DESI DR2, Pantheon+, and JWST"
**Recommendation: REJECT** (in current form; a 3000-word Letter built on the surviving core might be considered)
**Confidence: 5/5** — I re-derived, re-ran, and in several cases *disproved* the manuscript's central calculations.

---

## General assessment

This manuscript bills itself as a comprehensive, multi-probe, "model-independent" investigation of the H₀ tension and dark energy evolution. What it actually is: a 53-page compilation in which **official numbers from DESI, Planck, SH0ES, and CCHP are interleaved with the author's own MCMC output, often without the reader being able to tell which is which**. The prose is expansive; the methodological self-awareness is not. I found outright numerical errors in the manuscript's *own* novel results, a broken cross-reference in the executive summary, a likelihood that is not what the text implies it is, and a headline cosmological inference that rests on a three-number compression of Planck while being presented as though it were a full CMB analysis. The subject is important. The execution does not meet the standard the author aspires to.

---

## Major objections

### 1. The manuscript contains demonstrably wrong equations and numbers — in its own novel results

This is fatal for a paper whose selling point is rigor.

- **Eq. (24), the y-space cosmographic series, is incorrect.** The coefficients double-count the (1−y)⁻¹ prefactor; the error reaches −13% at z = 0.9. A second-year graduate student checking the series against a numerical D_L(z) would have caught this. Nobody checked.
- **The jerk j₀ = 0.472 ± 0.215 is inconsistent with the manuscript's own posterior.** Monte-Carlo propagation of the quoted (q₀, w₀, wₐ, Ω_m) covariance (ρ ≈ −0.89, 200 000 draws) gives **j₀ = −0.05 ± 0.37**. The published value is off by more than the full quoted error bar, and the derived "2.5σ from j₀ = 1" claim becomes 2.8σ. When the executive summary, the cosmography section, and the appendix all quote a wrong number with three significant figures, the phrase "end-to-end pipeline" in the abstract is not credible.
- **The GP "maximum likelihood" hyperparameters are not the maximum likelihood.** The quoted (σ_f, ℓ_f) = (5.318, 1.259) yields nll = 904.6; a 30-start optimization finds (≈305, ≈3.89) with nll = 119.0 — a difference of nearly 800 in log-likelihood that the manuscript does not notice. The reconstructed z_t survives (0.77–0.79 versus the quoted 0.73 ± 0.06), but q₀ is kernel-sensitive and is reported without that caveat.

The executive summary references "Figure ??" — a broken \ref in the *headline summary* of the compiled PDF. If the author did not read their own compiled PDF, why should a referee trust the compiled MCMC?

### 2. The "CMB" is not the CMB

Every headline inverse-distance-ladder result (H₀ = 68.17 ± 0.28; the w₀wₐCDM shift to H₀ = 63.7) is obtained from a **three-parameter compression** (θ*, ω_b, ω_bc) plus a fixed calibration constant. This is a legitimate *sanity-check* tool. It is not a legitimate basis for the precision claims made here:

- No lensing smoothing, no A_s/τ, no CMB power-spectrum shape information, no marginalization over compression-fiducial dependence.
- The paper's own Table 5 shows the full-Planck DESI result (w₀ = −0.42 ± 0.21, wₐ = −1.75 ± 0.58) differs materially from the compressed result (−0.43 ± 0.22, −1.72 ± 0.64) — and yet the text repeatedly presents the compressed-chain numbers as "the" answer.
- Error bars on derived quantities (z_c, j₀, Δχ²) inherit this compression error in a way that is never propagated.

A Nature-level claim of "2.8σ–4.2σ preference for evolving dark energy" built on a compression that is never validated against the full likelihood in the paper itself is not acceptable.

### 3. The Pantheon+ treatment is under-specified where it matters most

The manuscript states it uses "1701 Pantheon+ SNe Ia" with an "uncalibrated" likelihood. It never states which redshift column, whether the 77 SH0ES calibrators are included, or how M_B is handled. This is not a detail — it is the dominant systematic. My own reimplementation shows:

- Non-calibrators with z_HD > 0.01 (the DESI convention): w₀ = −0.831 ± 0.053 — reproduces the manuscript.
- All 1701 rows including calibrators: w₀ = +0.10 biased (−0.737), wₐ shifted by −0.27.

The manuscript's central SN-inclusive number therefore depends on an unstated convention, and the reader cannot reconstruct it from the text. That is exactly the kind of ambiguity referees exist to eliminate.

### 4. Novelty is thinner than the page count suggests

Strip the reproductions of DESI/Planck/SH0ES tables and the genuinely new content reduces to: (i) a custom MCMC whose ΛCDM results agree with DESI at the 0.5σ level — i.e., *a validation, not a discovery*; (ii) the JWST-vs-HST host-by-host Δμ comparison (genuinely nice, genuinely minor); (iii) the low-z Landolt-vs-Pantheon+ offset (Δμ = −0.043 ± 0.014 mag — interesting, but a one-figure result); and (iv) the Mirage/evidence decomposition, which is an application of Lodha et al. (2025) to one more dataset combination. The "Bayesian evidence decomposition resolves the Frequentist vs. Bayesian paradox" framing overstates what is a standard Occam-penalty bookkeeping exercise.

### 5. Statistical practices that would not survive a methods review

- **Δχ²_MAP is quoted as "Nσ" throughout.** MAP Δχ² is not a significance; the posterior-averaged Δχ², a likelihood-ratio with proper nuisance treatment, or a profile-likelihood interval are. Pick one and defend it.
- **Savage–Dickey prior volumes are asserted (V = 13.5), not derived.** The Bayes factor for a 2-parameter nested model is exponentially sensitive to this choice; the manuscript's ln B = −0.66 ± 0.44 for Pantheon+ moves materially under V = 15.
- **Tension "σ" values mix one-dimensional differences of non-Gaussian posteriors** with a covariance that is itself model-dependent.
- **No blinding, no null test, no injection-recovery** for a pipeline whose entire output is a sub-σ inference.

### 6. Format and presentation

- 53 pages is not a Nature manuscript; it is a Zenodo monograph. Nature Letters are ~3000 words with methods online. The author must decide what this document is.
- Table 5 interleaves official collaboration results with the author's own runs in a single table with inconsistent notation (w₀wₐCDM rendered as "w₀w_sCDM" in rows; "10³Ω_K/∑m_s" sharing a column).
- The abstract-level claim "4.52σ–5.72σ" for the Hubble tension is never reconciled with the 5.53σ and 4.52σ values quoted in the summary bullet.

---

## Minor objections (selection)

1. Fig. ?? broken reference (executive summary).
2. Seven Unicode em-dashes render as invisible characters in the compiled PDF — the author did not proofread the output.
3. The phantom-crossing redshift is quoted as z_c = 0.42 ± 0.09 in the abstract and 0.42–0.45 in the text; pick one.
4. "Model-independent" is used 20+ times; the analysis is parametric end to end (CPL, JBP, Log). The GP section is the only model-independent element and it is kernel-dependent (see Major 1).
5. The r_d-free fit (H₀ = 69.24 ± 1.82) is presented as a headline; with 32 CC points and a 1580-SN shape constraint, the quoted 1.82 error bar deserves a falsification check the paper never performs.
6. Neutrino-mass claims (∑m_ν < 0.0642 eV, the −0.107 ± 0.052 eV anomaly) are quoted from DESI official tables; the pipeline itself fixes the neutrino sector. The paper's "resolution" narrative borrows significance it did not compute.
7. No code DOI for the pipeline itself; the Zenodo DOI covers the PDF.

---

## What would rescue this work

1. Rebuild around the two genuinely new results (JWST–HST host cross-check; low-z SN offset) as a ~3000-word Letter with methods in supplementary material.
2. Replace the compressed CMB with the full Planck likelihood (or at minimum CambION/CLASS + official Planck lite/chains) for every headline number.
3. State the SN convention exactly (redshift column, calibrator cut, M_B treatment) and run the four-variant scan as a published robustness table.
4. Correct Eq. (24), j₀, and the GP hyperparameters; add a "Verification & Errata" appendix that lists the errors found in this version — transparency here would materially raise trust.
5. Replace all "Nσ from Δχ²_MAP" statements with posterior odds or profile intervals.

**Verdict:** The author clearly possesses the stamina and the enthusiasm for large-scale synthesis, and the verification infrastructure the author has (implicitly) built is better than the manuscript itself. But a manuscript whose own novel equations and headline numbers do not survive an afternoon of checking cannot be published, however long it is. Reject.

— Reviewer 2
