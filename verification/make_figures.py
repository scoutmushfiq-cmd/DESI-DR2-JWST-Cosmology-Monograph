import json, numpy as np, cosmo as cm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- Fig 1: w0-wa contours ----------
fig, ax = plt.subplots(figsize=(6.4, 5.2))
for tag, f, c in [("DESI+CMB", "chain_w0wa_desi_cmb.npy", "C0"),
                  ("DESI+CMB+CC", "chain_w0wa_desi_cmb_cc.npy", "C3")]:
    ch = np.load(f)[:, 2:4]
    lo1, hi1 = np.percentile(ch[:,0], [16,84]); lo2, hi2 = np.percentile(ch[:,1], [16,84])
    H, xe, ye = np.histogram2d(ch[:,0], ch[:,1], bins=60,
                               range=[[lo1-3*(hi1-lo1), hi1+3*(hi1-lo1)],
                                      [lo2-3*(hi2-lo2), hi2+3*(hi2-lo2)]])
    Hs = np.sort(H.ravel())[::-1]; cum = np.cumsum(Hs)/H.sum()
    l68 = Hs[np.searchsorted(cum, 0.68)]; l95 = Hs[np.searchsorted(cum, 0.95)]
    X, Y = np.meshgrid(0.5*(xe[1:]+xe[:-1]), 0.5*(ye[1:]+ye[:-1]))
    ax.contour(X, Y, H.T, levels=[l95, l68], colors=c, linewidths=[1.0, 1.8])
    ax.plot([], [], color=c, label=tag)
xx = np.linspace(-1.0, 0.2, 50)
ax.plot(xx, -3.66*(1+xx), "k--", lw=1.2, label=r"Mirage: $w_a=-3.66(1+w_0)$")
ax.plot(-1, 0, "k*", ms=12, label=r"$\Lambda$CDM")
ax.axhline(0, color="gray", lw=0.5); ax.axvline(-1, color="gray", lw=0.5)
ax.set_xlabel(r"$w_0$"); ax.set_ylabel(r"$w_a$")
ax.set_xlim(-2.2, 0.5); ax.set_ylim(-4, 1)
ax.legend(loc="lower left", fontsize=9)
ax.set_title(r"$w_0w_a$CDM posterior (paper Fig.~12 recreation)")
fig.tight_layout(); fig.savefig("fig_w0wa_contours.png", dpi=150); plt.close(fig)

# ---------- Fig 2: GP H(z) ----------
g = cm.gp_hz()
zt, mu, cov = g["zt"], g["mu"], g["cov"]
sd = np.sqrt(np.diag(cov))
z, y, sy = g["data"]
fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.fill_between(zt, mu-2*sd, mu+2*sd, alpha=0.15, color="C0", label="GP 95%")
ax.fill_between(zt, mu-sd, mu+sd, alpha=0.3, color="C0", label="GP 68%")
ax.plot(zt, mu, "C0", lw=1.8, label="GP median")
# LambdaCDM reference
zl = np.linspace(0, 2, 200)
Om = 0.30
Hlcdm = 68.0*np.sqrt(Om*(1+zl)**3 + 1-Om)
ax.plot(zl, Hlcdm, "k--", lw=1.2, label=r"$\Lambda$CDM ($\Omega_m$=0.30)")
is_cc = np.array([zz not in z_b for zz in z]) if False else None
ax.errorbar(z, y, yerr=sy, fmt="o", ms=3.5, color="gray", alpha=0.8, label="32 CC + 6 DESI $D_H/r_d$")
ax.set_xlabel("z"); ax.set_ylabel(r"$H(z)$ [km/s/Mpc]")
ax.set_title(r"GP reconstruction of $H(z)$ (paper Fig.~13c recreation)")
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig("fig_gp_hz.png", dpi=150); plt.close(fig)

# ---------- Fig 3: H0 forest ----------
rows = [("Planck 2018", *cm.H0_LADDER["Planck2018"]),
        ("DESI+CMB (LCDM)", *cm.H0_LADDER["DESI+CMB (LCDM)"]),
        ("DESI+CMB+PP (w0wa)", *cm.H0_LADDER["DESI+CMB+PP (w0wa)"]),
        ("rd-free (DESI+CC+PP) paper", *cm.H0_LADDER["rd-free (DESI+CC+PP)"]),
        ("rd-free (DESI+CC) THIS WORK", 69.21, 1.44),
        ("CCHP TRGB", *cm.H0_LADDER["CCHP JWST TRGB"]),
        ("JWST joint 3-method", *cm.H0_LADDER["JWST joint 3-method"]),
        ("SH0ES 2022", *cm.H0_LADDER["SH0ES 2022"]),
        ("SH0ES 2024", *cm.H0_LADDER["SH0ES 2024 (42SN)"])]
fig, ax = plt.subplots(figsize=(6.8, 4.6))
for i, (nm, h, s) in enumerate(rows[::-1]):
    c = "C3" if "SH0ES" in nm else ("C0" if "THIS WORK" in nm else "k")
    ax.errorbar(h, i, xerr=s, fmt="o", color=c, ms=5, capsize=3)
ax.axvspan(66.5, 68.5, alpha=0.08, color="k")
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows[::-1]], fontsize=8)
ax.set_xlabel(r"$H_0$ [km/s/Mpc]")
ax.set_title(r"$H_0$ ladder (paper Fig.~15 recreation)")
fig.tight_layout(); fig.savefig("fig_h0_forest.png", dpi=150); plt.close(fig)

# ---------- Fig 4: tension heatmap ----------
res = json.load(open("stage2_checks.json"))
T = res["tension"]
rnames = list(T.keys()); cnames = list(T[rnames[0]].keys())
M = np.array([[T[r][c] for c in cnames] for r in rnames])
fig, ax = plt.subplots(figsize=(5.6, 4.4))
im = ax.imshow(M, cmap="RdYlGn_r", vmin=1, vmax=6.5)
ax.set_xticks(range(len(cnames))); ax.set_xticklabels(cnames, rotation=30, fontsize=8)
ax.set_yticks(range(len(rnames))); ax.set_yticklabels(rnames, fontsize=8)
for i in range(len(rnames)):
    for j in range(len(cnames)):
        ax.text(j, i, f"{M[i,j]:.2f}", ha="center", va="center", fontsize=8)
fig.colorbar(im, label=r"$|H_0^{early}-H_0^{late}|/\sigma$")
ax.set_title("Hubble tension matrix (paper Table 8 recreation)")
fig.tight_layout(); fig.savefig("fig_tension_heatmap.png", dpi=150); plt.close(fig)

print("figures written")
