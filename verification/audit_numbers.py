"""Automated number audit: cross-checks quoted values in the manuscript
against the machine-readable verification artifacts, and reconciles
repository metadata (page count, figure count, chain count) with the
actual build. Run from verification/ after every manuscript edit:

    python audit_numbers.py
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VER = os.path.join(ROOT, "verification")
TEX = os.path.join(ROOT, "cosmology_monograph_full.tex")
PDF = os.path.join(ROOT, "The_Architecture_of_the_Cosmos_Monograph_Md_Mushfiqur_Rahim.pdf")

fails, checks = [], 0

def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        fails.append(msg)

tex = open(TEX, encoding="utf-8").read()

# 1. Model-comparison table vs model_comparison.json
mc = json.load(open(os.path.join(VER, "model_comparison.json")))
def _tex_num(pattern_fmt, value, tol=0.006):
    mm = re.search(pattern_fmt, tex)
    return mm is not None and abs(float(mm.group(1)) - value) <= tol

for model, pat in [("LCDM", r"\\Lambda\$CDM & ([0-9.]+) & 2"),
                   ("wCDM", r"wCDM & ([0-9.]+) & 3"),
                   ("CPL", r"CDM \(CPL\) & \\textbf\{([0-9.]+)\} & 4"),
                   ("JBP", r"JBP & ([0-9.]+) & 4"),
                   ("Log", r"Logarithmic & ([0-9.]+) & 4")]:
    check(_tex_num(pat, mc[model]["chi2_min"]),
          "chi2_min for %s (%.3f) not matched in tex" % (model, mc[model]["chi2_min"]))
for model, val in [("wCDM", mc["wCDM"]["lnB_SDX"]), ("CPL", mc["CPL"]["lnB_SDX"]),
                   ("JBP", mc["JBP"]["lnB_SDX"]), ("Log", mc["Log"]["lnB_SDX"])]:
    sign = "+" if val >= 0 else ""
    check(("$%s%.2f$" % (sign, val)) in tex,
          "lnB_SD for %s (%s%.2f) not found in tex" % (model, sign, val))

# 2. Savage-Dickey canonical vs both quoting sites
sd = json.load(open(os.path.join(VER, "savage_dickey_canonical.json")))
v15 = round(sd["cpl"]["V15_scott"], 2)
check(("$%+.2f$" % v15) in tex, "canonical SD lnB %.2f missing in tex" % v15)

# 3. z_c values vs zc_derivation.json
zc = json.load(open(os.path.join(VER, "zc_derivation.json")))
for key in ["desi_cmb_cpl", "desi_cmb_pantheon_cpl"]:
    med, st = zc[key]["median"], zc[key]["std"]
    mm = re.search(r"z_c = ([0-9.]+) \\pm ([0-9.]+)", tex)
    found = False
    for mm in re.finditer(r"z_c = ([0-9.]+) \\pm ([0-9.]+)", tex):
        if abs(float(mm.group(1)) - med) < 0.02 and abs(float(mm.group(2)) - st) < 0.02:
            found = True; break
    check(found, "z_c %s (%.3f +- %.3f) not matched in tex" % (key, med, st))
check("0.42 \\pm 0.09" not in tex, "superseded z_c = 0.42 +- 0.09 still present in tex")

# 4. Delta-lnL decomposition values
dl = json.load(open(os.path.join(VER, "dlnL_decomposition.json")))
for m in ["wcdm", "cpl", "jbp", "log"]:
    v = round(dl[m]["dlnL_trim_vs_lcdm"], 2)
    check(("%+.2f" % v) in tex, "dlnL trimmed value %s (%+.2f) missing in tex" % (m, v))

# 5. Figure count claim vs actual includegraphics targets
figs = set(re.findall(r"\\includegraphics\[[^\]]*\]\{([^}]*)\}", tex))
m = re.search(r"(\d+) Vector Figures", tex)
check(m is not None and int(m.group(1)) == len(figs),
      "figure-count banner (%s) != unique includegraphics (%d)" % (m.group(1) if m else "?", len(figs)))

# 6. Chain count claim vs verification/chains
nch = len([f for f in os.listdir(os.path.join(VER, "chains")) if f.endswith(".npy")])
readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
m = re.search(r"All (\d+) posterior chains", readme)
check(m is not None and int(m.group(1)) == nch,
      "README chain count (%s) != actual (%d)" % (m.group(1) if m else "?", nch))

# 7. Page count claim vs compiled PDF
if os.path.exists(PDF):
    try:
        from pypdf import PdfReader
        npages = len(PdfReader(PDF).pages)
        for pat in [r"Research Monograph \((\d+) Pages\)", r"\((\d+) Pages\)"]:
            mm = re.search(pat, readme)
            if mm:
                check(int(mm.group(1)) == npages,
                      "README page count (%s) != PDF pages (%d)" % (mm.group(1), npages))
                break
        mm = re.search(r"(\d+)-page research monograph", open(os.path.join(ROOT, "submission/cover_letter.md"), encoding="utf-8").read())
        check(mm is not None and int(mm.group(1)) == npages,
              "cover-letter page count (%s) != PDF pages (%d)" % (mm.group(1) if mm else "?", npages))
        zen = open(os.path.join(ROOT, ".zenodo.json"), encoding="utf-8").read()
        mm = re.search(r"A (\d+)-page comprehensive", zen)
        check(mm is not None and int(mm.group(1)) == npages,
              ".zenodo.json page count (%s) != PDF pages (%d)" % (mm.group(1) if mm else "?", npages))
    except ImportError:
        print("pypdf unavailable; page-count checks skipped")

# 8. GP hyperparameter search: artifact + released reference in tex
try:
    gs = json.load(open(os.path.join(VER, "gp_hyperparameter_search.json")))
    check(gs["n_starts"] == 30, "gp search n_starts != 30")
    check(gs["n_converged_to_best"] == 30, "gp search: not all 30 starts converged to best")
    check(abs(gs["best"]["sf"] - 305.09) < 0.5 and abs(gs["best"]["lf"] - 3.885) < 0.01,
          "gp search best != (305.09, 3.885)")
    check("gp\\_hyperparameter\\_search.py" in tex, "tex does not reference released gp_hyperparameter_search.py")
except FileNotFoundError:
    check(False, "gp_hyperparameter_search.json missing")

# 9. H-route crossing: artifact + corrected caption claim, stale claim absent
try:
    gc = json.load(open(os.path.join(VER, "gp_route_crossing.json")))
    check("0.38 \\pm 0.49" in tex, "tex missing per-draw H-route crossing 0.38 +- 0.49")
    check("z_c \\approx 0.14" in tex, "tex missing H-route median crossing z_c ~ 0.14")
    check("crosses the phantom divide (dashed) at $z_c \\approx 0.5$" not in tex,
          "stale VII-D claim (median crossing at z_c ~ 0.5) still present")
    check(abs(gc["per_draw_cross_median"] - 0.381) < 0.02,
          "gp_route_crossing.json median drift")
except FileNotFoundError:
    check(False, "gp_route_crossing.json missing")

# 10. Stale Round-4 claims absent
check("is not reproduced in the verification suite" not in tex,
      "stale 'Pantheon+ not reproduced' claim still present")
check("every two-parameter ansatz prefers $w(z) > -1$ today" not in tex,
      "stale tab:robustness invariant still present")

# 11. Verification figure scripts carry no working-note titles
for scr in ["make_figures.py", "make_figures2.py"]:
    s = open(os.path.join(VER, scr), encoding="utf-8").read()
    check("paper Fig." not in s and "paper $" not in s,
          "%s still contains working-note title" % scr)

# 12. cosmo.py gp_hz default = ML hyperparameters (m6)
cs = open(os.path.join(VER, "cosmo.py"), encoding="utf-8").read()
check("hyper=(305.10, 3.885)" in cs, "cosmo.py gp_hz default is not the ML hyperparameters")
check("(5.318, 1.259)" not in cs, "cosmo.py still contains superseded default (5.318, 1.259)")

# 13. figure_provenance.md covers every includegraphics target
prov_path = os.path.join(VER, "figure_provenance.md")
check(os.path.exists(prov_path), "figure_provenance.md missing")
if os.path.exists(prov_path):
    prov = open(prov_path, encoding="utf-8").read()
    for target in sorted(figs):
        base = os.path.basename(target)
        check(base in prov, "figure_provenance.md missing entry for %s" % target)

# 15. Literature-claims registry (Round-5 M4/m5): coverage + tex presence
try:
    lc = json.load(open(os.path.join(VER, "literature_claims.json")))
    claims = lc["claims"]
    check(len(claims) >= 15, "literature_claims.json has fewer than 15 registered claims")
    for c in claims:
        check(c.get("verification_status") in ("verified", "own-pipeline", "partial"),
              "claim %s has invalid verification_status" % c.get("id"))
        check(bool(c.get("source")) and bool(c.get("locator")),
              "claim %s missing source or locator" % c.get("id"))
    # verified external numbers that must appear in the tex
    for frag in ["0.126 \\pm 0.021", "72.34 \\pm 0.72", "-0.132", "69.61 \\pm 0.44",
                 "10.5\\text{--}20.7", "0.090", "71.96", "Phys.\\ Rev.\\ D 71, 023515",
                 "2505.08051", "2507.12401", "JCAP01(2026)041", "111, 123511"]:
        check(frag in tex, "tex missing verified literature value %r" % frag)
    # superseded / unverifiable numbers must be gone
    for frag in ["69.10", "-0.036 \\pm 0.014", "10027 \\pm 65", "139.70 \\pm 1.45",
                 "71.85", "alpha_{M,0} = -0.18", "1.09 \\pm 0.05",
                 "4.5\\text{--}5.2", "Universal Distance Modes Collaboration",
                 "quoted by Lodha et al."]:
        check(frag not in tex, "tex still contains superseded value %r" % frag)
    # citation hygiene: no mirror or personal-page links
    check("alphaxiv" not in tex, "tex still links to alphaxiv mirror")
    check("umich.edu" not in tex, "tex still links to umich personal page")
    check("Zaldarriaga (2026)" in tex.replace("M.\\ Zaldarriaga (2026)", "Zaldarriaga (2026)"),
          "tex missing Zaldarriaga (2026) author citation")
except FileNotFoundError:
    check(False, "literature_claims.json missing")

# 14. No orphaned figure assets: every figs/ file is referenced by the tex
figdir = os.path.join(ROOT, "figs")
if os.path.isdir(figdir):
    for f in os.listdir(figdir):
        check(f in tex, "orphaned asset figs/%s not referenced in tex" % f)

print("checks run:", checks)
if fails:
    print("FAILURES (%d):" % len(fails))
    for f in fails: print(" -", f)
    sys.exit(1)
print("ALL CHECKS PASS")
