# Union3 data (not committed — download from the official release)

`sn_extra.load_union3` expects `mu_mat_union3_cosmo_2_mu.fits` in this
directory (8.6 KB), from:

- https://github.com/rubind/union3_release
  (`mu_mat_union3_cosmo=2_mu.fits`; Union3 + UNITY1.5 compressed
  distances, Rubin et al. 2025)

FITS layout (per the release README): a 23 x 23 float64 matrix whose first
row is redshift, first column is distance modulus, and the remaining
22 x 22 block is the inverse covariance matrix of the binned mu.
