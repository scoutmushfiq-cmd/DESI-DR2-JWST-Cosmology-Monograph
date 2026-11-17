# Hostile Referee Report — Round 18

**Scope:** manuscript-internal cross-reference integrity and headline-value consistency (label/ref graph, duplicate labels, stale-value grep, abstract-vs-body value agreement).

**Verdict: MINOR REVISION.** No stale values anywhere (the Round-14–17 cleanups held); one systemic presentation defect found.

---

## Findings

### M1 — the two headline figures are never referenced in the running text

`fig:hubble_whisker` (fig1, the H0 forest comparison) and `fig:tension_heatmap` (fig8, the tension heatmap) — the manuscript's two flagship figures — carry captions and labels but no `\ref` anywhere in the body text; the reader is never pointed to them. The convergence table (`tab:convergence`) is likewise orphaned. Fixed: textual references added at their natural anchors (the Part V forest lead-in, the tension-matrix introduction, and the seed-stability paragraph); the audit now enforces a full label/ref integrity check (unresolved `\ref` targets — accounting for the listings `label={...}` form — duplicate labels, and mandatory references for the three floats).

### m2 — ~15 further floats/labels are never `\ref`-ed

The unreferenced set includes schematic book illustrations (`fig:cosmic_timeline_1_1`, `fig:roadmap_11_1`, …) and numbered display equations (equations need no reference). The schematics are acceptable in a monograph (each sits inside the section that discusses its content), but this is recorded here as a known presentational choice rather than silently ignored; the three scientifically load-bearing floats are fixed in M1.

## Verified-clean in this pass

- Label/ref graph: 88 `\label` + 1 listings label, 95 `\ref`, ZERO unresolved references in the compiled PDF (no "??" on any of the 66 pages).
- No duplicate labels.
- Stale-value grep: `69.24`, `69.21`, `69.25`, `0.0188`, `0.0175`, `82.20`, `6.80` — all absent; `10027 ± 45` is the live, artifact-backed H0r_d product (h0rd_check.json), not a stale value.
- Headline values consistent across abstract/intro/body: 68.17 ± 0.28 (×10), 4.52σ (×7), 5.43σ/6.27σ/6.04σ, z_c 0.35 ± 0.11 / 0.50 ± 0.08, 68.19 ± 1.45, 146.36 ± 2.88, 81–99.6%.
