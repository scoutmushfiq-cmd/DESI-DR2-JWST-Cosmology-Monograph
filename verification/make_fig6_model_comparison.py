"""Regenerate figs/fig6_model_comparison_bayes.pdf from the values quoted in
Table tab:model_comparison_full: transcribed published values (Lodha et al.
2025, DESI DR2 2025a) for the CPL/BA/EXP/LOG/JBP/thawing/emergent rows, and
this work's own values for the Mirage rows (daggered: DESI DR2 + CMB and
+ Pantheon+ from mirage_sd.json; double-daggered: Union3 and DES-Y5 from
sn_extra_results.json / nested_lnB.json).

Run from verification/:  python make_fig6_model_comparison.py
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, os.pardir, "figs", "fig6_model_comparison_bayes.pdf")

C_PAN = "#1f77b4"
C_UNI = "#ff7f0e"
C_DES = "#d62728"
C_DR1 = {"pan": "#9ecae1", "uni": "#fdd0a2", "des": "#f4a582"}

groups = [
    ("Emergent DE\n(1 param)", [
        ("pp", -0.05, False), ("des", -1.5, False)]),
    ("Calibrated Thawing\n(1 param)", [
        ("pp", -1.6, False), ("des", -7.1, False)]),
    ("Algebraic Thawing\n($w\\geq -1$, 2 params)", [
        ("pp", -2.9, False), ("des", -13.2, False)]),
    ("JBP Param.\n(2 params)", [
        ("uni", -13.6, False)]),
    ("CPL ($w_0w_a$CDM)\n(2 params)", [
        ("pp", -10.7, False), ("uni", -17.4, False), ("des", -21.0, False),
        ("pp1", -8.8, False), ("uni1", -14.5, False), ("des1", -17.7, False)]),
    ("BA / EXP / LOG\n(2 params)", [
        ("uni", -17.3, False), ("uni", -17.5, False), ("uni", -17.6, False)]),
    ("Mirage DE\n(1 param)", [
        ("cmb", -12.4, True), ("pp", -13.2, True),
        ("uni", -19.3, True), ("des", -17.0, True)]),
]

COLORS = {"pp": C_PAN, "uni": C_UNI, "des": C_DES,
          "pp1": C_DR1["pan"], "uni1": C_DR1["uni"], "des1": C_DR1["des"],
          "cmb": "#7f7f7f"}
LABELS = {"pp": "Pantheon+", "uni": "Union3", "des": "DES-Y5",
          "pp1": "Pantheon+ (DR1)", "uni1": "Union3 (DR1)",
          "des1": "DES-Y5 (DR1)", "cmb": "DESI DR2 + CMB"}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 5.4),
                               gridspec_kw={"width_ratios": [1.45, 1.0]})

x0 = 0.0
xticks, xlabels = [], []
bw = 0.24
for name, bars in groups:
    n = len(bars)
    xs = x0 + np.arange(n) * bw
    for (key, val, own), x in zip(bars, xs):
        ax1.bar(x, val, width=bw * 0.92, color=COLORS[key],
                hatch="///" if own else None,
                edgecolor="black" if own else "none", linewidth=0.6 if own else 0.0)
    xticks.append(x0 + (n - 1) * bw / 2)
    xlabels.append(name)
    x0 += n * bw + 0.55

ax1.axhline(-2.71, color="gray", ls=":", lw=1.0)
ax1.axhline(-4.61, color="gray", ls="--", lw=1.0)
ax1.text(0.1, -2.55, "90% threshold (1 dof)", fontsize=7, color="gray")
ax1.text(0.1, -4.45, "90% threshold (2 dof)", fontsize=7, color="gray")
ax1.axhline(0, color="black", lw=0.8)
ax1.set_xticks(xticks)
ax1.set_xticklabels(xlabels, fontsize=7.5)
ax1.set_ylabel(r"$\Delta\chi^2_{\rm MAP}$ vs. flat $\Lambda$CDM")
ax1.set_title(r"(a) Frequentist Fit Improvement $\Delta\chi^2_{\rm MAP}$ vs. $\Lambda$CDM", fontsize=10)
ax1.set_ylim(-23.5, 1.5)
handles = [plt.Rectangle((0, 0), 1, 1, color=C_PAN),
           plt.Rectangle((0, 0), 1, 1, color=C_UNI),
           plt.Rectangle((0, 0), 1, 1, color=C_DES),
           plt.Rectangle((0, 0), 1, 1, color=C_DR1["pan"]),
           plt.Rectangle((0, 0), 1, 1, facecolor="white", edgecolor="black", hatch="///")]
ax1.legend(handles, ["Pantheon+", "Union3", "DES-Y5", "Pantheon+/Union3/DES-Y5 (DR1)",
                     "Mirage (this work)"],
           fontsize=6.5, loc="lower left", framealpha=0.9)

dec = [("Pantheon+ (DR2)", 4.53, 5.19, -0.66, C_PAN),
       ("Union3 (DR2)", 7.78, 4.75, 3.03, C_UNI),
       ("DES-Y5 (DR2)", 9.42, 4.54, 4.88, C_DES),
       ("Pantheon+ (DR1)", 3.34, 4.88, -1.54, C_DR1["pan"]),
       ("Union3 (DR1)", 6.03, 4.41, 1.62, C_DR1["uni"]),
       ("DES-Y5 (DR1)", 7.67, 5.32, 2.35, C_DR1["des"])]
xs = np.arange(len(dec))
for i, (lbl, dlnl, dkl, lnb, col) in enumerate(dec):
    ax2.bar(i, dlnl, width=0.6, color=col, alpha=0.85,
            label=r"$\Delta\langle\ln\mathcal{L}\rangle_{\mathcal{P}}$" if i == 0 else None)
    ax2.bar(i, -dkl, width=0.6, color="gray", alpha=0.55,
            label=r"$-\mathcal{D}_{\rm KL}$ (Occam)" if i == 0 else None)
    ax2.plot(i, lnb, marker="D", color="black", markersize=6,
             label=r"net $\ln B_{w_0w_a,\Lambda}$" if i == 0 else None)
ax2.axhline(0, color="black", lw=0.8)
for y, lab in [(1.0, "Weak/Mod."), (2.5, "Mod./Strong"), (5.0, "Strong/Decisive")]:
    ax2.axhline(y, color="crimson", ls=":", lw=0.8)
    ax2.text(len(dec) - 0.45, y + 0.12, lab, fontsize=6, color="crimson")
ax2.set_xticks(xs)
ax2.set_xticklabels([d[0] for d in dec], fontsize=6.5, rotation=30, ha="right")
ax2.set_ylabel(r"$\ln B$ / Log-Likelihood Units")
ax2.set_title(r"(b) Nested Sampling Bayes Factor Decomposition (CPL)", fontsize=10)
ax2.legend(fontsize=7, loc="upper left")

fig.tight_layout()
fig.savefig(OUT)
print("wrote", os.path.normpath(OUT))
