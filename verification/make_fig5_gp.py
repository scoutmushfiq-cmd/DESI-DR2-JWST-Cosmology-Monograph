import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cosmo as cm

g = cm.gp_hz()
zt, mu, cov = g["zt"], g["mu"], g["cov"]
print("ML hyperparameters: sigma_f = %.2f, l_f = %.3f" % (g["sf"], g["lf"]))
print("z_t = %.3f +- %.3f, q0 = %.3f +- %.3f" % (g["z_t"][0], g["z_t"][1], g["q0"][0], g["q0"][1]))

rng = np.random.default_rng(23)
draws = rng.multivariate_normal(mu, cov, size=600)

Om0 = 0.300
Or = 9.2e-5
E2d = (draws / np.median(draws[:, 0])) ** 2
rhode = E2d - Om0 * (1 + zt)[None, :] ** 3 - Or * (1 + zt)[None, :] ** 4
fde = rhode / rhode[:, 0:1]
lnr = np.log(np.clip(rhode, 1e-6, None))
dlnr = np.gradient(lnr, zt, axis=1)
wz = -1.0 + (1.0 + zt)[None, :] / 3.0 * dlnr

dlnH = np.gradient(np.log(draws), zt, axis=1)
qz = -1.0 + (1.0 + zt)[None, :] * dlnH

wmed = np.median(wz, axis=0)
wlo, whi = np.percentile(wz, [16, 84], axis=0)
wlo2, whi2 = np.percentile(wz, [2.5, 97.5], axis=0)

fmed = np.median(fde, axis=0)
flo, fhi = np.percentile(fde, [16, 84], axis=0)
flo2, fhi2 = np.percentile(fde, [2.5, 97.5], axis=0)
z_pk = zt[np.argmax(fmed)]
f_pk = fmed.max()
print("f_DE peak: %.3f at z = %.3f" % (f_pk, z_pk))

qmed = np.median(qz, axis=0)
qlo, qhi = np.percentile(qz, [16, 84], axis=0)
qlo2, qhi2 = np.percentile(qz, [2.5, 97.5], axis=0)
print("q0 = %.3f" % qmed[0])

fig, axes = plt.subplots(2, 2, figsize=(11.0, 8.2))
(a, b), (c, d) = axes

zz = np.linspace(0, 2, 200)
w0b, wab = -0.4231, -1.7231
a.fill_between(zt, wlo2, whi2, alpha=0.15, color="C0", label="GP 95%")
a.fill_between(zt, wlo, whi, alpha=0.35, color="C0", label="GP 68%")
a.plot(zt, wmed, "C0", lw=1.8, label="GP median")
a.plot(zz, w0b + wab * zz / (1 + zz), "r-.", lw=1.2, label="best-fit CPL")
a.axhline(-1, color="k", lw=0.8, ls="--")
a.axhspan(-1.07, -0.93, color="gray", alpha=0.15)
a.set_xlim(0, 2); a.set_ylim(-1.6, -0.2)
a.set_xlabel("$z$"); a.set_ylabel("$w(z)$")
a.set_title("(a) GP reconstruction of $w(z)$", fontsize=11)
a.legend(fontsize=8, loc="lower right")

b.fill_between(zt, flo2, fhi2, alpha=0.15, color="C0")
b.fill_between(zt, flo, fhi, alpha=0.35, color="C0")
b.plot(zt, fmed, "C0", lw=1.8, label=r"$f_{\rm DE}(z)$ median")
b.axhline(1.0, color="k", lw=0.8, ls="--")
b.plot([z_pk], [f_pk], "ko", ms=4)
b.annotate(r"$f_{\rm DE}^{\rm max}\!\approx\!%.2f$ at $z\!\approx\!%.2f$" % (f_pk, z_pk),
           xy=(z_pk, f_pk), xytext=(0.75, 1.12), fontsize=9,
           arrowprops=dict(arrowstyle="->", lw=0.8))
b.set_xlim(0, 2)
b.set_xlabel("$z$"); b.set_ylabel(r"$f_{\rm DE}(z)=\rho_{\rm DE}(z)/\rho_{\rm DE,0}$")
b.set_title(r"(b) Normalized dark energy density", fontsize=11)
b.legend(fontsize=8, loc="lower left")

z_cc, h_cc, s_cc = cm.CC_DATA[:, 0], cm.CC_DATA[:, 1], cm.CC_DATA[:, 2]
dh = np.array([bb[4] for bb in cm.DESI_BAO[1:]])
sdh = np.array([bb[5] for bb in cm.DESI_BAO[1:]])
z_b = np.array([bb[1] for bb in cm.DESI_BAO[1:]])
rd = 147.09
h_b = cm.C_KMS / (rd * dh)
s_b = h_b * (sdh / dh)

amed = np.median(draws, axis=0)
alo, ahi = np.percentile(draws, [16, 84], axis=0)
alo2, ahi2 = np.percentile(draws, [2.5, 97.5], axis=0)
adot_med = amed / (1 + zt)
c.fill_between(zt, alo2 / (1 + zt), ahi2 / (1 + zt), alpha=0.15, color="C0")
c.fill_between(zt, alo / (1 + zt), ahi / (1 + zt), alpha=0.35, color="C0")
c.plot(zt, adot_med, "C0", lw=1.8, label=r"GP $\dot a = H/(1+z)$")
c.errorbar(z_cc, h_cc / (1 + z_cc), yerr=s_cc / (1 + z_cc), fmt="o",
           color="gray", ms=4, elinewidth=0.8, capsize=0, label="32 Cosmic Chronometers", zorder=5)
c.errorbar(z_b, h_b / (1 + z_b), yerr=s_b / (1 + z_b), fmt="s",
           color="crimson", ms=5, elinewidth=0.9, capsize=0,
           label=r"6 DESI DR2 $D_H/r_d$ bins", zorder=6)
c.set_xlim(0, 2)
c.set_xlabel("$z$"); c.set_ylabel(r"$\dot a = H(z)/(1+z)$  [km s$^{-1}$ Mpc$^{-1}$]")
c.set_title("(c) Comoving expansion speed vs. data", fontsize=11)
c.legend(fontsize=8, loc="upper right")

d.fill_between(zt, qlo2, qhi2, alpha=0.15, color="C0")
d.fill_between(zt, qlo, qhi, alpha=0.35, color="C0")
d.plot(zt, qmed, "C0", lw=1.8, label="GP median")
d.axhline(0, color="k", lw=0.8, ls="--")
z_t = g["z_t"][0]
d.plot([z_t], [0], "ko", ms=5)
d.annotate(r"$z_t \approx %.2f$" % z_t, xy=(z_t, 0), xytext=(z_t + 0.25, 0.35),
           fontsize=9, arrowprops=dict(arrowstyle="->", lw=0.8))
d.axhline(0.533 * 2 * 0.315 - 1.0, color="gray", lw=0.8, ls=":")
d.set_xlim(0, 2)
d.set_xlabel("$z$"); d.set_ylabel("$q(z)$")
d.set_title("(d) Deceleration parameter and transition", fontsize=11)
d.legend(fontsize=8, loc="upper right")

fig.suptitle("Non-parametric GP reconstruction (ML hyperparameters: "
             r"$\sigma_f \approx %.0f,\ \ell_f \approx %.2f$)" % (g["sf"], g["lf"]), fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig("fig5_gp_wz_reconstruction.pdf", bbox_inches="tight")
fig.savefig("fig5_gp_wz_reconstruction.png", dpi=150, bbox_inches="tight")
print("saved fig5_gp_wz_reconstruction.pdf/.png")
