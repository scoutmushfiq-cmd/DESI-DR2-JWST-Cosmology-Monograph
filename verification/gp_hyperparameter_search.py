"""Multi-start (30-start) Nelder-Mead search for the GP marginal-likelihood
optimum over (ln sigma_f, ln l_f), using the exact released gp_hz() data and
objective. Verifies that the released single-start default converges to the
global optimum found by the multi-start search. Run from verification/:

    python gp_hyperparameter_search.py
"""
import json
import os

import numpy as np
from scipy import optimize

import cosmo as cm

STARTS = 30


def main():
    g0 = cm.gp_hz(optimize_hp=False)
    z, y, sy = g0["data"]

    def nll(params):
        sf, lf = np.exp(params)
        K = sf**2 * np.exp(-0.5 * ((z[:, None] - z[None, :]) / lf) ** 2) \
            + np.diag(sy**2) + 1e-8 * np.eye(len(z))
        L = np.linalg.cholesky(K)
        alpha = np.linalg.solve(L.T, np.linalg.solve(L, y))
        return 0.5 * y @ alpha + np.log(np.diag(L)).sum()

    rng = np.random.default_rng(2025)
    results = []
    for i in range(STARTS):
        x0 = np.log([10.0 ** rng.uniform(0.5, 4.0), 10.0 ** rng.uniform(-1.5, 1.5)])
        r = optimize.minimize(nll, x0, method="Nelder-Mead")
        results.append(dict(start=[float(v) for v in np.exp(x0)],
                            sf=float(np.exp(r.x[0])), lf=float(np.exp(r.x[1])),
                            nll=float(r.fun), success=bool(r.success)))

    best = min(results, key=lambda r: r["nll"])
    single = cm.gp_hz()
    out = dict(
        n_starts=STARTS,
        objective="gp_hz marginal nll (32 CC + 6 radial DESI DR2 D_H/r_d, r_d=147.09)",
        best=dict(sf=best["sf"], lf=best["lf"], nll=best["nll"]),
        released_single_start=dict(sf=single["sf"], lf=single["lf"],
                                   z_t=list(single["z_t"]), q0=list(single["q0"])),
        nll_at_superseded_5318_1259=float(nll(np.log([5.318, 1.259]))),
        all_starts=[dict(sf=r["sf"], lf=r["lf"], nll=round(r["nll"], 4)) for r in results],
        n_converged_to_best=sum(1 for r in results if abs(r["nll"] - best["nll"]) < 1e-3),
    )
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "gp_hyperparameter_search.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("best: sf=%.3f lf=%.4f nll=%.3f" % (best["sf"], best["lf"], best["nll"]))
    print("single-start: sf=%.3f lf=%.4f" % (single["sf"], single["lf"]))
    print("starts converged to best: %d/%d" % (out["n_converged_to_best"], STARTS))


if __name__ == "__main__":
    main()
