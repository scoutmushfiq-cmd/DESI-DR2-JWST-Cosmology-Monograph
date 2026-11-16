"""Corner plot for the MCMC Pipeline rows of tab:cosmological_constraints.

Blue:   DESI DR2 + (theta*, w_b, w_bc)_CMB + Pantheon+          (chain_cpl_sn)
Orange: + CC + JWST CCHP TRGB prior (H0 = 68.81 +- 2.22)         (chain_cpl_pp_cc_trgb)
Red:    + CC + SH0ES prior (H0 = 73.04 +- 1.04)                 (chain_cpl_pp_cc_shoes)

All chains are committed Goodman & Weare runs (48 walkers, 2500 steps,
500 burn; 96,000 retained samples). Omega_m is derived per sample from the
slaved parametrization Omega_m = (w_bc + W_NU) / h^2.

Run from verification/:  python make_fig4_corner.py
Writes ../figs/fig4_mcmc_corner_plot.pdf
"""
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

from cosmo import W_NU

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "figs", "fig4_mcmc_corner_plot.pdf")

LABELS = [r"$H_0$", r"$\Omega_m$", r"$w_0$", r"$w_a$"]
SERIES = [
    (["chains/chain_cpl_sn_s1.npy", "chains/chain_cpl_sn_s2.npy"], "#1f77b4",
     "DESI DR2 + CMB + Pantheon+ (Uncalibrated)"),
    (["chains/chain_cpl_pp_cc_trgb.npy"], "#ff7f0e",
     "+ CC + JWST CCHP TRGB Prior ($H_0 = 68.81 \\pm 2.22$)"),
    (["chains/chain_cpl_pp_cc_shoes.npy"], "#d62728",
     "+ CC + SH0ES Cepheid Prior ($H_0 = 73.04 \\pm 1.04$)"),
]


def load(fns):
    parts = [np.load(os.path.join(HERE, fn))[::4] for fn in fns]
    c = np.concatenate(parts, axis=0)
    H0, wbc, w0, wa = c[:, 0], c[:, 1], c[:, 2], c[:, 3]
    Om = (wbc + W_NU) / (H0 / 100.0) ** 2
    return np.column_stack([H0, Om, w0, wa])


def contour_levels(d2, fracs=(0.68, 0.95)):
    d = gaussian_filter(d2, 1.5)
    d = d / d.sum()
    flat = np.sort(d.ravel())[::-1]
    csum = np.cumsum(flat)
    return [flat[np.searchsorted(csum, f)] for f in fracs]


def main():
    data = [(load(fns), color, lab) for fns, color, lab in SERIES]
    n = 4
    lims = []
    for i in range(n):
        lo = min(d[:, i].min() for d, _, _ in data)
        hi = max(d[:, i].max() for d, _, _ in data)
        lims.append((lo, hi))

    fig, axes = plt.subplots(n, n, figsize=(9.0, 8.6))
    for i in range(n):
        for j in range(n):
            ax = axes[i, j]
            if j > i:
                ax.axis("off")
                continue
            if i == j:
                for d, color, lab in data:
                    ax.hist(d[:, i], bins=60, range=lims[i], histtype="stepfilled",
                            color=color, alpha=0.45, density=True,
                            label=lab if i == 0 else None)
                    ax.hist(d[:, i], bins=60, range=lims[i], histtype="step",
                            color=color, lw=1.2, density=True)
                ax.set_xlim(lims[i])
                ax.set_yticks([])
            else:
                for d, color, lab in data:
                    d2, xe, ye = np.histogram2d(d[:, j], d[:, i], bins=50,
                                                range=[lims[j], lims[i]])
                    lv95, lv68 = sorted(contour_levels(d2))
                    xc = 0.5 * (xe[:-1] + xe[1:])
                    yc = 0.5 * (ye[:-1] + ye[1:])
                    ax.contour(xc, yc, d2.T, levels=[lv95, lv68], colors=color,
                               linewidths=[1.0, 1.4], linestyles=["dashed", "solid"])
                ax.set_xlim(lims[j])
                ax.set_ylim(lims[i])
            if i == n - 1:
                ax.set_xlabel(LABELS[j], fontsize=12)
            else:
                ax.set_xticklabels([])
            if j == 0:
                ax.set_ylabel(LABELS[i], fontsize=12)
            else:
                ax.set_yticklabels([])

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=1, fontsize=10.5,
               frameon=False, bbox_to_anchor=(0.72, 0.985))
    fig.suptitle(r"Goodman \& Weare Ensemble MCMC: $(H_0, \Omega_m, w_0, w_a)$"
                 "  (68% solid, 95% dashed)", y=0.995, fontsize=12)
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.93])
    fig.savefig(OUT, bbox_inches="tight")
    print("wrote", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
