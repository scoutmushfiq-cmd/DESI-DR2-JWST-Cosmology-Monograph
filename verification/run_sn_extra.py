"""Chains and evidence statistics for Mirage (and CPL / LambdaCDM baselines)
on DESI DR2 + CMB + Union3 and DESI DR2 + CMB + DES-SN5YR -- the two dataset
combinations whose Mirage rows were "---" in Round 6 because their SN
likelihoods were not implemented.

Usage (one model per invocation; chains are cached):
    python run_sn_extra.py union3 lcdm 101
    python run_sn_extra.py union3 cpl 1
    python run_sn_extra.py union3 mirage 71
    python run_sn_extra.py desy5 mirage 72 ...
    python run_sn_extra.py stats        # all chains present -> sn_extra_results.json

Method identical to run_mirage_sd.py (48 x 2500, burn 500, thin 16,
Delta-D = 30 trim, Savage-Dickey KDE at w0 = -1, half-chain scatter
errors, bounded multi-start Powell MAP).
"""
import json
import os
import sys
import time

import numpy as np
from scipy import optimize
from scipy import stats as sps

import cosmo
import sn_extra
from cosmo import Joint, run_mcmc, summarize

HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, "chains")
N_WALKERS, N_STEPS, BURN = 48, 2500, 500
THIN = 16
TRIM = 30.0
PRIOR_VOLUME = 3.0


def chi2_of(joint, samples, chunk=1500):
    out = np.empty(len(samples))
    for i in range(0, len(samples), chunk):
        out[i:i + chunk] = joint.chi2(samples[i:i + chunk])
    return out


def split_rhat(chains):
    parts = []
    for c in chains:
        h = len(c) // 2
        parts += [c[:h], c[h:2 * h]]
    n = min(len(p) for p in parts)
    arr = np.stack([p[:n] for p in parts])
    m, _, d = arr.shape
    means = arr.mean(axis=1)
    W = arr.var(axis=1, ddof=1).mean(axis=0)
    B = n * means.var(axis=0, ddof=1)
    var_hat = (n - 1) / n * W + B / n
    return np.sqrt(var_hat / W)


def map_opt(joint, n_starts=12, seed=7, warm=None):
    rng = np.random.default_rng(seed)
    b = joint.bounds()
    best = None
    starts = [np.array(warm)] if warm is not None else []
    starts += [np.array([rng.uniform(lo, hi) for lo, hi in b])
               for _ in range(n_starts)]
    for x0 in starts:
        r = optimize.minimize(lambda x: float(joint.chi2(x[None, :])[0]), x0,
                              method="Powell", bounds=b,
                              options=dict(maxiter=20000, xtol=1e-8, ftol=1e-10))
        if best is None or r.fun < best.fun:
            best = r
    return float(best.fun), [float(v) for v in best.x]


def sd_lnb(w0_samples, V=PRIOR_VOLUME, point=-1.0):
    kde_scott = sps.gaussian_kde(w0_samples)
    kde_silver = sps.gaussian_kde(w0_samples, bw_method="silverman")
    post_s = float(kde_scott([point])[0])
    post_v = float(kde_silver([point])[0])
    return (float(np.log((1.0 / V) / max(post_s, 1e-300))),
            float(np.log((1.0 / V) / max(post_v, 1e-300))),
            post_s)

JOINTS = {
    ("union3", "lcdm"): lambda: Joint(de="lcdm", sn=True, sn_set="union3"),
    ("union3", "cpl"): lambda: Joint(de="cpl", sn=True, sn_set="union3"),
    ("union3", "mirage"): lambda: Joint(de="mirage", sn=True, sn_set="union3"),
    ("desy5", "lcdm"): lambda: Joint(de="lcdm", sn=True, sn_set="desy5"),
    ("desy5", "cpl"): lambda: Joint(de="cpl", sn=True, sn_set="desy5"),
    ("desy5", "mirage"): lambda: Joint(de="mirage", sn=True, sn_set="desy5"),
}


def chain_file(ds, model, seed):
    return os.path.join(CH, f"chain_{model}_{ds}_s{seed}.npy")


def run_chain(ds, model, seed):
    fn = chain_file(ds, model, seed)
    if os.path.exists(fn):
        print("reusing", fn, flush=True)
        return fn
    joint = JOINTS[(ds, model)]()
    t0 = time.time()
    c = run_mcmc(joint, n_walkers=N_WALKERS, n_steps=N_STEPS, burn=BURN, seed=seed)
    np.save(fn, c)
    print(f"saved {fn} ({time.time()-t0:.0f}s)", flush=True)
    return fn


