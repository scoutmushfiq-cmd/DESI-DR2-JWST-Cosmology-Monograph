"""Stage 1 validation: theory sanity checks + profile-likelihood cross-checks."""
import numpy as np, json, time
import cosmo as cm

res = {}

# --- T1: theta* at Planck fiducial must reproduce 0.0104110 by construction
ts = cm.theta_star(67.36, 0.3153)
res["theta_fid"] = float(ts[0])

# --- T2: r_s(z*) and r_d sanity
g = cm.geometry(67.36, 0.3153)
iz = np.searchsorted(cm.ZGRID, cm.Z_STAR)
rs_star = g["rs"][0][iz] * cm.C_KMS / (np.sqrt(3.0) * 67.36)
res["rs_star_Mpc_raw"] = float(rs_star)   # uncalibrated; calibration factor below
res["TS_CAL"] = float(cm.TS_CAL)

# --- T3: H0*rd product for DESI+CMB LCDM best fit
# profile over (H0, Om) with w fixed
j = cm.Joint(w0wa=False)
t0 = time.time()
prof = cm.profile(j, fixed=None, grid=[0]) if False else None
# direct minimization over both params
from scipy import optimize
r = optimize.minimize(lambda x: j.chi2(np.array(x)[None, :])[0],
                      [68.0, 0.303], method="Nelder-Mead",
                      options=dict(xatol=1e-8, fatol=1e-10, maxiter=4000))
res["LCDM_DESI_CMB_best"] = dict(H0=float(r.x[0]), Om=float(r.x[1]), chi2=float(r.fun))
# 1-sigma from curvature (Hessian)
def hess(f, x, h=1e-4):
    n = len(x); H = np.zeros((n, n))
    for i in range(n):
        for k in range(n):
            e_i = np.eye(n)[i] * h; e_k = np.eye(n)[k] * h
            H[i, k] = (f(x + e_i + e_k) - f(x + e_i - e_k) - f(x - e_i + e_k) + f(x - e_i - e_k)) / (4 * h * h)
    return H
H = hess(lambda x: j.chi2(np.array(x)[None, :])[0], r.x)
cov = cm.cov_from_hess(H)
res["LCDM_DESI_CMB_sigma"] = dict(H0=float(np.sqrt(cov[0, 0])), Om=float(np.sqrt(cov[1, 1])),
                                  corr=float(cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])))

# --- T4: DESI alone -> Om (profile over H0)
j2 = cm.Joint(w0wa=False, cmb=False)
g_grid = np.linspace(0.25, 0.36, 45)
p = cm.profile(j2, fixed=(1,), grid=g_grid)
chi = np.array([x[1] for x in p]); oms = np.array([x[0] for x in p])
i0 = np.argmin(chi)
res["LCDM_DESI_only_Om"] = float(oms[i0])
# interpolate delta chi2 = 1 crossing
d = chi - chi[i0]
above = np.where(d > 1.0)[0]
if len(above):
    lo = oms[above[above < i0]].max() if any(above < i0) else oms[i0]
    hi = oms[above[above > i0]].min() if any(above > i0) else oms[i0]
    res["LCDM_DESI_only_Om_err"] = [float(oms[i0]-lo), float(hi-oms[i0])]
res["LCDM_DESI_only_chi2min"] = float(chi[i0])

# --- T5: w0waCDM DESI+CMB (compressed) best fit -> target w0=-0.43, wa=-1.72, H0=63.7
j3 = cm.Joint(w0wa=True)
r3 = optimize.minimize(lambda x: j3.chi2(np.array(x)[None, :])[0],
                       [64.0, 0.35, -0.4, -1.7], method="Nelder-Mead",
                       options=dict(xatol=1e-8, fatol=1e-10, maxiter=8000, maxfev=8000))
res["W0WA_DESI_CMB_best"] = dict(H0=float(r3.x[0]), Om=float(r3.x[1]),
                                 w0=float(r3.x[2]), wa=float(r3.x[3]), chi2=float(r3.fun))
H3 = hess(lambda x: j3.chi2(np.array(x)[None, :])[0], r3.x, h=1e-4)
cov3 = cm.cov_from_hess(H3)
res["W0WA_DESI_CMB_sigma"] = {n: float(np.sqrt(cov3[k, k])) for k, n in enumerate(["H0","Om","w0","wa"])}
res["W0WA_corr"] = float(cov3[2, 3] / np.sqrt(cov3[2, 2] * cov3[3, 3]))
res["dchi2_MAP_w0wa_vs_LCDM_DESI_CMB"] = float(r.fun - r3.fun)

# --- T6: pivot scale factor from posterior covariance (analytic from Hessian)
a_p = 1.0 + cov3[2, 3] / cov3[3, 3]
res["a_pivot"] = float(a_p)
res["z_pivot"] = float(1.0 / a_p - 1.0)
res["sigma_wp_factor"] = float(np.sqrt(1.0 - (cov3[2, 3]**2) / (cov3[2, 2] * cov3[3, 3])))

# --- T7: LCDM j0 and z_t check (must give j0=1, z_t ~ 0.65-0.67 for Om=0.3)
res["LCDM_j0_numeric"] = float(cm.j_of_z_numeric(0.0, 0.3153, -1.0, 0.0, 67.36))
res["LCDM_zt_numeric"] = float(cm.q_of_z(0.65, 0.3153, -1.0, 0.0, 67.36))
res["LCDM_q0_formula"] = float(0.5 + 1.5 * (1 - 0.3153) * (-1.0))

# --- T8: CPL j0 at DESI+CMB best fit (Eq. 23 of paper vs numeric)
Om3, w03, wa3 = r3.x[1], r3.x[2], r3.x[3]
res["CPL_j0_eq23"] = float(1.0 + 1.5 * (1 - Om3) * (3 * w03 * (1 + w03) + wa3))
res["CPL_j0_numeric"] = float(cm.j_of_z_numeric(0.0, Om3, w03, wa3, r3.x[0]))
res["CPL_q0_eq22"] = float(0.5 + 1.5 * (1 - Om3) * w03)
res["CPL_q0_numeric"] = float(cm.q_of_z(0.0, Om3, w03, wa3, r3.x[0]))
res["CPL_zc_bestfit"] = float(-w03 / wa3 - 1.0)

res["timing_profile_s"] = time.time() - t0
print(json.dumps(res, indent=2))
json.dump(res, open("stage1_checks.json", "w"), indent=2)
