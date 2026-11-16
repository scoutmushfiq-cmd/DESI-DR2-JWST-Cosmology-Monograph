# Referee Report — Round 3 (Post-Fix Re-Review)

**Manuscript:** *The Architecture of the Cosmos: Model-Independent Constraints on the Hubble Constant and Dark Energy from DESI DR2, Pantheon+, and JWST* (M. M. Rahim)
**Reviewed build:** commit `582226d`, branch `vibe/cosmos-verification-9d0230`, compiled PDF (57 pp)
**Verdict: MAJOR REVISION — third round.**

---

## Overall Assessment

I reviewed Round 2's fixes. Two of them I accept: the evidence-decomposition semantics paragraph is now statistically honest, and the code listing is finally a verbatim excerpt of the released pipeline (I diffed it against `verification/cosmo.py` — it checks out).

But the authors have once again fixed the *symptoms* I listed and shipped the correction with **fresh errors of exactly the same class they were correcting**. You wrote a referee-report section bragging that the metadata was reconciled with "the compiled 56-page reality" — the PDF in the same commit is **57 pages**. You wrote a caption saying $w(0) = -0.98 \pm 0.05$ — your own released draws give $\pm 0.09$. And in the process of harmonizing $z_c$ to $0.42 \pm 0.09$ across the manuscript, you left a figure caption in Part VII quoting **$z_c = 0.49 \pm 0.12$**, a number that appears nowhere else and is never derived anywhere at all.

Worse: I re-ran your own model comparison, and **two of the five χ²_min values in your robustness table are unconverged optimizer artifacts that your own committed chains beat by Δχ² ≈ 1.5–3.1.** The repository contradicts itself, table against chains, and neither the text nor the errata notices.

This is the third consecutive round in which the phrase "every number is verified" in the cover letter is falsified by an afternoon of recomputation. The physics case is real; the hygiene is not at the standard you claim.

---

## Major Objections

### MAJOR 1 — The robustness table's JBP and Log χ²_min are not optima; your own chains refute your own table

Table `tab:modelcomp_verification` (Part VII-C) prints:

| Model | χ²_min (table) | Best χ² in the *released chains* | Bounded MAP (re-optimized from chain-best) |
|---|---|---|---|
| JBP | 14.16 | **12.64** (`chain_jbp_desi_cmb_s11.npy`) | ≤ 12.64 |
| Logarithmic | 11.75 | **8.63** (`chain_log_desi_cmb_s22.npy`) | **8.625** at $(H_0, \omega_{bc}, w_0, w_a) = (64.70, 0.1424, -1.417, 0.978)$ |

The true $\Delta\chi^2_{\rm MAP}$(Log) is therefore **≈ −15.0, not the printed −11.88** — statistically indistinguishable from CPL's −15.29. The AIC and BIC columns for both models inherit the error (they are computed from $\chi^2_{\rm min}$). When I re-optimized JBP from its chain-best point, the optimizer ran to $w_a = 2.49$, *outside the stated prior bounds* — direct evidence that the χ² surface was never properly explored and that the original suite's optimizer output was accepted uncritically.

Three consequences the authors must confront:

1. The prose claim "the CPL form achieves the best χ²_min, AIC and BIC, while the logarithmic ansatz is competitive on DIC" is quantitatively wrong — Log is essentially **tied** with CPL on χ²_min (8.63 vs 8.34). Ironically the robustness *conclusion* (the preference for evolving dark energy is not a CPL artifact) gets **stronger** with the correct numbers; the printed table is wrong in the direction that flatters CPL's uniqueness.
2. The new "Semantics of the Δ⟨lnL⟩_P" paragraph quotes chain-based χ²_min values (ΛCDM 23.59, CPL 8.36, from `dlnL_decomposition.json`) that disagree with the same manuscript's table (23.63, 8.34) and, for JBP/Log, disagree grossly (12.60 vs 14.16; 8.65 vs 11.75). One document, two sets of "χ²_min", no reconciliation.
3. The table silently mixes methodologies: χ²_min/AIC/BIC from an optimizer, DIC from chains. After fixing MAJOR 1, state in the caption which column comes from which estimator.

