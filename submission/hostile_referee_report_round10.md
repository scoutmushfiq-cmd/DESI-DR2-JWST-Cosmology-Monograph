# Hostile Referee Report — Round 10

**Manuscript:** cosmology_monograph_full.tex (63 pp, post-Round-9, commit `9b777a6`)
**Verdict: MAJOR REVISION** — external verification of the newly added DES-Y5 likelihood against the actual public release exposes a dataset mislabeling that propagates through the table, the validation section, the abstract, and the Round-9 reconciliation sentence, which is factually wrong.

## Major findings

| # | Finding | Evidence | Severity |
| --- | --- | --- | --- |
| M1 | **The 1820-SN released distance file is not DES-SN5YR — it is DES-Dovekie.** The DES-SN5YR Hubble diagram comprises 1829 SNe (1635 DES SNe over 0.10 < z < 1.13 + 194 external low-z SNe over 0.025 < z < 0.10; DES Collaboration 2024, arXiv:2401.02929). The public distance release that ships with the official likelihood script (`DES-Dovekie_HD.csv`, 1820 rows; `STAT+SYS.npz`, nsn = 1820) is the **DES-Dovekie reanalysis** (Popovic et al. 2025, arXiv:2511.07517; MNRAS 548, stag632): a recalibrated sample with 1623 DES SNe (9 fewer) and 197 low-z SNe (3 more). The manuscript, table, READMEs, and fig6 legend all label our 1820-SN likelihood "DES-Y5" | Release repo file inventory; arXiv:2401.02929 abstract; arXiv:2511.07517 ("DES-SN5YR contained 1829 SNe total, compared to our 1820 SNe ... our low-redshift sample has 3 additional events ... and our DES sample has 9 fewer") | Major |
| M2 | **The Round-9 reconciliation sentence is factually wrong and the DES-Y5 Δχ² explanation is misattributed.** Part III claimed "the 1829-SN count refers to the upstream sample before the distance-release cuts" — false: 1829 is the DES-SN5YR analysis sample itself. Consequently the Part VII-B explanation of our Δχ²_MAP = −17.1 vs the published −21.0 ("compressed-CMB pattern ... opposite direction") is wrong: the dominant cause is that we evaluate the Dovekie 1820-SN recalibrated sample, not the SN5YR 1829-SN BEAMS analysis. The correct comparison is dramatic: our CPL MAP (w0, wa) = (−0.802, −0.749) versus the published **Dovekie** posterior (−0.803 ± 0.054, −0.72 ± 0.21) — agreement to 0.02σ/0.14σ, far stronger than the quoted ~1σ SN5YR comparison — and Dovekie's own published significance reduction (4.2σ → 3.2σ) independently corroborates that the recalibrated sample yields a smaller Δχ² than SN5YR | arXiv:2511.07517 abstract; `sn_extra_results.json` | Major |
| M3 | **Wrong redshift range for the DES-Y5 low-z subsample.** Part III states "194 external low-z SNe Ia spanning 0.025 < z < 1.13"; the low-z subsample spans 0.025 < z < 0.10 (the DES component spans 0.10 < z < 1.13) | arXiv:2401.02929 | Major |
| m1 | `verification/sn5yr/README.md` cites "Vincent et al. 2024" for the release; the SN5YR cosmology paper is DES Collaboration 2024 (arXiv:2401.02929) and the distance file is the Dovekie reanalysis (Popovic et al., arXiv:2511.07517) | README | Minor |
| m2 | fig6 Mirage "DES-Y5" bar is computed on the Dovekie release; the caption must say so | fig6 caption | Minor |
| m3 | `literature_claims.json` (`sn_extra_likelihood_validation`) validates against the SN5YR published posterior instead of the correct Dovekie posterior | registry | Minor |

## Fixes applied (researcher mode)

- M1/M2: Part III rewritten — DES-SN5YR (1829 SNe) and DES-Dovekie (1820-SN recalibrated reanalysis, Popovic et al. 2025, arXiv:2511.07517) now distinguished explicitly; our pipeline evaluates the released Dovekie file exactly as the official script does. Part VII-B validation now leads with the Dovekie posterior comparison (0.02σ/0.14σ agreement) and attributes the Δχ² difference to the sample difference, citing Dovekie's own 4.2σ → 3.2σ reduction; the wrong Round-9 sentence is deleted. Table ‡ row relabeled "DESI DR2 + CMB + DES-Dovekie"; caption updated. Abstract and Part VIII wording updated ("with DES-Y5 via its public DES-Dovekie distance release").
- M3: low-z range corrected to 0.025 < z < 0.10 (DES component 0.10 < z < 1.13).
- m1: sn5yr README citations corrected. m2: fig6 caption note added. m3: registry claim updated with the Dovekie comparison and a new artifact-backed value set.
- `audit_numbers.py` extended 291 → 310 checks (Dovekie/SN5YR distinction present, wrong sentence absent, low-z range, Dovekie posterior agreement, relabeled table row, README citations); all 310 pass.
