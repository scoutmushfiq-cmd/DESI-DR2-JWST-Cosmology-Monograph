# Hostile Referee Report — Round 5

**Manuscript:** *The Architecture of the Cosmos* (post-Round-4 revision, commit `aa328bb`)
**Reviewer stance:** Hostile Reviewer 2. No sugar-coating. This round I stopped auditing your tables — four rounds have made them bulletproof — and audited the two layers no previous pass touched: **Part VIII–IX physics interpretation** and **the literature claims**. I fetched the actual cited papers and checked the numbers against them.
**Verdict: MAJOR REVISION** — your *verification* is now publication-grade; your *citation and attribution hygiene* is not.

---

## What actually checked out (verified against the primary sources)

- **Neutrino block: exact.** Σm_ν < 0.0642 eV (95%), σ = 0.020 eV, N_eff = 3.23⁺⁰·³⁵₋₀.₃₄, Feldman–Cousins < 0.053 eV, 3σ effective-mass tension, w₀wₐCDM relaxation to < 0.163 eV — every number matches the abstract of Elbers et al. (arXiv:2503.14744v3) character for character. ✓
- **CCHP numbers: exact quadrature combinations.** 68.81 ± 2.22 = √(1.79² + 1.32²); 67.80 ± 2.72 = √(2.17² + 1.64²); 70.39 ± 1.94 = √(1.22² + 1.33² + 0.70²) — all three match Freedman et al. (arXiv:2408.06153v3) stat/sys components combined correctly. ✓
- Ω_m values (Planck 0.3153 ± 0.0073; DESI BAO-only 0.2975 ± 0.0086; Pantheon+ 0.334 ± 0.018) ✓; the 4.52σ, 5.53σ, 0.63σ, 0.16σ tension arithmetic ✓; the 2.5× neutrino relaxation (0.163/0.0642 = 2.54) ✓; the 3.0σ Chebat tension against the 0.059 eV floor ((0.059+0.107)/0.052 = 3.19) ✓; the 2026 eprints you cite (Carloni 2608.01215; Zaldarriaga 2606.30527) resolve on arXiv. ✓

So the numbers you *quote from papers you actually read* are fine. Here is the rest.

---

## MAJOR OBJECTIONS

### M1 — Part VIII claims "we extend our pipeline to three physical beyond-ΛCDM frameworks." No such extension exists anywhere in the released pipeline.

I grepped the entire released source tree: **zero** occurrences of EDE, Horndeski, α_M, IDE, or axion physics in `cosmo.py`, zero chains in `verification/chains/`, zero artifacts, and — by your own `figure_provenance.md` — fig7, the figure "illustrating" these results, is book-pipeline. Yet Part VIII states, in the first person:

- *Axion-like EDE:* f_EDE = 0.092 ± 0.024, r_d = 139.70 ± 1.45 Mpc, H₀ = 71.85 ± 0.88 km/s/Mpc — **no citation at all**;
- *Horndeski:* α_M,0 = −0.18 ± 0.07, z_c ≈ 0.44, Δχ²_MAP = −11.2 — **no citation at all**;
- *IDE:* ξ = −0.036 ± 0.014, H₀ = 69.10 ± 0.62 — Silva et al. (arXiv:2503.23225) is cited for the *framework*, but the numbers are presented as our fit ("yielding").

