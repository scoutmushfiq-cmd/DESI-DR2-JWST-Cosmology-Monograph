"""Per-draw phantom-divide crossing distribution of the H(z)-route GP w(z)
reconstruction, using the exact recipe of make_figures2.py (fig_gp_wz.png):
ML hyperparameters via gp_hz(), default_rng(23), 600 draws, rho_DE from the
E^2 subtraction with Om0 = 0.300, Or = 9.2e-5, log-gradient w(z). Run from
verification/:

    python gp_route_crossing.py
"""
import json
import os

import numpy as np

import cosmo as cm


def main():
    g = cm.gp_hz()
    zt, mu, cov = g["zt"], g["mu"], g["cov"]
    rng = np.random.default_rng(23)
    draws = rng.multivariate_normal(mu, cov, size=600)
    Om0, Or = 0.300, 9.2e-5
    E2d = (draws / np.median(draws[:, 0])) ** 2
    rhode = E2d - Om0 * (1 + zt)[None, :] ** 3 - Or * (1 + zt)[None, :] ** 4
    lnr = np.log(np.clip(rhode, 1e-6, None))
    dlnr = np.gradient(lnr, zt, axis=1)
    wz = -1.0 + (1.0 + zt)[None, :] / 3.0 * dlnr

    wmed = np.median(wz, axis=0)
    med_cross = [float(zt[i]) for i in np.where(np.diff(np.sign(wmed + 1)) != 0)[0]]

    per_draw = []
    for row in wz:
        idx = np.where(np.diff(np.sign(row + 1.0)) != 0)[0]
        if len(idx):
            i = idx[0]
            zc = zt[i] - (row[i] + 1.0) * (zt[i + 1] - zt[i]) / (row[i + 1] - row[i])
            per_draw.append(float(zc))
    per_draw = np.array(per_draw)

    out = dict(
        recipe="make_figures2.py fig_gp_wz recipe; gp_hz() ML hyperparameters "
               "(sigma_f=%.2f, l_f=%.4f), rng(23), 600 draws" % (g["sf"], g["lf"]),
        w0_median=float(wmed[0]),
        w0_std=float(wz[:, 0].std()),
        median_crossings=med_cross,
        w_at_0p5=float(np.interp(0.5, zt, wmed)),
        per_draw_cross_median=float(np.median(per_draw)),
        per_draw_cross_std=float(per_draw.std()),
        n_draws_with_crossing=int(len(per_draw)),
        n_draws=int(wz.shape[0]),
        frac_draws_crossing=float(len(per_draw) / wz.shape[0]),
        cpl_posterior_zc_desi_cmb=[0.495, 0.077],
        note="The H(z)-route median crosses w=-1 near z~0.14, not at the CPL "
             "posterior z_c~0.50; the two routes are consistent only at the "
             "level of the wide 68% band, not at the level of the median.",
    )
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "gp_route_crossing.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("w(0)=%.3f  median crossing(s)=%s  per-draw %.3f +- %.3f (%d/%d draws)"
          % (wmed[0], ["%.3f" % c for c in med_cross], out["per_draw_cross_median"],
             out["per_draw_cross_std"], len(per_draw), wz.shape[0]))


if __name__ == "__main__":
    main()