def run_stats(only=None):
    out_path = os.path.join(HERE, "sn_extra_results.json")
    out = json.load(open(out_path)) if os.path.exists(out_path) else {}
    dlnL_path = os.path.join(HERE, "dlnL_decomposition.json")
    dlnL = json.load(open(dlnL_path))

    for ds in ("union3", "desy5"):
        if only and ds != only:
            continue
        key = f"mirage_{ds}"
        print(f"=== {key} ===", flush=True)
        jm = JOINTS[(ds, "mirage")]()
        jl = JOINTS[(ds, "lcdm")]()
        mfiles = [chain_file(ds, "mirage", s) for s in (71, 72)]
        lfiles = [chain_file(ds, "lcdm", 101)]
        if not all(os.path.exists(f) for f in mfiles + lfiles):
            print("  chains missing, skipping (run the chain commands first)")
            continue
        chains = [np.load(f) for f in mfiles]
        cat = np.concatenate(chains, axis=0)
        w0 = cat[:, 2]
        lnB_scott, lnB_silver, post = sd_lnb(w0)
        # half-chain scatter over 4 half-chains of the 2 seeds
        halves = []
        for c in chains:
            h = len(c) // 2
            halves += [c[:h, 2], c[h:2 * h, 2]]
        lnB_half = [sd_lnb(h)[0] for h in halves]
        lnB_err = float(np.std(lnB_half, ddof=1))

        cm = cat[::THIN]
        cl = np.concatenate([np.load(f) for f in lfiles], axis=0)[::THIN]
        x2m = chi2_of(jm, cm)
        x2l = chi2_of(jl, cl)
        chi2_min_m, chi2_min_l = float(x2m.min()), float(x2l.min())
        mean_m = float(x2m[x2m <= chi2_min_m + TRIM].mean())
        mean_l = float(x2l[x2l <= chi2_min_l + TRIM].mean())
        dlnL_v = 0.5 * (mean_l - mean_m)
        d_kl = dlnL_v - lnB_scott

        map_m, x_m = map_opt(jm, warm=cm[x2m.argmin()])
        map_l, x_l = map_opt(jl, warm=cl[x2l.argmin()])
        jc = JOINTS[(ds, "cpl")]()
        cc = np.load(chain_file(ds, "cpl", 1))[::THIN]
        x2c = chi2_of(jc, cc)
        map_c, x_c = map_opt(jc, warm=cc[x2c.argmin()])

        # DIC (same estimator as run_mirage_sd: chi2(theta_bar) + 2 p_D)
        def dic(joint, samples):
            x2 = chi2_of(joint, samples)
            tb = samples.mean(axis=0)
            x2_bar = float(joint.chi2(tb[None, :])[0])
            p_D = float(x2.mean()) - x2_bar
            return x2_bar + 2 * p_D, p_D
        dic_m, pD_m = dic(jm, cm)
        dic_l, pD_l = dic(jl, cl)

        summ = summarize(cat, jm.pnames)
        rhat = split_rhat(chains)
        ess = [int(e) for e in cosmo.ess(cat)]

        out[key] = {
            "label": f"DESI DR2 BAO + CMB + {'Union3' if ds=='union3' else 'DES-SN5YR'}",
            "prior_volume": PRIOR_VOLUME,
            "lnB_SD_scott": lnB_scott, "lnB_SD_silverman": lnB_silver,
            "lnB_SD_err_halfchain": lnB_err,
            "posterior_density_at_w0_minus1": post,
            "chi2_min": chi2_min_m, "lcdm_chi2_min": chi2_min_l,
            "dchi2_map_vs_lcdm": chi2_min_m - chi2_min_l,
            "chi2_MAP_opt": map_m, "MAP_params": dict(zip(jm.pnames, x_m)),
            "lcdm_chi2_MAP_opt": map_l,
            "dchi2_MAP_opt_vs_lcdm": map_m - map_l,
            "cpl_chi2_MAP_opt": map_c,
            "cpl_MAP_params": dict(zip(JOINTS[(ds, "cpl")]().pnames, x_c)),
            "mean_chi2_trim30": mean_m,
            "dlnL_trim_vs_lcdm": dlnL_v,
            "D_KL": d_kl,
            "DIC": dic_m, "p_D": pD_m,
            "lcdm_DIC": dic_l, "lcdm_p_D": pD_l,
            "dDIC_vs_lcdm": dic_m - dic_l,
            "dAIC_vs_lcdm": (map_m + 2 * 3) - (map_l + 2 * 2),
            "summary": summ, "Rhat": [round(float(r), 4) for r in rhat],
            "ESS": ess, "n_samples_kde": int(len(w0)),
            "chains": [os.path.basename(f) for f in mfiles],
            "lcdm_reference_chains": [os.path.basename(f) for f in lfiles],
        }
        dlnL[key] = {
            "chi2_min": chi2_min_m, "mean_chi2_trim30": mean_m,
            "n_trimmed": int((x2m <= chi2_min_m + TRIM).sum()), "n": int(len(x2m)),
            "dlnL_trim_vs_lcdm": dlnL_v,
        }
        print(json.dumps(out[key], indent=1), flush=True)

    json.dump(out, open(out_path, "w"), indent=2)
    json.dump(dlnL, open(dlnL_path, "w"), indent=2)
    print("wrote", out_path, flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "stats":
        run_stats(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        ds, model, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
        assert (ds, model) in JOINTS, (ds, model)
        run_chain(ds, model, seed)
