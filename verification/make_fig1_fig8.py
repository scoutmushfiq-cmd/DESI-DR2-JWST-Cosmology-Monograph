"""Regenerate figs/fig1_hubble_tension_whisker.pdf and
figs/fig8_tension_heatmap_matrix.pdf from the current pipeline values.

The Sound-Horizon-Free row previously embedded the superseded
(H0, rd) = (69.24 +- 1.82, 146.99 +- 3.44); it is now derived from the
committed chains chain_rdfree_{lcdm,cpl}_desi_cc_pp.npy
(verification/rdfree_results.json): H0 = 68.19 +- 1.45,
rd = 146.36 +- 2.88, and the tension row is recomputed with
T = |H0_i - H0_j| / sqrt(sigma_i^2 + sigma_j^2).

The script asserts that all 36 unchanged heatmap cells reproduce the
values embedded in the previous figure, so any drift in the other rows
is caught rather than silently overwritten. Run from verification/:

    python make_fig1_fig8.py
"""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "figs")

rd = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rdfree_results.json")))
_h0, _s = rd["rdfree_cpl"]["H0"]
SHF_H0, SHF_S = round(_h0, 2), round(_s, 2)
assert (SHF_H0, SHF_S) == (68.19, 1.45), "rdfree_results.json H0 drifted: %s" % ((SHF_H0, SHF_S),)

# ---------------------------------------------------------------------------
# Fig 1: H0 whisker comparison (18 rows)
# ---------------------------------------------------------------------------
EARLY = "C0"; JWSTC = "C1"; SH0ESC = "C3"
rows = [
    ("Planck 2018 TT,TE,EE+lowE+lensing ($\\Lambda$CDM)", 67.36, 0.54, EARLY, False),
    ("DESI DR2 BAO + Planck CMB ($\\Lambda$CDM)", 68.17, 0.28, EARLY, False),
    ("DESI DR2 BAO + BBN ($\\omega_b h^2$ prior)", 68.51, 0.58, EARLY, False),
    ("DESI DR2 + CMB + Pantheon+ ($w_0 w_a$CDM)", 67.51, 0.59, EARLY, False),
    ("DESI DR2 + CMB + Union3 ($w_0 w_a$CDM)", 65.91, 0.84, EARLY, False),
    ("DESI DR2 + CMB + DES-Y5 ($w_0 w_a$CDM)", 66.74, 0.56, EARLY, False),
    ("DESI DR2 + CMB + CC + Pantheon+ + SH0ES ($w_0 w_a$CDM)", 68.51, 0.20, EARLY, False),
    ("Sound-Horizon-Free: DESI DR2 + CC + Pantheon+ ($r_d$ free)", SHF_H0, SHF_S, EARLY, False),
    ("CCHP JWST-Only JAGB (7 SNe Ia, NGC 4258 anchor)", 67.80, 2.72, JWSTC, False),
    ("CCHP JWST-Only TRGB (11 SNe Ia, NGC 4258 anchor)", 68.81, 2.22, JWSTC, False),
    ("CCHP JWST 3-Method Combined (TRGB+JAGB+Cepheids)", 69.96, 1.54, JWSTC, False),
    ("CCHP HST+JWST TRGB (24 SNe Ia calibrators)", 70.39, 1.94, JWSTC, False),
    ("Joint JWST TRGB ($D \\leq 25$ Mpc, 16 SNe Ia)", 72.10, 2.20, JWSTC, False),
    ("Joint JWST JAGB ($D \\leq 25$ Mpc, 16 SNe Ia)", 72.20, 2.20, JWSTC, False),
    ("Joint JWST 3-Method Combined (16 SNe Ia, $D \\leq 25$ Mpc)", 72.60, 2.00, JWSTC, False),
    ("JWST Cepheids ($D \\leq 25$ Mpc, 16 SNe Ia)", 73.40, 2.10, JWSTC, False),
    ("SH0ES HST Cepheids + Pantheon+ (37 hosts, 42 SNe Ia)", 73.04, 1.04, SH0ESC, True),
    ("SH0ES Full HST Cepheids + 4 Anchors (Riess et al. 2024)", 73.17, 0.86, SH0ESC, True),
]

fig, ax = plt.subplots(figsize=(10.7, 5.9))
ax.axvspan(67.36 - 0.54, 67.36 + 0.54, color=EARLY, alpha=0.10,
           label="Planck 2018 $\\Lambda$CDM (1$\\sigma$)")
ax.axvspan(73.17 - 0.86, 73.17 + 0.86, color=SH0ESC, alpha=0.10,
           label="SH0ES Cepheid Baseline (1$\\sigma$)")
ax.axvline(67.36, color="k", ls="--", lw=0.9, alpha=0.6)
ax.axvline(73.17, color="k", ls="--", lw=0.9, alpha=0.6)
n = len(rows)
for i, (nm, h, s, c, two_sigma) in enumerate(reversed(rows)):
    y = i
    if two_sigma:
        ax.errorbar(h, y, xerr=2 * s, fmt="none", ecolor=c, elinewidth=0.9, capsize=0, alpha=0.55)
        ax.errorbar(h, y, xerr=s, fmt="o", color=c, ms=5, capsize=3)
    else:
        ax.errorbar(h, y, xerr=s, fmt="o", color=c, ms=5, capsize=3)
    ax.text(h + s + 0.25, y, "%s $\\pm$ %s" % (("%.2f" % h), ("%.2f" % s)),
            va="center", fontsize=7.5, color=c)
