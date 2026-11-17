"""Automated number audit: cross-checks quoted values in the manuscript
against the machine-readable verification artifacts, and reconciles
repository metadata (page count, figure count, chain count) with the
actual build. Run from verification/ after every manuscript edit:

    python audit_numbers.py
"""
import json, os, re, subprocess, sys
import numpy as np

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
                 "16.2\\text{--}20.7", "0.090", "71.96", "Phys.\\ Rev.\\ D 71, 023515",
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

# 16. Round-6 M1: Mirage evidence must be artifact-backed by mirage_sd.json
msd_path = os.path.join(VER, "mirage_sd.json")
check(os.path.exists(msd_path), "mirage_sd.json missing")
if os.path.exists(msd_path):
    msd = json.load(open(msd_path))
    for key, frag in [("mirage_desi_cmb", "+3.49 \\pm 0.23"),
                      ("mirage_desi_cmb_pantheon", "+3.64 \\pm 0.94")]:
        v = msd[key]["lnB_SD_scott"]
        check(frag in tex, "Mirage lnB string %r missing in tex" % frag)
        check(abs(round(v, 2) - float(frag.split("+")[1].split(" ")[0])) < 0.006,
              "mirage_sd.json lnB %s (%.3f) inconsistent with tex string %r" % (key, v, frag))
    for key, frag in [("mirage_desi_cmb", "+5.62"),
                      ("mirage_desi_cmb_pantheon", "+6.03")]:
        v = round(msd[key]["dlnL_trim_vs_lcdm"], 2)
        check(("%+.2f" % v) in tex, "Mirage dlnL %s (%+.2f) missing in tex" % (key, v))
    for key in ["mirage_desi_cmb", "mirage_desi_cmb_pantheon"]:
        check(msd[key]["D_KL"] < 3.0,
              "Mirage D_KL %s not below 3 (Occam-halving claim)" % key)
# unverifiable Mirage values must be gone
for frag in ["+1.85", "+4.60", "+6.65", "+4.45", "+7.20", "+9.25",
             "3.2}\\boldsymbol{\\sigma}$ & $-8.5"]:
    check(frag not in tex, "tex still contains unverifiable Mirage value %r" % frag)

# 17. Round-6 M3: f_DE^max peak value must not be quoted anywhere
for frag in ["f_{\\rm DE}^{\\max} \\approx 1.09", "f_{\\rm DE} \\approx 1.09"]:
    check(frag not in tex, "tex still quotes unverifiable f_DE peak value (%r)" % frag)

# 18. Round-6 M2/m1/m2/m4: bibliography authorship and link hygiene
for frag in ["Sound-Horizon-Free BAO Collaboration", "Critical Review Collaboration",
             "Sound-Horizon-Free $H_0$ Collaboration",
             "Evidence for Dynamical Dark Energy Using DESI DR2",
             "universe-origins", "arxiv.org/html/2512.10585", "arxiv.org/html/2510.21976"]:
    check(frag not in tex, "tex still contains fabricated/unverified reference %r" % frag)
for frag in ["Gadbail", "Pantos", "Capozziello, H.\\ Chaudhary",
             "Wang \\& K.\\ Freese (2026)", "Cataneo \\& K.\\ Koyama (2026)"]:
    check(frag in tex, "tex missing corrected reference author %r" % frag)

# 19. Round-6 m5/m6: registry artifacts exist on disk; h0rd product artifact
for c in claims:
    if c.get("verification_status") == "own-pipeline":
        art = c.get("artifact")
        check(bool(art), "own-pipeline claim %s missing artifact field" % c["id"])
        if art:
            check(os.path.exists(os.path.join(ROOT, art)),
                  "own-pipeline artifact missing: %s" % art)
hrd_path = os.path.join(VER, "h0rd_check.json")
check(os.path.exists(hrd_path), "h0rd_check.json missing")
if os.path.exists(hrd_path):
    hrd = json.load(open(hrd_path))
    check("10027" in tex and "45" in tex,
          "tex missing H0*rd = 10027 +/- 45 string")
    check(abs(hrd["H0_rd"] - 10027.1) < 0.1 and abs(hrd["err_quadrature"] - 44.8) < 0.1,
          "h0rd_check.json values inconsistent with derivation")

# 20. Round-7: Mirage row in the verification table + provenance sentences
check("Mirage ($w_a = -3.66(1+w_0)$) & 11.24 & 3 & $-12.39" in tex,
      "tab:modelcomp_verification missing Mirage row (11.24/3/-12.39)")
check("17.24 & 19.36 & 17.19" in tex,
      "tab:modelcomp_verification Mirage AIC/BIC/DIC cells missing")
if os.path.exists(msd_path):
    mo = msd["mirage_desi_cmb"]["chi2_MAP_opt"]
    check(abs(round(mo, 2) - 11.24) < 0.006,
          "Mirage chi2_MAP_opt (%.3f) inconsistent with table value 11.24" % mo)
    w0m = msd["mirage_desi_cmb"]["summary"]["w0"]
    check(("-0.70 \\pm 0.11") in tex and
          abs(round(w0m["mean"], 2) + 0.70) < 0.006 and
          abs(round(w0m["std"], 2) - 0.11) < 0.006,
          "Mirage w0 (DESI+CMB) quote inconsistent with mirage_sd.json")
    w0p = msd["mirage_desi_cmb_pantheon"]["summary"]["w0"]
    check(("-0.83 \\pm 0.05") in tex and
          abs(round(w0p["mean"], 2) + 0.83) < 0.006 and
          abs(round(w0p["std"], 2) - 0.05) < 0.006,
          "Mirage w0 (Pantheon+) quote inconsistent with mirage_sd.json")
check("$V = 3.0$ (Mirage)" in tex, "tab:modelcomp_verification caption missing Mirage prior volume")
check("half-chain scatter" in tex, "Mirage lnB uncertainty provenance missing in tex")
check("for the supernova-inclusive datasets" not in tex,
      "Round-7 M2: D_KL 4.06 still labeled 'supernova-inclusive datasets'")
check("All Savage--Dickey values quoted in this monograph derive from this single canonical computation" not in tex,
      "Round-7 M1: false 'single canonical computation' claim still present")
