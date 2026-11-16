"""MAP-level variant scan: which Pantheon+ treatment reproduces the paper's
DESI+CMB+Pantheon+ CPL row (H0~67.4-67.5, w0~-0.84, wa~-0.57..-0.62)?"""
import json
import numpy as np
from scipy.optimize import minimize
import cosmo
from cosmo import Joint, chi2_sn

def load_variant(kind):
    d = np.genfromtxt("pantheon/sn_data.dat", names=True, dtype=None, encoding="utf-8")
    N = int(open("pantheon/sn_cov.cov").readline().split()[0])
    C = np.loadtxt("pantheon/sn_cov.cov", skiprows=1).reshape(N, N)
    C = 0.5 * (C + C.T)
    if kind == "zhd_all":
        m = np.ones(N, bool); z = d["zHD"]
    elif kind == "zcmb_all":
        m = np.ones(N, bool); z = d["zCMB"]
    elif kind == "zhd_cut":
        m = (d["IS_CALIBRATOR"] == 0) & (d["zHD"] > 0.01); z = d["zHD"]
    elif kind == "zcmb_cut":
        m = (d["IS_CALIBRATOR"] == 0) & (d["zCMB"] > 0.01); z = d["zCMB"]
    C = C[np.ix_(m, m)]
    Cinv = np.linalg.inv(C)
    return {"z": z[m].astype(float), "mb": d["m_b_corr"][m].astype(float),
            "Cinv": Cinv, "Cinv_1": Cinv @ np.ones(m.sum()),
            "C_11": float(np.ones(m.sum()) @ (Cinv @ np.ones(m.sum()))), "N": int(m.sum())}

def chi2_sn_var(S, H0, Om, w0, wa):
    g = cosmo.geometry(np.atleast_1d(H0), np.atleast_1d(Om), w0, wa)
    I_at = np.array([np.interp(S["z"], cosmo.ZGRID, g["I"][k]) for k in range(len(np.atleast_1d(H0)))])
    DL = np.maximum((1.0 + S["z"])[None, :] * (cosmo.C_KMS / np.atleast_1d(H0)[:, None]) * I_at, 1e-8)
    r = S["mb"][None, :] - (5.0 * np.log10(DL) + 25.0)
    Cr = r @ S["Cinv"].T
    A = np.einsum("ni,ni->n", r, Cr)
    B = Cr @ np.ones(S["N"])
    return (A - B ** 2 / S["C_11"])[0]

results = {}
for kind in ["zhd_all", "zcmb_all", "zhd_cut", "zcmb_cut"]:
    S = load_variant(kind)
    def total(x, with_cc=False):
        H0, wbc, w0, wa = x
        Om = (wbc + cosmo.W_NU) / (H0 / 100.0) ** 2
        c = cosmo.chi2_bao(np.array([H0]), np.array([Om]), w0, wa)[0]
        c += cosmo.chi2_cmb(np.array([H0]), np.array([Om]), w0, wa)[0]
        c += ((wbc - cosmo.X_CMB_OBS[2]) / cosmo.SIG_WBC) ** 2
        c += ((cosmo.W_B_FID - cosmo.X_CMB_OBS[1]) / cosmo.SIG_WB) ** 2
        c += chi2_sn_var(S, H0, Om, w0, wa)
        return c
    best = None
    for x0 in ([67.5, 0.142, -0.84, -0.6], [68.0, 0.141, -0.75, -0.9], [67.0, 0.143, -0.9, -0.4]):
        r = minimize(total, x0, method="Nelder-Mead",
                     options={"maxiter": 4000, "xatol": 1e-4, "fatol": 1e-4})
        if best is None or r.fun < best.fun:
            best = r
    H0, wbc, w0, wa = best.x
    Om = (wbc + cosmo.W_NU) / (H0 / 100.0) ** 2
    results[kind] = {"chi2": float(best.fun), "H0": float(H0), "Om": float(Om),
                     "w0": float(w0), "wa": float(wa)}
    print(kind, "->", results[kind], flush=True)

with open("sn_variant_scan.json", "w") as f:
    json.dump(results, f, indent=2)
