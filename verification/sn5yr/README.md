# DES-SN5YR data (not committed — download from the official release)

`sn_extra.load_desy5` expects `des5yr_processed.npz` in this directory,
built by `verification/download_sn_extra_data.py` from two official files:

- `DES-Dovekie_HD.csv` — Hubble diagram (1820 SNe Ia, zHD > 0)
  (`4_DISTANCES_COVMAT/DES-Dovekie_HD.csv`)
- `STAT+SYS.npz` — upper triangle of the INVERSE stat+sys covariance
  (`4_DISTANCES_COVMAT/STAT+SYS.npz`); the release's own
  `DES-Dovekie-SN_Likelihood.py` documents this format

Source: https://github.com/des-science/DES-SN5YR (official DES-SN5YR
release repository, DES Collaboration 2024, arXiv:2401.02929).

Note on the distance file: `DES-Dovekie_HD.csv` is NOT the 1829-SN
DES-SN5YR analysis sample itself but its recalibrated reanalysis
DES-Dovekie (Popovic et al. 2025, arXiv:2511.07517): 1820 SNe
(1623 DES SNe and 197 low-z SNe), shipped with the release's official
likelihood script `DES-Dovekie-SN_Likelihood.py`.

The covariance files are not redistributed here because of their size and
the release's preferred distribution channel.
