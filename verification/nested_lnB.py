"""Pure-numpy ellipsoidal nested sampling: an independent cross-check of the
Savage-Dickey KDE Bayes factors (the Round-7/Nature-readiness referee risk:
SD lnB rests on a KDE density estimate at the nested point; nested sampling
integrates the evidence directly, with no KDE and no nested-point density).

Runs one (dataset, model) pair per invocation and checkpoints into
nested_lnB.json:

    python nested_lnB.py desi_cmb lcdm
    python nested_lnB.py desi_cmb mirage
    python nested_lnB.py desi_cmb cpl
    python nested_lnB.py sn mirage          # DESI DR2 + CMB + Pantheon+
    python nested_lnB.py union3 mirage ...

Priors mirror the MCMC exactly (H0 ~ U[40,100], omega_bc ~ U[0.130,0.155],
w0 ~ U[-2.5,0.5] for Mirage, (w0,wa) ~ U[-2.5,0.5] x U[-4,1] for CPL), so
lnB(model, LambdaCDM) = lnZ_model - lnZ_LambdaCDM on the same data.

Algorithm: standard nested sampling with nlive live points; at each
iteration the worst point is replaced by rejection sampling from a
single ellipsoid (mean/covariance of the live points, scale-expanded)
until the logZ remaining-mass estimate falls below the tolerance.
"""
import json
import os
import sys

import numpy as np
from scipy.special import logsumexp

import cosmo
from cosmo import Joint

HERE = os.path.dirname(os.path.abspath(__file__))

DATASETS = {
    "desi_cmb": dict(),
    "sn": dict(sn=True),
    "union3": dict(sn=True, sn_set="union3"),
    "desy5": dict(sn=True, sn_set="desy5"),
}
MODELS = {
    "lcdm": dict(de="lcdm"),
    "mirage": dict(de="mirage"),
    "cpl": dict(de="cpl"),
    "wcdm": dict(de="wcdm"),
}
NLIVE = 128
TARGET_dlnZ = 0.10
SEED = 2026
NBATCH = 128


def logL_batch(joint, X):
    return -0.5 * joint.chi2(X)


def ellipsoid_sample(m, C, f2, n, rng):
    d = len(m)
    L = np.linalg.cholesky(C)
    z = rng.standard_normal((n, d))
    z /= np.linalg.norm(z, axis=1, keepdims=True)
    rad = np.sqrt(f2) * rng.uniform(size=(n, 1)) ** (1.0 / d)
    return m[None, :] + (z * rad) @ L.T


def mahalanobis_max(X, m, C):
    Ci = np.linalg.inv(C)
    dm = X - m[None, :]
    return np.max(np.einsum("ij,jk,ik->i", dm, Ci, dm))


