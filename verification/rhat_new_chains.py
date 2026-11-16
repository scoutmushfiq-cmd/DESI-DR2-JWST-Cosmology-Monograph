"""Split-Rhat for the eight Union3 / DES-Dovekie chains committed in
verification/chains/ (the runtime Rhat in sn_extra_results.json covers only
the Mirage pairs). The committed chains are flattened (96,000 x n) draws, so
the Gelman-Rubin statistic is computed on 8 disjoint 12,000-draw segments
(split-Rhat); for the Mirage pairs the two seeds are additionally treated as
independent chains. Writes rhat_new_chains.json.

Run from verification/:  python rhat_new_chains.py
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

CHAIN_PARAMS = {
    "chain_lcdm_union3_s101.npy": ["H0", "wbc"],
    "chain_lcdm_desy5_s101.npy": ["H0", "wbc"],
    "chain_cpl_union3_s1.npy": ["H0", "wbc", "w0", "wa"],
    "chain_cpl_desy5_s1.npy": ["H0", "wbc", "w0", "wa"],
    "chain_mirage_union3_s71.npy": ["H0", "wbc", "w0"],
    "chain_mirage_union3_s72.npy": ["H0", "wbc", "w0"],
    "chain_mirage_desy5_s71.npy": ["H0", "wbc", "w0"],
    "chain_mirage_desy5_s72.npy": ["H0", "wbc", "w0"],
}

MIRAGE_PAIRS = {
    "mirage_union3": ["chain_mirage_union3_s71.npy", "chain_mirage_union3_s72.npy"],
    "mirage_desy5": ["chain_mirage_desy5_s71.npy", "chain_mirage_desy5_s72.npy"],
}


def gelman_rubin(segs):
    m, n, d = segs.shape
    means = segs.mean(axis=1)
    B = n * means.var(axis=0, ddof=1)
    W = segs.var(axis=1, ddof=1).mean(axis=0)
    vhat = (n - 1) / n * W + B / n
    return np.sqrt(vhat / W)


def main():
    out = {"method": "split-Rhat: 8 disjoint 12,000-draw segments per chain "
                     "(Gelman-Rubin); Mirage pairs additionally cross-seed "
                     "(2 seeds x 4 segments)",
           "chains": {}}
    for f, names in CHAIN_PARAMS.items():
        c = np.load(os.path.join(HERE, "chains", f))
        segs = c.reshape(8, -1, c.shape[1])
        r = gelman_rubin(segs)
        out["chains"][f] = {n: round(float(x), 5) for n, x in zip(names, r)}
    for pair, files in MIRAGE_PAIRS.items():
        cs = [np.load(os.path.join(HERE, "chains", f)) for f in files]
        d = cs[0].shape[1]
        segs = np.stack([c[i * 12000:(i + 1) * 12000] for c in cs
                         for i in range(8)])
        r = gelman_rubin(segs)
        out["chains"][pair + "__crossseed"] = {
            n: round(float(x), 5) for n, x in zip(CHAIN_PARAMS[files[0]], r)}
    allvals = [v for entry in out["chains"].values() for v in entry.values()]
    out["max_rhat"] = round(max(allvals), 5)
    json.dump(out, open(os.path.join(HERE, "rhat_new_chains.json"), "w"),
              indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
