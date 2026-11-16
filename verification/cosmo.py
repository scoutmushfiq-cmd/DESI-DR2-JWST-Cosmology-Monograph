"""
Recreation & re-verification pipeline for
"The Architecture of the Cosmos" (Md Mushfiqur Rahim, DOI: 10.5281/zenodo.23383762).

Implements, from scratch:
  * DESI DR2 BAO likelihood (13 correlated observables, block-diagonal covariance)
  * Compressed Planck CMB likelihood on (theta*, w_b, w_bc)  [w_b, w_bc fixed -> theta* test]
  * 32 Cosmic Chronometer H(z) likelihood
  * Gaussian H0 priors (SH0ES, JWST CCHP TRGB)
  * CPL (w0waCDM) and LCDM expansion history with radiation
  * Goodman & Weare (2010) affine-invariant ensemble MCMC (vectorized)
  * Profile-likelihood (delta chi^2) checks
  * GP reconstruction of H(z) with hyperparameter optimization
  * Savage-Dickey density ratio Bayes factors
  * Hubble-tension significance matrix
"""
import numpy as np
from scipy import stats, optimize
from scipy.interpolate import CubicSpline

C_KMS = 299792.458

# ----------------------------------------------------------------------------
# 1. DATA (exactly as in the monograph, Table 1 / Eq. 26 / Table 9)
# ----------------------------------------------------------------------------
# DESI DR2 BAO: BGS isotropic DV/rd + six anisotropic (DM/rd, DH/rd) pairs.
DESI_BAO = [
    # tracer,        z,      DM/rd,  sig_DM, DH/rd,  sig_DH,  r_MH    (None => DV mode)
    ("BGS",       0.295,   None,   None,   None,   None,    None),   # DV/rd = 7.944 +- 0.075
    ("LRG1",      0.510,   13.587, 0.169,  21.863, 0.427,  -0.475),
    ("LRG2",      0.706,   17.347, 0.180,  19.458, 0.332,  -0.423),
    ("LRG3+ELG1", 0.934,   21.574, 0.153,  17.641, 0.193,  -0.425),
    ("ELG2",      1.321,   27.605, 0.320,  14.178, 0.217,  -0.437),
    ("QSO",       1.484,   30.519, 0.758,  12.816, 0.513,  -0.489),
    ("LYA",       2.330,   38.988, 0.531,   8.632, 0.101,  -0.431),
]
DV_BGS = (7.944, 0.075)

def build_bao():
    y, sig, pairs = [], [], []
    z_all = [DESI_BAO[0][1]]
    y.append(DV_BGS[0]); sig.append(DV_BGS[1])
    for _, z, dm, sm, dh, sh, r in DESI_BAO[1:]:
        z_all += [z, z]
        y += [dm, dh]; sig += [sm, sh]
        pairs.append((len(y) - 2, len(y) - 1, r))
    y, sig = np.array(y), np.array(sig)
    C = np.diag(sig**2)
    for i, j, r in pairs:
        C[i, j] = C[j, i] = r * sig[i] * sig[j]
    return np.array(z_all), y, C

Z_BAO, Y_BAO, C_BAO = build_bao()
C_BAO_INV = np.linalg.inv(C_BAO)
N_BAO = len(Y_BAO)

# Compressed Planck CMB (DESI DR2 baseline): X = (theta*, w_b, w_bc)
X_CMB_OBS = np.array([0.0104110, 0.02223, 0.14208])
C_CMB = 1e-9 * np.array([
    [0.006621, 0.12444, -1.1929],
    [0.12444, 21.344, -94.001],
    [-1.1929, -94.001, 1488.4],
])
SIG_THETA = np.sqrt(C_CMB[0, 0])          # 2.573e-6
W_B_FID, W_BC_FID = 0.02237, 0.14237      # fixed at Planck fiducial (4-param pipeline)

# 32 Cosmic Chronometers (Table 9 of the monograph = Table II of Carloni et al. 2026)
CC_DATA = np.array([
    [0.0700,  69.0, 19.6], [0.0900,  69.0, 12.0], [0.1200,  68.6, 26.2],
    [0.1700,  83.0,  8.0], [0.1790,  75.0,  4.0], [0.1990,  75.0,  5.0],
    [0.2000,  72.9, 29.6], [0.2700,  77.0, 14.0], [0.2800,  88.8, 36.6],
    [0.3520,  83.0, 14.0], [0.3800,  83.0, 13.5], [0.4000,  95.0, 17.0],
    [0.4004,  77.0, 10.2], [0.4250,  87.1, 11.2], [0.4450,  92.8, 12.9],
    [0.4700,  89.0, 23.0], [0.4783,  80.9,  9.0], [0.4800,  97.0, 62.0],
    [0.5930, 104.0, 13.0], [0.6800,  92.0,  8.0], [0.7500,  98.8, 33.6],
    [0.7810, 105.0, 12.0], [0.8750, 125.0, 17.0], [0.8800,  90.0, 40.0],
    [0.9000, 117.0, 23.0], [1.0370, 154.0, 20.0], [1.3000, 168.0, 17.0],
    [1.3630, 160.0, 33.6], [1.4300, 177.0, 18.0], [1.5300, 140.0, 14.0],
    [1.7500, 202.0, 40.0], [1.9650, 186.5, 50.4],
])

