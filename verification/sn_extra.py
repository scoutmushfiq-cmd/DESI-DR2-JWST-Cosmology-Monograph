"""Union3 and DES-SN5YR supernova likelihoods (official binned/unbinned
distance releases), completing the two dataset combinations whose Mirage
rows were left as "---" in Round 6 because these likelihoods were not
implemented.

Data (downloaded from the official releases, not committed -- see the
README.md in each subdirectory):

* Union3:  verification/union3/mu_mat_union3_cosmo_2_mu.fits
  (rubind/union3_release; Amber et al. 2025 / Rubin et al., Union3+UNITY1.5)
  23 x 23 float64 FITS: row 0 = redshifts, column 0 = distance moduli,
  the remaining 22 x 22 block is the inverse covariance of the binned mu.
* DES-SN5YR: verification/sn5yr/DES-Dovekie_HD.csv + STAT+SYS.npz
  (des-science/DES-SN5YR; the npz stores the upper triangle of the
  INVERSE stat+sys covariance, as documented in the release's
  DES-Dovekie-SN_Likelihood.py).

Both likelihoods marginalize the SN absolute-magnitude offset analytically
with the standard scalar-sweep formula chi2 = A - B^2/C_11 (identical to
the Pantheon+ treatment in cosmo.chi2_sn), so all four SN compilations are
compared on exactly the same footing.
"""
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_CACHE = {}

C_KMS = 299792.458
ZGRID = None  # filled lazily from cosmo to avoid a circular import


def _zgrid():
    global ZGRID
    if ZGRID is None:
        import cosmo
        ZGRID = cosmo.ZGRID
    return ZGRID


def load_union3():
    if "union3" in _CACHE:
        return _CACHE["union3"]
    path = os.path.join(HERE, "union3", "mu_mat_union3_cosmo_2_mu.fits")
    if not os.path.exists(path):
        _CACHE["union3"] = None
        return None
    raw = open(path, "rb").read()
    n = 23
    data = np.frombuffer(raw[2880:2880 + n * n * 8], dtype=">f8").reshape(n, n)
    z = data[0, 1:].astype(float)
    mu = data[1:, 0].astype(float)
    icov = data[1:, 1:].astype(float)
    icov = 0.5 * (icov + icov.T)
    C_11 = float(np.ones(len(z)) @ icov @ np.ones(len(z)))
    _CACHE["union3"] = dict(z=z, mu=mu, icov=icov, C_11=C_11,
                            icov_1=icov @ np.ones(len(z)), N=len(z))
    return _CACHE["union3"]


def load_desy5():
    if "desy5" in _CACHE:
        return _CACHE["desy5"]
    path = os.path.join(HERE, "sn5yr", "des5yr_processed.npz")
    if not os.path.exists(path):
        _CACHE["desy5"] = None
        return None
    d = np.load(path)
    z, zhel, mu, icov = d["zhd"], d["zhel"], d["mu"], d["icov"]
    Cinv = 0.5 * (icov + icov.T)
    N = len(z)
    Cinv_1 = Cinv @ np.ones(N)
    _CACHE["desy5"] = dict(z=z, zhel=zhel, mu=mu, icov=Cinv,
                           icov_1=Cinv_1, C_11=float(Cinv_1.sum()), N=N)
    return _CACHE["desy5"]


def _chi2_generic(S, H0, Om, w0, wa, use_zhel=False):
    """Analytically M-marginalized chi2 for a mu-based SN compilation."""
    import cosmo
    H0 = np.atleast_1d(H0)
    g = cosmo.geometry(H0, Om, w0, wa)
    I_at = np.empty((len(H0), S["N"]))
    for k in range(len(H0)):
        I_at[k] = np.interp(S["z"], _zgrid(), g["I"][k])
    D_C = (C_KMS / H0[:, None]) * I_at
    fac = (1.0 + S["zhel"]) if use_zhel else (1.0 + S["z"])
    mu_th = 5.0 * np.log10(np.maximum(fac[None, :] * D_C, 1e-8)) + 25.0
    r = mu_th - S["mu"][None, :]
    Cr = r @ S["icov"].T
    A = np.einsum("ni,ni->n", r, Cr)
    B = Cr @ np.ones(S["N"])
    out = A - B ** 2 / S["C_11"]
    # extreme corners of the prior box can overflow the distance integral;
    # the catastrophic-cancellation chi2 there is numerical garbage, not a
    # likelihood, so pin it to a large positive value for the optimizers
    return np.where(np.isfinite(out), out, 1e30)


def chi2_sn_set(name, H0, Om, w0=-1.0, wa=0.0):
    S = load_union3() if name == "union3" else load_desy5()
    if S is None:
        raise RuntimeError(
            "%s data missing: run verification/download_sn_extra_data.py"
            % name)
    return _chi2_generic(S, H0, Om, w0, wa, use_zhel=(name == "desy5"))
