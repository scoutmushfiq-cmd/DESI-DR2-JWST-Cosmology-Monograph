# PRD / JCAP Conversion Plan — from the 66-page monograph to a journal submission

**Status at writing:** monograph `cosmology_monograph_full.tex` = 66 pages,
508/508 audit checks pass, all artifacts committed, 22 hostile-review rounds
closed. This document is the section-by-section map for producing a
Physical Review D (or JCAP) regular-article submission, plus the readiness
assessment and the remaining-work checklist.

---

## 1. Readiness assessment

| Component | Readiness | Notes |
| --- | --- | --- |
| Physics content, tables, verified numbers | **~95%** | All 508 audit checks pass; every number artifact-backed; attribution discipline enforced by audit |
| Figures (15 PDFs, all with provenance rows) | **~90%** | All vector PDFs; need single-column re-layout (PRD: 8.6 cm single / 17.5 cm double); fig2 lacks a committed generator (known limitation) |
| Text structure | **~40%** | Book-style "Parts I–X" must become PRD numbered sections; "Part VII-B"-style cross-references must be rewritten; monograph apparatus (Observational Scope banner, schematic book illustrations, pedagogical boxes) must be cut or moved |
| References | **~70%** | 73-entry enumerated list; must convert to REVTeX `\bibliography`/BibTeX with journal abbreviations (Phys. Rev. D volume/page style) |
| Length | **—** | 66 pages → target 40–55 REVTeX pages (PRD regular article); the cuts come from the pedagogical apparatus, not the results |

**Recommended venue order:** (1) PRD (regular article) — the monograph's tone,
length, and completeness fit PRD best; (2) JCAP — equally strong fit, slightly
faster turnaround; (3) Nature distillation runs in parallel
(`nature_letter.tex`, already drafted).

---

## 2. Section mapping (monograph → PRD)

| Monograph part | PRD section | Action |
| --- | --- | --- |
| Part I (Introduction, two anomalies) | I. INTRODUCTION | Keep ~85%; compress the JWST-calibration history; keep the two-question framing |
| Part II (Observational Scope banner) | I. Introduction, final paragraph | Convert the banner to prose; drop the "26 Vector Figures" count |
| Part III (Formalism: background cosmology, slaved parametrization) | II. FORMALISM | Keep; move the cosmographic expansion (4th-order) to an Appendix |
| Part IV (Data: BAO, CMB compression, CC, SNe) | III. DATA AND LIKELIHOODS | Keep the three data tables (tab:desi_dr2_data, tab:cc_data/tab:cc_full_32 — merge the two CC tables into one); keep the two-level compression validation |
| Part V (Local calibrations: JWST/HST ladder, host cross-check) | IV. LOCAL CALIBRATIONS | Keep tab:host_galaxy_distances + fig10/fig13; move the schematic ladder illustrations out |
| Part VI (MCMC results, sound-horizon-free fit) | V. RESULTS: DISTANCE-LADDER FITS | Keep tab:cosmological_constraints, fig1, fig4, tab:convergence |
| Part VII (Dynamical DE: frequentist + Bayesian + Mirage) | VI. RESULTS: DYNAMICAL DARK ENERGY | Keep tab:model_comparison_full, tab:modelcomp_verification, fig3, fig6; keep the Δ⟨lnL⟩ semantics paragraph verbatim (audit-enforced) |
| Part VII-A/B (GP reconstruction, validation) | VII. MODEL-INDEPENDENT RECONSTRUCTION | Keep fig5 + the route-consistency qualifier (audit-enforced); keep z_c legacy disclosure |
| Part VIII (EDE / Horndeski / IDE) | VIII. EARLY AND BEYOND-ΛCDM SOLUTIONS | Keep fig7 + fig11 (forecast) |
| Part IX (Neutrinos) | IX. NEUTRINO MASSES | Keep fig12; the Σmν < 0.064/0.16 eV results |
| Part X (Conclusions: the two questions answered) | X. CONCLUSIONS | Keep the two-question structure; update the 5.72σ pairing sentence (audit-enforced) |
| References (73 enumerated) | BibTeX database | Convert; keep the "Verified Primary Sources" annotation style in the arXiv notes |
| Limitations §8 | XI. LIMITATIONS (or merge into Conclusions) | Keep every bullet (nested-lnB scoping, z_c legacy block, fig2 generator, unreferenced schematics) |
| Corrections appendix | Appendix A | Keep (GP hyperparameter search, j₀ Monte Carlo) |
| Schematic book illustrations (~15) | **Cut** | Presentational choice of the monograph; not journal material |
| Pedagogical boxes / margin notes | **Cut** | Monograph apparatus |

---

## 3. Mechanical conversion checklist

1. **Class:** `\documentclass[aps,prd,twocolumn,superscriptaddress,nofootinbib]{revtex4-2}` (JCAP alternative: `\documentclass[jcp,linenumbers]{jcap}`).
2. **Cross-references:** global rewrite of every "Part ~X" / "Part VII-B" to `\ref{sec:...}`; the audit's Round-18 label/ref integrity check will catch stragglers.
3. **Figures:** re-size to PRD column widths; regenerate via the committed generators (`make_fig1_fig8.py`, `make_fig4_corner.py`, `make_fig5_gp.py`, `make_fig6_model_comparison.py`, `make_figures.py`, `make_figures2.py`) at target sizes rather than rescaling; re-run the three patch scripts (`patch_fig7.py`, `patch_fig10_fig13.py`) after regeneration.
4. **Tables:** `tab:cosmological_constraints` and `tab:tension_matrix` are full-width — use `table*`; the CC table merge (tab:cc_data + tab:cc_full_32 → one).
5. **Bibliography:** build `refs.bib` from the 73 entries; PRD style = abbreviated journals + arXiv IDs; keep DOIs where present (w4c6-1r5j, qqc6-76z4, w9pk-xsk7, 29rq-lgby).
6. **Audit port:** `audit_numbers.py` currently greps the monograph tex; after conversion, point its `tex` path at the PRD source and re-baseline the 508 checks (the artifact-value checks transfer unchanged; the fragment checks need the new wording).
7. **Cover letter:** adapt `cover_letter.md` (journal-specific: editors' names, PRD scope statement).
8. **Length pass:** target ≈45 REVTeX pages; the first cut is the monograph's pedagogical layer (~12 pages), the second is duplicated derivations between Parts III and VI.

## 4. Estimated effort

- REVTeX skeleton + section mapping + cross-reference rewrite: **1 working session**
- Figure regeneration at column widths + patch re-runs: **1 session**
- BibTeX conversion + reference-style pass: **1 session**
- Audit re-baseline (508 checks) + full compile + hostile-review round on the new source: **1–2 sessions**

Total: **4–5 working sessions** from the current state to a submittable PRD draft.