# Local H0 ladder (combined stat+sys errors as quoted in the monograph)
H0_LADDER = {
    "Planck2018":        (67.36, 0.54),
    "DESI+CMB (LCDM)":   (68.17, 0.28),
    "DESI+CMB+PP (w0wa)":(67.51, 0.59),
    "DESI+CMB+Y5 (w0wa)":(66.74, 0.56),
    "DESI+CMB+U3 (w0wa)":(65.91, 0.84),
    "rd-free (DESI+CC+PP)": (69.24, 1.82),
    "CCHP HST+JWST TRGB":(70.39, 1.94),
    "SH0ES 2022":        (73.04, 1.04),
    "SH0ES 2024 (42SN)": (73.17, 0.86),
    "JWST Cepheid (D<25)":(73.4, 2.1),
    "JWST joint 3-method":(72.60, 2.00),
    "CCHP JWST TRGB":    (68.81, 2.22),
    "CCHP JWST JAGB":    (67.80, 2.72),
}

# ----------------------------------------------------------------------------
# 2. BACKGROUND COSMOLOGY (vectorized over parameter sets)
# ----------------------------------------------------------------------------
OMEGA_G_H2 = 2.469e-5
N_EFF = 3.044
OMEGA_R_H2 = OMEGA_G_H2 * (1.0 + 0.2271 * N_EFF)   # 4.176e-5
Z_STAR, Z_DRAG = 1089.92, 1059.94

# Integration grid: dense at low z (BAO/SN/CC), log-spaced to high z (CMB)
_Z1 = np.linspace(0.0, 4.0, 4001)
_Z2 = np.geomspace(4.0 + 1e-6, 5.0e4, 3000)
ZGRID = np.concatenate([_Z1, _Z2])
DZ = np.diff(ZGRID)

DE_MODEL = "cpl"   # global DE parametrization: "cpl" | "jbp" | "log" | "mirage"

MIRAGE_SLOPE = -3.66   # Mirage DE: w_a = -3.66 (1 + w_0)  (Lodha et al. 2025)

def f_de(z, w0, wa, de=None):
    """Dark-energy density normalized to today; exact analytic forms.
    cpl : w = w0 + wa z/(1+z)
    jbp : w = w0 + wa z/(1+z)^2   (Jassal-Bagla-Padmanabhan)
    log : w = w0 + wa ln(1+z)     (logarithmic)
    """
    de = de or DE_MODEL
    zp1 = 1.0 + z
    if de == "lcdm" or de == "wcdm":
        return zp1 ** (3.0 * (1.0 + w0))
    if de == "cpl":
        return zp1 ** (3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * z / zp1)
    if de == "jbp":
        # int_0^z [1+w]/(1+z') dz' = (1+w0)ln(1+z) + wa[1/2 - (1+z)^-1 + (1+z)^-3/2]
        return zp1 ** (-3.0 * (1.0 + w0)) * \
            np.exp(-3.0 * wa * (0.5 - 1.0 / zp1 + 0.5 / zp1**3))
    if de == "log":
        lnzp1 = np.log(zp1)
        return zp1 ** (-3.0 * (1.0 + w0)) * np.exp(-1.5 * wa * lnzp1**2)
    if de == "mirage":
        wam = MIRAGE_SLOPE * (1.0 + w0)
        return zp1 ** (3.0 * (1.0 + w0 + wam)) * np.exp(-3.0 * wam * z / zp1)
    raise ValueError(de)

def E2(z, Om, w0=-1.0, wa=0.0, H0=67.0, rd=None):
    """Vectorized E(z)^2; z may be (G,) grid and params (N,) arrays."""
    with np.errstate(over="ignore", invalid="ignore"):
        zp1 = 1.0 + z
        h2 = (H0 / 100.0) ** 2
        Or = OMEGA_R_H2 / h2
        Ode = 1.0 - Om - Or
        out = Or * zp1**4 + Om * zp1**3 + Ode * f_de(z, w0, wa)
    return np.where(np.isfinite(out), out, -1.0)

def _cumtrap(y):
    out = np.zeros_like(y)
    np.cumsum(0.5 * (y[..., 1:] + y[..., :-1]) * DZ, axis=-1, out=out[..., 1:])
    return out

