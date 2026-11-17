# Hostile Referee Report — Round 16

**Scope:** audit of the Round-15 fix pass, with external verification of the DESI DR2 transcriptions against the published record (arXiv:2503.14738, v3 = Phys. Rev. D 112, 083515, 2025).

**Verdict: MINOR REVISION.** The Round-15 caption and validation-paragraph fixes are correct and artifact-backed; three minor issues remain.

---

## Findings

### m1 — the audit does not enforce the tex-quoted scatter numbers

The Round-15 audit section checks `sd_chain_scatter.json` against hardcoded values (pairs_std 0.513, singles_std 0.900, range 2.08–3.36) but never checks that the tex actually quotes these derived numbers. If the tex sentence were edited or lost, the audit would stay green while the manuscript silently dropped the Round-15 M3 fix. Fixed: the audit now enforces the tex fragments ("standard deviation $0.90$", "standard deviation $0.51$", "mean $2.54$", the ranges +1.78 to +3.90 and +2.08 to +3.36).

### m2 — "every subset" overstates the coverage

The Round-15 tex sentence says "recomputing the CPL value from every subset of the four released ... chains" — but only the four single chains and six two-chain subsets were computed (10 of 15 non-empty subsets; the four triples were omitted as redundant with their complements). Reworded to state the exact coverage.

### m3 — the intro summary presents the published 68.17 ± 0.28 without attribution

The foundational-results paragraph reads "DESI DR2 BAO combined with Planck CMB yields H0 = 68.17 ± 0.28 (Ωm = 0.3027 ± 0.0036)" — indistinguishable from a claim that our pipeline yields this value, while our committed chain gives 68.35 ± 0.33 (the Round-15 M1/M2 point, now clarified in Part VII-B and in the table caption, but not in the intro summary). Fixed: an explicit parenthetical attributes the 68.17/0.3027 pair to the official DESI DR2 values and points to our chain values and Part VII-B.

## External verification (published record)

- arXiv:2503.14738 abstract (v3): the dynamical-DE preference is 3.1σ for DESI BAO + CMB and 2.8–4.2σ with SNe — matching the monograph's transcribed 2.8σ (Pantheon+), 3.8σ (Union3), 4.2σ (DES-Y5), and the 3.1σ DESI+CMB row.
- The monograph's headline DESI DR2 transcriptions (ΛCDM DESI+CMB H0 = 68.17 ± 0.28, Ωm = 0.3027 ± 0.0036; w0wa w0 = −0.42 ± 0.21, wa = −1.75 ± 0.58) match the published DESI DR2 values as widely quoted; the second w0wa pair used in the compressed-baseline context (−0.43 ± 0.22, −1.72 ± 0.64) agrees with the full-CamSpec pair to < 0.1σ in every parameter as the tex states. The two pairs correspond to DESI's two CMB treatments (compressed baseline vs full-CamSpec cross-check), consistent with the monograph's Part VII-B account.
- Σmν < 0.064 eV (ΛCDM) / < 0.16 eV (w0wa) 95% limits in the abstract match the monograph's neutrino section.

## Verified-clean in this pass

- The Round-15 scatter numbers in the tex match `sd_chain_scatter.json` exactly (recomputed: singles 1.7841/3.8980/2.7435/2.3084, std 0.900; pairs 2.0766–3.3552, std 0.513, mean 2.544; all-chain 2.6005).
- The rewritten table caption and Part VII-B paragraph contain no residual "agree exactly" or "compressed-chain posteriors" attributions; the audit enforces both.
- fig13 idempotency and gridline assertions hold on the committed PDF.
