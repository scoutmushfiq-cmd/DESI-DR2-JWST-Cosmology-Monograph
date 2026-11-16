import json, numpy as np, cosmo as cm, time

results = {}

def run(tag, joint, seed, n_steps=2500, burn=500):
    t0 = time.time()
    ch = cm.run_mcmc(joint, n_walkers=48, n_steps=n_steps, burn=burn, seed=seed)
    np.save(f"chain_{tag}.npy", ch)
    names = joint.pnames
    s = cm.summarize(ch, names)
    results[tag] = {k: [round(v["mean"],4), round(v["std"],4)] for k,v in s.items()}
    results[tag]["ess"] = [round(float(x)) for x in cm.ess(ch)]
    print(f"{tag}: {dict((k, results[tag][k]) for k in names)} ESS={results[tag]['ess']} ({time.time()-t0:.0f}s)", flush=True)
    return ch

JL = cm.Joint(de="lcdm")
JC = cm.Joint(de="cpl")
JW = cm.Joint(de="wcdm")
JJ = cm.Joint(de="jbp")
JG = cm.Joint(de="log")

# multi-seed convergence runs
for seed in [101, 202, 303]:
    run(f"lcdm_desi_cmb_s{seed}", JL, seed)
for seed in [111, 222, 333]:
    run(f"w0wa_desi_cmb_s{seed}", JC, seed)
run("w0wa_desi_cmb_cc_s777", cm.Joint(de="cpl", cc=True), 777)

# new parametrizations (2 seeds each)
for seed in [11, 22]:
    run(f"wcdm_desi_cmb_s{seed}", JW, seed)
for seed in [11, 22]:
    run(f"jbp_desi_cmb_s{seed}", JJ, seed)
for seed in [11, 22]:
    run(f"log_desi_cmb_s{seed}", JG, seed)

json.dump(results, open("nature_suite_results.json","w"), indent=1)
print("DONE")
