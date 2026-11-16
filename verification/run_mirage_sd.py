"""Mirage Dark Energy chains, Savage-Dickey Bayes factors, and the
likelihood / Occam decomposition -- computed on our own released chains.

Round-6 referee major M1: the manuscript previously quoted Mirage lnB values
(+1.85 / +4.60 / +6.65) transcribed from nowhere; this script produces the
genuine artifact (mirage_sd.json) backing every Mirage evidence number in
the paper, for the two dataset combinations our pipeline implements
(DESI DR2 + CMB, and DESI DR2 + CMB + Pantheon+).

Method
------
* Mirage DE: one free parameter w0 with w_a = -3.66 (1 + w_0) enforced
  (Lodha et al. 2025, arXiv:2503.14743); flat prior w0 ~ U[-2.5, 0.5],
  prior volume V = 3.0.
* MCMC: Goodman-Weare ensemble, 48 walkers, 2500 steps, 500 burn-in,
  2 seeds per dataset (cosmo.run_mcmc, band-aware initialization).
* Savage-Dickey density ratio at the nested point w0 = -1 (which implies
  w_a = 0, i.e. flat LambdaCDM): lnB = ln[ (1/V) / p(w0 = -1 | data) ],
  Gaussian KDE on the concatenated w0 samples.
* Delta<lnL>: posterior mean chi2 within the likelihood-dominated region,
  defined by the same Delta-D = 30 tail trim used for the DIC
  (dlnL_decomposition.json semantics), thin factor 16
  (2 x 96000 / 16 = 12000 samples per model).
* D_KL = Delta<lnL>_trim - lnB_SD   (Occam penalty).
* Cross-checks: recomputes the CPL and LambdaCDM decompositions from the
  existing released chains and compares with the archived values.

Outputs: mirage_sd.json; mirage keys appended to dlnL_decomposition.json;
chains saved as chains/chain_mirage_*.npy.
"""
import json
import os

import numpy as np
from scipy import stats, optimize

import cosmo
from cosmo import Joint, run_mcmc, summarize

HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, "chains")

SEEDS = (71, 72)
N_WALKERS, N_STEPS, BURN = 48, 2500, 500
THIN = 16
TRIM = 30.0
PRIOR_VOLUME = 3.0
MIRAGE_POINT = -1.0


def chi2_of(joint, samples, chunk=1500):
    out = np.empty(len(samples))
    for i in range(0, len(samples), chunk):
        out[i:i + chunk] = joint.chi2(samples[i:i + chunk])
    return out


def split_rhat(chains):
    """Split-Rhat per column; chains is a list of (n, d) arrays."""
    parts = []
    for c in chains:
        h = len(c) // 2
        parts += [c[:h], c[h:2 * h]]
    n = min(len(p) for p in parts)
    arr = np.stack([p[:n] for p in parts])          # (m, n, d)
    m, _, d = arr.shape
    means = arr.mean(axis=1)                        # (m, d)
    W = arr.var(axis=1, ddof=1).mean(axis=0)        # (d,)
    B = n * means.var(axis=0, ddof=1)               # (d,)
    var_hat = (n - 1) / n * W + B / n
    return np.sqrt(var_hat / W)


def map_opt(joint, n_starts=12, seed=7):
    """Bounded MAP chi2 minimization (Powell, multiple starts in the prior box)."""
    rng = np.random.default_rng(seed)
    b = joint.bounds()
    best = None
    for _ in range(n_starts):
        x0 = np.array([rng.uniform(lo, hi) for lo, hi in b])
        r = optimize.minimize(lambda x: float(joint.chi2(x[None, :])[0]), x0,
                              method="Powell", bounds=b,
                              options=dict(maxiter=20000, xtol=1e-8, ftol=1e-10))
        if best is None or r.fun < best.fun:
            best = r
    return float(best.fun), [float(v) for v in best.x]


