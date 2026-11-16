src = open('cosmo.py').read()

# 1. Guard f_de / E2 against overflow -> NaN
old = """def E2(z, Om, w0=-1.0, wa=0.0, H0=67.0, rd=None):
    \"\"\"Vectorized E(z)^2; z may be (G,) grid and params (N,) arrays.\"\"\"
    zp1 = 1.0 + z
    h2 = (H0 / 100.0) ** 2
    Or = OMEGA_R_H2 / h2
    Ode = 1.0 - Om - Or
    return (Or * zp1**4 + Om * zp1**3 + Ode * f_de(z, w0, wa))"""
new = """def E2(z, Om, w0=-1.0, wa=0.0, H0=67.0, rd=None):
    \"\"\"Vectorized E(z)^2; z may be (G,) grid and params (N,) arrays.\"\"\"
    with np.errstate(over="ignore", invalid="ignore"):
        zp1 = 1.0 + z
        h2 = (H0 / 100.0) ** 2
        Or = OMEGA_R_H2 / h2
        Ode = 1.0 - Om - Or
        out = Or * zp1**4 + Om * zp1**3 + Ode * f_de(z, w0, wa)
    return np.where(np.isfinite(out), out, -1.0)"""
assert old in src, "E2 block"
src = src.replace(old, new)

# guard in geometry: negative/NaN E2 -> huge E (rejected by likelihood)
old = """    e2 = Or * zp1**4 + Om2 * zp1**3 + Ode * f_de(ZGRID[None, :], w0[:, None], wa[:, None])
    E = np.sqrt(np.maximum(e2, 1e-14))"""
new = """    e2 = Or * zp1**4 + Om2 * zp1**3 + Ode * f_de(ZGRID[None, :], w0[:, None], wa[:, None])
    bad = ~np.isfinite(e2) | (e2 <= 1e-14)
    e2 = np.where(bad, 1.0, e2)
    E = np.where(bad, 1e6, np.sqrt(e2))"""
assert old in src, "geometry block"
src = src.replace(old, new)

# 2. fix q_of_z: g already is dlnE/dln(1+z); q = -1 + g
old = """    g = (np.log(Ep) - np.log(Em)) / (np.log(z + eps + 1.0) - np.log(np.maximum(z - eps, 0.0) + 1.0))
    return -1.0 + (1.0 + z) * g"""
new = """    g = (np.log(Ep) - np.log(Em)) / (np.log(z + eps + 1.0) - np.log(np.maximum(z - eps, 0.0) + 1.0))
    return -1.0 + g"""
assert old in src, "q_of_z block"
src = src.replace(old, new)

# 3. robust covariance helper
old = """# ----------------------------------------------------------------------------
# 6. DERIVED QUANTITIES FROM CPL POSTERIORS"""
new = """def cov_from_hess(H):
    Hi = np.linalg.pinv(H)
    evals, evecs = np.linalg.eigh(Hi)
    evals = np.clip(evals, 0.0, None)
    return evecs @ np.diag(evals) @ evecs.T

# ----------------------------------------------------------------------------
# 6. DERIVED QUANTITIES FROM CPL POSTERIORS"""
assert old in src, "cov helper"
src = src.replace(old, new)

# 4. rewrite j_of_z_numeric cleanly (docstring avoids triple-quote clash)
old_start = src.index("def j_of_z_numeric(")
old_end = src.index("def derived_cpl(")
new_fn = (
    "def j_of_z_numeric(z, Om, w0, wa, H0=68.0):\n"
    "    # j(z) = a^2 a''' / (a')^3 via finite differences of a(t) from exact E(z).\n"
    "    a_asc = np.geomspace(1e-3, 1.0, 3000)\n"
    "    z_grid = 1.0 / a_asc - 1.0\n"
    "    H = H0 * np.sqrt(np.maximum(E2(z_grid, Om, w0, wa, H0), 1e-12))\n"
    "    integrand = 1.0 / (a_asc * H)\n"
    "    t = np.concatenate([[0.0], np.cumsum(0.5 * (integrand[1:] + integrand[:-1]) * np.diff(a_asc))])\n"
    "    a_of_t = CubicSpline(t, a_asc)\n"
    "    tt = np.linspace(t[0] + 1e-8, t[-1] - 1e-8, 20000)\n"
    "    aa = a_of_t(tt)\n"
    "    d1 = a_of_t(tt, 1); d3 = a_of_t(tt, 3)\n"
    "    j = aa**2 * d3 / d1**3\n"
    "    a_target = 1.0 / (1.0 + z)\n"
    "    return float(np.interp(a_target, aa, j))\n\n"
)
src = src[:old_start] + new_fn + src[old_end:]

open('cosmo.py', 'w').write(src)
print("all patches applied")
