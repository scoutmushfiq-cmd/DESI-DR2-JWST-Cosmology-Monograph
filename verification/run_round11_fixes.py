"""Round-11 fix computations: (a) the missing cpl_union3 nested run plus
second seeds for all CPL nested configurations and two extra Mirage-Union3
seeds; (b) re-derivation of the tab:cosmological_constraints MCMC Pipeline
(+TRGB) and (+SH0ES) rows from the current pipeline (DESI DR2 + CMB +
Pantheon+ + CC + H0 prior), with chains committed; (c) bounded multi-start
MAP chi2 for LambdaCDM and CPL on each of those configurations.

Run from verification/:  python run_round11_fixes.py
"""
import json
import os
import subprocess
import sys
import time

import numpy as np
from scipy.optimize import minimize

import cosmo
from cosmo import Joint, run_mcmc, summarize

HERE = os.path.dirname(os.path.abspath(__file__))

NESTED_RUNS = [
    ("union3", "cpl", 2026),
    ("desi_cmb", "cpl", 2027),
    ("sn", "cpl", 2027),
    ("union3", "cpl", 2027),
    ("desy5", "cpl", 2027),
    ("union3", "mirage", 2028),
    ("union3", "mirage", 2029),
]


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
    for ds, model, seed in NESTED_RUNS:
        print("nested:", ds, model, seed, flush=True)
        subprocess.run([sys.executable, "nested_lnB.py", ds, model, str(seed)],
                       check=True, cwd=HERE)

    TRGB = cosmo.H0_LADDER["CCHP JWST TRGB"]
    SHOES = cosmo.H0_LADDER["SH0ES 2022"]
    out = {}
    for tag, prior in [("cpl_pp_cc_trgb", TRGB), ("cpl_pp_cc_shoes", SHOES)]:
        t0 = time.time()
        j = Joint(w0wa=True, de="cpl", cc=True, sn=True, h0_prior=prior)
        ch = run_mcmc(j, n_walkers=48, n_steps=2500, burn=500, seed=4242)
        np.save(os.path.join(HERE, "chains", f"chain_{tag}.npy"), ch)
        s = summarize(ch, j.pnames)
        entry = {k: [round(v["mean"], 4), round(v["std"], 4)] for k, v in s.items()}
        H0m, H0s = entry["H0"]
        wbcm, wbcs = entry["wbc"]
        h2 = (H0m / 100.0) ** 2
        Om = (wbcm + cosmo.W_NU) / h2
        Om_s = np.sqrt((2 * Om / H0m * H0s) ** 2 + (wbcs / h2) ** 2)
        entry["Om"] = [round(float(Om), 4), round(float(Om_s), 4)]
        chi2_cpl, _ = map_fit(Joint(w0wa=True, de="cpl", cc=True, sn=True,
                                   h0_prior=prior))
        chi2_lcdm, _ = map_fit(Joint(de="lcdm", cc=True, sn=True,
                                     h0_prior=prior))
        entry["chi2_MAP_cpl"] = round(chi2_cpl, 3)
        entry["chi2_MAP_lcdm"] = round(chi2_lcdm, 3)
        entry["dchi2_MAP"] = round(chi2_cpl - chi2_lcdm, 3)
        entry["runtime_s"] = round(time.time() - t0)
        out[tag] = entry
        print(tag, entry, flush=True)

    json.dump(out, open(os.path.join(HERE, "pipeline_rows_results.json"), "w"),
              indent=1)
    print("DONE in %.0f s" % (time.time() - t_all), flush=True)


if __name__ == "__main__":
    main()