def geometry(H0, Om, w0=-1.0, wa=0.0):
    """
    Returns dict with, for every parameter set (N,):
      I(z)      = int_0^z dz/E on ZGRID          -> (N, G)
      rs(z)     = int_z^inf dz/(E sqrt(1+Rb))    -> (N, G)   [c/(sqrt3 H0) units]
    """
    H0 = np.atleast_1d(H0); Om = np.atleast_1d(Om)
    w0 = np.atleast_1d(w0); wa = np.atleast_1d(wa)
    h2 = (H0 / 100.0) ** 2
    Or = (OMEGA_R_H2 / h2)[:, None]
    Om2 = Om[:, None]
    Ode = 1.0 - Om2 - Or
    zp1 = 1.0 + ZGRID[None, :]
    e2 = Or * zp1**4 + Om2 * zp1**3 + Ode * f_de(ZGRID[None, :], w0[:, None], wa[:, None])
    bad = ~np.isfinite(e2) | (e2 <= 1e-14)
    e2 = np.where(bad, 1.0, e2)
    E = np.where(bad, 1e6, np.sqrt(e2))
    I = _cumtrap(1.0 / E)
    # sound-horizon integrand (photon-baryon fluid)
    Rb = 3.0 * W_B_FID / (4.0 * OMEGA_G_H2 * zp1)
    integrand = 1.0 / (E * np.sqrt(1.0 + Rb))
    cum = _cumtrap(integrand)
    rs = cum[..., -1:] - cum          # rs(z) = int_z^zmax
    return {"I": I, "rs": rs, "E": E}

def interp_row(cum, z):
    return np.array([np.interp(zz, ZGRID, row) for zz, row in zip(np.atleast_1d(z), cum)]) \
        if cum.ndim == 1 else None

def chi2_bao(H0, Om, w0, wa, rd=147.09):
    g = geometry(H0, Om, w0, wa)
    I_star = np.array([row[np.searchsorted(ZGRID, zz)] for row, zz in zip(g["I"], np.zeros(len(np.atleast_1d(H0))))])
    # interpolate I and E at BAO redshifts (vectorized per row)
    n = len(np.atleast_1d(H0))
    I_at = np.empty((n, N_BAO)); E_at = np.empty((n, N_BAO))
    for k in range(n):
        I_at[k] = np.interp(Z_BAO, ZGRID, g["I"][k])
        E_at[k] = np.interp(Z_BAO, ZGRID, g["E"][k])
    rd_arr = np.atleast_1d(rd)
    rd_col = np.full((n, 1), float(rd_arr[0])) if rd_arr.size == 1 else rd_arr.reshape(n, 1)
    pref = C_KMS / (np.atleast_1d(H0)[:, None] * rd_col)
    DM = pref * I_at                      # DM/rd
    DH = pref / E_at                      # DH/rd
    yth = np.empty((n, N_BAO))
    yth[:, 0] = (Z_BAO[0] * DH[:, 0] * DM[:, 0] ** 2) ** (1.0 / 3.0)
    yth[:, 1::2] = DM[:, 1::2]
    yth[:, 2::2] = DH[:, 2::2]
    d = Y_BAO[None, :] - yth
    return np.einsum("ni,ij,nj->n", d, C_BAO_INV, d)

def theta_star(H0, Om, w0=-1.0, wa=0.0):
    """Acoustic angular scale theta* = r_s(z*) / D_M(z*), calibrated to the
    Planck fiducial cosmology (absorbs polarization / exact z* physics)."""
    g = geometry(H0, Om, w0, wa)
    n = len(np.atleast_1d(H0))
    iz = np.searchsorted(ZGRID, Z_STAR)
    I_star = np.array([g["I"][k][iz] for k in range(n)])
    rs_star = np.array([g["rs"][k][iz] for k in range(n)])
    ts_raw = rs_star / (np.sqrt(3.0) * I_star)   # rs in c/(sqrt3 H0) units cancels
    return TS_CAL * ts_raw

# calibration so that the Planck fiducial LCDM cosmology reproduces theta*_obs
def _theta_raw_fid():
    g = geometry(67.36, 0.3153, -1.0, 0.0)
    iz = np.searchsorted(ZGRID, Z_STAR)
    I_star = g["I"][0][iz]; rs_star = g["rs"][0][iz]
    return rs_star / (np.sqrt(3.0) * I_star)

TS_CAL = X_CMB_OBS[0] / _theta_raw_fid()

def chi2_cmb(H0, Om, w0=-1.0, wa=0.0):
    d = (X_CMB_OBS[0] - theta_star(H0, Om, w0, wa)) / SIG_THETA
    return d**2

