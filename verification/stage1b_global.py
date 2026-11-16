"""Stage 1b: robust global optimization via coarse grid + Nelder-Mead polish."""
import numpy as np, json
from scipy import optimize
import cosmo as cm

def global_min(joint, n_grid=40, polish_starts=6, seed=0):
    b = joint.bounds()
    rng = np.random.default_rng(seed)
    # coarse random + edge search
    cand = [np.array([(lo + hi) / 2 for lo, hi in b])]
    for _ in range(600):
        x = np.array([rng.uniform(lo, hi) for lo, hi in b])
        cand.append(x)
    chi = np.array([joint.chi2(x[None, :])[0] for x in cand])
    order = np.argsort(chi)
    best = None
    for i in order[:polish_starts]:
        r = optimize.minimize(lambda x: joint.chi2(np.array(x)[None, :])[0], cand[i],
                              method="Nelder-Mead",
                              options=dict(xatol=1e-8, fatol=1e-10, maxiter=20000, maxfev=20000))
        if best is None or r.fun < best.fun:
            best = r
    return best

def hess(f, x, h=1e-4):
    n = len(x); H = np.zeros((n, n))
    for i in range(n):
        for k in range(n):
            ei = np.eye(n)[i] * h; ek = np.eye(n)[k] * h
            H[i, k] = (f(x + ei + ek) - f(x + ei - ek) - f(x - ei + ek) + f(x - ei - ek)) / (4 * h * h)
    return H

res = {}

# LCDM DESI+CMB
j = cm.Joint(w0wa=False)
r = global_min(j)
H = hess(lambda x: j.chi2(np.array(x)[None, :])[0], r.x)
cov = cm.cov_from_hess(H)
res["LCDM_DESI_CMB"] = dict(H0=float(r.x[0]), Om=float(r.x[1]), chi2=float(r.fun),
                            s_H0=float(np.sqrt(cov[0, 0])), s_Om=float(np.sqrt(cov[1, 1])),
                            corr=float(cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])))
print("LCDM DESI+CMB:", res["LCDM_DESI_CMB"])

# w0wa DESI+CMB
j3 = cm.Joint(w0wa=True)
r3 = global_min(j3)
H3 = hess(lambda x: j3.chi2(np.array(x)[None, :])[0], r3.x)
cov3 = cm.cov_from_hess(H3)
res["W0WA_DESI_CMB"] = dict(
    H0=float(r3.x[0]), Om=float(r3.x[1]), w0=float(r3.x[2]), wa=float(r3.x[3]),
    chi2=float(r3.fun),
    s_H0=float(np.sqrt(cov3[0, 0])), s_Om=float(np.sqrt(cov3[1, 1])),
    s_w0=float(np.sqrt(cov3[2, 2])), s_wa=float(np.sqrt(cov3[3, 3])),
    corr_w0wa=float(cov3[2, 3] / np.sqrt(cov3[2, 2] * cov3[3, 3])))
res["dchi2_MAP"] = float(r.fun - r3.fun)
a_p = 1.0 + cov3[2, 3] / cov3[3, 3]
res["pivot"] = dict(a_p=float(a_p), z_p=float(1 / a_p - 1),
                    sigma_wp_factor=float(np.sqrt(1 - cov3[2, 3]**2 / (cov3[2, 2] * cov3[3, 3]))))
print("W0WA DESI+CMB:", res["W0WA_DESI_CMB"])
print("dchi2_MAP:", res["dchi2_MAP"], " pivot:", res["pivot"])

json.dump(res, open("stage1b_global.json", "w"), indent=2)
