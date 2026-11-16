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
check("63 pages" in readme, "README missing the 63-page compile claim")
check("~59 MB" not in readme, "Round-8 m1: README still claims ~59 MB of chains")
check("~86 MB" in readme, "README missing the ~86 MB chain-size claim")
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
        ("union3", ["-19.3", "4.4", "-17.3", "-17.4", "+9.17", "+6.75 \\pm 0.02"]),
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
                           ("mirage_union3", "+6.75 \\pm 0.02", 0.02),
                           ("mirage_desy5", "+5.04 \\pm 0.19", 0.19),
                           ("cpl_desi_cmb", "+2.37", None)]:
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
check(len(chain_files) == 35, "expected 35 chain files, found %d" % len(chain_files))
check("All 35 posterior chains" in readme, "README chain count not updated to 35")
check("All 27 posterior chains" not in readme, "README still quotes the stale 27-chain count")
for art in ["sn_extra.py", "nested_lnB.py", "sn_extra_results.json", "nested_lnB.json", "download_sn_extra_data.py"]:
    check(art in readme, "README missing new artifact %s" % art)
for f in ["submission/referee_response_template.md", "submission/cover_letter.md"]:
    body = open(os.path.join(ROOT, f), encoding="utf-8").read()
    check("+6.75" in body and "+5.04" in body if f.endswith("referee_response_template.md") else True,
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
check("satisfy $\\widehat{R} \\le 1.001$" in tex,
      "Part VII-B missing the new-chain R-hat statement")

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
