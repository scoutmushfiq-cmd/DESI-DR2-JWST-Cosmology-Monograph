"""Stage 2: full MCMC suite — recreates the monograph's Table 5 (bottom rows)."""
import numpy as np, json, time, sys
import cosmo as cm

OUT = {}
t_start = time.time()

def run(name, joint, **kw):
    t0 = time.time()
    p0 = cm.init_walkers_on_band(joint, kw.get("n_walkers", 48), seed=hash(name) % 2**31)
    chain = cm.run_mcmc(joint, p0=p0, **{k: v for k, v in kw.items() if k != "n_walkers"})
    summ = cm.summarize(chain, joint.pnames)
    OUT[name] = dict(summary=summ, n_samples=int(len(chain)),
                     runtime_s=round(time.time() - t0, 1))
    np.save(f"chain_{name}.npy", chain)
    print(f"[{name}] " + ", ".join(f"{k}={v['mean']:.4f}+-{v['std']:.4f}" for k, v in summ.items()),
          f"({OUT[name]['runtime_s']}s)", flush=True)
    return chain

# 1. LCDM DESI+CMB  (target: H0=68.17+-0.28, Om=0.3027+-0.0036)
c1 = run("lcdm_desi_cmb", cm.Joint(w0wa=False), n_walkers=48, n_steps=2500, burn=500)

# 2. w0wa DESI+CMB (target, monograph compressed-CMB row: w0=-0.43+-0.22, wa=-1.72+-0.64)
c2 = run("w0wa_desi_cmb", cm.Joint(w0wa=True), n_walkers=48, n_steps=3000, burn=600)

# 3. w0wa DESI+CMB+CC (monograph proxy: base MCMC row w0=-0.846+-0.050 with PP)
c3 = run("w0wa_desi_cmb_cc", cm.Joint(w0wa=True, cc=True), n_walkers=48, n_steps=3000, burn=600)

# 4. + SH0ES prior (target: H0=68.64+-0.50, w0=-0.866+-0.051, wa=-0.678+-0.217)
c4 = run("w0wa_desi_cmb_cc_shoes", cm.Joint(w0wa=True, cc=True, h0_prior=(73.04, 1.04)),
         n_walkers=48, n_steps=3000, burn=600)

# 5. + JWST CCHP TRGB prior (target: H0=67.52+-0.54, w0=-0.849+-0.050, wa=-0.571+-0.192)
c5 = run("w0wa_desi_cmb_cc_trgb", cm.Joint(w0wa=True, cc=True, h0_prior=(70.39, 1.94)),
         n_walkers=48, n_steps=3000, burn=600)

# 6. rd-free LCDM DESI+CC (partial check of monograph rd-free row: H0=69.24+-1.82)
c6 = run("rdfree_lcdm_desi_cc", cm.Joint(w0wa=False, rd_free=True, cmb=False, cc=True),
         n_walkers=48, n_steps=2500, burn=500)

OUT["total_runtime_s"] = round(time.time() - t_start, 1)
json.dump(OUT, open("mcmc_results.json", "w"), indent=2)
print("DONE in", OUT["total_runtime_s"], "s")
