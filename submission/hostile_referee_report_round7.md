# Hostile Referee Report — Round 7

**Scope:** audit of the Round-6 fixes (Mirage artifact, bibliography corrections, registry enforcement), conducted with the same policy as Rounds 3–6: every number traced to a released artifact, every sentence checked for attribution drift introduced by the fixes themselves.

**Verdict: MINOR REVISION.** The Round-6 response is substantively correct: the Mirage evidence is now computed from released chains (`verification/mirage_sd.json`, 4 new chains, R̂ ≤ 1.001), the fabricated bibliographic authorships are fixed against arXiv, and the audit (179 checks) passes. However, the Mirage insertion left **five consistency defects** in its wake — two of them claims that were *true before Round 6 and are false after it*.

## Majors

**M1. "All Savage–Dickey values quoted in this monograph derive from this single canonical computation" (Part VII-A, semantics paragraph) is now FALSE.**
Before Round 6 this sentence was true. After Round 6 the manuscript quotes two additional Savage–Dickey values (Mirage +3.49/+3.64) that are computed from a *different* set of chains with a *different* prior volume (V = 3.0), archived in `mirage_sd.json`, not `savage_dickey_canonical.json`. As written, the sentence contradicts the table footnote introduced in the same round.

**M2. The CPL Occam penalty D_KL ≈ 4.06 is labeled "our chain-level estimate … for the supernova-inclusive datasets" — wrong dataset.**
The decomposition values used to derive 4.06 (Δ⟨lnL⟩ = +6.66; lnB = +2.60) are computed on the DESI DR2 + CMB chains (χ²_min 23.59 / 8.36 — no SN term; the SN-inclusive χ²_min would be ≈1413/1400). The label must be corrected, and the text should state the useful consequence: the Mirage D_KL = 2.13 is computed on the *same* DESI DR2 + CMB chains, so the halving comparison is apples-to-apples.

## Minors

**m1. The Mirage posterior constraints are never quoted.** The manuscript now reports Mirage evidence and Δχ² but not the Mirage posterior itself; the reader cannot see that w_0(Mirage, + Pantheon+) = −0.83 ± 0.05 is statistically identical to the CPL value −0.838 ± 0.055 — which is precisely the expected behavior of a model whose second direction is unconstrained, and is worth stating.

**m2. `tab:modelcomp_verification` has no Mirage row** even though every input (χ²_min, DIC, lnB_SD) is now released. The verification table should carry the Mirage row like every other ansatz, with its prior volume stated in the caption and the "Priors and evidence volumes" paragraph.

**m3. Part VII-B "three robust conclusions" paragraph predates the Mirage row** and says the improvement is "concentrated in the correlated (w0, wa) direction, exactly as the mirage-axis analysis of Part V predicts" — with the Mirage chain now released, this can and should be quantified (−12.4 of −15.3 captured by one parameter).

**m4. The Mirage lnB uncertainties (±0.23, ±0.94) have no stated provenance in the manuscript** (they are half-chain scatter; documented only in the JSON method note). One clause in the table footnote suffices.

**Response:** all five addressed in the fixing commit; audit extended 179 → 189 checks.