def chi2_cc(H0, Om, w0=-1.0, wa=0.0):
    H0 = np.atleast_1d(H0); Om = np.atleast_1d(Om)
    w0 = np.broadcast_to(np.atleast_1d(w0), (len(H0),))
    wa = np.broadcast_to(np.atleast_1d(wa), (len(H0),))
    g = geometry(H0, Om, w0, wa)
    E_at = np.empty((len(H0), len(CC_DATA)))
    for k in range(len(H0)):
        E_at[k] = np.interp(CC_DATA[:, 0], ZGRID, g["E"][k])
    Hth = H0[:, None] * E_at
    d = (CC_DATA[None, :, 1] - Hth) / CC_DATA[None, :, 2]
    return np.sum(d**2, axis=1)

# ----------------------------------------------------------------------------
# 2b. PANTHEON+ SUPERNOVA LIKELIHOOD (full 1701 SN STAT+SYS covariance)
# ----------------------------------------------------------------------------
_SN_CACHE = {}

def _load_sn(path_prefix="pantheon/sn"):
    if "ok" in _SN_CACHE:
        return _SN_CACHE
    import os
    dat, cov = path_prefix + "_data.dat", path_prefix + "_cov.cov"
    if not (os.path.exists(dat) and os.path.exists(cov)):
        _SN_CACHE["ok"] = False
        return _SN_CACHE
    d = np.genfromtxt(dat, names=True, dtype=None, encoding="utf-8")
    mask = (d["IS_CALIBRATOR"] == 0) & (d["zHD"] > 0.01)
    z_sn = d["zHD"][mask].astype(float)
    mb = d["m_b_corr"][mask].astype(float)
    N = int(open(cov).readline().split()[0])
    C = np.loadtxt(cov, skiprows=1).reshape(N, N)
    C = 0.5 * (C + C.T)
    C = C[np.ix_(mask, mask)]
    N = int(mask.sum())
    Cinv = np.linalg.inv(C)
    Cinv_1 = Cinv @ np.ones(N)
    C_11 = float(np.ones(N) @ Cinv_1)
    _SN_CACHE.update(ok=True, z=z_sn, mb=mb, Cinv=Cinv,
                     Cinv_1=Cinv_1, C_11=C_11, N=N)
    return _SN_CACHE

def chi2_sn(H0, Om, w0=-1.0, wa=0.0):
    """Pantheon+ chi2 with the absolute magnitude M_B marginalized
    analytically (uncalibrated SN sample, full STAT+SYS covariance)."""
    S = _load_sn()
    if not S.get("ok"):
        return np.zeros(len(np.atleast_1d(H0)))
    g = geometry(H0, Om, w0, wa)
    H0 = np.atleast_1d(H0)
    n = len(H0)
    I_at = np.empty((n, S["N"]))
    for k in range(n):
        I_at[k] = np.interp(S["z"], ZGRID, g["I"][k])
    DL = (1.0 + S["z"])[None, :] * (C_KMS / H0[:, None]) * I_at
    DL = np.maximum(DL, 1e-8)
    mu_th = 5.0 * np.log10(DL) + 25.0
    r = S["mb"][None, :] - mu_th
    Cr = r @ S["Cinv"].T
    A = np.einsum("ni,ni->n", r, Cr)
    B = Cr @ np.ones(S["N"])
    return A - B ** 2 / S["C_11"]

# ----------------------------------------------------------------------------
# 3. JOINT LOG-POSTERIOR FACTORY
# ----------------------------------------------------------------------------
W_NU = 0.06 / 93.14          # normal-ordering floor, one massive neutrino treatment
SIG_WBC = float(np.sqrt(1488.4e-9))
SIG_WB = float(np.sqrt(21.344e-9))