check("identical estimator (Scott-rule Gaussian KDE evaluated at the nested point) applied to the dedicated Mirage chains" in tex,
      "Round-7 M1 fix sentence missing")

# 21. Round-8: package consistency — README bullets, referee-response template,
# and cover letter must carry the same artifact-backed numbers as the tex.
check("0.42 \\pm 0.09" not in readme,
      "Round-8 M1: README still quotes superseded z_c = 0.42 +- 0.09")
check("0.50 \\pm 0.08" in readme and "0.35 \\pm 0.11" in readme,
      "README missing dataset-specific z_c values (0.50 +- 0.08 / 0.35 +- 0.11)")
check("58 pages" not in readme, "Round-8 m1: README still claims 58 pages")
check("66 pages" in readme, "README missing the 66-page compile claim")
check("~59 MB" not in readme and "~92 MB" not in readme,
      "README still claims a stale chain size (~59 MB / ~92 MB)")
check("~97 MB" in readme, "README missing the ~97 MB chain-size claim")
TPL = os.path.join(ROOT, "submission", "referee_response_template.md")
check(os.path.exists(TPL), "referee_response_template.md missing")
if os.path.exists(TPL):
    tpl = open(TPL, encoding="utf-8").read()
    for frag in ["4.5\u20135.2", "4.5--5.2", "+1.85", "0.42 \u00b1 0.09", "z_c \u2248 0.42"]:
        check(frag not in tpl,
              "Round-8 M2: referee template still contains retracted value %r" % frag)
    for frag in ["D_KL = 4.06", "ln B = +3.49 \u00b1 0.23", "+3.64 \u00b1 0.94",
                 "D_KL = 2.13", "2.40", "0.50 \u00b1 0.08", "0.35 \u00b1 0.11"]:
        check(frag in tpl, "referee template missing artifact-backed value %r" % frag)
CL = os.path.join(ROOT, "submission", "cover_letter.md")
check(os.path.exists(CL), "cover_letter.md missing")
if os.path.exists(CL):
    cl = open(CL, encoding="utf-8").read()
    check("0.42 \u00b1 0.09" not in cl,
          "Round-8 M3: cover letter still quotes superseded z_c = 0.42 +- 0.09")
    check("0.35 \u00b1 0.11" in cl and "0.50 \u00b1 0.08" in cl,
          "cover letter missing dataset-specific z_c values")
# Round-8 M4: verification-table caption must describe the Mirage row's actual methodology
check("12{,}000 for the Mirage row" in tex,
      "caption missing Mirage 12,000-draw DIC provenance")
check("Powell for the Mirage row" in tex,
      "caption missing Powell optimizer attribution for the Mirage row")
check("differs by 0.03 for Mirage" in tex,
      "caption missing the Scott-Silverman 0.03 Mirage difference")
check("bounded multi-start L-BFGS-B optimization" not in tex,
      "caption still claims L-BFGS-B for all rows")
check("Silverman's gives identical values to the quoted precision" not in tex,
      "caption still claims identical Silverman values for all rows")
if os.path.exists(msd_path):
    check("ESS_note" in msd.get("method", {}),
          "Round-8 m2: mirage_sd.json missing ESS cutoff-annotation method note")

# 22. Union3 / DES-Y5 Mirage rows vs sn_extra_results.json and nested_lnB.json
snx_path = os.path.join(VER, "sn_extra_results.json")
nested_path = os.path.join(VER, "nested_lnB.json")
if os.path.exists(snx_path):
    snx = json.load(open(snx_path))
    # table cells for the dagger-dagger rows
    for ds, cells in [
        ("union3", ["-19.3", "4.4", "-17.3", "-17.4", "+9.17", "+6.74 \\pm 0.03"]),
        ("desy5", ["-17.0", "4.1", "-15.0", "-15.2", "+8.03", "+5.04 \\pm 0.19"]),
    ]:
        for cell in cells:
            check(cell in tex, "Mirage %s row missing table cell %s" % (ds, cell))
    # numeric agreement between tex cells and the artifact
    u = snx["mirage_union3"]; d5 = snx["mirage_desy5"]
    check(abs(u["dchi2_MAP_opt_vs_lcdm"] + 19.3) < 0.06, "union3 dchi2_MAP_opt mismatch vs tex -19.3")
    check(abs(d5["dchi2_MAP_opt_vs_lcdm"] + 17.0) < 0.06, "desy5 dchi2_MAP_opt mismatch vs tex -17.0")
    check(abs(u["dAIC_vs_lcdm"] + 17.3) < 0.06, "union3 dAIC mismatch vs tex -17.3")
    check(abs(d5["dAIC_vs_lcdm"] + 15.0) < 0.06, "desy5 dAIC mismatch vs tex -15.0")
    check(abs(u["dDIC_vs_lcdm"] + 17.4) < 0.06, "union3 dDIC mismatch vs tex -17.4")
    check(abs(d5["dDIC_vs_lcdm"] + 15.2) < 0.06, "desy5 dDIC mismatch vs tex -15.2")
    check(abs(u["dlnL_trim_vs_lcdm"] - 9.17) < 0.006, "union3 dlnL mismatch vs tex +9.17")
    check(abs(d5["dlnL_trim_vs_lcdm"] - 8.03) < 0.006, "desy5 dlnL mismatch vs tex +8.03")
    check(abs(u["lnB_SD_scott"] - 8.71) < 0.006 and abs(u["lnB_SD_err_halfchain"] - 3.03) < 0.006,
          "union3 Savage-Dickey cross-check mismatch vs tex +8.71 +/- 3.03")
    check(abs(d5["lnB_SD_scott"] - 5.21) < 0.006 and abs(d5["lnB_SD_err_halfchain"] - 1.93) < 0.006,
          "desy5 Savage-Dickey cross-check mismatch vs tex +5.21 +/- 1.93")
    # validation-paragraph numbers (own CPL MAP and published comparison)
    check(abs(u["cpl_chi2_MAP_opt"] - u["lcdm_chi2_MAP_opt"] + 20.6) < 0.06,
          "union3 own CPL MAP dchi2 mismatch vs tex -20.6")
    check(abs(d5["cpl_chi2_MAP_opt"] - d5["lcdm_chi2_MAP_opt"] + 17.1) < 0.06,
          "desy5 own CPL MAP dchi2 mismatch vs tex -17.1")
    check("(-0.665, -1.093)" in tex and "(-0.802, -0.749)" in tex,
          "Part VII-B missing own CPL MAP parameters for Union3/DES-Y5")
    check("(-0.752 \\pm 0.057, -0.86)" in tex, "Part VII-B missing published DES-Y5 CPL posterior")
    check("94\\%" in tex and "99.6\\%" in tex, "mirage recovery percentages missing")
