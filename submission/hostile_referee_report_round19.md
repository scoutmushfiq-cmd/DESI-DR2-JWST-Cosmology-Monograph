# Round 19 — Hostile Referee Report (reproducibility drill)

**Scope:** every released generator that can be re-run without re-downloading
external data was executed from a clean state against the committed inputs, and
its output compared to the committed artifacts. This is the audit a referee
would demand before the code is released alongside the manuscript.

## Findings

### M1 — `patch_fig7.py` is not idempotent (FIXED)
Re-running `python patch_fig7.py` on the already-patched committed figure
crashes with `AssertionError: marker (146.99, 69.25) color drifted:
(1.0, 1.0, 1.0)`: the pre-patch assertion at step 1 expects the superseded
Sound-Horizon-Free marker at (146.99, 69.25), but on the patched figure that
position is covered by the white patch rectangle (fill (1,1,1)). The script
fails *before* `saveIncr()`, so the committed figure is never corrupted — but a
reproducer following the README hits a hard, misleading crash instead of a
clean skip. **Fix:** an idempotency guard (step 0) now detects the patched
state (no stale `± 65` / `0.092` text, SHF-colored marker within 0.05 of
(146.36, 68.19)) and exits 0 with an explicit "already patched; nothing to do"
message. Verified: re-run exits 0 and the figure MD5 is unchanged
(`f8c6061b568ef76ce6ab2558426724c9`).

### Verified-clean (all reproduce exactly)

| Generator | Result |
| --- | --- |
| `make_fig1_fig8.py` | All 36 unchanged heatmap cells assert-reproduce; regenerated fig1/fig8 are **text-identical** to the committed PDFs (byte-level MD5 differs only through the PDF `CreationDate` stamp — content, vector paths, and all 1213/1270 extracted text characters identical) |
| `patch_fig7.py` (after M1 fix) | Idempotent skip, exit 0, figure byte-unchanged |
| `rhat_new_chains.py` | `rhat_new_chains.json` **byte-identical** to the committed artifact; max split-R̂ = 1.00371 (tex quotes 1.0037) |
| `h0rd_check.py` | `h0rd_check.json` **byte-identical**; `10027 \pm 45` (err_quadrature 44.8, err_montecarlo 44.9) |
| Chain inventory | 39 `chains/*.npy` files, 97 MB on disk — matches the §12 / cover-letter / audit claims |

## Verdict

The released pipeline is deterministic at the artifact level: every JSON
artifact checked regenerates byte-identically, both flagship figures regenerate
content-identically, and the one non-idempotent patch script is fixed. No
remaining reproducibility blocker.