def sd_lnb(w0_samples, V=PRIOR_VOLUME, point=MIRAGE_POINT):
    kde_scott = stats.gaussian_kde(w0_samples)
    kde_silver = stats.gaussian_kde(w0_samples, bw_method="silverman")
    post_s = float(kde_scott([point])[0])
    post_v = float(kde_silver([point])[0])
    return (float(np.log((1.0 / V) / max(post_s, 1e-300))),
            float(np.log((1.0 / V) / max(post_v, 1e-300))),
            post_s)


def decompose(joint_m, joint_l, files_m, files_l):
    """chi2 statistics on thinned samples for model vs LambdaCDM reference."""
    cm = np.concatenate([np.load(os.path.join(CH, f)) for f in files_m])[::THIN]
    cl = np.concatenate([np.load(os.path.join(CH, f)) for f in files_l])[::THIN]
    x2m = chi2_of(joint_m, cm)
    x2l = chi2_of(joint_l, cl)
    chi2_min_m = float(x2m.min())
    chi2_min_l = float(x2l.min())
    mean_m = float(x2m[x2m <= chi2_min_m + TRIM].mean())
    mean_l = float(x2l[x2l <= chi2_min_l + TRIM].mean())
    dlnL = 0.5 * (mean_l - mean_m)
    return dict(
        chi2_min=chi2_min_m, mean_chi2_trim30=mean_m,
        n_trimmed=int((x2m <= chi2_min_m + TRIM).sum()), n=int(len(x2m)),
        dlnL_trim_vs_lcdm=dlnL,
        _lcdm=dict(chi2_min=chi2_min_l, mean_chi2_trim30=mean_l,
                   n=int(len(x2l))))


OUT = {"method": {
    "mirage_definition": "w_a = -3.66 (1 + w_0), one free parameter w_0 "
                         "(Lodha et al. 2025, arXiv:2503.14743)",
    "prior": "w_0 ~ U[-2.5, 0.5], prior volume V = 3.0; H0 ~ U[40, 100], "
             "omega_bc ~ U[0.130, 0.155] as in all other chains",
    "savage_dickey": "lnB = ln[(1/V) / KDE(p(w_0 = -1 | data))], nested point "
                     "w_0 = -1 implies w_a = 0 (flat LambdaCDM)",
    "mcmc": "Goodman-Weare ensemble, 48 walkers, 2500 steps, 500 burn-in, "
            "2 seeds per dataset",
    "dlnL_semantics": "posterior mean chi2 within Delta-D = 30 of chi2_min "
                      "(likelihood-dominated region), thin factor 16, "
                      "identical to dlnL_decomposition.json",
    "D_KL": "D_KL = Delta<lnL>_trim - lnB_SD",
}}

DATASETS = {
    "mirage_desi_cmb": dict(
        joint=Joint(de="mirage"), ref=Joint(de="lcdm"),
        run_files=[f"chain_mirage_desi_cmb_s{s}.npy" for s in SEEDS],
        ref_files=["chain_lcdm_desi_cmb_s101.npy", "chain_lcdm_desi_cmb_s202.npy"],
        label="DESI DR2 BAO + CMB"),
    "mirage_desi_cmb_pantheon": dict(
        joint=Joint(de="mirage", sn=True), ref=Joint(de="lcdm", sn=True),
        run_files=[f"chain_mirage_sn_s{s}.npy" for s in SEEDS],
        ref_files=["chain_lcdm_sn_s1.npy", "chain_lcdm_sn_s2.npy"],
        label="DESI DR2 BAO + CMB + Pantheon+"),
}

dlnL_path = os.path.join(HERE, "dlnL_decomposition.json")
with open(dlnL_path) as f:
    dlnL = json.load(f)