if os.path.exists(nested_path):
    ns = json.load(open(nested_path))["summary"]
    for key, cell, err in [("mirage_desi_cmb", "+3.65 \\pm 0.35", 0.35),
                           ("mirage_sn", "+3.40 \\pm 0.35", 0.35),
                           ("mirage_union3", "+6.74 \\pm 0.03", 0.03),
                           ("mirage_desy5", "+5.04 \\pm 0.19", 0.19),
                           ("cpl_desi_cmb", "+2.78 \\pm 0.42", 0.42)]:
        check(cell in tex, "nested-sampling value %s missing from tex" % key)
        v = ns[key]["lnB"]
        quoted = float(re.search(r"([+-][0-9.]+)", cell).group(1))
        check(abs(v - quoted) < 0.006, "nested lnB for %s (%.3f) disagrees with quoted %s" % (key, v, cell))
        if err is not None:
            check(abs(ns[key]["err"] - err) < 0.006, "nested err for %s (%.3f) disagrees with quoted %s" % (key, ns[key]["err"], cell))
    check("Nested-sampling cross-check of the Mirage Bayes factors" in tex,
          "Part VII-B missing the nested-sampling cross-check paragraph")
    check("Official Union3 and DES-Dovekie likelihood validation" in tex,
          "Part VII-B missing the official-likelihood validation paragraph")
    check("verification/nested\\_lnB.json" in tex, "tex missing nested_lnB.json artifact pointer")
# absence of the superseded no-evidence sentences
check("deliberately quote no Mirage evidence" not in tex,
      "superseded 'deliberately quote no Mirage evidence' sentence still present")
check("we quote no Mirage evidence" not in tex,
      "superseded 'we quote no Mirage evidence' sentence still present")
check("whose supernova likelihoods our pipeline does not re-implement" not in tex,
      "superseded 'does not re-implement' caption sentence still present")
check("$^{\\ddagger}$" in tex, "dagger-dagger marker missing from the table rows")
# README package metadata: chain count and new artifacts
chain_files = [f for f in os.listdir(os.path.join(VER, "chains")) if f.endswith(".npy")]
check(len(chain_files) == 39, "expected 39 chain files, found %d" % len(chain_files))
check("All 39 posterior chains" in readme, "README chain count not updated to 39")
check("All 27 posterior chains" not in readme and "All 37 posterior chains" not in readme,
      "README still quotes a stale chain count")
for art in ["sn_extra.py", "nested_lnB.py", "sn_extra_results.json", "nested_lnB.json", "download_sn_extra_data.py"]:
    check(art in readme, "README missing new artifact %s" % art)
for f in ["submission/referee_response_template.md", "submission/cover_letter.md"]:
    body = open(os.path.join(ROOT, f), encoding="utf-8").read()
    check("+6.74" in body and "+5.04" in body if f.endswith("referee_response_template.md") else True,
          "%s missing the Union3/DES-Y5 Mirage evidence values" % f)

# 23. Round-9 fixes: fig6 regeneration, 1820 reconciliation, abstract Mirage evidence, new-chain R-hat
check(os.path.exists(os.path.join(VER, "make_fig6_model_comparison.py")),
      "fig6 generator script missing")
check("regenerated" in open(os.path.join(VER, "figure_provenance.md"), encoding="utf-8").read(),
      "figure_provenance.md fig6 entry not updated to regenerated")
check("hatched Mirage bars are computed" in tex and "in this work (Table" in tex,
      "fig:bayes_comparison caption missing the hatched this-work note")
check("both contain exactly these 1820 SNe" in tex,
      "Part III missing the 1820-vs-1829 sample reconciliation (Dovekie wording)")
check("22 binned distance moduli of the official release" in tex and "(1+z_{\\rm HEL})" in tex,
      "Part III missing the Union3/DES-Y5 operational likelihood spec")
check("computes its own Mirage-axis evidence for all four dataset combinations" in tex,
      "abstract missing the own-pipeline Mirage evidence sentence")
check("recovering $81\\text{--}99.6\\%$ of the CPL" in tex,
      "abstract missing the Mirage CPL-recovery range")
check("with a maximum of $1.0037$ across all parameter--chain combinations" in tex,
      "Part VII-B missing the split-R-hat statement (max 1.0037)")
check("two seeds for Mirage, one each for the others" in tex,
      "Part VII-B missing the corrected per-model seed counts")

# 24. Round-10 fixes: DES-Dovekie identification (the released 1820-SN file is the
# recalibrated reanalysis of DES-SN5YR, Popovic et al. 2025, arXiv:2511.07517,
# NOT the 1829-SN DES-SN5YR analysis sample), corrected low-z redshift range,
# Dovekie-posterior validation, and relabeled table/README rows.
n_dovekie = tex.count("DES-Dovekie")
check(n_dovekie >= 8, "tex mentions DES-Dovekie only %d times (expected >= 8)" % n_dovekie)
check("Popovic et al." in tex and "2511.07517" in tex,
      "tex missing the Dovekie citation (Popovic et al. 2025, arXiv:2511.07517)")
check("refers to the upstream sample before the distance-release cuts" not in tex,
      "superseded Round-9 rationalization sentence still present in tex")
check("0.025 < z < 0.10" in tex, "tex missing the corrected low-z redshift range 0.025 < z < 0.10")
check("0.025 < z < 1.13" not in tex, "tex still quotes the wrong low-z range 0.025 < z < 1.13")
check("(-0.803 \\pm 0.054, -0.72 \\pm 0.21)" in tex,
      "tex missing the published Dovekie posterior (-0.803 +/- 0.054, -0.72 +/- 0.21)")
check("0.02\\sigma" in tex and "0.14\\sigma" in tex,
      "tex missing the 0.02-sigma / 0.14-sigma Dovekie agreement statement")
