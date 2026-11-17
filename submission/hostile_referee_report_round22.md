# Round 22 — Hostile Referee Report (data-layer transcription integrity)

**Scope:** the layer no previous round audited — whether the *numbers printed
in the manuscript's data tables* are the *numbers the likelihood actually
consumes*. Every transcription between the published data releases, the tex
tables, and `cosmo.py` was cross-checked cell by cell, plus the GP and
σ-pairing claims against their artifacts.

## Findings

### m1 — The abstract's GP-consistency sentence is stronger than the artifact supports (NOT YET FIXED)
The abstract/summary (tex L234) states: *"Non-parametric GP reconstructions
are consistent with this phantom crossing at $z_c = 0.50 \pm 0.08$."* But the
released artifact `verification/gp_route_crossing.json` says, in its own
`note` field: the $H(z)$-route median crosses $w = -1$ near **$z \approx 0.14$,
not at the CPL posterior $z_c \approx 0.50$**, and *"the two routes are
consistent only at the level of the wide 68% band, not at the level of the
median"* (only 430/600 = 71.7% of draws cross at all). The fig5 caption
(tex L793) words this correctly and carefully; the abstract sentence drops the
qualifier and reads as median-level agreement. *Required fix:* one clause in
the abstract/summary matching the caption's qualifier (band-level consistency;
the direct-$w(z)$ median crossing is not resolvable at higher significance).

### m2 — The 5.72σ figure's inputs are never stated (apparent inconsistency on naive pairing)
The abstract bullet (tex L205) and the summary (tex L247) quote
"4.52σ vs. DESI DR2+CMB, rising to 5.72σ vs. Planck 2018 alone" directly after
quoting SH0ES $73.04 \pm 1.04$. The arithmetic: 4.52σ = $73.04$ vs $68.17$;
but 5.72σ = **$73.17 \pm 0.86$ (4-anchor ladder) vs $67.36 \pm 0.54$
(Planck)** — pairing the sentence's own quoted $73.04$ with Planck gives
**4.85σ**, not 5.72σ. Both numbers are individually artifact-backed
(`H0_LADDER` in `cosmo.py`), but the pairing that produces 5.72σ is never
stated in either place. *Required fix:* one parenthetical
"(using the 4-anchor ladder $73.17 \pm 0.86$)" at both sites.

### m3 — The data tables and the likelihood are never machine-compared (audit gap)
The 32-point CC table (`tab:cc_data`, `tab:cc_full_32`) and the 13-observable
BAO table (`tab:desi_dr2_data`) are transcriptions of `cosmo.py`'s `CC_DATA`
and `DESI_BAO`/`DV_BGS`, but no audit check enforces their agreement — a silent
edit to either side would go unnoticed. *Required fix:* audit section parsing
`CC_DATA` and `DESI_BAO` from `cosmo.py` and asserting every $(z, H, \sigma_H)$
and every $(D_M/r_d, \sigma_M, D_H/r_d, \sigma_H, r_{M,H})$ appears in the tex
tables.

## Verified-clean (exact matches)

| Check | Result |
| --- | --- |
| CC table ↔ `cosmo.py` `CC_DATA` | **32/32 cells exact** in both `tab:cc_data` and `tab:cc_full_32` ($z$, $H$, $\sigma_H$ all match to the printed precision) |
| BAO table ↔ `cosmo.py` `DESI_BAO` + `DV_BGS` | **13/13 observables exact**: BGS $7.944 \pm 0.075$; LRG1 $13.587 \pm 0.169$ / $21.863 \pm 0.427$ ($r=-0.475$); LRG2 $17.347 \pm 0.180$ / $19.458 \pm 0.332$ ($-0.423$); LRG3+ELG1 $21.574 \pm 0.153$ / $17.641 \pm 0.193$ ($-0.425$); ELG2 $27.605 \pm 0.320$ / $14.178 \pm 0.217$ ($-0.437$); QSO $30.519 \pm 0.758$ / $12.816 \pm 0.513$ ($-0.489$); Ly$\alpha$ $38.988 \pm 0.531$ / $8.632 \pm 0.101$ ($-0.431$) |
| Observable count | $13 = 1$ isotropic $+ 6 \times 2$ anisotropic, consistent everywhere (abstract, §data, fig5 caption "15 data points = 13 + θ* + ω_bc") |
| GP claims vs `gp_hyperparameter_search.json` | $\sigma_f \approx 305$ (305.09), $\ell_f \approx 3.89$ (3.8853), marginal log-likelihood $-119.0$ (nll 119.01) — all match |
| GP claims vs `gp_route_crossing.json` | $w(0) = -0.97 \pm 0.09$ ($-0.9748 \pm 0.0941$), $z_t = 0.77 \pm 0.08$ ($0.765 \pm 0.083$), $q_0 \approx -0.52 \pm 0.13$ ($-0.512 \pm 0.131$) — all match |
| 4.52σ and 5.53σ pairings | $73.04$ vs $68.17 \Rightarrow 4.52$; $73.17$ vs $68.17 \Rightarrow 5.53$ — correct as quoted |

## Verdict

**MINOR REVISION** — no transcription errors anywhere in the data layer (a
genuinely clean sweep), but two prose-level overstatements (m1, m2) and one
audit gap (m3). All mechanical fixes; no scientific result changes.
