"""Round-15 M3 fix: committed generator for the canonical Savage-Dickey
artifact, plus a chain-subset scatter analysis that quantifies the
posterior-sampling systematic of the density-ratio estimator.

Background: savage_dickey_canonical.json was produced by an ad-hoc run and
had no committed generator (only its V15_scott_2chains field was
reproducible, via the run_mirage_sd.py cross-check). This script regenerates
every lnB row of that artifact from the committed chains with the same
estimator (cosmo.savage_dickey: Gaussian KDE at the nested LambdaCDM point,
lnB = ln[(1/V) / post]) and asserts exact agreement:

  wcdm : 1-D KDE on w0, prior volume V = 2.5,  chains wcdm s11+s22
  cpl  : 2-D KDE on (w0, wa), V = 15, all four DESI DR2 + CMB CPL chains
         (n = 403,200); variants V = 13.5 and the two-chain subset s111+s222
  jbp  : 2-D KDE on (w0, wa), V = 15,          chains jbp s11+s22
  log  : 2-D KDE on (w0, wa), V = 15,          chains log s11+s22

It then computes the Savage-Dickey lnB for every subset of the four CPL
chains (4 singles, 6 pairs; triples omitted as redundant with the complements)
and writes sd_chain_scatter.json with the scatter statistics quoted in the
manuscript's evidence-semantics paragraph.

The z_c block of savage_dickey_canonical.json is a legacy computation from
the same ad-hoc run and is NOT regenerated; it is retained in the artifact
as-is (see VERIFICATION_REPORT.md Round 15).

Run from verification/:  python run_sd_canonical.py   (~1 min)
"""
import itertools
import json
import os

import numpy as np

import cosmo

HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.path.join(HERE, "chains")
CANON = os.path.join(HERE, "savage_dickey_canonical.json")
SCATTER = os.path.join(HERE, "sd_chain_scatter.json")

CPL_FILES = ["chain_w0wa_desi_cmb.npy", "chain_w0wa_desi_cmb_s111.npy",
             "chain_w0wa_desi_cmb_s222.npy", "chain_w0wa_desi_cmb_s333.npy"]


def sd(files, cols, volume, point):
    chain = np.concatenate([np.load(os.path.join(CH, f)) for f in files])
    return cosmo.savage_dickey(chain[:, cols], volume, point)


def main():
    canon = json.load(open(CANON))

    vals = {
        "wcdm_lnB_scott": sd(["chain_wcdm_desi_cmb_s11.npy",
                              "chain_wcdm_desi_cmb_s22.npy"],
                             slice(2, 3), 2.5, (-1.0,)),
        "cpl_V15_all4chains": sd(CPL_FILES, slice(2, 4), 15.0, (-1.0, 0.0)),
        "cpl_V13.5_all4chains": sd(CPL_FILES, slice(2, 4), 13.5, (-1.0, 0.0)),
        "cpl_V15_2chains_s111_s222": sd(["chain_w0wa_desi_cmb_s111.npy",
                                         "chain_w0wa_desi_cmb_s222.npy"],
                                        slice(2, 4), 15.0, (-1.0, 0.0)),
        "jbp_V15": sd(["chain_jbp_desi_cmb_s11.npy",
                       "chain_jbp_desi_cmb_s22.npy"],
                      slice(2, 4), 15.0, (-1.0, 0.0)),
        "log_V15": sd(["chain_log_desi_cmb_s11.npy",
                       "chain_log_desi_cmb_s22.npy"],
                      slice(2, 4), 15.0, (-1.0, 0.0)),
    }
    targets = {
        "wcdm_lnB_scott": canon["wcdm"]["lnB_scott"],
        "cpl_V15_all4chains": canon["cpl"]["V15_scott"],
        "cpl_V13.5_all4chains": canon["cpl"]["V13.5_scott"],
        "cpl_V15_2chains_s111_s222": canon["cpl"]["V15_scott_2chains"],
        "jbp_V15": canon["jbp"]["V15_scott"],
        "log_V15": canon["log"]["V15_scott"],
    }
    for k, v in vals.items():
        assert abs(v - targets[k]) < 5e-3, \
            "canonical lnB row %s not reproduced: %.6f vs %.6f" \
            % (k, v, targets[k])
        print("canonical row reproduced: %-28s %+.4f (target %+.4f)"
              % (k, v, targets[k]))

    chains = [np.load(os.path.join(CH, f))[:, 2:4] for f in CPL_FILES]
    singles, pairs = {}, {}
    for i, c in enumerate(chains):
        singles[CPL_FILES[i]] = cosmo.savage_dickey(c, 15.0, (-1.0, 0.0))
    for i, j in itertools.combinations(range(4), 2):
        pairs["%s+%s" % (CPL_FILES[i], CPL_FILES[j])] = \
            cosmo.savage_dickey(np.concatenate([chains[i], chains[j]]),
                                15.0, (-1.0, 0.0))
    s_val = np.array(list(singles.values()))
    p_val = np.array(list(pairs.values()))
    out = {
        "estimator": "cosmo.savage_dickey, 2-D KDE on (w0, wa), V = 15, "
                     "nested point (w0, wa) = (-1, 0)",
        "cpl_files": CPL_FILES,
        "n_all4chains": int(sum(len(c) for c in chains)),
        "all4chains_lnB": float(vals["cpl_V15_all4chains"]),
        "singles": singles,
        "pairs": pairs,
        "singles_std": float(s_val.std(ddof=1)),
        "singles_mean": float(s_val.mean()),
        "pairs_std": float(p_val.std(ddof=1)),
        "pairs_mean": float(p_val.mean()),
        "pairs_min": float(p_val.min()),
        "pairs_max": float(p_val.max()),
        "note": "posterior-sampling systematic of the Savage-Dickey "
                "density ratio, quantified as the scatter of the lnB "
                "estimate across chain subsets of the four committed "
                "DESI DR2 + CMB CPL chains",
    }
    with open(SCATTER, "w") as f:
        json.dump(out, f, indent=1)
    print("scatter: singles std %.3f | pairs std %.3f (mean %.3f, "
          "range %.2f-%.2f) | all4chains %+.4f"
          % (out["singles_std"], out["pairs_std"], out["pairs_mean"],
             out["pairs_min"], out["pairs_max"], out["all4chains_lnB"]))
    print("ALL CANONICAL SAVAGE-DICKEY ROWS REPRODUCED FROM COMMITTED CHAINS")


if __name__ == "__main__":
    main()