check("from $4.2\\sigma$ to $3.2\\sigma$" in tex,
      "tex missing the Dovekie significance-reduction corroboration (4.2 to 3.2 sigma)")
check("DESI DR2 + CMB + \\textbf{DES-Dovekie}" in tex,
      "verification table dagger-dagger row not relabeled to DES-Dovekie")
check("not the 1829-SN DES-SN5YR analysis sample" in tex,
      "table caption missing the Dovekie-vs-SN5YR distinction")
check("via its public DES-Dovekie distance release" in tex,
      "abstract missing the Dovekie distance-release wording")
check("recalibrated 1820-SN reanalysis of DES-SN5YR" in tex,
      "tex missing the recalibrated-reanalysis description")
sn5yr_readme = open(os.path.join(VER, "sn5yr", "README.md"), encoding="utf-8").read()
check("2511.07517" in sn5yr_readme and "Popovic" in sn5yr_readme,
      "sn5yr README missing the Dovekie citation (Popovic et al. 2025, arXiv:2511.07517)")
check("2401.02929" in sn5yr_readme and "DES Collaboration 2024" in sn5yr_readme,
      "sn5yr README missing the DES-SN5YR citation (DES Collaboration 2024, arXiv:2401.02929)")
check("Vincent et al. 2024" not in sn5yr_readme,
      "sn5yr README still cites the nonexistent 'Vincent et al. 2024'")
check("DES-Dovekie" in readme and "DESI+CMB+DES-Dovekie Mirage" in readme,
      "README missing the Dovekie clarification / relabeled Mirage row")
lit = json.load(open(os.path.join(VER, "literature_claims.json")))
_slv = [c for c in lit["claims"] if c["id"] == "sn_extra_likelihood_validation"]
check(len(_slv) == 1, "literature_claims missing sn_extra_likelihood_validation entry")
if _slv:
    _blob = json.dumps(_slv[0])
    check("-0.803" in _blob and "0.054" in _blob and "2511.07517" in _blob,
          "sn_extra_likelihood_validation claim missing the Dovekie posterior / citation")
    check("sample itself" in _blob,
          "sn_extra_likelihood_validation claim missing the sample-difference explanation")

# 25. Round-11 fixes: fig5 annotation (retracted z_c = 0.42 removed), nested lnB
# seed structure (2 seeds per CPL configuration, 4 for Mirage-Union3), split-R-hat
# artifact for the eight new chains, own-chain MCMC Pipeline rows (no undefined
# Q_CMB symbol), and the corrected sn_joint chi2 fields.
_rhat_path = os.path.join(VER, "rhat_new_chains.json")
check(os.path.exists(_rhat_path), "rhat_new_chains.json missing")
if os.path.exists(_rhat_path):
    _rh = json.load(open(_rhat_path))
    check(len([k for k in _rh["chains"] if k.endswith(".npy")]) == 12,
          "rhat_new_chains.json has %d chain entries, expected 12" % len([k for k in _rh["chains"] if k.endswith(".npy")]))
    check(_rh["max_rhat"] <= 1.005, "rhat_new_chains max_rhat %.5f exceeds 1.005" % _rh["max_rhat"])
    check(abs(_rh["max_rhat"] - 1.0037) < 0.0006,
          "rhat_new_chains max_rhat %.5f disagrees with quoted 1.0037" % _rh["max_rhat"])
check("z_c = 0.42" not in tex and "z_c \\approx 0.42" not in tex,
      "retracted z_c = 0.42 still present in tex")
_fig5 = os.path.join(ROOT, "figs", "fig5_gp_wz_reconstruction.pdf")
check(os.path.exists(_fig5), "fig5_gp_wz_reconstruction.pdf missing")
if os.path.exists(_fig5):
    try:
        import pymupdf
        _t5 = pymupdf.open(_fig5)[0].get_text()
        check("0.42" not in _t5, "fig5 still annotates the retracted z_c ~ 0.42")
        check("0.16" in _t5, "fig5 missing the z ~ 0.16 peak annotation")
    except Exception as _e:
        check(False, "fig5 PDF text extraction failed: %s" % _e)
check("Q_{\\rm CMB}" not in tex, "undefined symbol Q_CMB still present in tex")
check("$(\\theta_*,\\omega_b,\\omega_{\\rm bc})_{\\rm CMB}$ + Pantheon+" in tex,
      "MCMC Pipeline Base row missing the defined CMB compression notation")
_sj_path = os.path.join(VER, "sn_joint_results.json")
check(os.path.exists(_sj_path), "sn_joint_results.json missing")
if os.path.exists(_sj_path):
    _sj = json.load(open(_sj_path))["pantheon_joint"]
    check(_sj["lcdm"]["chi2_min"] > 1000, "sn_joint lcdm chi2_min %.3f still corrupted" % _sj["lcdm"]["chi2_min"])
    check(_sj["cpl"]["chi2_min"] > 1000, "sn_joint cpl chi2_min %.3f still corrupted" % _sj["cpl"]["chi2_min"])
    _sdm = json.load(open(os.path.join(VER, "sn_map_dchi2.json")))
    check(abs(_sdm["dchi2_map"] + 13.3) < 0.06, "sn_map_dchi2 dchi2_map disagrees with tex -13.3")
    check("-13.3" in tex, "tex missing the Base-row dchi2 -13.3")
for _frag in ["$0.3112 \\pm 0.0060$", "$67.65 \\pm 0.59$", "$-0.831 \\pm 0.053$",
              "$-0.661 \\pm 0.196$", "$r_d = 147.09$ (fixed)",
              "$0.3107 \\pm 0.0059$", "$67.73 \\pm 0.57$", "$-0.838 \\pm 0.053$",
              "$-0.646 \\pm 0.195$", "$-12.9$ ($3.2\\sigma$)",
              "$0.2992 \\pm 0.0051$", "$69.00 \\pm 0.52$", "$-0.904 \\pm 0.052$",
              "$-0.556 \\pm 0.198$", "$-12.5$ ($3.1\\sigma$)"]:
    check(_frag in tex, "MCMC Pipeline table row fragment missing from tex: %s" % _frag)
