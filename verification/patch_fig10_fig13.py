"""Round-13 m1+m2 fix: surgically patch two legacy figures.

fig10_jwst_vs_hst_host_comparison.pdf:
  the panel legend "SH0ES Restricted to Same N = 11 Hosts (71.20 +/- 1.85)"
  quotes an uncertainty (+/- 1.85) that is backed nowhere in the paper; the
  center 71.20 is backed by the H0^HST,sub column of the JWST/HST comparison
  table. The label is reduced to "(71.20)".

fig13_non_cepheid_lensing_lowz_sn.pdf:
  the H0pe marker in panel (a) carries a symmetric +/- 6.80 bar (68.60-82.20)
  while the paper and its table quote the asymmetric credible interval
  75.40 +8.10/-5.50 (69.90-83.50). The bar is redrawn asymmetrically and the
  in-panel label is corrected. Axis calibration is read off the tick labels
  (H0 = 65, 70, 75, 80 at page x = 238.70, 293.74, 348.77, 403.81).

Both patches are deterministic on the committed input PDFs and assert every
pre-patch geometry before touching anything; they are idempotent (already
patched figures are detected and skipped).

Run from verification/:  python patch_fig10_fig13.py
"""
import os
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "fig7_DejaVuSans.ttf")
USE_DEJAVU = os.path.exists(FONT)
CRIMSON = (0.7450980544090271, 0.07058823853731155, 0.23529411852359772)

# ---------------------------------------------------------------- fig10 -----
F10 = os.path.join(ROOT, "figs", "fig10_jwst_vs_hst_host_comparison.pdf")
doc = pymupdf.open(F10)
page = doc[0]
hits = page.search_for("71.20 \u00b1 1.85")
if not hits and "71.20" in page.get_text():
    doc.close()
    print("fig10: already patched ('+/- 1.85' absent, center 71.20 present)")
else:
    assert len(hits) == 1, \
        "fig10: expected exactly one '71.20 +/- 1.85' span, got %d" % len(hits)
    r = hits[0]
    page.add_redact_annot(r)
    page.apply_redactions()
    if USE_DEJAVU:
        page.insert_font(fontname="DejaVuSans", fontfile=FONT)
    page.insert_text(pymupdf.Point(r.x0, r.y1 - 1.4), "71.20",
                     fontname="DejaVuSans" if USE_DEJAVU else "helv",
                     fontsize=7.0, color=(0, 0, 0))
    doc.saveIncr()
    doc.close()
    doc = pymupdf.open(F10)
    txt = doc[0].get_text()
    assert "1.85" not in txt, "fig10: stale +/- 1.85 still present"
    assert "71.20" in txt, "fig10: backed center 71.20 lost"
    doc.close()
    print("fig10: unbacked '+/- 1.85' removed; label now '(71.20)'")

# ---------------------------------------------------------------- fig13 -----
F13 = os.path.join(ROOT, "figs", "fig13_non_cepheid_lensing_lowz_sn.pdf")
X65, X80 = 238.70, 403.81          # page x of the H0 = 65 and 80 tick labels
PT_PER_H0 = (X80 - X65) / 15.0
ROW_Y = 251.82                      # page y of the H0pe row
CAP_HALF = 3.5                      # caps span ROW_Y +/- 3.5

def to_x(h0):
    return X65 + (h0 - 65.0) * PT_PER_H0

def scan_h0pe(page):
    marker = None
    bar = None
    caps = []
    for g in page.get_drawings():
        rct = g["rect"]
        if abs((rct.y0 + rct.y1) / 2 - ROW_Y) > 3.5:
            continue
        if rct.width > 100 and rct.height < 1 and g.get("color") == CRIMSON:
            bar = rct
        elif 4 < rct.width < 7 and 4 < rct.height < 7 and g.get("fill") == CRIMSON:
            marker = rct
        elif rct.width < 1.5 and abs(rct.height - 7.0) < 0.5 and \
                (g.get("fill") == CRIMSON or g.get("color") == CRIMSON):
            caps.append(rct)
    return marker, bar, caps

doc = pymupdf.open(F13)
page = doc[0]
old_label = page.search_for("75.40 \u00b1 6.80")
if not old_label and "+8.10" in page.get_text():
    doc.close()
    print("fig13: already patched (asymmetric label present)")
