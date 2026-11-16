"""DESI DR2 + CMB + Pantheon+ (full 1701-SN STAT+SYS covariance) joint MCMC.

Targets (paper Table 5, MCMC Pipeline Base row):
    Om = 0.3115 +- 0.0049, H0 = 67.42 +- 0.52,
    w0 = -0.846 +- 0.050, wa = -0.565 +- 0.204, rd = 147.16 +- 0.28,
    dchi2_MAP = -10.4 (2.8 sigma)
and the official DESI DR2 CPL row: Om 0.3114+-0.0057, H0 67.51+-0.59,
w0 -0.838+-0.055, wa -0.62^(+0.22)_(-0.19), dchi2 -10.7 (2.8 sigma).
"""
import json
import numpy as np
import cosmo
from cosmo import Joint, run_mcmc, summarize, init_walkers_on_band, h0_on_band

OUT = {}

def _summ_dict(summ):
    return {k: {kk: float(vv) for kk, vv in v.items()} for k, v in summ.items()}

def fit(de, seeds=(1, 2), n_steps=2500):
    joint = Joint(w0wa=(de == "cpl"), sn=True, de=de)
    chains = []
    for s in seeds:
        c = run_mcmc(joint, n_walkers=48, n_steps=n_steps, burn=500, seed=s)
        chains.append(c)
        np.save(f"chain_{de}_sn_s{s}.npy", c)
    names = joint.pnames
    full = np.concatenate(chains, axis=0)
    summ = summarize(full, names)
    best = None
    for c in chains:
        i = np.argmin(c[:, -1])
        if best is None or c[i, -1] < best:
            best = c[i, -1]
    return summ, best, names

print("=== LambdaCDM  DESI+CMB+Pantheon+ ===", flush=True)
sum_l, best_l, _ = fit("lcdm")
print(sum_l, flush=True)

print("=== CPL  DESI+CMB+Pantheon+ ===", flush=True)
sum_c, best_c, names_c = fit("cpl")
print(sum_c, flush=True)

OUT["pantheon_joint"] = {
    "sample": "Pantheon+ cosmology subsample (non-calibrators, zHD>0.01), "
              "full STAT+SYS covariance, M_B marginalized analytically",
    "lcdm": {"summary": _summ_dict(sum_l), "chi2_min": float(best_l)},
    "cpl": {"summary": _summ_dict(sum_c), "chi2_min": float(best_c)},
    "dchi2_map_cpl_vs_lcdm": float(best_c - best_l),
}

# H0 on the Omega_m band minimum for each model (MAP-style check)
x2l = h0_on_band(0.3115, -1.0, 0.0)
OUT["pantheon_joint"]["lcdm_bandmin_chi2"] = float(x2l)
OUT["targets"] = {
    "paper_mcmc_base": {"H0": [67.42, 0.52], "Om": [0.3115, 0.0049],
                        "w0": [-0.846, 0.050], "wa": [-0.565, 0.204],
                        "dchi2": -10.4},
    "desi_official_cpl": {"H0": [67.51, 0.59], "Om": [0.3114, 0.0057],
                          "w0": [-0.838, 0.055], "wa": [-0.62, 0.22],
                          "dchi2": -10.7},
}

with open("sn_joint_results.json", "w") as f:
    json.dump(OUT, f, indent=2)
print(json.dumps(OUT, indent=2), flush=True)