_pr_path = os.path.join(VER, "pipeline_rows_results.json")
check(os.path.exists(_pr_path), "pipeline_rows_results.json missing")
if os.path.exists(_pr_path):
    _pr = json.load(open(_pr_path))
    _t = _pr["cpl_pp_cc_trgb"]; _s = _pr["cpl_pp_cc_shoes"]
    check(abs(_t["Om"][0] - 0.3107) < 0.0006 and abs(_t["Om"][1] - 0.0059) < 0.0006,
          "pipeline +TRGB Om disagrees with tex 0.3107 +/- 0.0059")
    check(abs(_t["H0"][0] - 67.73) < 0.006 and abs(_t["H0"][1] - 0.57) < 0.006,
          "pipeline +TRGB H0 disagrees with tex 67.73 +/- 0.57")
    check(abs(_t["w0"][0] + 0.838) < 0.0006 and abs(_t["wa"][0] + 0.646) < 0.0006,
          "pipeline +TRGB (w0, wa) disagrees with tex")
    check(abs(_t["dchi2_MAP"] + 12.9) < 0.06, "pipeline +TRGB dchi2 disagrees with tex -12.9")
    check(abs(_s["Om"][0] - 0.2992) < 0.0006 and abs(_s["Om"][1] - 0.0051) < 0.0006,
          "pipeline +SH0ES Om disagrees with tex 0.2992 +/- 0.0051")
    check(abs(_s["H0"][0] - 69.00) < 0.006 and abs(_s["H0"][1] - 0.52) < 0.006,
          "pipeline +SH0ES H0 disagrees with tex 69.00 +/- 0.52")
    check(abs(_s["w0"][0] + 0.904) < 0.0006 and abs(_s["wa"][0] + 0.556) < 0.0006,
          "pipeline +SH0ES (w0, wa) disagrees with tex")
    check(abs(_s["dchi2_MAP"] + 12.5) < 0.06, "pipeline +SH0ES dchi2 disagrees with tex -12.5")
check("$69.00 \\pm 0.52$ in our unbinned-prior run" in tex,
      "narrative missing the updated unbinned-prior SH0ES-run H0")
check("68.64" not in tex, "superseded +SH0ES row value 68.64 still present in tex")
for _fn, _mean in [("chains/chain_cpl_desy5_s1.npy", None),
                   ("chains/chain_cpl_union3_s1.npy", None)]:
    _p = os.path.join(VER, _fn)
    check(os.path.exists(_p), "own-posterior chain %s missing" % _fn)
if all(os.path.exists(os.path.join(VER, _fn)) for _fn, _ in
       [("chains/chain_cpl_desy5_s1.npy", 0), ("chains/chain_cpl_union3_s1.npy", 0)]):
    _cd = np.load(os.path.join(VER, "chains/chain_cpl_desy5_s1.npy"))
    _cu = np.load(os.path.join(VER, "chains/chain_cpl_union3_s1.npy"))
    check(abs(_cd[:, 2].mean() + 0.798) < 0.006 and abs(_cd[:, 3].mean() + 0.774) < 0.006,
          "Dovekie own-posterior means disagree with tex (-0.798, -0.774)")
    check(abs(_cu[:, 2].mean() + 0.657) < 0.006 and abs(_cu[:, 3].mean() + 1.134) < 0.006,
          "Union3 own-posterior means disagree with tex (-0.657, -1.134)")
check("(-0.798 \\pm 0.055, -0.774 \\pm 0.212, 67.45 \\pm 0.54)" in tex,
      "Part VII-B missing the own Dovekie posterior sentence")
check("(-0.657 \\pm 0.085, -1.134 \\pm 0.278, 65.99 \\pm 0.83)" in tex,
      "Part VII-B missing the own Union3 posterior sentence")
check("seed half-ranges quantify seed-to-seed reproducibility" in tex
      and "$\\approx 0.46$ nats" in tex,
      "Part VII-B missing the sqrt(H/nlive) evidence-uncertainty caveat")
check("a consistency that holds at the $68\\%$-band level" in tex,
      "Executive Summary missing the GP H(z)-route 68%-band caveat")
check("The official DESI DR2 analysis, combining" in tex,
      "abstract bullet 3 missing the official-analysis attribution fix")
check("in the official analyses (our re-implementation chains" in tex,
      "abstract bullet 2 missing the own-chain H0 provenance")
check("$H_0 = 68.81 \\pm 2.22\\text{ km s}^{-1}\\text{ Mpc}^{-1}$, orange" in tex,
      "fig4 caption missing the corrected TRGB prior value 68.81 +/- 2.22")
check("$H_0 = 70.39 \\pm 1.94\\text{ km s}^{-1}\\text{ Mpc}^{-1}$, orange" not in tex,
      "fig4 caption still quotes the wrong 70.39 prior as the TRGB prior")
check(os.path.exists(os.path.join(VER, "make_fig4_corner.py")), "make_fig4_corner.py missing")
check("make_fig4_corner.py" in open(os.path.join(VER, "figure_provenance.md"), encoding="utf-8").read(),
      "figure_provenance.md missing the fig4 released-generator entry")


# 26. Round-12 fixes: per-dof sigma convention (M1), twelve-chain split-R-hat
# claim (M2), artifact-backed Sound-Horizon-Free row and recomputed tension
# row (M3), and package-wide staleness (M4/m1-m4).
check("degrees of freedom equal to the number of added parameters" in tex,
      "Part VII missing the per-dof sigma-convention semantics statement")
for _frag in ["$-13.3$ ($\\mathbf{3.2}\\boldsymbol{\\sigma}$)",
              "$-12.9$ ($3.2\\sigma$)", "$-12.5$ ($3.1\\sigma$)",
              "$-4.7$ ($1.7\\sigma$)"]:
    check(_frag in tex, "Round-12 M1/M3: tex missing significance fragment %s" % _frag)
check("($3.6\\sigma$)" not in tex and "($3.5\\sigma$)" not in tex,
      "Round-12 M1: superseded 3.6/3.5-sigma conversions still present in tex")
check("All twelve new MCMC chains" in tex and "All eight new MCMC chains" not in tex,
      "Round-12 M2: split-R-hat claim not extended to all twelve chains")