ax.set_yticks(range(n))
ax.set_yticklabels([r[0] for r in reversed(rows)], fontsize=7.5)
ax.set_xlim(62.5, 80.0)
ax.set_xlabel("$H_0$ [km s$^{-1}$ Mpc$^{-1}$]")
ax.set_title("Hubble Constant Determinations: Early-Universe, DESI DR2 Inverse Ladder,\nand JWST/HST Calibrations",
             fontsize=11)
ax.legend(loc="lower right", fontsize=8, framealpha=0.9)
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "fig1_hubble_tension_whisker.pdf"))
plt.close(fig)

# ---------------------------------------------------------------------------
# Fig 8: 7 x 6 tension heatmap
# ---------------------------------------------------------------------------
col_heads = [("SH0ES 4-Anchor\nCepheids", 73.17, 0.86),
             ("SH0ES HST+\nPantheon+", 73.04, 1.04),
             ("Joint JWST\n3-Method", 72.60, 2.00),
             ("CCHP HST+JWST\nTRGB", 70.39, 1.94),
             ("CCHP JWST\nTRGB Only", 68.81, 2.22),
             ("CCHP JWST\nJAGB Only", 67.80, 2.72)]
row_heads = [("Planck 2018 $\\Lambda$CDM", 67.36, 0.54),
             ("DESI DR2 + CMB $\\Lambda$CDM", 68.17, 0.28),
             ("DESI DR2 + BBN $\\Lambda$CDM", 68.51, 0.58),
             ("DESI DR2+CMB+Pan+ $w_0w_a$", 67.51, 0.59),
             ("DESI DR2+CMB+DESY5 $w_0w_a$", 66.74, 0.56),
             ("DESI DR2+CMB+Union3 $w_0w_a$", 65.91, 0.84),
             ("Sound-Horizon-Free Late-Time", SHF_H0, SHF_S)]

# previously embedded values (extracted from the superseded figure); the
# Sound-Horizon-Free row is recomputed, everything else must reproduce
EXPECTED = {
    "Planck 2018 $\\Lambda$CDM":            [5.72, 4.85, 2.53, 1.50, 0.63, 0.16],
    "DESI DR2 + CMB $\\Lambda$CDM":         [5.53, 4.52, 2.19, 1.13, 0.29, 0.14],
    "DESI DR2 + BBN $\\Lambda$CDM":         [4.49, 3.80, 1.96, 0.93, 0.13, 0.26],
    "DESI DR2+CMB+Pan+ $w_0w_a$":           [5.43, 4.62, 2.44, 1.42, 0.57, 0.10],
    "DESI DR2+CMB+DESY5 $w_0w_a$":          [6.27, 5.33, 2.82, 1.81, 0.90, 0.38],
    "DESI DR2+CMB+Union3 $w_0w_a$":         [6.04, 5.33, 3.08, 2.12, 1.22, 0.66],
    "Sound-Horizon-Free Late-Time":         None,
}

T = np.zeros((len(row_heads), len(col_heads)))
for i, (_, h1, s1) in enumerate(row_heads):
    for j, (_, h2, s2) in enumerate(col_heads):
        T[i, j] = abs(h1 - h2) / np.sqrt(s1 ** 2 + s2 ** 2)
for i, (nm, _, _) in enumerate(row_heads):
    exp = EXPECTED[nm]
    got = [round(v, 2) for v in T[i]]
    if exp is None:
        continue
    assert got == exp, "row %r drifted: got %s expected %s" % (nm, got, exp)
print("unchanged rows reproduce the previous figure exactly")

def sev(v):
    return "SEVERE" if v >= 3 else "CONSIST."

fig, ax = plt.subplots(figsize=(9.6, 5.5))
im = ax.imshow(T, cmap="RdYlGn_r", vmin=0, vmax=6.5, aspect="auto")
ax.set_xticks(range(len(col_heads)))
ax.set_xticklabels(["%s\n($%.2f\\pm%.2f$)" % (nm, h, s) for nm, h, s in col_heads], fontsize=7.5)
ax.set_yticks(range(len(row_heads)))
ax.set_yticklabels(["%s\n($%.2f \\pm %.2f$)" % (nm, h, s) for nm, h, s in row_heads], fontsize=7.5)
for i in range(len(row_heads)):
    for j in range(len(col_heads)):
        v = T[i, j]
        ax.text(j, i, "%.2f\n(%s)" % (v, sev(v)), ha="center", va="center",
                fontsize=7.5, color="black")
cb = fig.colorbar(im, ax=ax, pad=0.02)
cb.set_label("Gaussian Tension Significance $|T_{ij}|$ [$\\sigma$]")
ax.set_title("Comprehensive 7 $\\times$ 6 Hubble Tension Significance Matrix\nAcross Early- and Late-Universe Probes", fontsize=11)
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "fig8_tension_heatmap_matrix.pdf"))
plt.close(fig)
print("fig1 + fig8 regenerated (Sound-Horizon-Free row = %.2f +- %.2f)" % (SHF_H0, SHF_S))
