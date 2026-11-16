"""Download the official Union3 and DES-SN5YR SN data releases (the two
compilations whose Mirage rows were "---" until their likelihoods were
implemented) and build the processed caches sn_extra.py reads.

Run once from verification/:
    python download_sn_extra_data.py
"""
import os
import ssl
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=180, context=CTX).read()


def fetch(url, dest):
    if os.path.exists(dest):
        print("exists:", dest)
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    data = get(url)
    open(dest, "wb").write(data)
    print("downloaded:", dest, len(data), "bytes")


def build_desy5():
    toks = []
    for line in open(os.path.join(HERE, "sn5yr", "DES-Dovekie_HD.csv")):
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("VARNAMES"):
            continue
        if s.startswith("SN:"):
            s = s[3:].strip()
        toks.append(s.split())
    names = "zHD zHEL MU MUERR MUERR_VPEC MUERR_SYS PROBIA_BEAMS".split()
    num = {nm: np.array([float(t[-7 + i]) for t in toks])
           for i, nm in enumerate(names)}
    ww = num["zHD"] > 0.0
    d = np.load(os.path.join(HERE, "sn5yr", "STAT+SYS.npz"))
    n = int(d["nsn"][0])
    icov = np.zeros((n, n))
    icov[np.triu_indices(n)] = d["cov"]
    il = np.tril_indices(n, -1)
    icov[il] = icov.T[il]
    sel = np.where(ww)[0]
    np.savez_compressed(
        os.path.join(HERE, "sn5yr", "des5yr_processed.npz"),
        zhd=num["zHD"][ww], zhel=num["zHEL"][ww], mu=num["MU"][ww],
        muerr=num["MUERR"][ww], icov=icov[np.ix_(sel, sel)])
    print("des5yr_processed.npz written:", int(ww.sum()), "SNe")


if __name__ == "__main__":
    fetch("https://raw.githubusercontent.com/rubind/union3_release/main/"
          "mu_mat_union3_cosmo%3D2_mu.fits",
          os.path.join(HERE, "union3", "mu_mat_union3_cosmo_2_mu.fits"))
    fetch("https://raw.githubusercontent.com/des-science/DES-SN5YR/main/"
          "4_DISTANCES_COVMAT/DES-Dovekie_HD.csv",
          os.path.join(HERE, "sn5yr", "DES-Dovekie_HD.csv"))
    fetch("https://raw.githubusercontent.com/des-science/DES-SN5YR/main/"
          "4_DISTANCES_COVMAT/STAT%2BSYS.npz",
          os.path.join(HERE, "sn5yr", "STAT+SYS.npz"))
    build_desy5()