_rdf_path = os.path.join(VER, "rdfree_results.json")
check(os.path.exists(_rdf_path), "rdfree_results.json missing")
if os.path.exists(_rdf_path):
    _rdf = json.load(open(_rdf_path))
    _c = _rdf["rdfree_cpl"]
    check(abs(_c["H0"][0] - 68.19) < 0.006 and abs(_c["H0"][1] - 1.45) < 0.006,
          "rdfree CPL H0 disagrees with tex 68.19 +/- 1.45")
    check(abs(_c["Om"][0] - 0.3050) < 0.0006 and abs(_c["Om"][1] - 0.0132) < 0.0006,
          "rdfree CPL Om disagrees with tex 0.3050 +/- 0.0132 (chain-direct, Round 13)")
    check(abs(_c["w0"][0] + 0.891) < 0.0006 and abs(_c["w0"][1] - 0.058) < 0.0006,
          "rdfree CPL w0 disagrees with tex -0.891 +/- 0.058")
    check(abs(_c["wa"][0] + 0.245) < 0.0006 and abs(_c["wa"][1] - 0.357) < 0.0006,
          "rdfree CPL wa disagrees with tex -0.245 +/- 0.357")
    check(abs(_c["rd"][0] - 146.36) < 0.006 and abs(_c["rd"][1] - 2.88) < 0.006,
          "rdfree CPL rd disagrees with tex 146.36 +/- 2.88")
    check(abs(_rdf["dchi2_MAP_cpl_vs_lcdm"] + 4.7) < 0.06,
          "rdfree dchi2_MAP disagrees with tex -4.7")
for _frag in ["$0.3050 \\pm 0.0132$", "$68.19 \\pm 1.45$", "$-0.891 \\pm 0.058$",
              "$-0.245 \\pm 0.357$", "$r_d = 146.36 \\pm 2.88$"]:
    check(_frag in tex, "Round-12 M3: Sound-Horizon-Free row fragment missing from tex: %s" % _frag)
for _stale in ["69.24", "146.99", "0.2929", "$-0.900 \\pm 0.052$", "$-0.042 \\pm 0.454$"]:
    check(_stale not in tex, "Round-12 M3: superseded Sound-Horizon-Free value %r still in tex" % _stale)
check("Sound-Horizon-Free ($r_d$ free)} ($68.19 \\pm 1.45$) & $2.72\\sigma$ & $2.95\\sigma$" in tex,
      "Round-12 M3: tension-matrix Sound-Horizon-Free row not recomputed")
check("($69.24 \\pm 1.82$)" not in tex, "Round-12 M3: old tension-row H0 still present")
check("MCMC Run 2" not in tex, "Round-12 m1: undefined 'MCMC Run 2' still in tex")
check("rdfree\\_results.json" in tex, "Round-12 m2: caption missing the rdfree_results.json pointer")
check("chain\\_rdfree\\_" in tex, "Round-12 m2: caption missing the rdfree chain names")
check(os.path.exists(os.path.join(VER, "make_fig1_fig8.py")), "make_fig1_fig8.py missing")
for _fn in ["fig1_hubble_tension_whisker.pdf", "fig8_tension_heatmap_matrix.pdf"]:
    _fp = os.path.join(ROOT, "figs", _fn)
    check(os.path.exists(_fp), "regenerated figure missing: %s" % _fn)
    if os.path.exists(_fp):
        try:
            import pymupdf as _pm
            _t = _pm.open(_fp)[0].get_text()
            check("68.19" in _t and "69.24" not in _t,
                  "%s still embeds the superseded Sound-Horizon-Free values" % _fn)
        except Exception as _e:
            check(False, "%s text extraction failed: %s" % (_fn, _e))
if os.path.exists(TPL):
    check("+6.74 \u00b1 0.03" in tpl, "Round-12 M4: template missing the corrected +6.74 +/- 0.03")
    check("DES-Dovekie distance release" in tpl, "Round-12 M4: template missing the Dovekie label")
    check("+6.75" not in tpl and "DES-SN5YR likelihoods" not in tpl,
          "Round-12 M4: template still contains stale values")
check("four for Mirage on Union3" in readme, "Round-12 M4: README missing the four-seed Mirage wording")
check("+6.74 \u00b1 0.03" in readme, "Round-12 M4: README missing the corrected +6.74 +/- 0.03")
if os.path.exists(CL):
    check("split-R" in cl and "1.0037" in cl,
          "Round-12 m4: cover letter missing the split-R-hat statement")


# 27. Round-13 fixes: chain-direct Sound-Horizon-Free Omega_m (M1), surgical
# fig7 marker/label patch (M2), two-tier fig8 severity labeling (M3), and the
# five minors (fig13 asymmetric H0pe bar, fig10 unbacked error, fig11 forecast
# caveat, fig1 thick/thin rewording, fig2 reference-model statement).
_r12 = open(os.path.join(VER, "run_round12_fixes.py"), encoding="utf-8").read()
check("Om_draws = (ch[:, 1] + cosmo.W_NU) / (ch[:, 0] / 100.0) ** 2" in _r12,
      "Round-13 M1: run_round12_fixes.py missing the chain-direct Om computation")
check("Om_s = np.sqrt" not in _r12,
      "Round-13 M1: quadrature Om propagation still present in run_round12_fixes.py")
if os.path.exists(_rdf_path):
    _l = _rdf["rdfree_lcdm"]
    check(abs(_l["Om"][0] - 0.3044) < 0.0006 and abs(_l["Om"][1] - 0.0077) < 0.0006,
          "Round-13 M1: rdfree LCDM Om disagrees with chain-direct 0.3044 +/- 0.0077")
check("$0.3050 \\pm 0.0132$" in tex and "0.0188" not in tex,
      "Round-13 M1: tex Sound-Horizon-Free Om not updated to chain-direct 0.3050 +/- 0.0132")
check(os.path.exists(os.path.join(VER, "patch_fig7.py")) and
      os.path.exists(os.path.join(VER, "patch_fig10_fig13.py")) and
      os.path.exists(os.path.join(VER, "fig7_DejaVuSans.ttf")),
      "Round-13 M2: fig7/fig10/fig13 patch scripts or bundled font missing")
