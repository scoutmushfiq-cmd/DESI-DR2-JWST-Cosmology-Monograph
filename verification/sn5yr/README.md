# DES-SN5YR data (not committed — download from the official release)

`sn_extra.load_desy5` expects `des5yr_processed.npz` in this directory,
built by `verification/download_sn_extra_data.py` from two official files:

- `DES-Dovekie_HD.csv` — Hubble diagram (1820 SNe Ia, zHD > 0)
  (`4_DISTANCES_COVMAT/DES-Dovekie_HD.csv`)
- `STAT+SYS.npz` — upper triangle of the INVERSE stat+sys covariance
  (`4_DISTANCES_COVMAT/STAT+SYS.npz`); the release's own
  `DES-Dovekie-SN_Likelihood.py` documents this format

Source: https://github.com/des-science/DES-SN5YR (DES-SN5YR release,
Vincent et al. 2024).

The covariance files are not redistributed here because of their size and
the release's preferred distribution channel.
