# Hostile Referee Report — Round 4

**Manuscript:** *The Architecture of the Cosmos: Model-Independent Constraints on the Hubble Constant and Dark Energy from DESI DR2, Pantheon+, and JWST* (post-Round-3 revision, commit `4397117`)
**Reviewer stance:** Hostile Reviewer 2. No sugar-coating. Every objection below is backed by a check I actually ran against the manuscript, the released source, and the released artifacts.
**Verdict: MAJOR REVISION** — the automated number audit you added (22/22 passing) guards *tabulated scalars*, and that is exactly why the remaining defects have all migrated to *prose, captions, and provenance claims* — the places your audit cannot see. I went there. I found five majors.

---

## What actually checked out (so you cannot claim I did not look)

- `nll` at the quoted ML hyperparameters: **119.01** (manuscript: −119.0); at (5.318, 1.259): **904.55** (manuscript: −904.6). ✓
- The released `gp_hz()` single-start Nelder–Mead converges to σ_f = 305.100, ℓ_f = 3.8854, z_t = 0.765 ± 0.083, q₀ = −0.512 ± 0.131 — matching every quoted figure. ✓
- Scott ≡ Silverman bit-identity for the 2D nested points is *mathematically exact* (Silverman's d = 2 prefactor (4/(d+2))^(1/(d+4)) = 1), not a bug; the 1D wCDM case correctly differs in the 4th decimal. I checked before accusing. ✓
- Chains: 23 on disk. ESS minimum 85,811. PDF: 57 pages. Audit: 22/22. ✓

Now the part that should worry you.

---

## MAJOR OBJECTIONS

### M1 — The Part VII systematics paragraph says the Pantheon+ likelihood "is not reproduced in the verification suite." Your own repository reproduces it. Which manuscript am I reading?

> *"The Pantheon+ likelihood (1701 light curves, 1701 × 1701 statistical + systematic covariance) is not reproduced in the verification suite; SN-inclusive constraints are quoted from the published analyses."* — Part VII, "Type Ia supernovae" paragraph

This is flatly false **against your own delivered tree**:

- `verification/pantheon/` (data loader + provenance README),
- `verification/run_sn_joint.py`, `verification/sn_joint_results.json` (full STAT+SYS covariance, analytic M_B marginalization, ΛCDM and CPL joint chains),
- `verification/chains/chain_{lcdm,cpl}_sn_s{1,2}.npy` — four SN-inclusive chains,
- and the manuscript's **own** Table caption (Supernova Sample-Convention Robustness Scan) quoting *your reproduced* full-likelihood MCMC posteriors: H₀ = 67.65 ± 0.59, w₀ = −0.831 ± 0.053, wₐ = −0.661 ± 0.196.

The same paragraph then asserts the +SH0ES-prior rows "are SN-controlled and **cannot be recovered** from BAO + CMB + CC alone" — while `chain_w0wa_desi_cmb_cc_shoes.npy` and `chain_w0wa_desi_cmb_cc_trgb.npy` sit in your chains directory and the corner-plot figure (fig:mcmc_corner) displays exactly that run.

This is the stalest kind of error: a paragraph written *before* the Pantheon+ integration that survived three review rounds in a manuscript whose Round-1 fix headline was the Pantheon+ integration. It simultaneously (a) contradicts the paper, (b) contradicts the repo, and (c) **undersells your own strongest verification** — you ran a 1701-covariance SN likelihood from scratch and matched the official DESI DR2 constraints to 0.1σ, and one section later you tell the referee you never did.

**Required:** rewrite the paragraph to state what was actually done (full likelihood reproduced, convention, validation against the official posterior), and cross-reference the SN-convention table.

### M2 — The tab:robustness caption states an "invariant" that two of the three rows directly beneath it falsify — and it is your paper's headline claim

Caption of tab:robustness:

> *"the invariant statements are (i) every two-parameter ansatz prefers w(z) > −1 today with more negative w in the past..."*

The table directly below:

| Model | w₀ | wₐ |
|---|---|---|
| JBP | **−1.08 ± 0.06** | **+0.73 ± 0.25** |
| Logarithmic | **−1.31 ± 0.12** | **+0.71 ± 0.22** |

Both are **phantom today** (w₀ < −1 at >1σ for Log), and both have **positive** wₐ — for JBP/Log the equation of state *rises* toward quintessence at z ≈ 1 and returns to phantom today and at high z. That is the **opposite crossing direction** to CPL (w₀ = −0.48 ± 0.31, wₐ = −1.71 ± 0.72: quintessence today, phantom in the past). The MAP fits in tab:modelcomp_verification agree (JBP w₀ = −1.14, Log w₀ = −1.42).

So the sign of the late-time deviation from ΛCDM — the thing your abstract, conclusions, and Part VIII interpretation are built on — is **parametrization-dependent**, your own chains show it, and the manuscript neither states it, discusses it, nor reconciles it with the headline narrative. "Three robust conclusions" says the *preference for evolving dark energy* is robust — fine — but the caption's invented "invariant (i)" is false as written, and the physical implications of the JBP/Log crossing direction (a phantom-today solution with a quintessence bump is a qualitatively different dark sector) are never mentioned. A Nature referee will read tab:robustness, see the contradiction in ten seconds, and stop trusting every summary paragraph upstream of it.

**Required:** (a) correct the caption invariant to what is actually shared (improved fit; |deviation| from ΛCDM; not the sign); (b) add an explicit discussion of the direction-of-crossing parametrization dependence, including why CPL remains the physically motivated baseline and what JBP/Log's preference means for the phantom-crossing story; (c) sweep the abstract/conclusions for any sentence implying all parametrizations agree on w₀ > −1 today.

### M3 — The Part VII-D caption asserts a phantom crossing at z_c ≈ 0.5 that the figure does not show. I recomputed the figure's exact recipe. The median crosses at z ≈ 0.14.

Caption of fig:gpwz_verification:

> *"The GP median (blue) crosses the phantom divide (dashed) at z_c ≈ 0.5, consistent with the CPL posterior estimate z_c = 0.50 ± 0.08 (Eq. zc_derivation)."*

I re-ran the exact recipe that generated this figure (`make_figures2.py`: `gp_hz()` at the ML hyperparameters, `default_rng(23)`, 600 draws, the same ρ_DE subtraction and log-gradient):

- GP median w(0) = **−0.975**
- median crossings of w = −1: **z ≈ 0.14** (one crossing)
- median w(0.5) = **−1.105**

The median crosses at **0.14, not 0.5**. The caption takes the CPL posterior number, paints it onto a reconstruction that crosses somewhere else entirely, and calls the agreement "consistent." That is not an approximation; it is a caption describing a feature the plotted curve does not have. Worse, your own Part VI fig5a caption says the crossing "is **not resolvable** at higher significance from the H(z) route alone" — the two captions describe the same H(z)-route reconstruction with opposite evidential claims. And note the irony: your Round-3 fix *added* the eq:zc_derivation cross-reference to this caption, upgrading its apparent rigor while the asserted number remained unattached to the plotted curve. Your audit script checks z_c = 0.50 ± 0.08 *as a string* — it has no way to know the figure underneath the caption disagrees.

**Required:** recompute and state the actual H-route median crossing (z ≈ 0.14) with its uncertainty, present it as a *tension* with — not a confirmation of — the CPL posterior z_c, harmonize with the fig5a "not resolvable" statement, and extend the audit to caption-claims that are checkable from released recipes.

### M4 — Part VI claims a "30-start Nelder–Mead" hyperparameter search. No such search exists anywhere in the released code.

> *"marginal log-likelihood maximization (30-start Nelder–Mead over (ln σf, ln ℓf)) yields optimal hyperparameters σf ≈ 305 ... ℓf ≈ 3.89"*

The released pipeline (`cosmo.py::gp_hz`) performs a **single-start** `Nelder-Mead` from `log((5.318, 1.259))` — the superseded values your own text calls "a poor region of the marginal-likelihood surface." `make_fig5_gp.py`, the Round-2 figure script, simply calls `gp_hz()`. I searched every released `.py`: there is no multi-start loop, anywhere.

You were saved by luck: I verified the single start happens to converge to exactly the quoted optimum (305.100, 3.8854, nll = 119.01). But "the described experiment does not exist in the released code" is precisely the defect class your Round-2 referee flagged as a *decorative listing*, and three rounds later it is still present — now in the methods text instead of the listing. If the 30-start search was ever run, its code was never released; if it was never run, the methods section describes a fiction.

**Required:** either release the actual multi-start search (and its start-point log), or correct the text to describe what the released code does — single-start Nelder–Mead from the historical start, *verified* to reach the global optimum by an independent multi-start check (which you should then actually run and archive).

### M5 — "The complete, executable source ships with the manuscript." Eleven of your twenty-six figures have no generator in the released tree.

The Reproducibility Statement and the listing caption claim *"the complete, executable source ships with the manuscript"* and *"all driver scripts ... ships with the manuscript source tree."* I checked which included figures have released generators:

- **Have generators:** fig5 (`make_fig5_gp.py`), fig_corner_w0wa / fig_gp_wz / fig_om_diagnostic (`make_figures.py`, `make_figures2.py`).
- **No generator anywhere in the tree:** fig1 (H₀ whiskers), fig2 (BAO residuals), fig3 (w₀–wₐ contours), fig4 (MCMC corner), **fig6 (Bayes-factor decomposition — a figure whose entire content is quantitative claims)**, fig7 (EDE/Horndeski), fig8 (tension heatmap), fig10 (JWST vs HST hosts), fig11 (forecast), fig12 (neutrino), fig13 (low-z SN).

That is **11 of the 26 figures your own scope box advertises**. For fig6 this is not a hygiene issue: it plots Δχ²_MAP and ln B decompositions, the exact quantities your Round-3 correction just showed can silently go stale. A figure whose numbers cannot be audited is a liability you have already been burned by twice.

**Required:** ship generators for all included figures (or an explicit per-figure provenance table stating which are reproduced from the published literature with references, and which are original), and narrow the Reproducibility Statement to what is actually true.

---

## MINOR OBJECTIONS

- **m1 — Prior-volume bookkeeping is inconsistent between the modelcomp caption and the prose.** The caption honestly discloses V = 2.5 (wCDM) and V = 15 (two-parameter models). Four pages later, "Priors and evidence volumes" declares *"the verification suite adopts V = 15"* with no qualification — contradicting the caption — and the wCDM chain's actual prior w₀ ∈ [−2.0, 0.5] (cosmo.py `bounds()`) is disclosed nowhere, even though it differs from the CPL prior w₀ ∈ [−2.5, 0.5] used in the same table. Two different w₀ priors silently coexist in one evidence table.
- **m2 — The Observational Scope box advertises "1701 Pantheon+ SNe Ia"; your adopted convention uses 1580** (non-calibrators, z_HD > 0.01, per §3.3 and your own robustness table). State "1580 used of 1701" in the box; advertising the larger number is exactly the inflation a referee suspects.
- **m3 — The released verification PNGs embed working-note titles.** fig_gp_wz.png's in-image title reads *"GP reconstruction of w(z) (paper Fig.~13a recreation)"* — a reference to a figure number that does not exist in this monograph. Publication figures do not carry working-session labels.
- **m4 — Orphaned and duplicate assets.** `figs/fig9_cosmic_chronometers_3d_phase.pdf` is never included in the document; eight PNG duplicates of included PDF figures ship unused. Your audit checks the figure *banner* count but not orphaned assets — so the repo can drift indefinitely without a flag.
- **m5 — Audit blind spots are now the dominant defect class.** All five majors above are invisible to `audit_numbers.py`: caption-vs-figure claims (M3), methods-vs-code claims (M4), prose-vs-repo claims (M1), caption invariants (M2), and generator presence (M5). An audit that only re-matches tabulated strings certifies the one thing that was already correct and ignores everything else.
- **m6 — `gp_hz(hyper=(5.318, 1.259))` keeps the superseded values as the released default.** Harmless today because `optimize_hp=True`, but any user calling `gp_hz(optimize_hp=False)` silently reproduces the discredited reconstruction. Change the default to the ML values.

---

## Summary

| # | Severity | One-line statement |
|---|---|---|
| M1 | Major | Paper says the Pantheon+ likelihood was never reproduced; the repo reproduces it and the paper quotes the result three sections earlier |
| M2 | Major | tab:robustness caption's "invariant" is falsified by its own JBP/Log rows; the parametrization-dependence of the crossing *direction* is never discussed |
| M3 | Major | VII-D caption claims a z_c ≈ 0.5 median crossing; the figure's own recipe crosses at z ≈ 0.14 |
| M4 | Major | "30-start Nelder–Mead" exists in the text, not in the code |
| M5 | Major | 11/26 figures have no released generator under a "complete source" claim |
| m1–m6 | Minor | Prior-volume prose contradiction; 1701-vs-1580 scope box; working-note figure titles; orphaned assets; audit blind spots; stale GP defaults |

The tabulated numbers are now clean — your audit did its job. What remains is the layer above the numbers: captions that describe figures they don't match, methods that describe code that wasn't released, and a robustness table whose caption contradicts its own contents. Fix the layer, not the strings.