_f7 = _pm.open(os.path.join(ROOT, "figs", "fig7_ede_horndeski_degeneracy.pdf"))[0]
_t7 = _f7.get_text()
check("\u00b1 65" not in _t7 and "\u00b1 45" in _t7,
      "Round-13 M2: fig7 hyperbola label not corrected to +/- 45")
check("0.092" not in _t7 and "\u2248 0.09" in _t7,
      "Round-13 M2: fig7 EDE legend not corrected to the backed f_EDE range")
_f8 = _pm.open(os.path.join(ROOT, "figs", "fig8_tension_heatmap_matrix.pdf"))[0]
_t8 = _f8.get_text()
check("MOD." not in _t8 and _t8.count("SEVERE") == 13,
      "Round-13 M3: fig8 severity labels not on the two-tier >=3-sigma scheme")
check("two-tier severity label" in tex and "labeled SEVERE" in tex,
      "Round-13 M3: fig8 caption missing the two-tier labeling description")
check("published means and uncertainties" in tex and "from our pipeline outputs" not in tex,
      "Round-13 M3: fig8 caption still overstates provenance ('our pipeline outputs')")
_f13 = _pm.open(os.path.join(ROOT, "figs", "fig13_non_cepheid_lensing_lowz_sn.pdf"))[0]
_t13 = _f13.get_text()
check("75.40 \u00b1 6.80" not in _t13 and "+8.10" in _t13 and "5.50" in _t13,
      "Round-13 m1: fig13 H0pe label not corrected to the asymmetric interval")
_f10 = _pm.open(os.path.join(ROOT, "figs", "fig10_jwst_vs_hst_host_comparison.pdf"))[0]
_t10 = _f10.get_text()
check("1.85" not in _t10 and "71.20" in _t10,
      "Round-13 m2: fig10 still quotes the unbacked +/- 1.85")
check("75.40^{+8.10}_{-5.50}" in tex and "75.40 \\pm 6.80" not in tex,
      "Round-13 m1: tex still quotes the symmetric H0pe interval")
check("only the two SH0ES rows" in tex,
      "Round-13 m4: fig1 caption still overgeneralizes the 2-sigma bars")
check("\\Omega_m = 0.334" in tex,
      "Round-13 m5: fig2 caption missing the explicit reference model")
check("illustrative projections" in tex,
      "Round-13 m3: fig11 caption missing the illustrative-forecast caveat")

# 14. No orphaned figure assets: every figs/ file is referenced by the tex
figdir = os.path.join(ROOT, "figs")
if os.path.isdir(figdir):
    for f in os.listdir(figdir):
        check(f in tex, "orphaned asset figs/%s not referenced in tex" % f)

# 15. Round-14 fixes: caption-float placement (M1), fig13 gridline redraw (M2),
# stale-orphan and template cleanup (M3), and the m1-m4 provenance disclosures.
_tlines = tex.splitlines()
def _near(anchor, needle, back=0, fwd=4):
    for i, ln in enumerate(_tlines):
        if anchor in ln:
            for j in range(max(0, i - back), min(len(_tlines), i + fwd)):
                if needle in _tlines[j]:
                    return True
    return False
check(_near("fig8_tension_heatmap_matrix.pdf", "two-tier")
      and _near("fig8_tension_heatmap_matrix.pdf", "SEVERE"),
      "Round-14 M1: the two-tier severity labeling is not in the fig8 figure caption itself")
check(not _near("\\label{tab:tension_matrix}", "two-tier", back=3)
      and _near("\\label{tab:tension_matrix}", "set in bold", back=3),
      "Round-14 M1: table caption must use the bold rule, not the two-tier severity labels")
check(not os.path.exists(os.path.join(VER, "rdfree_result.json")),
      "Round-14 M3: stale orphan artifact verification/rdfree_result.json still present")
_tpl = open(os.path.join(ROOT, "submission", "referee_response_template.md"),
            encoding="utf-8").read()
check("68.19" in _tpl and "69.24" not in _tpl and "69.21" not in _tpl,
      "Round-14 M3: referee-response template still validates the superseded r_d-free row")
_prov = open(os.path.join(VER, "figure_provenance.md"), encoding="utf-8").read()
check("patch_fig7.py" in _prov and "patch_fig10_fig13.py" in _prov,
      "Round-14 m3: figure_provenance.md rows do not name the in-place patch scripts")
_readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
check("patch_fig7" in _readme and "patch_fig10_fig13" in _readme
      and "make_fig1_fig8" in _readme,
      "Round-14 m4: README reproduce paragraph does not name the figure patch scripts")
check("V15\\_scott\\_2chains" in tex and "+0.76" in tex,
      "Round-14 m2: tex does not disclose the Savage-Dickey chain-subset systematic")
check("not the transcribed official values" in tex,
      "Round-14 m1: Mirage-recovery sentence still lacks the basis qualifier")
try:
    import pymupdf as _pm14
    _f13 = _pm14.open(os.path.join(ROOT, "figs",
                                   "fig13_non_cepheid_lensing_lowz_sn.pdf"))
    _GRID = (0.6901198029518127, 0.6902418732643127, 0.6901045441627502)
    _hits = []
    for _g in _f13[0].get_drawings():
        _c = _g.get("color")
        if _c is None or _g.get("fill") is not None:
            continue
        if all(abs(_c[i] - _GRID[i]) < 0.01 for i in range(3)):
            _r = _g["rect"]
            if _r.y0 < 251.82 < _r.y1 and abs(_r.height - 9.4) < 1.5:
                _hits.append(round(_r.x0, 2))
    _f13.close()
    check(all(any(abs(h - gx) < 0.1 for h in _hits) for gx in (293.74, 348.77)),
          "Round-14 M2: fig13 gridlines still cut across the patched H0pe row band")
except ImportError:
    print("pymupdf unavailable; fig13 gridline check skipped")

# 16. Round-15 fixes: tension-matrix caption attribution (M1), compressed-CMB
# validation paragraph attribution (M2), derived Savage-Dickey scatter (M3),
# and the severity-boundary alignment (m1).
check("sole exception is the Sound-Horizon-Free row" in tex
      and "the DESI DR2 + CMB rows and the Sound-Horizon-Free row" not in tex
      and "agree exactly; Part VII-B" not in tex,
      "Round-15 M1: tension-matrix caption still attributes the published DESI rows to our chains")
