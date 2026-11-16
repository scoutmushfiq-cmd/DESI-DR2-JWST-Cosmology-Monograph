# Hostile Referee Report — Round 6

**Manuscript:** *The Architecture of the Cosmos: Model-Independent Constraints on the Hubble Constant and Dark Energy from DESI DR2, Pantheon+, and JWST* (60-page build, commit 4314c35)
**Referee stance:** Reviewer 2. No sugar. I read the diff of your Round-5 fix, then I audited the fix itself. This is what happens when you patch symptoms instead of running a systematic pass.

## Recommendation: MAJOR REVISION

Round 5 fixed the EDE/IDE/Horndeski numbers correctly — those edits are now source-verified and I have no complaint about them. But the same audit exposed that the fix was applied with a spotlight, not a floodlight. You corrected **one** invented author name ("Universal Distance Modes Collaboration" → Zaldarriaga) and left **four more** of the exact same defect class sitting in the very next lines of the same bibliography. Worse, you "resolved" the unverifiable Mirage Bayes factors by re-attributing them from Lodha et al. to *your own chains* — and your own released chains contain **no Mirage computation at all**. That is not a fix. That is laundering an unverifiable number through the phrase "our Savage–Dickey estimates."

---

## Major findings

### M1 — The Mirage lnB "own estimates" have no artifact behind them. You invented provenance.
Part VIII, the Highlights, Part X, and Table `tab:model_comparison_full` now state that Mirage lnB = +1.85/+4.60/+6.65 (±0.32) are "our Savage–Dickey estimates on the released chains," and that the Occam penalty is "roughly halved relative to CPL in our chain-level decomposition (ΔD_KL ≈ 2.6 versus ≈ 5.1)." I checked the released tree:

- `verification/savage_dickey_canonical.json` — keys: `wcdm, cpl, jbp, log, zc`. **No Mirage.**
- `verification/dlnL_decomposition.json` — keys: `lcdm, wcdm, cpl, jbp, log`. **No Mirage.**
- No script in `verification/` computes a Mirage likelihood, a Mirage chain, or a Mirage Δ⟨lnL⟩. There are no Mirage chains in `verification/chains/`.

So the Round-5 text replaced "quoted by Lodha et al." (unverifiable) with "our estimates" (nonexistent). The ±0.32 error bars are equally orphaned. And the footnote's "(prior volumes as in Table tab:modelcomp_verification)" is meaningless for a 1-parameter model whose prior volume you never defined. **Either** implement the Mirage axis (w_a = −3.66(1+w₀)), run the chains, compute the Savage–Dickey ratios, and release the artifact — **or** delete the Mirage lnB column entries, the ±0.32, and the "halved Occam penalty" claims from Highlights, Part VIII, Part X, and the table. A paper that lectures referees about evidence decomposition (Part VII-B) does not get to assert decompositions it never computed.

### M2 — Four more invented bibliography author names, one corrected and four ignored.
The Round-5 fix established the correct standard: real authors, real titles. You applied it to exactly one entry. Still in the bibliography:

| TeX entry (as written) | Reality (verified on arXiv) |
| --- | --- |
| "Critical Review Collaboration (2025)", title *"Is Dark Energy Dynamical in the DESI Era? A Critical Review of BAO, CMB, and Low-Redshift Supernova Systematics"* | **S. Capozziello, H. Chaudhary, T. Harko, G. Mustafa (2025/2026)**, actual title: *"Is Dark Energy Dynamical in the DESI Era? A Critical Review"* (arXiv:2512.10585; the subtitle in your bibliography is embellished — it does not exist) |
| "Sound-Horizon-Free $H_0$ Collaboration (2026)", *"Insights from a Diverse Set of Sound-Horizon-Free $H_0$ Measurements"* | **I. Pantos & L. Perivolaropoulos (2026)**, actual title: *"Dissecting the Hubble tension: Insights from a diverse set of Sound Horizon-free H0 measurements"* (arXiv:2601.00650) |
| "Sound-Horizon-Free BAO Collaboration (2026)", *"A sound-horizon-free measurement of the Hubble constant from DESI DR2"* | Single-author paper (G. N., arXiv:2604.24050), actual title ends *"...using artificial neural networks"* — your title is truncated mid-sentence; published in PRD (DOI 10.1103/29rq-lgby) |
| "DESI DR2 Ly$\alpha$ Forest Dark Energy Analysis (2025)", *"Evidence for Dynamical Dark Energy Using DESI DR2 Ly$\alpha$ Forest BAO"* | **S. Capozziello, H. Chaudhary, G. Mustafa, S. K. J. Pacif**, actual title: *"Evidence of dynamical dark energy found via the DESI DR2 Lymanα forest"* (arXiv:2510.21976; published A&A 2026) |

Also: "Y. Wang & K. Freese (2025)" — real authors, but the actual title is *"Model-Independent Dark Energy Measurements from DESI DR2 **and Planck 2015 Data**"* (arXiv:2505.17415; published JCAP02(2026)023), and you cite the v4 HTML URL. Six entries in a 31-entry bibliography with fabricated or truncated metadata is not a rounding error; it is a pattern. A Nature referee will run the same script I did. Fix every entry or do not call the section "References and **Verified** Primary Sources."

