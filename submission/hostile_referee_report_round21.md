# Round 21 — Hostile Referee Report (provenance cross-check of figure-anchor numbers)

**Scope:** every place the manuscript or a released artifact anchors a derived
number to a *source* was cross-checked against the committed chains and the
attribution rules established in Rounds 15–17. This is the misattribution
class that has now been caught three times; this round asks whether any
instance survived.

## Findings

### M1 — The fig7 hyperbola is attributed to "our chain" but uses the official DESI value (NOT YET FIXED)
`cosmology_monograph_full.tex` L1059 (fig7 caption) states the
$H_0 r_d \approx 10027 \pm 45$ gray hyperbola is *"computed from our joint
DESI DR2 + CMB chain, $H_0 = 68.17 \pm 0.28$ km/s/Mpc"*. This is false
provenance, twice over:

1. The committed chain `chains/chain_lcdm_desi_cmb.npy` gives
   **$H_0 = 68.35 \pm 0.33$** (established in Round 15 and stated in the
   manuscript's own Part VII-B). The value used, $68.17 \pm 0.28$, is the
   **official published DESI DR2** determination.
2. The manuscript therefore contradicts *itself*: Part VII-B explicitly says
   "our committed compressed-CMB chains give $H_0 = 68.35 \pm 0.33$", while the
   fig7 caption says "our joint DESI DR2 + CMB chain" gives 68.17 ± 0.28. A
   referee reading both catches this in one pass.

The same false provenance is baked into the artifact layer:
`verification/h0rd_check.py` docstring ("our joint DESI DR2 + CMB LambdaCDM
chain") and the `h0rd_check.json` `H0.source` field ("joint DESI DR2 + CMB
LambdaCDM chain (verification/chains/chain_lcdm_desi_cmb*.npy)") — the JSON
names the chain files as the source of a number those files do not produce.

*Required fix:* caption → "computed from the official DESI DR2 + CMB
$\Lambda$CDM determination ($H_0 = 68.17 \pm 0.28$; DESI Collaboration 2025a)"
(the hyperbola itself is unchanged — it is a legitimate anchor on the published
value); `h0rd_check.py` docstring and the JSON `source` field corrected to cite
the published determination; the artifact regenerated so the released metadata
is honest.

### m1 — The audit never checks the fig7 caption's attribution (audit gap that allowed M1)
`audit_numbers.py` §19 verifies the hyperbola *values* (10027.1 / 44.8) but
nothing enforces *what the caption claims about provenance*. Add a check that
the tex no longer contains "our joint DESI DR2 + CMB chain" and that
`h0rd_check.json`'s source fields cite the published determination, so this
class cannot regress a fourth time.

### m2 — TLS verification disabled in a released download script
`verification/download_sn_extra_data.py` sets
`ssl.CERT_NONE` / `check_hostname = False` for its urllib fetches of the Union3
and DES-Dovekie releases. For a script shipped in the public reproduction
package this is a supply-chain hygiene defect: any intervening network can
substitute the SN data silently, and the pipeline would never notice. Use the
default verified context (with a documented fallback note if a specific host
chain was the reason this was added). Relatedly, the README reproduce paragraph
does not mention that the Pantheon+ files (`pantheon/sn_data.dat`,
`sn_cov.cov`) must be fetched manually per `verification/pantheon/README.md`
before `run_mcmc_all.py` — the reproduce path silently assumes them.

## Verified-clean

- **References section** (Part: "References and Verified Primary Sources"):
  73 enumerated entries; every arXiv ID cited in the running text
  (2503.14738, 2503.14743, 2608.01215, 2408.06153, 2408.03474, 2408.11770,
  2112.04510, 2202.04077, 2112.03863, 1807.06209, 2503.23225, 2505.08051,
  2608.27566, 2512.10585, …) has a corresponding full entry.
- The abstract's "$H_0 = 68.17 \pm 0.28$" bullet correctly attributes it to
  "DESI DR2 BAO + Planck CMB" (published result, no chain claim).
- Cover letter, README, `.zenodo.json`, and `figure_provenance.md` contain no
  10027/hyperbola provenance claim (nothing to fix there).
- `figure_provenance.md` row 20 ("every pre-patch geometry asserted,
  idempotent") is now accurate post-Round-19.

## Verdict

**MINOR REVISION** — one provenance misattribution (M1, same class as Rounds
15–17, third recurrence: the sweep missed the figure-caption layer), one audit
gap (m1), one hygiene defect (m2). All are mechanical fixes; no scientific
result changes.
