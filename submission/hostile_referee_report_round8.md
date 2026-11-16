# Hostile Referee Report — Round 8

**Manuscript:** The Architecture of the Cosmos: Model-Independent Constraints on the Hubble Constant and Dark Energy from DESI DR2, Pantheon+, and JWST
**Referee stance:** Adversarial. No sweetness. The manuscript's internal text has survived seven rounds; this round I audited **the rest of the submission package** — the README a reader lands on, the cover letter an editor reads first, the pre-drafted referee responses the authors will send with the revision, and the exact wording of the verification-table caption. That is where the manuscript now bleeds.

**Verdict: MAJOR REVISION.**

The LaTeX source is now largely clean — I verified the code listing is still verbatim-consistent with `cosmo.py` (0 missing lines), the σ-range strings match, and there is no abstract-environment gap. But the *package* that would be uploaded to Nature contradicts the paper it accompanies. You shipped a referee-response template that quotes a value **your own Round-5 process removed from the manuscript as unverifiable**, and a cover letter that quotes a phantom-crossing redshift **your own Round-3 process retracted as irreproducible**. If I were handling this at Nature and opened the supplementary template before the PDF, I would desk-reject on credibility alone: the authors' own canned answers contain numbers their own errata superseded. That is not a typo class; that is a package-consistency failure, and it is systemic — because your 189-check audit guards the tex and *only* the tex.

---

## MAJOR 1 — README still advertises the retracted z_c = 0.42 ± 0.09

`README.md`, Overview bullet 2:

> "...crossing the phantom divide $w = -1$ at $z_c = 0.42 \pm 0.09$."

Round 3 established that 0.42 ± 0.09 was derived nowhere, and Round 3's fix replaced it with the dataset-specific Monte-Carlo propagation: **z_c = 0.50 ± 0.08 (DESI DR2 + CMB)** and **0.35 ± 0.11 (DESI DR2 + CMB + Pantheon+)**, archived in `verification/zc_derivation.json`. Every one of the ten tex occurrences was corrected. The README was not. The first thing any visitor — or any journal editor who follows the repository link in the cover letter — reads is a number the manuscript itself declares superseded.

The systemic cause is worse than the symptom: `audit_numbers.py` checks `"0.42 \pm 0.09" not in tex` but never opens the README bullets. Your audit guards the artifact you keep editing, not the artifacts you forgot you shipped.

## MAJOR 2 — The pre-drafted referee responses quote values the manuscript retracted as fabricated

`submission/referee_response_template.md`, "Pre-drafted responses," Comment on Δχ²_MAP vs Bayesian evidence:

> "D_KL ≈ 4.5–5.2 (Part VII, Table 7) ... restores positive evidence (ln B = +1.85)."

Both numbers were **removed from the manuscript by your own process**: the D_KL ≈ 4.5–5.2 range was retracted in Round 5 as not locatable in Lodha et al., and ln B = +1.85 was retracted in Round 6 as having no artifact backing (absent from every released chain and script). The manuscript now says D_KL = 4.06 (CPL, own chain-level decomposition) and Mirage ln B = +3.49 ± 0.23 / +3.64 ± 0.94 (own Savage–Dickey artifact, `mirage_sd.json`). The template — a document **designed to be pasted into a journal response** — still argues from the retracted numbers. A referee who cross-reads the template against Part VII would conclude the authors' own responses do not believe their own errata.

Same file, the phantom-crossing Q&A:

> "Is the phantom crossing (z_c ≈ 0.42) an artifact ...? ... z_c = −(1+w₀)/(1+w₀+wₐ) = 0.42 ± 0.09"

Stale in both the question and the answer. The correct, manuscript-consistent answer quotes 0.50 ± 0.08 (DESI+CMB) / 0.35 ± 0.11 (+Pantheon+) from the posterior propagation of Eq. (zc_derivation).

## MAJOR 3 — Cover letter quotes the retracted z_c

`submission/cover_letter.md`:

> "...with a phantom divide crossing at z_c = 0.42 ± 0.09"

This is the **first technical number the Nature editor reads**, and it is the one value in the entire project with an explicit retraction trail in three referee reports. The cover letter was updated for page count in Rounds 6–7 but its physics content was never audited.

## MAJOR 4 — The verification-table caption misdescribes the Mirage row it was extended to cover

`tab:modelcomp_verification` caption (Round 7 added a Mirage row but did not re-derive the caption's methodology claims against the Mirage pipeline). Three statements are now false for that row:

1. **"χ²_min, Δχ²_MAP ... come from bounded multi-start L-BFGS-B optimization"** — the Mirage MAP (`chi2_MAP_opt` in `mirage_sd.json`) comes from multi-start **Powell** (`map_opt()` in `run_mirage_sd.py`), not L-BFGS-B. The caption asserts a specific optimizer that was not used for one of the six rows.
2. **"DIC is computed from 4,000 posterior draws"** — the Mirage DIC used **12,000** draws (thin factor 16 over 96,000 retained samples per chain). The other five rows use 4,000; the caption states one number for a column that has two.
3. **"Silverman's gives identical values to the quoted precision"** — for Mirage, Scott gives +3.49 and Silverman +3.46 (`lnB_SD_scott` / `lnB_SD_silverman`): a 0.03 difference, visible at the quoted 2-decimal precision. The caption's claim is falsified by the artifact added one caption ago.

## Minor 1 — README reproduction paragraph: stale page count and chain size

`README.md`: "**58 pages, zero errors**" (the compiled PDF is 62 pages — your own page-count sync updated the "(62 Pages)" banner but missed this second, differently-formatted occurrence) and "~59 MB" of chains (actual: ~68 MB after the four Round-6 Mirage chains).

## Minor 2 — Mirage ESS values are a cutoff artifact, not measurements

`mirage_sd.json` reports ESS = 192,000 **exactly, for every parameter, in both datasets**. That is because `ess()` returns the full sample count when lag-1 autocorrelation falls below the 0.05 cutoff — i.e. the value means "autocorrelation below detection," not an estimated effective sample size. The tex does not quote these ESS numbers, so nothing false is printed; but the artifact ships a value that a referee will read as 192,000 independent draws. Annotate the method note before anyone cites it.

## Verified non-issues (so the response can be short)

- `lst:python_pipeline` remains verbatim-consistent with `cosmo.py` (0 missing lines).
- README "4.52σ–5.72σ" matches the tex tension matrix.
- No abstract environment exists; the executive-summary bullets serve that role by design.

---

## Required actions

1. README bullet 2: replace the retracted z_c with the dataset-specific values, matching the tex.
2. `referee_response_template.md`: rewrite the Δχ²/evidence and phantom-crossing answers with the current artifact-backed numbers (D_KL 4.06 CPL / 2.13–2.40 Mirage; ln B +3.49 ± 0.23 / +3.64 ± 0.94; z_c 0.50 ± 0.08 / 0.35 ± 0.11).
3. `cover_letter.md`: same z_c correction.
4. `tab:modelcomp_verification` caption: state the Mirage row's actual optimizer (Powell), its 12,000-draw DIC, and the 0.03 Scott–Silverman difference quoted as part of the uncertainty.
5. README reproduction paragraph: 62 pages; ~68 MB.
6. `mirage_sd.json`: annotate the ESS cutoff semantics in the method note.
7. **Systemic fix:** extend `audit_numbers.py` to scan the README bullets, the referee-response template, and the cover letter for every superseded value the tex checks already cover. An audit that only guards one file is how M1–M3 happened.
