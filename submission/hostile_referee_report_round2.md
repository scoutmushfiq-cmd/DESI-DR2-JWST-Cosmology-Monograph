# Referee Report — Reviewer 2, Round 2

**Manuscript:** "The Architecture of the Cosmos" (revised, 56 pp)
**Recommendation: REJECT** (again; see "What changed" and "What still kills it")
**Confidence: 5/5** — I re-checked every Round-1 fix against the released pipeline, and then kept digging.

---

## What the authors fixed (credit where due)

Round 1's six major objections were addressed with unusual seriousness: the missing JWST–HST figure now exists and every `\ref` resolves; the tension-range baselines are labeled; the Pantheon+ convention is stated and defended by a four-variant robustness table; the compressed CMB is validated in-paper against the full-Planck DESI posteriors (< 0.1σ per parameter — this is now the strongest part of the manuscript); the statistics semantics are separated; "model-independent" is finally used with discipline. The author also survived my j₀, Eq. (24), and GP-hyperparameter findings with a candid errata appendix. This is better scholarship than most submissions I see.

It is still not publishable. Here is why.

---

## Major objections, Round 2

### 1. The abstract contradicts the paper's own corrected GP analysis — the headline z_t is stale

The errata appendix and the corrected GP section (Part VI) now honestly state that under the maximum-likelihood hyperparameters the acceleration onset is **z_t = 0.77–0.79**. Yet the **abstract**, the **conclusions**, the **milestone figure caption**, and the **GP figure caption** all still quote **z_t = 0.73 ± 0.06** — a number the paper itself has demoted. The reader meets the stale value first and the correction last, in an appendix. A correction that does not propagate to the abstract is not a correction; it is a contradiction. Fix every instance or delete the claim.

### 2. The Bayesian-evidence table's key column cannot be reproduced from the paper's own equation

Equation (evidence decomposition, Part VII) defines

  ln B = Δ⟨ln L⟩_P − ΔD_KL,

with each average taken under the respective model's own posterior. I evaluated exactly this quantity from the paper's own released chains (DESI DR2 + CMB; four seeds per model, 20 000-sample batched evaluation):

  ⟨χ²⟩_ΛCDM = 25.61, ⟨χ²⟩_CPL = 52.70 → **Δ⟨ln L⟩_P = −13.5**,

i.e. the posterior-averaged log-likelihood *decreases* under CPL. The manuscript's evidence table instead prints a **positive** Δ⟨ln L⟩ (implied ≈ +6.3, given the quoted D_KL ≈ 4.5–5.2 and ln B = +1.78). Both cannot be true under the equation as written. Either the table's estimator is not the equation's estimator (in which case the equation and the glossary entry are wrong), or the column is wrong (in which case the Bayes factors — the paper's central "frequentist vs. Bayesian paradox" narrative — are unsupported). The Savage–Dickey route (ln B = +2.6 to +2.7, robust to the prior volume at the 0.11 level) is the one piece of this section I could reproduce; the decomposition table I could not. This must be resolved before any journal sees the manuscript.

### 3. The printed code is not the code that produced the numbers

The 128-line Listing (`lst:python_pipeline`) uses Gauss–Legendre quadrature (`leggauss(24)`, `leggauss(48)`) and a standalone implementation. The actual pipeline that produced every table in this manuscript and its verification suite (`verification/cosmo.py`) uses a hybrid trapezoidal grid, a slaved Ω_m parametrization, and a completely different structure; the string `leggauss` appears **zero** times in it. The manuscript therefore prints a decorative code listing that has never generated a single quoted number. For a paper whose Round-1 defense was "full reproducibility," shipping showcase code that matches nothing is worse than shipping none.

### 4. The repository metadata describes a different paper