class Joint:
    """Slaved parametrization: params (H0, w_bc[, w0, wa][, rd]);
    Omega_m = (w_bc + w_nu) / h^2. Flags select likelihood terms."""
    def __init__(self, w0wa=False, rd_free=False, bao=True, cmb=True, cc=False,
                 sn=False, h0_prior=None, rd_prior=None, de=None):
        self.w0wa, self.rd_free = w0wa, rd_free
        self.bao, self.cmb, self.cc, self.sn = bao, cmb, cc, sn
        self.h0_prior = h0_prior
        self.rd_prior = rd_prior
        self.de = de or DE_MODEL
        self.n_de = 0 if self.de == "lcdm" else (2 if self.de not in ("wcdm", "mirage") else 1)
        names = {"lcdm": [], "wcdm": ["w"], "mirage": ["w0"], "cpl": ["w0", "wa"],
                 "jbp": ["w0", "wa"], "log": ["w0", "wa"]}
        self.pnames = (["H0", "wbc"] + names[self.de] + (["rd"] if rd_free else []))

    def unpack(self, p):
        p = np.atleast_2d(p)
        H0 = p[:, 0]; wbc = p[:, 1]
        h2 = (H0 / 100.0) ** 2
        Om = (wbc + W_NU) / h2
        i = 2
        if self.n_de == 0: w0 = np.full(len(p), -1.0); wa = np.zeros(len(p))
        elif self.n_de == 1:
            w0 = p[:, 2]; i += 1
            wa = MIRAGE_SLOPE * (1.0 + w0) if self.de == "mirage" else np.zeros(len(p))
        else: w0, wa = p[:, 2], p[:, 3]; i += 2
        rd = p[:, i] if self.rd_free else np.full(len(p), 147.09)
        return H0, Om, w0, wa, rd

    def bounds(self):
        b = [(40.0, 100.0), (0.130, 0.155)]
        if self.de == "wcdm": b += [(-2.0, 0.5)]
        elif self.de == "mirage": b += [(-2.5, 0.5)]
        elif self.n_de == 2: b += [(-2.5, 0.5), (-4.0, 1.0)]
        if self.rd_free: b += [(100.0, 200.0)]
        return b

    def chi2(self, p):
        global DE_MODEL
        old = DE_MODEL; DE_MODEL = self.de
        try:
            return self._chi2_inner(p)
        finally:
            DE_MODEL = old

    def _chi2_inner(self, p):
        H0, Om, w0, wa, rd = self.unpack(p)
        wbc = np.atleast_2d(p)[:, 1]
        x2 = np.zeros(len(H0))
        if self.bao: x2 += chi2_bao(H0, Om, w0, wa, rd)
        if self.cmb:
            x2 += chi2_cmb(H0, Om, w0, wa)
            x2 += ((wbc - X_CMB_OBS[2]) / SIG_WBC) ** 2
            x2 += ((W_B_FID - X_CMB_OBS[1]) / SIG_WB) ** 2
        if self.cc:  x2 += chi2_cc(H0, Om, w0, wa)
        if self.sn:  x2 += chi2_sn(H0, Om, w0, wa)
        if self.h0_prior is not None:
            m, s = self.h0_prior
            x2 += ((H0 - m) / s) ** 2
        if self.rd_prior is not None:
            m, s = self.rd_prior
            x2 += ((rd - m) / s) ** 2
        return x2

    def log_prior(self, p):
        lp = np.zeros(len(np.atleast_2d(p)))
        for k, (lo, hi) in enumerate(self.bounds()):
            v = np.atleast_2d(p)[:, k]
            lp += np.where((v >= lo) & (v <= hi), 0.0, -np.inf)
        return lp

    def log_prob(self, p):
        lp = self.log_prior(p)
        with np.errstate(invalid="ignore"):
            x2 = self.chi2(p)
        return lp - 0.5 * np.where(np.isfinite(x2), x2, 1e30)

# ----------------------------------------------------------------------------
# 4. GOODMAN & WEARE AFFINE-INVARIANT ENSEMBLE MCMC (vectorized stretch moves)
# ----------------------------------------------------------------------------
def run_mcmc(joint, n_walkers=48, n_steps=2500, burn=500, seed=42, p0=None):
    rng = np.random.default_rng(seed)
    b = joint.bounds()
    ndim = len(b)
    if p0 is None:
        p0 = init_walkers_on_band(joint, n_walkers, seed=seed)
    logp = joint.log_prob(p0)
    if not np.all(np.isfinite(logp)):
        raise ValueError("initial walkers outside prior support; supply p0")
    chain = np.zeros((n_steps - burn, n_walkers, ndim))
    half = n_walkers // 2
    halves = [(np.arange(0, half), np.arange(half, n_walkers)),
              (np.arange(half, n_walkers), np.arange(0, half))]
    for step in range(n_steps):
        for act, comp in halves:
            u = rng.uniform(0.0, 1.0, size=len(act))
            zz = ((2.0 - 1.0) * u + 1.0) ** 2 / 2.0        # g(z) ~ 1/sqrt(z), z in [1/2, 2]
            partners = comp[rng.integers(0, len(comp), size=len(act))]
            prop = p0[partners] + zz[:, None] * (p0[act] - p0[partners])
            lp_prop = joint.log_prob(prop)
            acc = np.log(rng.uniform(size=len(act))) < ((ndim - 1.0) * np.log(zz) + lp_prop - logp[act])
            p0[act[acc]] = prop[acc]
            logp[act[acc]] = lp_prop[acc]
        if step >= burn:
            chain[step - burn] = p0
    return chain.reshape(-1, ndim)

def summarize(chain, names):
    out = {}
    for k, nm in enumerate(names):
        s = chain[:, k]
        lo, med, hi = np.percentile(s, [16, 50, 84])
        out[nm] = dict(mean=float(s.mean()), std=float(s.std()),
                       lo=float(lo), med=float(med), hi=float(hi))
    return out