**Required:** re-optimize JBP and Log with bound-respecting multi-start (seeded from the chains), republish χ²_min, Δχ²_MAP, AIC, BIC for all five rows, and rewrite the "Second robust conclusion" sentence to reflect that Log matches CPL on fit quality.

### MAJOR 2 — Two mutually inconsistent Savage–Dickey evidences for the same model, dataset, and nested point

- Table `tab:modelcomp_verification`, caption "prior volumes … V = 15 (CPL)": $\ln B_{\rm SD} = \mathbf{+1.78}$.
- Part VII-B "Semantics" paragraph, added in the Round-1 fix round: "$\ln B = \mathbf{+2.71}$ (CPL over ΛCDM) … varying the CPL prior volume from V = 13.5 to V = 15 shifts lnB by only 0.11 (+2.71 → **+2.60**)."

Same model (CPL), same data (DESI DR2 + CMB), same nested point $(-1, 0)$, same stated estimator (Savage–Dickey density ratio from the released chains), same prior volume V = 15 — and the manuscript prints **+1.78 and +2.60 in two different sections**, both sourced to `verification/`. The two artifacts (`model_comparison.json`: `lnB_SDX = 1.78`; `posterior_avg_dchi2.json`: 2.60–2.71) evidently used different KDE bandwidths, chain sets, or prior-volume normalizations, and nobody reconciled them. On a paper whose entire Part VII is about getting Bayesian evidence semantics right, an unreconciled 0.8 discrepancy in the headline Bayes factor is disqualifying.

**Required:** one canonical SD computation, one number, one stated kernel/bandwidth/prior-volume convention, both JSON artifacts regenerated from it, and the VII-B paragraph and the table brought into agreement.

### MAJOR 3 — The harmonized z_c = 0.42 ± 0.09 is contradicted by your own Part VII figure caption and derived nowhere

- Part VII verification figure caption (`fig_gp_wz.png`): "The GP median (blue) crosses the phantom divide (dashed) at $z_c \approx 0.5$, consistent with the CPL posterior estimate $z_c = \mathbf{0.49 \pm 0.12}$."
- Everywhere else (6 occurrences): $z_c = \mathbf{0.42 \pm 0.09}$.

$0.49 \pm 0.12$ appears exactly once in the entire manuscript, is never derived, and flatly contradicts the value the Round-1 errata claims was "harmonized everywhere." Beyond the contradiction: **the manuscript never derives 0.42 ± 0.09 at all.** No formula, no dataset attribution, no error propagation. The derivation ($z_c = -(1+w_0)/(1+w_0+w_a)$ propagated through the $(w_0, w_a)$ posterior) exists only in the referee-response *template*, not in the paper. Which dataset's posterior does 0.42 come from — Pantheon+ (which gives ≈ 0.35), Union3 (≈ 0.44), DES-Y5? The reader cannot tell, and neither, I suspect, can the authors.

**Required:** print the $z_c$ formula, state the dataset and posterior it is propagated from, show the Monte Carlo error derivation, and fix or delete the $0.49 \pm 0.12$ caption.

### MAJOR 4 — The page-count metadata is wrong again, in the very commit that claimed to fix it

The compiled PDF at `582226d` has **57 pages**. The README says "56-page" in four places, the cover letter says "a 56-page research monograph", `.zenodo.json` says "A 56-page … monograph", and VERIFICATION_REPORT §14 says "56-page compiled PDF" twice. Round 2's fix table literally contains the sentence "reconcile … with the compiled 56-page reality" — that number was already stale when it was committed, because the same commit's listing replacement and caption rewrites grew the document. This is now the *second consecutive round* in which the page count in the metadata does not match the artifact in the same tree.

**Required:** stop hand-maintaining the page count. Derive it from the build (or omit it), and reconcile every occurrence.