else:
    assert len(old_label) == 1, "fig13: expected one '75.40 +/- 6.80' label"
    marker, bar, caps = scan_h0pe(page)
    assert marker is not None, "fig13: H0pe marker not found"
    assert bar is not None, "fig13: H0pe error bar not found"
    assert len(caps) == 2, "fig13: expected 2 caps, found %d" % len(caps)
    mk_h0 = 65.0 + ((marker.x0 + marker.x1) / 2 - X65) / PT_PER_H0
    lo_h0 = 65.0 + (min(c.x0 for c in caps) - X65) / PT_PER_H0
    hi_h0 = 65.0 + (max(c.x0 for c in caps) - X65) / PT_PER_H0
    assert abs(mk_h0 - 75.40) < 0.05, "fig13: marker H0 drifted: %.3f" % mk_h0
    assert abs(lo_h0 - 68.60) < 0.05 and abs(hi_h0 - 82.20) < 0.05, \
        "fig13: symmetric bar endpoints drifted: %.3f-%.3f" % (lo_h0, hi_h0)
    print("pre-patch geometry verified: marker %.2f, bar %.2f-%.2f"
          % (mk_h0, lo_h0, hi_h0))

    lr = old_label[0]
    page.add_redact_annot(lr)
    page.apply_redactions()

    page.draw_rect(pymupdf.Rect(bar.x0 - 1.0, ROW_Y - CAP_HALF - 1.2,
                                marker.x0 + 0.05, ROW_Y + CAP_HALF + 1.2),
                   color=None, fill=(1, 1, 1), width=0)
    page.draw_rect(pymupdf.Rect(marker.x1 - 0.05, ROW_Y - CAP_HALF - 1.2,
                                bar.x1 + 1.0, ROW_Y + CAP_HALF + 1.2),
                   color=None, fill=(1, 1, 1), width=0)

    XL, XH = to_x(69.90), to_x(83.50)
    page.draw_line(pymupdf.Point(XL, ROW_Y), pymupdf.Point(XH, ROW_Y),
                   color=CRIMSON, width=1.2)
    for xc in (XL, XH):
        page.draw_line(pymupdf.Point(xc, ROW_Y - CAP_HALF),
                       pymupdf.Point(xc, ROW_Y + CAP_HALF),
                       color=CRIMSON, width=1.2)

    if USE_DEJAVU:
        page.insert_font(fontname="DejaVuSans", fontfile=FONT)
    NEW_TXT = "75.40 +8.10/\u22125.50"
    fnt = pymupdf.Font(fontfile=FONT) if USE_DEJAVU else pymupdf.Font("helv")
    tw = fnt.text_length(NEW_TXT, fontsize=7.2)
    page.draw_rect(pymupdf.Rect(lr.x0 - 1.0, lr.y0 - 0.5,
                                lr.x0 + tw + 2.0, lr.y1 + 0.5),
                   color=None, fill=(1, 1, 1), width=0)
    page.insert_text(pymupdf.Point(lr.x0, lr.y1 - 1.4), NEW_TXT,
                     fontname="DejaVuSans" if USE_DEJAVU else "helv",
                     fontsize=7.2, color=(0, 0, 0))
    doc.saveIncr()
    doc.close()

    doc = pymupdf.open(F13)
    page = doc[0]
    txt = page.get_text()
    assert "75.40 \u00b1 6.80" not in txt, "fig13: stale symmetric label still present"
    assert "+8.10" in txt and "5.50" in txt, "fig13: corrected label missing"
    marker2, bar2, caps2 = scan_h0pe(page)
    new_lo, new_hi = to_x(69.90), to_x(83.50)
    assert any(abs(c.x0 - new_lo) < 0.1 for c in caps2), \
        "fig13: new lower cap missing at x=%.2f" % new_lo
    assert any(abs(c.x0 - new_hi) < 0.1 for c in caps2), \
        "fig13: new upper cap missing at x=%.2f" % new_hi
    covers = [g["rect"] for g in page.get_drawings()
              if g.get("fill") == (1.0, 1.0, 1.0)
              and g["rect"].y0 < ROW_Y < g["rect"].y1]
    assert any(c.x0 <= bar.x0 and c.x1 >= marker.x0 for c in covers), \
        "fig13: old lower bar segment not covered"
    assert any(c.x0 <= marker.x1 and c.x1 >= bar.x1 for c in covers), \
        "fig13: old upper bar segment not covered"
    assert marker2 is not None and \
        abs(65.0 + ((marker2.x0 + marker2.x1) / 2 - X65) / PT_PER_H0 - 75.40) < 0.05, \
        "fig13: marker disturbed"
    doc.close()
    print("fig13: asymmetric bar 69.90-83.50 drawn, label '75.40 +8.10/-5.50' set")

print("post-patch checks pass for both figures")