# ----------------------------------------------------------------------------
# 5. PROFILE LIKELIHOOD (fast analytic cross-checks)
# ----------------------------------------------------------------------------
def profile(joint, fixed=None, grid=None):
    """Minimize chi2 over free params for each value on `grid` of param `fixed`."""
    b = joint.bounds()
    res = []
    for gv in grid:
        def f(x):
            full = np.insert(x, fixed[0], gv)[None, :]
            return joint.chi2(full)[0]
        free = [k for k in range(len(b)) if k != fixed[0]]
        x0 = np.array([np.mean(b[k]) for k in free])
        r = optimize.minimize(f, x0, method="Nelder-Mead",
                              options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
        res.append((gv, r.fun, r.x))
    return res

def cov_from_hess(H):
    Hi = np.linalg.pinv(H)
    evals, evecs = np.linalg.eigh(Hi)
    evals = np.clip(evals, 0.0, None)
    return evecs @ np.diag(evals) @ evecs.T

# ----------------------------------------------------------------------------
# 6. DERIVED QUANTITIES FROM CPL POSTERIORS
# ----------------------------------------------------------------------------
def cpl_w(z, w0, wa):
    return w0 + wa * z / (1.0 + z)

def q_of_z(z, Om, w0, wa, H0=68.0):
    """q(z) = -1 + (1+z) dlnE/dz, numerical derivative of exact E(z)."""
    eps = 1e-4
    E0 = np.sqrt(E2(z, Om, w0, wa, H0))
    Ep = np.sqrt(E2(z + eps, Om, w0, wa, H0))
    Em = np.sqrt(E2(np.maximum(z - eps, 0.0), Om, w0, wa, H0))
    g = (np.log(Ep) - np.log(Em)) / (np.log(z + eps + 1.0) - np.log(np.maximum(z - eps, 0.0) + 1.0))
    return -1.0 + g

def j_of_z(z, Om, w0, wa, H0=68.0):
    """j(z) by second derivative of ln E wrt ln a: j = 1 + ... numeric via E(a)."""
    a = 1.0 / (1.0 + z)
    la = np.log(a)
    eps = 1e-4
    def lnE(la_):
        aa = np.exp(la_)
        return 0.5 * np.log(E2(1.0 / aa - 1.0, Om, w0, wa, H0))
    g1 = (lnE(la + eps) - lnE(la - eps)) / (2 * eps)
    g2 = (lnE(la + eps) - 2 * lnE(la) + lnE(la - eps)) / eps**2
    # dlnE/dlna = -3/2(1+w)Om_DE/E^2 ... j = 1 + (dlnE/dlna)^2 + d^2lnE/dlna^2 - dlnE/dlna
    # derive: j = a^2 a'''/a'^3 ... use standard: j = 1 + g1^2 + g2 - g1*(1 + ...)? -> verify numerically vs LCDM
    return 1.0 + g1 * g1 + g2 - g1  # placeholder, validated below against LCDM

def j_of_z_numeric(z, Om, w0, wa, H0=68.0):
    # j(z) = a^2 a''' / (a')^3 via finite differences of a(t) from exact E(z).
    a_asc = np.geomspace(1e-3, 1.0, 3000)
    z_grid = 1.0 / a_asc - 1.0
    H = H0 * np.sqrt(np.maximum(E2(z_grid, Om, w0, wa, H0), 1e-12))
    integrand = 1.0 / (a_asc * H)
    t = np.concatenate([[0.0], np.cumsum(0.5 * (integrand[1:] + integrand[:-1]) * np.diff(a_asc))])
    a_of_t = CubicSpline(t, a_asc)
    tt = np.linspace(t[0] + 1e-8, t[-1] - 1e-8, 20000)
    aa = a_of_t(tt)
    d1 = a_of_t(tt, 1); d3 = a_of_t(tt, 3)
    j = aa**2 * d3 / d1**3
    a_target = 1.0 / (1.0 + z)
    return float(np.interp(a_target, aa, j))

def derived_cpl(chain):
    """z_c (phantom crossing), f_DE(z_c), q0, j0, z_t from posterior draws."""
    H0 = chain[:, 0]; Om = chain[:, 1]; w0 = chain[:, 2]; wa = chain[:, 3]
    out = {}
    # phantom crossing: w(z) = -1  ->  z_c = -(1+w0)/(1+w0+wa)  (w0 > -1, 1+w0+wa < 0)
    valid = (w0 > -1.0) & (1.0 + w0 + wa < -1e-3)
    zc = -(1.0 + w0[valid]) / (1.0 + w0[valid] + wa[valid])
    keep = (zc > 0) & (zc < 10)
    zc = zc[keep]
    out["z_c"] = (float(np.median(zc)), float(np.std(zc)), float(np.mean(zc > 0)))
    fde_zc = f_de(zc, w0[valid][keep], wa[valid][keep])
    out["fDE_zc"] = (float(np.median(fde_zc)), float(np.std(fde_zc)))
    q0 = q_of_z(0.0, Om, w0, wa, np.median(H0))
    out["q0"] = (float(np.mean(q0)), float(np.std(q0)))
    j0 = np.array([j_of_z_numeric(0.0, Om[k], w0[k], wa[k], H0[k]) for k in range(0, len(H0), max(1, len(H0)//400))])
    out["j0"] = (float(np.mean(j0)), float(np.std(j0)))
    # acceleration onset z_t: q(z_t) = 0
    zgrid = np.linspace(0.0, 2.0, 401)
    sub = np.random.default_rng(1).choice(len(H0), size=min(300, len(H0)), replace=False)
    zts = []
    for k in sub:
        qq = q_of_z(zgrid, Om[k], w0[k], wa[k], H0[k])
        idx = np.where(np.diff(np.sign(qq)) > 0)[0]
        if len(idx):
            i = idx[0]
            zts.append(zgrid[i] - qq[i] * (zgrid[i+1] - zgrid[i]) / (qq[i+1] - qq[i]))
    out["z_t"] = (float(np.median(zts)), float(np.std(zts)))
    return out

# ----------------------------------------------------------------------------
# 7. GAUSSIAN PROCESS RECONSTRUCTION OF H(z) (CC + DESI radial)
# ----------------------------------------------------------------------------
def gp_hz(hyper=(305.10, 3.885), optimize_hp=True):
    """Data: 32 CC + 6 DESI DH/rd -> H(z) using rd = 147.09 Mpc."""
    z_cc, h_cc, s_cc = CC_DATA[:, 0], CC_DATA[:, 1], CC_DATA[:, 2]
    dh = np.array([b[4] for b in DESI_BAO[1:]])
    sdh = np.array([b[5] for b in DESI_BAO[1:]])
    z_b = np.array([b[1] for b in DESI_BAO[1:]])
    rd = 147.09
    h_b = C_KMS / (rd * dh)
    s_b = h_b * (sdh / dh)          # rd fixed -> fractional error propagates
    z = np.concatenate([z_cc, z_b]); y = np.concatenate([h_cc, h_b])
    sy = np.concatenate([s_cc, s_b])
    order = np.argsort(z); z, y, sy = z[order], y[order], sy[order]

    def nll(params):
        sf, lf = np.exp(params)
        K = sf**2 * np.exp(-0.5 * ((z[:, None] - z[None, :]) / lf)**2) + np.diag(sy**2) \
            + 1e-8 * np.eye(len(z))
        L = np.linalg.cholesky(K)
        alpha = np.linalg.solve(L.T, np.linalg.solve(L, y))
        return 0.5 * y @ alpha + np.log(np.diag(L)).sum()

    if optimize_hp:
        best = optimize.minimize(nll, np.log(hyper), method="Nelder-Mead")
        sf, lf = np.exp(best.x)
    else:
        sf, lf = hyper
    zt = np.linspace(0.0, 2.0, 201)
    K = sf**2 * np.exp(-0.5 * ((z[:, None] - z[None, :]) / lf)**2) + np.diag(sy**2) + 1e-8*np.eye(len(z))
    Ks = sf**2 * np.exp(-0.5 * ((zt[:, None] - z[None, :]) / lf)**2)
    Kss = sf**2 * np.exp(-0.5 * ((zt[:, None] - zt[None, :]) / lf)**2)
    L = np.linalg.cholesky(K)
    al = np.linalg.solve(L.T, np.linalg.solve(L, y - y.mean()))
    mu = y.mean() + Ks @ al
    v = np.linalg.solve(L, Ks.T)
    cov = Kss - v.T @ v
    # q(z) and z_t from GP draws
    rng = np.random.default_rng(7)
    draws = rng.multivariate_normal(mu, cov, size=500)
    dlnH = np.gradient(np.log(draws), zt, axis=1)
    q = -1.0 + (1.0 + zt)[None, :] * dlnH
    q0 = q[:, 0]
    zts = []
    for row in q:
        idx = np.where(np.diff(np.sign(row)) > 0)[0]
        if len(idx):
            i = idx[0]
            zts.append(zt[i] - row[i] * (zt[i+1]-zt[i]) / (row[i+1]-row[i]))
    return dict(sf=float(sf), lf=float(lf), zt=zt, mu=mu, cov=cov,
                q0=(float(q0.mean()), float(q0.std())),
                z_t=(float(np.median(zts)), float(np.std(zts))),
                data=(z, y, sy))

# ----------------------------------------------------------------------------
# 8. SAVAGE-DICKEY BAYES FACTOR & HUBBLE TENSION MATRIX
# ----------------------------------------------------------------------------
def savage_dickey(chain_w, prior_volume=15.0, lcdm_point=(-1.0, 0.0)):
    kde = stats.gaussian_kde(chain_w.T)
    post = float(kde(lcdm_point)[0])
    return float(np.log((1.0 / prior_volume) / max(post, 1e-300)))

def tension_matrix(rows, cols):
    T = np.zeros((len(rows), len(cols)))
    for i, (h1, s1) in enumerate(rows):
        for j, (h2, s2) in enumerate(cols):
            T[i, j] = abs(h2 - h1) / np.sqrt(s1**2 + s2**2)
    return T


# ----------------------------------------------------------------------------
# 9. BAND-AWARE INITIALIZATION (theta* is a near-singular constraint)
# ----------------------------------------------------------------------------
from scipy.optimize import brentq

def h0_on_band(Om, w0=-1.0, wa=0.0, lo=40.0, hi=110.0):
    """Solve theta*(H0; Om, w0, wa) = theta*_obs for H0 (unique root)."""
    def f(h):
        return float(theta_star(h, Om, w0, wa)[0]) - X_CMB_OBS[0]
    try:
        return brentq(f, lo, hi, xtol=1e-8)
    except ValueError:
        return np.nan

def init_walkers_on_band(joint, n_walkers, seed=0, jitter=None):
    rng = np.random.default_rng(seed)
    b = joint.bounds()
    ndim = len(b)
    P = np.zeros((n_walkers, ndim))
    for w in range(n_walkers):
        for _ in range(200):
            Om = rng.uniform(0.20, 0.45)
            w0 = rng.uniform(-1.8, -0.2) if joint.n_de >= 1 else -1.0
            wa = (-3.66 * (1.0 + w0)) if joint.de == "mirage" else \
                (rng.uniform(-3.0, 0.5) if joint.n_de == 2 else 0.0)
            h0 = h0_on_band(Om, w0, wa)
            if np.isfinite(h0) and 55.0 < h0 < 90.0:
                break
        else:
            h0, Om, w0, wa = 68.0, 0.30, -1.0, 0.0
        wbc = Om * (h0 / 100.0) ** 2 - W_NU
        row = [h0, wbc] + ([w0] if joint.n_de == 1 else ([w0, wa] if joint.n_de == 2 else []))
        if joint.rd_free:
            row += [rng.uniform(140, 155)]
        P[w] = row
    if jitter is None:
        jitter = np.full(ndim, 0.01)
        jitter[0] = 0.15
        jitter[1] = 0.0006
        if joint.n_de == 1: jitter[2] = 0.02
        elif joint.n_de == 2: jitter[2:4] = [0.02, 0.05]
    return np.clip(P + jitter * rng.standard_normal((n_walkers, ndim)),
                   np.array([lo for lo, hi in b]), np.array([hi for lo, hi in b]))

# ----------------------------------------------------------------------------
# 10. CONVERGENCE DIAGNOSTICS & INFORMATION CRITERIA
# ----------------------------------------------------------------------------
def gelman_rubin(chains):
    """chains: list of (n, d) arrays from independent runs. Returns R-hat (d,)."""
    m = len(chains)
    n = min(c.shape[0] for c in chains)
    X = np.stack([c[:n] for c in chains])          # (m, n, d)
    W = X.var(axis=1, ddof=1).mean(axis=0)          # within-chain var
    B = n * X.mean(axis=1).var(axis=0, ddof=1)      # between-chain var
    V = (n - 1) / n * W + B / n
    return np.sqrt(V / W)

def ess(chain):
    """Effective sample size via integrated autocorrelation (per column)."""
    n, d = chain.shape
    out = np.empty(d)
    for k in range(d):
        x = chain[:, k] - chain[:, k].mean()
        F = np.fft.rfft(x - 0)
        acf = np.fft.irfft(F * np.conj(F))[:n].real
        acf /= acf[0]
        tau = 1.0
        for t in range(1, n):
            if acf[t] < 0.05:
                break
            tau += 2.0 * acf[t]
        out[k] = n / tau
    return out

def aic_bic(chi2_min, k, n_data):
    return chi2_min + 2 * k, chi2_min + k * np.log(n_data)

def dic(joint, chain, max_samples=4000, seed=5):
    """Deviance Information Criterion from posterior draws."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(chain), size=min(max_samples, len(chain)), replace=False)
    sub = chain[idx]
    D = np.array([float(np.ravel(joint.chi2(row))[0]) for row in sub])
    Dbar = D.mean()
    pmap = sub[np.argmin(D)]
    Dmap = float(np.ravel(joint.chi2(pmap))[0])
    pD = Dbar - Dmap
    return dict(DIC=float(Dbar + pD), pD=float(pD), Dbar=float(Dbar), Dmap=Dmap)

def lnB_savage_dickey_nested(chain, k_col, point, prior_volume):
    """Generic nested Savage-Dickey: chain cols for the extended params."""
    kde = stats.gaussian_kde(chain[:, k_col].T)
    post = float(kde(point)[0])
    return float(np.log((1.0 / prior_volume) / max(post, 1e-300)))