### MAJOR 5 — The Round-2 GP caption rewrite introduced a wrong uncertainty: w(0) = −0.98 ± 0.05

The regenerated figure's own draws give 16/84 percentiles of $w(0)$ of $[-1.057, -0.873]$ around a median of $-0.975$, i.e. $w(0) = -0.98 \pm \mathbf{0.09}$. The caption says $\pm 0.05$ — a factor-of-two understatement of the interval, introduced in the very edit that was supposed to make this caption "describe exactly what the figure shows." I checked because I was told to; a Nature referee will check because they are paid to distrust you.

**Required:** correct to $\pm 0.09$, and re-derive every number in that caption from the regeneration script's printed output (`make_fig5_gp.py` prints them all) rather than from memory.

### MAJOR 6 — "11 Vector Figures" survives in the Observational Scope box, directly under the abstract

Line 240 of the source: the scope banner advertises "**11 Vector Figures**" while the manuscript contains **26** `\includegraphics` targets and the README (correctly, as of Round 2) says 26. This stale count from the original 11-figure preprint has now survived two dedicated metadata-cleanup rounds. There is no excuse at this point: every integer in a "scope" banner is a claim, and this one is false by 2.4×.

**Required:** correct to 26, and sweep the manuscript for any remaining draft-era counts (figures, tables, pages, chains) with an automated pass, not eyeballs.

---

## Minor Objections

1. **m1 —** In `tab:modelcomp_verification`, the $\ln B_{\rm SD}$ column is "---" for JBP and Log with no stated reason. The KDE density ratio is computable for any nested point; either compute both or state why they are omitted.
2. **m2 —** `submission/referee_response_template.md` answers "JBP and Log … independently improve χ² by ≥ 9.5" — after MAJOR 1 is fixed this is true but understated (≥ 15); sync it, and note the template's $z_c$ formula should migrate into the manuscript per MAJOR 3.
3. **m3 —** The convergence table says ESS "≥ 85,811" while the cover letter now says "≥ 85 800". Pick one rounding convention.
4. **m4 —** VERIFICATION_REPORT §14's "56-page compiled PDF" (×2) becomes wrong the moment MAJOR 4 is fixed; quote the count programmatically or drop it.
5. **m5 —** The GP caption uses both `$f_{\rm DE}^{\rm max}$` and `$f_{\rm DE}^{\max}$` for the same quantity. Cosmetic, but in a 57-page monograph about numerical rigor, cosmetics are read as a proxy.
6. **m6 —** The DIC caption's tail-trim rationale ("pathological $w_a \to -4$ draws") and the new Δ⟨lnL⟩ paragraph's trim are now two separate descriptions of the same ΔD = 30 convention; cross-reference one from the other so a reader does not have to infer they are identical.

---

## What I Do Not Object To (for the record)

- The listing is now genuinely verbatim (diffed against `verification/cosmo.py`, all three segments match).
- The Δ⟨lnL⟩ tail-trim semantics paragraph is statistically correct and the reproduced values (+1.30 / +6.66 / +4.16 / +6.57) do bracket the quoted lnB once D_KL is subtracted.
- The z_t = 0.77–0.79 propagation is consistent across abstract, conclusions, captions, and errata.
- The README's Pantheon+/DES-Y5 attribution swap is fixed correctly.

---

## demanded before any further review round

1. Re-optimize JBP/Log (MAJOR 1) and republish the corrected model-comparison table + prose.
2. One canonical Savage–Dickey number (MAJOR 2).
3. Derive z_c in the text; kill 0.49 ± 0.12 (MAJOR 3).
4. Programmatic page/figure/count reconciliation across README, .zenodo.json, cover letter, and the report (MAJORS 4, 6).
5. Re-derive every caption number from the generating script's output (MAJOR 5).

The pattern across three rounds is identical: the corrections are reactive, hand-copied, and never re-audited after being typed. Build a checklist script that extracts every quoted number from the LaTeX and diffs it against the JSON artifacts, run it in CI, and stop making me find these.