- README title, edition line, overview paragraph, and repository-contents section: "**48-page** monograph" — the compiled PDF is **56 pages**.
- README: "All **17** posterior chains (~51 MB)" — there are **23**; and "compiled with Tectonic (**53 pages**)" — superseded by the authors' own Round-2 build.
- README: "full **10**-section report" — the report has **14** sections.
- README Overview bullet 2 attributes (w₀ = −0.752 ± 0.058, wₐ = −0.86 ± 0.24) to "**with Pantheon+**" — per the manuscript's own Table 5 these are the **DES-Y5** values; the Pantheon+ values are (−0.838 ± 0.055, −0.62). The repository's front page swaps the two SN compilations.
- `.zenodo.json` describes a "48-page" monograph; the Zenodo DOI (10.5281/zenodo.23383762) therefore resolves to a stale, partially incorrect version of record. Version the record or update the metadata.

None of these is physics, but all of them are the same failure mode: text written once and never reconciled with reality. A referee who finds four stale numbers on the front page will not trust the ones inside.

### 5. The new robustness table commits the sin it was built to expose

Table `tab:sn_convention_robustness` compares MAP χ² across fits to **different datasets** (1578, 1580, and 1701 rows), and the surrounding text quotes "the z_CMB-based selection is disfavored (Δχ² = +34 at the MAP)". χ² values are not comparable across different sample sizes and covariance subsets — that is Cosmology 101. The parameter-level comparisons in the table are informative; the Δχ² sentence is not defensible and must be cut or replaced by a like-for-like statistic (e.g., an information criterion applied to a common subsample, or a posterior-predictive comparison).

### 6. The main-text GP figure is computed at hyperparameters the paper itself rejects

Figure `fig:gp_reconstruction` (the four-panel GP showcase of Part VI) was produced with the superseded kernel (σ_f = 5.318, ℓ_f = 1.259) — the very setting the errata appendix now flags as ~800 log-likelihood units off the optimum. Only the *verification* figures use the corrected kernel. The main text therefore displays a reconstruction the paper's own appendix calls suboptimal, with no flag on the figure. Regenerate the figure at the ML hyperparameters or caption the discrepancy.

---

## Minor objections, Round 2

1. Errata: "all 21 posterior chains" — the released count is 23. (See Major 4: this is a disease, not a typo.)
2. Convergence table: ESS "≈ 96 000" (abstract-adjacent text) vs "≥ 85 811" (table) — quote the conservative number everywhere.
3. The cover letter promises "2.8σ–4.2σ" and "ESS ≈ 96 000"; sync it with the final manuscript numbers before submission.
4. The robustness table's "Adopted" row (H₀ = 67.64) and the MCMC posterior (67.65 ± 0.59) are consistent — good — but the table caption should state that the four rows are MAP fits while the quoted posterior is a mean; a careful reader will otherwise see a 0.01 discrepancy and wonder.
5. Union3 and DES-Y5 likelihoods remain un-re-implemented (acknowledged). For a manuscript whose DES-Y5 claims reach 4.2σ, "we quote the collaboration" is thin; at minimum, re-run DES-Y5 through the released pipeline as was done for Pantheon+.
6. The milestone figure caption (Fig. 1) hard-codes z_t = 0.73 — same disease as Major 1.

---

## Verdict

Round 1 proved the author can take a beating and fix things — rare and commendable. Round 2 shows the deeper problem: **the manuscript is not yet a single coherent object.** Its abstract argues with its appendix; its evidence table argues with its own equation; its printed code argues with its released pipeline; its front page argues with its PDF. Every individual fix was real, but the manuscript's parts were never re-reconciled after the fixes.

**Prescription (concrete, in order):**
1. Propagate the corrected z_t (and q₀/j₀ policy) to abstract, conclusions, and every caption; regenerate the main GP figure at ML hyperparameters.
2. Resolve Major 2: either reproduce the Δ⟨ln L⟩ column with a stated, defensible estimator or replace the decomposition table with the (reproducible) Savage–Dickey results and say so.
3. Delete or replace the decorative code listing with an actual excerpt of `verification/cosmo.py` (or a pseudocode box) plus a link to the archived pipeline.
4. Reconcile all repository metadata (page count, chain count, section count, SN attribution in README bullet 2, `.zenodo.json`) with the compiled 56-page reality; version the Zenodo record.
5. Remove the cross-sample Δχ² sentence from the robustness table.
6. Re-run DES-Y5 (and ideally Union3) through the released pipeline.

Do these six things and this becomes a manuscript I would advocate for. As submitted: reject.

— Reviewer 2
