import json, numpy as np, cosmo as cm, time
results = {}
def run(tag, joint, seed, n_steps=2500, burn=500):
    t0 = time.time()
    ch = cm.run_mcmc(joint, n_walkers=48, n_steps=n_steps, burn=burn, seed=seed)
    np.save(f"chain_{tag}.npy", ch)
    s = cm.summarize(ch, joint.pnames)
    results[tag] = {k: [round(v["mean"],4), round(v["std"],4)] for k,v in s.items()}
    results[tag]["ess"] = [round(float(x)) for x in cm.ess(ch)]
    print(f"{tag}: done ({time.time()-t0:.0f}s)", flush=True)
run("jbp_desi_cmb_s22", cm.Joint(de="jbp"), 22)
run("log_desi_cmb_s11", cm.Joint(de="log"), 11)
run("log_desi_cmb_s22", cm.Joint(de="log"), 22)
json.dump(results, open("remaining_results.json","w"), indent=1)
print("DONE")
