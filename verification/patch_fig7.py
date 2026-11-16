"""Round-13 M2 fix: surgically patch figs/fig7_ede_horndeski_degeneracy.pdf.

Three defects fixed in place (the patch is deterministic on the committed
input PDF, so it is reproducible):
  1. the Sound-Horizon-Free marker is moved from the superseded
     (r_d, H0) = (146.99, 69.25) to the committed-chain values (146.36, 68.19)
     (verification/rdfree_results.json, chain_rdfree_cpl_desi_cc_pp.npy);
  2. the hyperbola label "H0rd = 10027 +/- 65" is corrected to "+/- 45"
     (verification/h0rd_check.json: err_quadrature 44.8, err_montecarlo 44.9);
  3. the unbacked legend value "f_EDE = 0.092 +/- 0.024" is replaced by the
     caption's own backed range "f_EDE ~ 0.09-0.13" (Poulin et al. 2025).

Before patching, the script asserts that every other marker sits at its
expected data coordinate, so any drift in the legacy figure is caught.

Run from verification/:  python patch_fig7.py
"""
import os
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figs", "fig7_ede_horndeski_degeneracy.pdf")
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "fig7_DejaVuSans.ttf")

# axis calibration extracted from the tick-label positions of the committed PDF
X0, X1 = 51.3, 338.3          # page x of rd = 136 .. 152
Y0, Y1 = 237.7, 55.5          # page y of H0 = 66 .. 74
RD0, RD1, H0_0, H0_1 = 136.0, 152.0, 66.0, 74.0

def to_page(rd, h0):
    px = X0 + (rd - RD0) * (X1 - X0) / (RD1 - RD0)
    py = Y0 + (h0 - H0_0) * (Y1 - Y0) / (H0_1 - H0_0)
    return px, py

def from_page(px, py):
    rd = RD0 + (px - X0) * (RD1 - RD0) / (X1 - X0)
    h0 = H0_0 + (py - Y0) * (H0_1 - H0_0) / (Y1 - Y0)
    return rd, h0

doc = pymupdf.open(FIG)
page = doc[0]

# --- 1. assert every marker position before touching anything -------------
EXPECTED = {
    (147.09, 68.18): (0.11, 0.31, 0.85),   # Flat LambdaCDM (DESI DR2 + CMB)
    (147.15, 67.52): (0.02, 0.59, 0.41),   # w0waCDM (DESI DR2 + CMB + Pantheon+)
    (139.70, 71.86): (0.49, 0.23, 0.93),   # Early Dark Energy
    (146.99, 69.25): (0.75, 0.07, 0.24),   # Sound-Horizon-Free (superseded)
}
found = {}
for g in page.get_drawings():
    r = g["rect"]
    if 1.5 < r.width < 9 and 1.5 < r.height < 9 and abs(r.width - r.height) < 2.5 \
            and r.y1 < 250 and r.x0 > 35 and g.get("fill"):
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        rd, h0 = from_page(cx, cy)
        key = (round(rd, 2), round(h0, 2))
        if key in EXPECTED:
            found[key] = tuple(round(c, 2) for c in g["fill"])
for key, col in EXPECTED.items():
    assert key in found, "expected marker %s not found in fig7" % (key,)
    assert found[key] == col, "marker %s color drifted: %s" % (key, found[key])
print("all four legacy markers verified at their expected coordinates")

# --- 2. move the Sound-Horizon-Free marker ---------------------------------
SHF_OLD = to_page(146.99, 69.25)
SHF_NEW = to_page(146.36, 68.19)
SHF_COL = (0.745, 0.071, 0.235)
page.draw_rect(pymupdf.Rect(SHF_OLD[0] - 4, SHF_OLD[1] - 4,
                            SHF_OLD[0] + 4, SHF_OLD[1] + 4),
               color=None, fill=(1, 1, 1), width=0)
RAD = 2.5
page.draw_circle(SHF_NEW, RAD, color=SHF_COL, fill=SHF_COL, width=0.8)
print("SHF marker moved to (r_d, H0) = (146.36, 68.19)")

# --- 3. text corrections ----------------------------------------------------
USE_DEJAVU = os.path.exists(FONT)

def replace_text(old_sub, new_sub, size=7.2):
    rects = page.search_for(old_sub)
    assert rects, "fig7: search text not found: %r" % old_sub
    r = rects[0]
    page.add_redact_annot(r)
    page.apply_redactions()
    if USE_DEJAVU:
        page.insert_font(fontname="DejaVuSans", fontfile=FONT)
    page.insert_text(pymupdf.Point(r.x0, r.y1 - 1.4), new_sub,
                     fontname="DejaVuSans" if USE_DEJAVU else "helv",
                     fontsize=size, color=(0, 0, 0))
    return r

replace_text("\u00b1 65", "\u00b1 45")
print("hyperbola label corrected to 10027 +/- 45")
replace_text("= 0.092 \u00b1 0.024", "\u2248 0.09\u20130.13")
print("EDE legend corrected to f_EDE ~ 0.09-0.13")

doc.saveIncr()
doc.close()

# --- 4. post-patch verification ---------------------------------------------
doc = pymupdf.open(FIG)
page = doc[0]
txt = page.get_text()
assert "0.092" not in txt and "0.126" not in txt, "stale EDE value still present"
assert "\u00b1 65" not in txt, "stale hyperbola error still present"
moved = []
for g in page.get_drawings():
    r = g["rect"]
    if 1.5 < r.width < 9 and 1.5 < r.height < 9 and abs(r.width - r.height) < 2.5 \
            and r.y1 < 250 and r.x0 > 35 and g.get("fill") \
            and all(abs(c - s) < 0.01 for c, s in zip(g["fill"], SHF_COL)):
        moved.append(from_page((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))
assert moved and abs(moved[-1][0] - 146.36) < 0.05 and abs(moved[-1][1] - 68.19) < 0.05, \
    "new SHF marker not found at (146.36, 68.19): %s" % moved
print("post-patch checks pass: SHF marker at (%.2f, %.2f)" % moved[-1])