Three possibilities: these are literature values (then cite them precisely and drop "we extend our pipeline" — presenting another group's posteriors in the first person is misattribution); they are your own (then where are the likelihoods, the chains, the artifacts?); or they are estimates (then say so). As released, the quantitative core of your interpretation section is **unverifiable by all three of your own standards** — not ours, not cited, not audited. This is Round-4 M1's defect class, surviving in the one section you have never audited.

**Required:** per number — either a precise citation with locator and third-person phrasing, or a released likelihood + chains + JSON artifact routed through `audit_numbers.py`.

### M2 — A 58-page monograph with **no bibliography**.

There is no `thebibliography`, no `bibitem`, no reference list — the entire citation apparatus is inline `\href` links of wildly varying format: "arXiv:2503.14738", "DOI:10.1103/w9pk-xsk7", a personal group-page PDF, an alphaxiv mirror, and at least one title-as-author string (M3). Nature does not review manuscripts in this state; the submission portal will not parse it. Four rounds of hostile review and nobody noticed the paper has no reference list — because the numbers were always more interesting than the plumbing. **Required:** a complete, consistently formatted bibliography (author, year, journal/arXiv, DOI); every inline claim keyed to it.

### M3 — Citation defects that signal the bibliography was assembled, not curated.

1. **"Universal Distance Modes 2026, arXiv:2606.30527"** — that is the paper's **title**, not its author. The paper is by **Matias Zaldarriaga** (I fetched it). Citing a title in the author position is a blinking sign that citations were machine-assembled and never checked.
2. **Chebat et al. 2026** cited via `public.websites.umich.edu/~huterer/...` — a personal group-page PDF, not a primary record; personal pages rot.
3. **TDCOSMO XXVII** cited via an `alphaxiv.org/ja/` mirror — an aggregator, in a non-English locale path, instead of arXiv itself.
4. **Vikman (2005)** — the no-go theorem the entire Part VIII crossing discussion leans on — has **no reference entry anywhere**. An uncited theorem is an unsupported theorem.
5. **Silva et al. 2025** cited without its journal reference (Phys. Rev. D 111, 123511 (2025)) while other entries carry DOIs — inconsistent to the point of sloppiness.

### M4 — External quantitative claims quoted without locators; several I could not verify from the cited sources.

- Mirage ln B = +1.85 (Pantheon+), +4.60 (Union3), +6.65 (DES-Y5); the D_KL ≈ 4.5–5.2 range; the "Occam penalty is halved (ΔD_KL ≈ 2.6 instead of 5.1)" claim — all attributed to Lodha et al. (arXiv:2503.14743), none with a table/section locator, none recoverable from the abstract.
- f_DE^max = 1.09 **± 0.05** (abstract, Part VI caption, glossary) — Lodha's f_DE reconstruction is a *curve*; where does a ±0.05 uncertainty on its maximum come from? Give the locator or drop the error bar.
- Algebraic-thawing Δχ² = −2.9 (Pantheon+), −13.2 (DES-Y5) — no locator.
- **H₀ r_d = 10027 ± 65 km/s** (fig7 caption, "gray hyperbola") — DESI DR1's analogous ΛCDM best-fit product was 1.0194 × 10⁴ km/s; I could not verify 10027 ± 65 from the DR2 abstract. Provide the table it comes from, or the derivation.
- The mirage-axis slope **wₐ = −3.66(1 + w₀)** is presented as a universal principal axis; the slope of the D_M(z_*)-invariant line is Ω_m-dependent. State the derivation or the Ω_m at which −3.66 holds.

**Required:** every external number carries a locator (Table X / Fig. Y / §Z); numbers read off figures are labeled as such.

---

## MINOR OBJECTIONS

- **m1 — The "ΛCDM q₀" baseline silently switches between fits.** Eq. (cosmography): q₀,ΛCDM = −0.533 ± 0.008 — that is the *Pantheon+ joint* Ω_m = 0.3114 ± 0.0057 propagated (1.5 × 0.0057 = 0.0086 ✓). The fig5 caption compares against −0.53. But your own DESI DR2 + CMB ΛCDM chain (Ω_m = 0.3007 ± 0.0049) gives q₀ = **−0.549 ± 0.007**. Three "ΛCDM" baselines, none labeled with the fit they come from.
- **m2 — EDE "reducing the SH0ES tension to 1.1σ" is irreproducible from the quoted inputs:** (73.04 − 71.85)/√(1.04² + 0.88²) = **0.87σ**, not 1.1σ. Show the inputs or fix the number.
- **m3 — The abstract headline "w₀ > −1, wₐ < 0" still lacks the CPL qualifier** that your own Round-4 crossing-direction paragraph now makes mandatory: your JBP and Log chains prefer the opposite direction, and the abstract is the one part referees read before deciding to trust you.
- **m4 — Scope box "24 JWST/HST Hosts"** vs Freedman's "24 SN Ia *calibrators* from both HST and JWST": hosts and calibrators are different objects; Part IV should use one term consistently.
- **m5 — The audit still cannot see Parts VIII–IX.** Every defect this round lives outside `audit_numbers.py`'s reach. A `literature_claims.json` registry (claim → value → source → locator) would make external numbers auditable too.

---

## Summary

| # | Severity | One-line statement |
|---|---|---|
| M1 | Major | Part VIII quotes precise EDE/Horndeski/IDE posteriors "from our pipeline" that has no EDE/Horndeski/IDE code, chains, or citations |
| M2 | Major | No bibliography exists in a 58-page monograph |
| M3 | Major | Title cited as author; personal-page and mirror links; Vikman (2005) uncited; inconsistent journal refs |
| M4 | Major | External numbers without locators; f_DE ± 0.05 and H₀r_d = 10027 ± 65 unverifiable |
| m1–m5 | Minor | q₀ baseline switches fits; EDE 1.1σ ≠ 0.87σ; abstract lacks CPL qualifier; hosts vs calibrators; audit blind spot |

Four rounds ago the numbers were wrong. Now the numbers are right and the *attribution* is not. A Nature referee will forgive a rounding error; they will not forgive a theorem with no reference, a title posing as an author, or a section of precise posteriors that no one can trace to anyone.
