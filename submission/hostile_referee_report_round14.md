# Hostile Referee Report — Round 14 (post Round-13-fix audit)

**Verdict: MAJOR REVISION** (again — this time two of the majors are defects **introduced by the Round-13 fix pass itself**, which is exactly why every fix must be re-audited).

Scope of this round: (i) re-verification of the Round-13 fixes at the rendered-PDF level, (ii) caption-to-float attachment, (iii) package-level consistency (stale artifacts, referee template), (iv) provenance of every derived percentage claim.

---

## Major findings

### M1 — The Round-13 M3 caption fix was applied to the wrong float

The Round-13 fix rewrote the caption containing "Values exceeding $3\sigma$ … highlighted in bold" into a two-tier SEVERE/CONSIST. description. But that caption (line ~822) belongs to **`tab:tension_matrix`, the $5\times 8$ TABLE** — not to fig8. The table contains **no SEVERE/CONSIST. labels**; it signals severity with `\mathbf` bold, for which the *original* wording was correct. Meanwhile the **actual fig8 caption** (`fig:tension_heatmap`, line ~739) still does not describe the two-tier labels that the regenerated figure now embeds.

Net state after Round 13: the table caption describes labels the table does not have, and the figure caption omits the labels the figure does have. The audit passed because it only greps the tex globally ("two-tier severity label" in tex) and never checks **which float a caption sentence is attached to** — a blind spot that must itself be closed.

### M2 — The Round-13 fig13 patch cut the panel-(a) gridlines

The white-out rectangles used to erase the old symmetric H0pe bar (`[277.3–350.1]` and `[356.3–429.0]` at $y = 247.1$–$256.5$) also erased segments of the gray vertical gridlines at $x \approx 293.74$, $348.77$, and $403.81$ in the H0pe row band. Confirmed visually at $10\times$ zoom: the gridlines now have clean rectangular gaps behind the bar and the label. The patch script's post-assertions checked the bar, caps, marker, and text — but not the collateral damage to unrelated ink. The label's white backing box additionally blanks the $x=403.81$ gridline across its full height (acceptable — it reads as a text background — but the bar-region gaps are pure defects).

### M3 — A stale orphan artifact and a referee-response template that "validates" superseded numbers

1. `verification/rdfree_result.json` (singular) still contains the **superseded** sound-horizon-free fit: `H0 = 69.212 ± 1.443`, `rd = 146.771 ± 2.87`, `H0rd = 10154.5 ± 71`, `Om = 0.2974 ± 0.0083` — directly contradicting the authoritative `rdfree_results.json` (68.19 ± 1.45, 146.36 ± 2.88, 10027 ± 45). It is referenced by no script and no tex string; it is a landmine for anyone re-running the package or diffing artifacts.
2. Worse, `submission/referee_response_template.md` still contains the row "`r_d-free H₀ | 69.24 ± 1.82 | 69.21 ± 1.44 | ✓`" — i.e., the template instructs future referee responses to declare the **superseded row verified against the superseded artifact**. Rounds 12–13 fixed the template's `+6.75` and DES-SN5YR staleness but missed this row.

## Minor findings

### m1 — The "81–99.6% recovery" sentence (Part I summary) omits its basis

Line ~234 quotes the **transcribed official** CPL $\Delta\chi^2_{\rm MAP}$ values ($-10.7$ Pantheon+, $-17.4$ Union3, $-21.0$ DES-Y5) and then says the Mirage axis recovers "81–99.6% of the CPL $\Delta\chi^2_{\rm MAP}$ improvement". Computed against the values quoted in the same sentence, the ratios are **123%, 111%, 81%** — two exceed 100%. The claim is in fact computed against **our own pipeline** CPL values ($-15.3$, $-13.3$, $-20.6$, $-17.1$), and the qualified statement exists in the table footnote, the fig6 caption, and Part VII — but this sentence, standing alone, invites a reader to compute a contradiction.

### m2 — The canonical CPL Savage–Dickey value hides its dominant systematic

The semantics paragraph asserts robustness to prior volume ($+2.71 \to +2.60$, shift 0.11) and bandwidth. But the canonical artifact itself records `V15_scott_2chains = 3.355` — a two-chain recomputation shifts $\ln B$ by **+0.76**, six times the prior-volume effect and nowhere disclosed. The qualitative conclusion (positive CPL evidence) survives, but quoting a density-ratio value with no uncertainty while its own artifact demonstrates an $\mathcal{O}(0.4)$-nat chain-sampling systematic is not defensible.

### m3 — `figure_provenance.md` does not reference the new patch scripts

fig7, fig10, and fig13 are listed as "book-pipeline" with no mention of `patch_fig7.py` / `patch_fig10_fig13.py`, which are now part of the released reproduction chain.

### m4 — README reproduction instructions omit the patch scripts

The README reproduce paragraph names the MCMC and suite scripts but not the three figure generators/patch scripts a reader needs to rebuild every modified figure.

## Verified clean this round (no action)

- fig8 SEVERE count **13** independently recomputed from the generator's own $T_{ij}$ values (2+2+2+2+2+3+0); caption range 5.43–6.27σ correct; all 42 cell values unchanged.
- Tension cells 2.72/2.95/4.52/5.72 recomputed from the quoted $(H_0,\sigma)$ pairs — exact.
- fig1 generator: exactly two `two_sigma=True` rows, both SH0ES — matches the reworded caption; 18 rows.
- fig2 legend contains $\Omega_m = 0.334$, $H_0 = 73.04$ — matches the amended caption.
- fig10 label now renders as a clean "(71.20)" (no gap, no stray paren); fig13 non-H0pe labels (73.50±2.80, 73.30±2.40, 73.90±3.00, 70.80±4.20, 68.17±0.28) all present.
- Mirage $\ln B$ network internally consistent: $+5.62 - 2.13 = +3.49$; $+6.03 - 2.40 = +3.63 \approx +3.64$; Scott/Silverman values and half-spread errors ($\pm 0.23$, $\pm 0.94$) all backed in `mirage_sd.json`; nested cross-check paragraph matches `nested_lnB.json` ($+3.65\pm0.35$, $+3.40\pm0.35$, $+6.74\pm0.03$, $+5.04\pm0.19$).
- $z_c$ values (0.35 ± 0.11, 0.50 ± 0.08) match `savage_dickey_canonical.json` medians (0.345 ± 0.107, 0.495 ± 0.077).
- Referee template's other re-run values trace to `convergence_diagnostics.json` (e.g., 68.351).
- No stale 0.3048/0.0188/69.24/146.99 anywhere in tex, README, `.zenodo.json`, or cover letter.
- Scott == Silverman to 14 digits is mathematically correct for 2-D KDE (identical bandwidth exponents at $d=2$), not a bug.
