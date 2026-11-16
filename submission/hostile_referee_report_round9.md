# Hostile Referee Report — Round 9

**Manuscript:** cosmology_monograph_full.tex (63 pp, post-Round-8 + Union3/DES-Y5 Mirage extension, commit `bdf3aca`)
**Verdict: MAJOR REVISION** — the Round-8 manuscript was internally consistent, but the Round-9 extension (filling the Mirage Union3/DES-Y5 rows and adding the nested-sampling cross-check) re-introduced one figure–table contradiction, one sample-size inconsistency with the released data product, and left the abstract and the convergence section silent about the manuscript's own strongest new evidence.

## Major findings

| # | Finding | Evidence | Severity |
| --- | --- | --- | --- |
| M1 | **Figure–table contradiction.** `fig:bayes_comparison` (panel a) still displays the transcribed Lodha et al. Mirage values (−16.2 Union3, −20.7 DES-Y5), while Table `tab:model_comparison_full` and the caption now quote this work's −19.3 and −17.0. A reader comparing figure and table sees two different Mirage results for the same datasets. | `figs/fig6_model_comparison_bayes.pdf` (extracted text: Mirage bars from the pre-extension values); `figure_provenance.md` line 28 ("published Δχ²_MAP and ln B decomposition values") | Major |
| M2 | **Sample-size inconsistency for DES-Y5.** Part III describes DES-Y5 as "1635 photometrically classified DES supernovae combined with 194 external low-z SNe Ia" (1829), but every own-pipeline number in the manuscript is computed on the 1820-SN released DES-Dovekie distance sample (`nsn = 1820` in the released `STAT+SYS.npz`; all 1820 released rows have zHD > 0, so the official `DES-Dovekie-SN_Likelihood.py` cut retains all of them). The 1829 figure is the light-curve sample count, not the released distance sample. The manuscript never reconciles the two numbers. | `verification/sn5yr/STAT+SYS.npz` (`nsn=1820`); `DES-Dovekie_HD.csv` (1820 rows, min zHD = 0.025); official script line 52 (`ww = data['zHD']>0.00`) | Major |
| M3 | **Abstract omits the manuscript's own strongest evidence.** The abstract quotes only the published CPL lnB values (−0.66/+3.03/+4.88, all transcribed) and never states that this work computes its own Mirage-axis Bayes factors for all four dataset combinations — the single most distinctive quantitative result of the monograph. | Abstract, second-result paragraph | Major |
| M4 | **Convergence of the 8 new chains is asserted nowhere in the manuscript.** The Union3/DES-Y5 Mirage rows rest on chains whose R̂ is only in the JSON artifact; Part VII-B (Sampler Convergence) tabulates only ΛCDM and w₀wₐCDM on DESI DR2 + CMB. | `tab:convergence`; `sn_extra_results.json` (R̂ ≤ 1.001) | Moderate |
| M5 | **Union3 likelihood evaluation is under-specified in Part III.** The text describes the compilation (2087 SNe, 22 nodes) but never states that the pipeline evaluates the 22 binned μ with the released inverse covariance under the (1+z) convention — the reader cannot tell what "evaluated against Union3" means operationally. | Part III, SN subsection | Moderate |
| m1 | `figure_provenance.md` still lists fig6 as pure transcription; after regeneration it is part own-pipeline. | line 28 | Minor |

## Fixes applied (researcher mode)

- M1: `verification/make_fig6_model_comparison.py` written; fig6 regenerated from the table's values (hatched bars for the four own-pipeline Mirage entries, published values for all transcribed rows); caption amended ("hatched bars: computed in this work"); provenance updated.
- M2: Part III now states that the released DES-Dovekie distance file and covariance contain 1820 SNe, that the official zHD > 0 cut retains all 1820, and that the 1829 count refers to the upstream light-curve sample; the validation paragraph in Part VII-B cross-references this.
- M3: Abstract gains the own-pipeline Mirage evidence sentence (lnB = +3.4 to +6.8 across all four dataset combinations, nested sampling + Savage–Dickey cross-check).
- M4: Part VII-B states R̂ ≤ 1.001 for the eight new chains (96,000 retained samples each).
- M5: Part III now specifies the Union3 evaluation (22 binned μ, released inverse covariance, (1+z) convention) and the DES-Y5 evaluation ((1+z_HEL) convention of the official script).
- m1: `figure_provenance.md` fig6 entry rewritten.
- `audit_numbers.py` extended 283 → 291 checks (fig6 generator + provenance, 1820-reconciliation sentence, abstract Mirage sentence, R̂ sentence, Union3 evaluation spec).