### M3 — Your own verification registry contradicts the manuscript it certifies.
`verification/literature_claims.json` marks `lodha_mirage_zc` — the claim that the direct f_DE reconstruction "peaks at f_DE^max ≈ 1.09" — as **"verified"**. It is not. Your accessible-source verification located the *redshift* of the maximum (z_c ≈ 0.45); the *value* 1.09 was never located in any accessible Lodha text, which is precisely why you stripped its ±0.05 everywhere else. The glossary and fig5 caption still assert 1.09 as an attributed fact. A registry whose verification_status field lies is worse than no registry: it converts an honest gap into a false certificate. Downgrade that entry to `partial` (z_c verified, peak value not independently located) and soften the two remaining "≈ 1.09" assertions to match, or locate the number in the published PRD tables.

### M4 — The algebraic-thawing row: you flagged it, then shipped it anyway.
The registry honestly says `partial`: "source document only partially accessible; exact entry transcribed from the cited tables." So the manuscript knowingly prints Δχ² = −2.9/−13.2, ΔAIC, and ΔDIC for the algebraic thawing class that nobody has verified against the published PRD tables — in a table whose caption tells the reader everything else is from Lodha et al. You cannot have it both ways: a "partial" flag in a JSON file does not sanitize a printed number. The PRD version (10.1103/w4c6-1r5j) is accessible to any reader with a subscription; verify the row against it or cut it. Same for the new footnote's claim that the Mirage ΔAIC/ΔDIC/Δ⟨lnL⟩ entries are "transcribed from Lodha et al." — you verified the Δχ² range (10.5–20.7) and nothing else in those rows. The footnote asserts more than your evidence.

### M5 — The Mirage table rows and the "1 extra degree of freedom" claim are now load-bearing without support.
Round-5 made Mirage *more* central, not less: the Highlights bullet, Part VIII item 2, and Part X all route the "Frequentist vs. Bayesian paradox resolution" through Mirage lnB values that M1 shows are uncomputed. If M1 is resolved by deletion, the headline claim "Bayesian evidence decomposition resolves the Frequentist vs. Bayesian paradox **via Mirage Dark Energy**" collapses to a CPL-only statement with an inconclusive Pantheon+ result — which is a far weaker (and honest) paper. Decide which paper you are writing.

---

## Minor findings

- **m1.** Cataneo & Koyama is dated "Phys. Rev. D (2025)" in the bibliography; the PRD publication (DOI 10.1103/ckns-5ytv) is 2026 (v2 revised July 2026). Fix the year.
- **m2.** arXiv:2604.24050 bibliography entry lacks its PRD DOI (10.1103/29rq-lgby) and truncates the title (see M2).
- **m3.** Part IX cites `universe-origins.dk/sloth/?p=714` — a group webpage — as a source for TDCOSMO numerical results. Cite the paper; drop the group page.
- **m4.** The in-text Lyα entry is dated "(2025)" while the published version is A&A 2026; harmonize.
- **m5.** The audit's absence-list is string-based and its presence-list for Mirage ("own-pipeline") values checks only that the *tex* contains 1.85/4.60/6.65 — not that any *artifact* does. The audit therefore certifies M1's laundering as "ALL CHECKS PASS." Add artifact-presence checks for every registry entry marked `own-pipeline`.
- **m6.** The H₀r_d = 10027 ± 45 quadrature derivation lives only as prose in VERIFICATION_REPORT §18; it is not reproducible from any committed script or JSON. One ten-line script or a JSON field would close this.
- **m7.** Part VIII Horndeski bullet: "Several recent analyses report that the DESI phantom-crossing preference has been argued to point toward..." — a double-hedged sentence that attributes an attribution. Say who argues what, once.
- **m8.** `literature_claims.json` `lodha_thawing_dchi2_table` gives a `note` but the manuscript table caption gives the reader no corresponding signal for that row (the footnote covers Mirage only).

## What I do not complain about

For the record, since you will accuse me of only attacking: the Silva IDE numbers, the Poulin EDE numbers, the Zaldarriaga/Chebat/Vikman citations, the H₀r_d re-derivation arithmetic (68.17×147.09 = 10026.7; σ = 44.9), the q₀ baseline labeling, the CPL qualifiers, the scope-box fix, and the 138-check audit expansion are all correct and properly sourced now. Parts I–VII and the neutrino block of Part IX remain in acceptable shape. The problem is concentrated where it has been since Round 1: Part VIII's beyond-ΛCDM section and the bibliography's back rows.

## Verdict table

| ID | Severity | One-line summary |
| --- | --- | --- |
| M1 | Major | Mirage lnB "own estimates" backed by zero artifacts — provenance invented |
| M2 | Major | Four more fabricated bibliography author names + two truncated titles |
| M3 | Major | Registry marks an unverified value (f_DE^max = 1.09) as "verified" |
| M4 | Major | "Partial"-flagged thawing numbers printed without reader-facing caveat |
| M5 | Major | Headline Mirage claim becomes load-bearing on unsupported numbers |
| m1–m8 | Minor | Year errors, missing DOIs, group-page citation, audit blind spot, unreproducible ±45 |

**Accept only after:** Mirage is either computed-and-released or excised end-to-end; every bibliography entry passes an author/title check against arXiv; the registry's status field matches reality; and the audit gains artifact-presence checks for all own-pipeline claims.