check("at or above $3\\sigma$ (severe tension) are set in bold" in tex,
      "Round-15 m1: table caption severity rule not aligned with the fig8 >= 3 sigma rule")
check("our committed compressed-CMB chains give $H_0 = 68.35" in tex
      and "0.3007" in tex
      and "the compressed-chain posteriors" not in tex
      and "agree exactly" not in tex,
      "Round-15 M2: compressed-CMB validation paragraph still misattributes DESI's published values to our chains")
_c = np.load(os.path.join(VER, "chains", "chain_lcdm_desi_cmb.npy"))
check(abs(_c[:, 0].mean() - 68.35) < 0.01 and abs(_c[:, 0].std() - 0.33) < 0.01,
      "Round-15 M2: chain_lcdm_desi_cmb disagrees with the quoted 68.35 +/- 0.33")
_w = np.load(os.path.join(VER, "chains", "chain_w0wa_desi_cmb.npy"))
check(abs(_w[:, 2].mean() + 0.48) < 0.01 and abs(_w[:, 3].mean() + 1.71) < 0.01
      and abs(_w[:, 0].mean() - 63.60) < 0.01,
      "Round-15 M2: chain_w0wa_desi_cmb disagrees with the quoted (-0.48, -1.71, 63.60)")
check("mathcal{O}(0.4)" not in tex and "run\\_sd\\_canonical.py" in tex
      and "sd\\_chain\\_scatter.json" in tex,
      "Round-15 M3: tex does not cite the derived scatter artifacts (or still quotes the invented O(0.4) scale)")
_scs_path = os.path.join(VER, "sd_chain_scatter.json")
check(os.path.exists(os.path.join(VER, "run_sd_canonical.py")) and os.path.exists(_scs_path),
      "Round-15 M3: Savage-Dickey generator or scatter artifact missing")
if os.path.exists(_scs_path):
    _scs = json.load(open(_scs_path))
    check(abs(_scs["all4chains_lnB"] - 2.6005) < 5e-4
          and abs(_scs["pairs_std"] - 0.513) < 5e-3
          and abs(_scs["singles_std"] - 0.900) < 5e-3
          and abs(_scs["pairs_min"] - 2.08) < 5e-3
          and abs(_scs["pairs_max"] - 3.36) < 5e-3,
          "Round-15 M3: sd_chain_scatter.json disagrees with the tex-quoted scatter (0.90 singles, 0.51 pairs, 2.08-3.36)")
_vr = open(os.path.join(VER, "VERIFICATION_REPORT.md"), encoding="utf-8").read()
check("legacy computation" in _vr and "zc" in _vr,
      "Round-15 m2: VERIFICATION_REPORT does not document the legacy z_c block")

# 17. Round-16 fixes: tex-quoted scatter fragments enforced against the
# artifact, the 'every subset' overstatement removed, and the intro-summary
# attribution clarified.
if os.path.exists(_scs_path):
    check("standard deviation $0.90$" in tex and "standard deviation $0.51$" in tex
          and "mean $2.54$" in tex and "+1.78$ to $+3.90" in tex
          and "+2.08$ to $+3.36" in tex,
          "Round-16 m1: tex does not quote the artifact-derived scatter numbers")
check("every subset of the four" not in tex
      and "four single chains and the six two-chain subsets" in tex,
      "Round-16 m2: tex still overstates the subset coverage ('every subset')")
check("official DESI DR2 values --- our committed chains give $68.35" in tex,
      "Round-16 m3: intro summary still presents the published 68.17 without our-chain attribution")

# 18. Round-17 fixes: submission-package staleness (VERIFICATION_REPORT §12
# chain counts, cover-letter attribution).
_nch = len([f for f in os.listdir(os.path.join(VER, "chains")) if f.endswith(".npy")])
check(_nch == 39, "Round-17: expected 39 committed chains, found %d" % _nch)
check("39 posterior chains (~97 MB)" in _readme,
      "Round-17: README chain count/size stale")
check("Round-17 update" in _vr and "39 posterior chains (~97 MB)" in _vr
      and "removed in Round 14" in _vr,
      "Round-17: VERIFICATION_REPORT section 12 not updated (17 chains / ~51 MB snapshot, orphan named)")
_cl = open(os.path.join(ROOT, "submission", "cover_letter.md"), encoding="utf-8").read()
check("reproduction of the official DESI DR2 inverse-distance-ladder determination" in _cl
      and "68.35 ± 0.33" in _cl and "68.19 ± 1.45" in _cl
      and "an inverse-distance-ladder determination H₀ = 68.17" not in _cl,
      "Round-17: cover letter still presents the published 68.17 as an own determination")
check("85 811" in _cl and "1.0037" in _cl and "1.014" in _cl,
      "Round-17: cover letter convergence claims missing")
_conv = json.load(open(os.path.join(VER, "convergence_diagnostics.json")))
check(any(abs(v - 85811) < 1 for _l in [_conv["ess_cpl_per_chain"], _conv["ess_lcdm_per_chain"]]
          for _seg in _l for v in (_seg if isinstance(_seg, list) else [_seg])),
      "Round-17: ESS 85811 not found in convergence_diagnostics.json")

# 19. Round-18 fixes: cross-reference integrity (the two headline figures and
# the convergence table were never referenced in the running text).
_all_labels = set(re.findall(r"\\label\{([^}]+)\}", tex))
_all_labels |= set(re.findall(r"label=\{([^}]+)\}", tex))
_all_refs = set(re.findall(r"\\ref\{([^}]+)\}", tex))
check(not (_all_refs - _all_labels),
      "Round-18: unresolved \\ref targets: %s" % sorted(_all_refs - _all_labels))
check(not [l for l in _all_labels if len(re.findall(r"\\label\{%s\}" % re.escape(l), tex)) > 1],
      "Round-18: duplicate labels in tex")
for _req in ["fig:hubble_whisker", "fig:tension_heatmap", "tab:convergence"]:
    check("\\ref{%s}" % _req in tex,
          "Round-18: %s never referenced in the running text" % _req)

print("checks run:", checks)
if fails:
    print("FAILURES (%d):" % len(fails))
    for f in fails: print(" -", f)
    sys.exit(1)
print("ALL CHECKS PASS")