for key, cfg in DATASETS.items():
    print(f"=== {key} ({cfg['label']}) ===", flush=True)
    joint = cfg["joint"]
    chains = []
    for s in SEEDS:
        fn = os.path.join(CH, cfg["run_files"][SEEDS.index(s)])
        if os.path.exists(fn):
            print("  reusing", fn, flush=True)
        else:
            c = run_mcmc(joint, n_walkers=N_WALKERS, n_steps=N_STEPS,
                         burn=BURN, seed=s)
            np.save(fn, c)
            print("  saved", fn, flush=True)
        chains.append(np.load(fn))
    names = joint.pnames
    summ = summarize(np.concatenate(chains, axis=0), names)
    rhat = split_rhat(chains)
    ess = [int(e) for e in cosmo.ess(np.concatenate(chains, axis=0))]

    w0 = np.concatenate(chains, axis=0)[:, 2]
    lnB_scott, lnB_silver, post = sd_lnb(w0)

    dec = decompose(joint, cfg["ref"], cfg["run_files"], cfg["ref_files"])
    lcdm_info = dec.pop("_lcdm")
    dchi2 = dec["chi2_min"] - lcdm_info["chi2_min"]
    d_kl = dec["dlnL_trim_vs_lcdm"] - lnB_scott

    map_m, x_m = map_opt(joint)
    map_l, x_l = map_opt(cfg["ref"])
    dchi2_opt = map_m - map_l

    OUT[key] = {
        "label": cfg["label"],
        "prior_volume": PRIOR_VOLUME,
        "lnB_SD_scott": lnB_scott, "lnB_SD_silverman": lnB_silver,
        "posterior_density_at_w0_minus1": post,
        "chi2_min": dec["chi2_min"],
        "lcdm_chi2_min": lcdm_info["chi2_min"],
        "dchi2_map_vs_lcdm": dchi2,
        "chi2_MAP_opt": map_m, "MAP_params": dict(zip(names, x_m)),
        "lcdm_chi2_MAP_opt": map_l,
        "lcdm_MAP_params": dict(zip(cfg["ref"].pnames, x_l)),
        "dchi2_MAP_opt_vs_lcdm": dchi2_opt,
        "mean_chi2_trim30": dec["mean_chi2_trim30"],
        "dlnL_trim_vs_lcdm": dec["dlnL_trim_vs_lcdm"],
        "D_KL": d_kl,
        "summary": summ, "Rhat": [round(float(r), 4) for r in rhat],
        "ESS": ess, "n_samples_kde": int(len(w0)),
        "chains": cfg["run_files"],
        "lcdm_reference_chains": cfg["ref_files"],
    }
    dlnL[key] = dec
    print(json.dumps(OUT[key], indent=1), flush=True)

# --- cross-checks against existing released chains -------------------------
print("=== cross-checks ===", flush=True)
jc = Joint(de="cpl")
cc = np.concatenate([np.load(os.path.join(CH, f))
                     for f in ["chain_w0wa_desi_cmb_s111.npy",
                               "chain_w0wa_desi_cmb_s222.npy"]])[::THIN]
x2c = chi2_of(jc, cc)
cpl_chi2_min = float(x2c.min())
cpl_chain = np.concatenate(
    [np.load(os.path.join(CH, f)) for f in ["chain_w0wa_desi_cmb_s111.npy",
                                            "chain_w0wa_desi_cmb_s222.npy"]])
cpl_lnb = cosmo.savage_dickey(cpl_chain[:, 2:4], prior_volume=15.0,
                              lcdm_point=(-1.0, 0.0))
OUT["cross_checks"] = {
    "cpl_chi2_min_thin16": cpl_chi2_min,
    "cpl_lnB_SD_recomputed_V15": cpl_lnb,
    "cpl_chi2_MAP_opt": map_opt(jc)[0],
    "cpl_lnB_SD_canonical": 2.60,
    "mirage_dchi2_vs_cpl_dchi2_desi_cmb": {
        "mirage": OUT["mirage_desi_cmb"]["dchi2_map_vs_lcdm"],
        "cpl": cpl_chi2_min - OUT["mirage_desi_cmb"]["lcdm_chi2_min"]},
    "note": "Mirage should recover most of the CPL Delta-chi2 with one "
            "parameter; CPL lnB recomputation validates the KDE pipeline "
            "against the canonical Savage-Dickey artifact.",
}
print(json.dumps(OUT["cross_checks"], indent=1), flush=True)

with open(os.path.join(HERE, "mirage_sd.json"), "w") as f:
    json.dump(OUT, f, indent=2)
with open(dlnL_path, "w") as f:
    json.dump(dlnL, f, indent=2)
print("wrote mirage_sd.json and updated dlnL_decomposition.json", flush=True)
