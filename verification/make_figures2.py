import json, numpy as np, cosmo as cm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- Fig 5: corner plot (CPL DESI+CMB, 4 chains combined) ----------
files = ["chain_w0wa_desi_cmb.npy","chain_w0wa_desi_cmb_s111.npy",
         "chain_w0wa_desi_cmb_s222.npy","chain_w0wa_desi_cmb_s333.npy"]
ch = np.vstack([np.load(f) for f in files])
H0, wbc, w0, wa = ch[:,0], ch[:,1], ch[:,2], ch[:,3]
Om = (wbc + cm.W_NU)/(H0/100)**2
data = np.column_stack([H0, Om, w0, wa])
labels = [r"$H_0$", r"$\Omega_m$", r"$w_0$", r"$w_a$"]
lims = [(62,66),(0.32,0.40),(-1.5,0.5),(-3.5,0.2)]
n = 4
fig, axes = plt.subplots(n, n, figsize=(8.5, 8.5))
plt.subplots_adjust(wspace=0.05, hspace=0.05)
for i in range(n):
    for j in range(n):
        ax = axes[i,j]
        if j > i:
            ax.axis("off"); continue
        if i == j:
            ax.hist(data[:,i], bins=60, range=lims[i], color="C0", alpha=0.6, density=True)
            lo, hi = np.percentile(data[:,i], [16,84])
            ax.axvline(lo, color="C3", lw=0.8); ax.axvline(hi, color="C3", lw=0.8)
            ax.set_xlim(lims[i])
            if j>0: ax.set_yticklabels([])
            if i<n-1: ax.set_xticklabels([])
        else:
            xj, xi = data[:,j], data[:,i]
            Hh, xe, ye = np.histogram2d(xj, xi, bins=50, range=[lims[j], lims[i]])
            Hs = np.sort(Hh.ravel())[::-1]; cum = np.cumsum(Hs)/Hs.sum()
            l68 = Hs[np.searchsorted(cum,0.68)]; l95 = Hs[np.searchsorted(cum,0.95)]
            X, Y = np.meshgrid(0.5*(xe[1:]+xe[:-1]), 0.5*(ye[1:]+ye[:-1]))
            ax.contour(X, Y, Hh.T, levels=[l95,l68], colors="C0", linewidths=[0.8,1.4])
            ax.set_xlim(lims[j]); ax.set_ylim(lims[i])
            if i<n-1: ax.set_xticklabels([])
            if j>0: ax.set_yticklabels([])
        if i==n-1: ax.set_xlabel(labels[j], fontsize=11)
        if j==0: ax.set_ylabel(labels[i], fontsize=11)
fig.suptitle(r"$w_0w_a$CDM, DESI DR2 + CMB (4 chains, $R_{hat}\leq1.014$)", y=0.92)
fig.savefig("fig_corner_w0wa.png", dpi=150, bbox_inches="tight"); plt.close(fig)

# ---------- Fig 6: GP w(z) reconstruction ----------
g = cm.gp_hz()
zt, mu, cov = g["zt"], g["mu"], g["cov"]
rng = np.random.default_rng(23)
draws = rng.multivariate_normal(mu, cov, size=600)
Om0 = 0.300
E2d = (draws/ (np.median(draws[:,0])))**2  # normalize by H(z=0) draw
# rho_DE(z)/rho_crit0 = E^2 - Om(1+z)^3 - Or(1+z)^4, with Or from Om0 fiducial
Or = 9.2e-5
rhode = E2d - Om0*(1+zt)[None,:]**3 - Or*(1+zt)[None,:]**4
lnr = np.log(np.clip(rhode, 1e-6, None))
dlnr = np.gradient(lnr, zt, axis=1)
wz = -1.0 + (1.0+zt)[None,:]/3.0 * dlnr
wmed = np.median(wz, axis=0); wlo = np.percentile(wz, 16, axis=0); whi = np.percentile(wz, 84, axis=0)
wlo2 = np.percentile(wz, 2.5, axis=0); whi2 = np.percentile(wz, 97.5, axis=0)
fig, ax = plt.subplots(figsize=(6.4,4.6))
ax.fill_between(zt, wlo2, whi2, alpha=0.15, color="C0", label="GP 95%")
ax.fill_between(zt, wlo, whi, alpha=0.3, color="C0", label="GP 68%")
ax.plot(zt, wmed, "C0", lw=1.8, label="GP median")
# CPL best fit
zpl = np.linspace(0,2,200)
w0b, wab = -0.4231, -1.7231
wcpl = w0b + wab*zpl/(1+zpl)
ax.plot(zpl, wcpl, "r-.", lw=1.2, label="best-fit CPL")
ax.axhline(-1, color="k", lw=0.8, ls="--")
ax.axhspan(-1-0.07, -1+0.07, color="gray", alpha=0.15)
ax.set_xlim(0,2); ax.set_ylim(-2.5, 0.5)
ax.set_xlabel("z"); ax.set_ylabel(r"$w(z)$")
ax.set_title(r"GP reconstruction of $w(z)$ (paper Fig.~13a recreation)")
ax.legend(fontsize=8, loc="lower left")
fig.tight_layout(); fig.savefig("fig_gp_wz.png", dpi=150); plt.close(fig)

# ---------- Fig 7: Om(z) diagnostic ----------
zl = np.linspace(0.001, 2.0, 300)
H0b = 68.35
Omlcdm = ((H0b*np.sqrt(Om0*(1+zl)**3+1-Om0)/H0b)**2 - 1)/(((1+zl)**3)-1)
# data: Om at each CC point + DESI DH points using best-fit H0
z_cc, h_cc, s_cc = cm.CC_DATA[:,0], cm.CC_DATA[:,1], cm.CC_DATA[:,2]
dh = np.array([b[4] for b in cm.DESI_BAO[1:]]); sdh = np.array([b[5] for b in cm.DESI_BAO[1:]])
z_b = np.array([b[1] for b in cm.DESI_BAO[1:]])
h_b = cm.C_KMS/(147.09*dh); s_b = h_b*(sdh/dh)
zd = np.concatenate([z_cc, z_b]); Hd = np.concatenate([h_cc, h_b]); sd = np.concatenate([s_cc, s_b])
o = np.argsort(zd); zd, Hd, sd = zd[o], Hd[o], sd[o]
mask = zd > 0.05
zd, Hd, sd = zd[mask], Hd[mask], sd[mask]
om_data = ((Hd/H0b)**2 - 1)/((1+zd)**3 - 1)
om_err = 2*Hd**2/(H0b**2*((1+zd)**3-1))*sd
fig, ax = plt.subplots(figsize=(6.4,4.4))
ax.errorbar(zd, om_data, yerr=om_err, fmt="o", ms=4, color="gray", label="32 CC + 6 DESI $D_H$")
ax.axhline(Om0, color="k", ls="--", lw=1.2, label=r"$\Lambda$CDM: $\Omega_m$=0.300")
# CPL prediction
E2cpl = Om0*(1+zl)**3 + (1-Om0-9.2e-5)*cm.f_de(zl, w0b, wab) + 9.2e-5*(1+zl)**4
om_cpl = ((E2cpl) - 1)/(((1+zl)**3)-1)
ax.plot(zl, om_cpl, "r-.", lw=1.2, label="best-fit CPL")
ax.set_xlabel("z"); ax.set_ylabel(r"$\Omega_m(z)$ diagnostic")
ax.set_ylim(0.1, 0.6)
ax.set_title(r"$Om(z)$ diagnostic (paper $\S$6 recreation)")
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig("fig_om_diagnostic.png", dpi=150); plt.close(fig)
print("3 figures done")
