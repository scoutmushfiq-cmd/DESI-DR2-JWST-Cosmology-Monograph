"""Round-12 fix computations: committed r_d-free chains (CPL and LambdaCDM)
on DESI DR2 + CC + Pantheon+ with r_d free, replacing the unverifiable
Sound-Horizon-Free row of tab:cosmological_constraints, plus bounded
multi-start MAP chi2 for both models on the same configuration.

Run from verification/:  python run_round12_fixes.py
"""
import json
import os
import time

import numpy as np
from scipy.optimize import minimize

import cosmo
from cosmo import Joint, run_mcmc, summarize

HERE = os.path.dirname(os.path.abspath(__file__))


def map_fit(joint, n_starts=12, seed=99):
    rng = np.random.default_rng(seed)
    b = np.array(joint.bounds())
    best = (np.inf, None)
    starts = [b[:, 0] + (b[:, 1] - b[:, 0]) * rng.uniform(0.2, 0.8, len(b[:, 0]))
              for _ in range(n_starts)]
    for x0 in starts:
        try:
            r = minimize(joint.chi2, x0, method="Nelder-Mead",
                         options=dict(maxiter=20000, xatol=1e-6, fatol=1e-8))
        except Exception:
            continue
        if r.fun < best[0] and np.all(r.x >= b[:, 0]) and np.all(r.x <= b[:, 1]):
            best = (float(r.fun), r.x)
    return best


def main():
    t_all = time.time()
    out = {}
    for tag, w0wa, seed in [("rdfree_lcdm", False, 61), ("rdfree_cpl", True, 62)]:
        t0 = time.time()
        j = Joint(w0wa=w0wa, de=("lcdm" if not w0wa else "cpl"), rd_free=True, bao=True, cmb=False, cc=True, sn=True)
        ch = run_mcmc(j, n_walkers=48, n_steps=2500, burn=500, seed=seed)
        np.save(os.path.join(HERE, "chains", f"chain_{tag}_desi_cc_pp.npy"), ch)
        s = summarize(ch, j.pnames)
        entry = {k: [round(v["mean"], 4), round(v["std"], 4)] for k, v in s.items()}
        H0m, H0s = entry["H0"]
        Om_draws = (ch[:, 1] + cosmo.W_NU) / (ch[:, 0] / 100.0) ** 2
        entry["Om"] = [round(float(Om_draws.mean()), 4), round(float(Om_draws.std()), 4)]
        out[tag] = entry
        print(tag, entry, "%.0f s" % (time.time() - t0), flush=True)

    for tag, w0wa in [("rdfree_lcdm", False), ("rdfree_cpl", True)]:
        j = Joint(w0wa=w0wa, de=("lcdm" if not w0wa else "cpl"), rd_free=True, bao=True, cmb=False, cc=True, sn=True)
        chi2, x = map_fit(j)
        out[tag]["chi2_MAP"] = round(chi2, 3)
        out[tag]["MAP_params"] = [round(float(v), 4) for v in x]
        print(tag, "chi2_MAP", round(chi2, 3), flush=True)

    out["dchi2_MAP_cpl_vs_lcdm"] = round(
        out["rdfree_cpl"]["chi2_MAP"] - out["rdfree_lcdm"]["chi2_MAP"], 3)
    out["config"] = "Joint(bao=True, cmb=False, cc=True, sn=True, rd_free=True); DESI DR2 + CC + Pantheon+, r_d free"
    json.dump(out, open(os.path.join(HERE, "rdfree_results.json"), "w"), indent=1)
    print("DONE in %.0f s" % (time.time() - t_all), flush=True)


if __name__ == "__main__":
    main()
