import json, numpy as np, cosmo as cm

res = {}

# --- derived CPL quantities from w0wa chains (convert wbc -> Om) ---
for tag, f in [("desi_cmb", "chain_w0wa_desi_cmb.npy"),
               ("desi_cmb_cc", "chain_w0wa_desi_cmb_cc.npy")]:
    ch = np.load(f)
    H0, wbc, w0, wa = ch[:,0], ch[:,1], ch[:,2], ch[:,3]
    Om = (wbc + cm.W_NU) / (H0/100)**2
    conv = np.column_stack([H0, Om, w0, wa])
    res[f"derived_{tag}"] = cm.derived_cpl(conv)

# --- GP reconstruction ---
try:
    g = cm.gp_hz()
    res["gp"] = {"sigma_f": g["sf"], "ell_f": g["lf"],
                 "q0": g["q0"], "z_t": g["z_t"]}
except Exception as e:
    res["gp_error"] = repr(e)

# --- Savage-Dickey ln B (w0wa chains; LCDM point (-1,0)) ---
for tag, f, pv in [("desi_cmb", "chain_w0wa_desi_cmb.npy", 15.0),
                   ("desi_cmb_cc", "chain_w0wa_desi_cmb_cc.npy", 15.0)]:
    ch = np.load(f)
    res[f"lnB_{tag}"] = cm.savage_dickey(ch[:, 2:4], prior_volume=pv)

# --- tension matrix: early vs late rows ---
early = [("Planck2018",), ("DESI+CMB (LCDM)",), ("DESI+CMB+PP (w0wa)",),
         ("DESI+CMB+Y5 (w0wa)",), ("DESI+CMB+U3 (w0wa)",)]
rows = [cm.H0_LADDER[k[0]] for k in early]
cols = [cm.H0_LADDER[k] for k in ["SH0ES 2022", "SH0ES 2024 (42SN)",
                                  "JWST Cepheid (D<25)", "JWST joint 3-method"]]
T = cm.tension_matrix(rows, cols)
res["tension"] = {k[0]: {c: round(float(T[i,j]),2) for j,c in
                  enumerate(["SH0ES22","SH0ES24","JWST_Cep","JWST_joint"])}
                  for i,k in enumerate(early)}

# --- Mirage DE check: 1-param model wa = -3.66*(1+w0) vs full CPL ---
def mirage_chi2():
    from scipy import optimize
    J = cm.Joint(w0wa=True)
    def f2(x):  # x = [H0, wbc, w0]; wa = -3.66*(1+w0)
        p = np.atleast_2d(x).copy()
        p = np.column_stack([p, -3.66*(1.0+p[:,2])])
        return J.chi2(p)[0]
    best = None
    for x0 in [[68.,0.1423,-0.8], [65.,0.140,-0.6], [70.,0.144,-1.0]]:
        r = optimize.minimize(f2, x0, method="Nelder-Mead",
                              options=dict(xatol=1e-7, fatol=1e-9, maxiter=8000))
        if best is None or r.fun < best.fun: best = r
    return float(best.fun), [float(v) for v in best.x]
mchi, mx = mirage_chi2()
res["mirage"] = {"chi2": mchi, "best": mx}

# best-fit CPL chi2 for comparison (from global min on band)
res["cpl_best_chi2_ref"] = json.load(open("stage1c_min.json")) if False else None

json.dump(res, open("stage2_checks.json","w"), indent=1, default=str)
print(json.dumps(res, indent=1, default=str))
