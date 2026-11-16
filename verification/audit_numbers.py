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

print("checks run:", checks)
if fails:
    print("FAILURES (%d):" % len(fails))
    for f in fails: print(" -", f)
    sys.exit(1)
print("ALL CHECKS PASS")