def nested_run(joint, d, nlive=NLIVE, target=TARGET_dlnZ, seed=SEED,
               expand=1.5, nbatch=NBATCH):
    rng = np.random.default_rng(seed)
    b = joint.bounds()

    def prior(n):
        return np.column_stack(
            [rng.uniform(lo, hi, size=n) for lo, hi in b])

    X = prior(nlive)
    L = logL_batch(joint, X)
    logw_shell = np.log1p(-np.exp(-1.0 / nlive))     # log(1 - e^{-1/nlive})
    logZ = -1e300
    logZ2 = 0.0
    logSWL = -1e300
    t = 0
    logX = 0.0
    while True:
        i = int(L.argmin())
        logZ = np.logaddexp(logZ, L[i] + logX + logw_shell)
        logZ2 = np.logaddexp(logZ2, 2 * L[i] + 2 * logX + 2 * logw_shell)
        logSWL = np.logaddexp(logSWL, 2 * L[i] + logX + logw_shell)
        Lw = L[i]
        logX -= 1.0 / nlive
        t += 1
        # remaining-mass termination: logX + max(L) below logZ by target
        if logX + L.max() - logZ < target:
            break
        if t > 200000:
            break
        # ellipsoid around live points (excluding the dead one)
        live = np.delete(X, i, axis=0)
        m = live.mean(axis=0)
        C = np.cov(live.T)
        C = np.atleast_2d(C)
        r2max = mahalanobis_max(live, m, C)
        f2 = r2max * expand ** 2
        done = False
        f2_try = f2
        for attempt in range(60):
            prop = ellipsoid_sample(m, C, f2_try, nbatch, rng)
            ok = np.all((prop >= np.array(b)[:, 0]) &
                        (prop <= np.array(b)[:, 1]), axis=1)
            prop = prop[ok]
            if len(prop):
                Lp = logL_batch(joint, prop)
                acc = Lp > Lw
                if acc.any():
                    j = int(np.flatnonzero(acc)[rng.integers(acc.sum())])
                    X[i] = prop[j]
                    L[i] = Lp[j]
                    done = True
                    break
            f2_try *= 2.0          # enlarge and retry
        if not done:
            # fallback: sample from the prior (rare)
            for _ in range(10000):
                x = prior(1)[0]
                lx = logL_batch(joint, x[None, :])[0]
                if lx > Lw:
                    X[i], L[i] = x, lx
                    break
    # final: average the live points over the remaining shell (trapezoid)
    logZ = np.logaddexp(logZ,
                        logsumexp(L) - np.log(nlive) + logX)
    logZ2 = np.logaddexp(logZ2,
                         logsumexp(2 * L) + 2 * logX - 2 * np.log(nlive))
    logSWL = np.logaddexp(logSWL,
                          logsumexp(2 * L) + logX - np.log(nlive))
    with np.errstate(invalid="ignore", over="ignore"):
        d2 = logZ2 - 2 * logZ
        err = float(np.sqrt(np.expm1(d2))) if 0 <= d2 < 25 else np.nan
        H = float(np.exp(logSWL - logZ) - logZ) if logSWL > -1e299 else np.nan
        err_param = float(np.sqrt(max(H, 0.0) / nlive)) if np.isfinite(H) else np.nan
    return float(logZ), err, t, H, err_param


def main(ds, model, seed=SEED, nlive=NLIVE):
    out_path = os.path.join(HERE, "nested_lnB.json")
    out = json.load(open(out_path)) if os.path.exists(out_path) else {}
    key = f"{model}_{ds}_s{seed}"
    joint = Joint(**MODELS[model], **DATASETS[ds])
    d = len(joint.pnames)
    lnZ, err, it, H, err_param = nested_run(joint, d, seed=seed, nlive=nlive)
    out[key] = {"lnZ": lnZ, "lnZ_err": err, "iterations": it,
                "H": H, "err_paramfree": err_param,
                "nlive": nlive, "d": d, "seed": seed,
                "priors": "H0~U[40,100], wbc~U[0.130,0.155], "
                          + ("w0~U[-2.5,0.5] (V=3.0)" if model == "mirage"
                             else "w0~U[-2.5,0.5], wa~U[-4,1] (V=15)"
                             if model == "cpl" else "w~U[-2,0.5] (V=2.5)"
                             if model == "wcdm" else "-")}
    json.dump(out, open(out_path, "w"), indent=2)
    print(key, "lnZ =", round(lnZ, 3), "+/-", round(err, 3),
          "iterations", it, flush=True)
    lcdm_keys = [k for k in out if k.startswith(f"lcdm_{ds}")]
    if lcdm_keys:
        lnB = lnZ - out[lcdm_keys[0]]["lnZ"]
        out[key]["lnB_vs_lcdm"] = lnB
        json.dump(out, open(out_path, "w"), indent=2)
        print("lnB(model, LambdaCDM) =", round(lnB, 3), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],
         int(sys.argv[3]) if len(sys.argv) > 3 else SEED,
         int(sys.argv[4]) if len(sys.argv) > 4 else NLIVE)
