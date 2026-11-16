"""H0 * rd product check for the fig:ede_horndeski gray hyperbola.

Round-6 minor m6: the quadrature error derivation for H0 r_d = 10027 +/- 45
was previously given only in prose; this script makes it a released artifact.

Inputs (both from released artifacts / canonical values used throughout):
  H0  = 68.17 +/- 0.28 km/s/Mpc  (our joint DESI DR2 + CMB LambdaCDM chain)
  r_d = 147.09 +/- 0.26 Mpc      (Planck sound horizon, fixed in all chains)

Independent factors -> relative errors add in quadrature:
  H0 r_d = 68.17 * 147.09 = 10027.1 km/s
  sigma = sqrt((147.09*0.28)^2 + (68.17*0.26)^2) = 44.8 km/s
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

H0, H0_ERR = 68.17, 0.28
RD, RD_ERR = 147.09, 0.26

prod = H0 * RD
err = float(np.sqrt((RD * H0_ERR) ** 2 + (H0 * RD_ERR) ** 2))

# Monte Carlo cross-check of the quadrature propagation
rng = np.random.default_rng(11)
mc = rng.normal(H0, H0_ERR, 2_000_000) * rng.normal(RD, RD_ERR, 2_000_000)

OUT = {
    "H0": {"value": H0, "err": H0_ERR,
           "source": "joint DESI DR2 + CMB LambdaCDM chain (verification/chains/chain_lcdm_desi_cmb*.npy)"},
    "rd": {"value": RD, "err": RD_ERR,
           "source": "Planck sound horizon (fixed prior mean in all chains)"},
    "H0_rd": round(prod, 1),
    "err_quadrature": round(err, 1),
    "err_montecarlo": round(float(mc.std()), 1),
    "relative_err": round(err / prod, 5),
    "tex_string": "10027 \\pm 45",
    "note": "Relative errors 0.41% and 0.18% are independent (CMB chain H0 vs Planck rd), "
            "so quadrature addition is exact to Monte Carlo precision.",
}
assert abs(prod - 10027.1) < 0.1, prod
assert abs(err - 44.8) < 0.1, err
assert abs(OUT["err_montecarlo"] - err) < 0.5

with open(os.path.join(HERE, "h0rd_check.json"), "w") as f:
    json.dump(OUT, f, indent=2)
print(json.dumps(OUT, indent=2))
