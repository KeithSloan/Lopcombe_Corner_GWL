"""Build Lopcombe_Start_of_Winter_Level.pdf from the analysis outputs."""
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph as _P, Spacer, Table, TableStyle, Image, PageBreak

BASE = "."
RES = json.load(open(f"{BASE}/output/haduk/start_level_results.json"))
PNG = f"{BASE}/output/haduk/Lopcombe_start_level.png"
OUT = f"{BASE}/docs/reports/Lopcombe_Start_of_Winter_Level.pdf"
ORANGE, INK2 = "#eb6834", "#52514e"

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=17, leading=21, spaceAfter=4, alignment=0)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontSize=9, textColor=colors.HexColor(INK2), spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12, leading=15, spaceBefore=10, spaceAfter=4)
BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontSize=9.5, leading=13, spaceAfter=4)
BUL = ParagraphStyle("BUL", parent=BODY, leftIndent=12, bulletIndent=2)
NOTE = ParagraphStyle("NOTE", parent=BODY, backColor=colors.HexColor("#eef4fc"),
                      borderColor=colors.HexColor("#2a78d6"), borderWidth=0.8, borderPadding=6,
                      spaceBefore=6, spaceAfter=10)
SMALL = ParagraphStyle("SMALL", parent=BODY, fontSize=8, leading=10, textColor=colors.HexColor(INK2))


def P(text, style):
    return _P(text.replace("²", "<super>2</super>"), style)


def bullets(items):
    return [_P(t.replace("²", "<super>2</super>"), BUL, bulletText="•") for t in items]


def table(rows, widths, font=8.5, bold_rows=(), left=False):
    t = Table(rows, colWidths=widths, repeatRows=1)
    st = [("FONT", (0, 0), (-1, -1), "Helvetica", font),
          ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", font),
          ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor(INK2)),
          ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f1")]),
          ("ALIGN", (1, 0), (-1, -1), "LEFT" if left else "RIGHT"),
          ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    st += [("FONT", (0, r), (-1, r), "Helvetica-Bold", font) for r in bold_rows]
    t.setStyle(TableStyle(st))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor(INK2))
    canvas.drawString(18 * mm, 10 * mm, "Lopcombe Corner borehole (EA E14150) · Start-of-winter level analysis · updated 20 Oct 2026")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


import pandas as pd
RL = json.load(open(f"{BASE}/output/haduk/start_level_results_logger.json"))
D = pd.read_csv(f"{BASE}/output/haduk/start_level_winters.csv")
M, ML = RES["models"], RL["models"]
lab = lambda y: f"{y - 1}/{str(y)[2:]}"
m1, m2 = M["octmar"], M["octmar_start"]
k_rain, k_start = m2["coef"][1], m2["coef"][2]
pv = lambda p: "&lt; 0.001" if p < 0.001 else f"{p:.3f}"

s = [P("Lopcombe Corner — Does the Level at the Start of Winter Matter?", H1),
     P(f"Winter peak vs Oct–Mar rainfall with and without the 1 October groundwater level · {RES['n']} winters "
       f"{lab(RES['first'])}–{lab(RES['last'])} · levels: full EA record (manual dips and daily logger) · rainfall: "
       "HadUK-Grid 1 km, borehole cell · updated 20 Oct 2026", SUB),
     P(f"<b>Bottom line.</b> Yes. Adding the 1 October level to Oct–Mar rainfall raises the share of winter-peak variation "
       f"explained from {m1['r2']:.2f} to <b>{m2['r2']:.2f}</b> and cuts the typical error from {m1['rmse']:.1f} m to "
       f"{m2['rmse']:.1f} m. Each extra metre of starting level adds about <b>{k_start:.1f} m</b> to the peak "
       f"(p {pv(m2['p'][2])}). Because the well drains back to almost the same level every autumn "
       f"({RES['start_level_mean']:.2f} ± {RES['start_level_sd']:.2f} m), rainfall is still the main driver — but a high "
       "start makes a flood noticeably more likely.", NOTE),
     P("<i>This replaces the version issued earlier on 20 Oct 2026, which used 25 winters and logger-era peaks that "
       "were later found to be too low in several years. With the full EA record the effect is stronger and is now "
       "tested over all winters back to 1963/64.</i>", SMALL),
     P("1. What the start level is", H2)]
s += bullets([
    "The level on 1 October, interpolated between the nearest readings (within 21 days), before winter recharge begins. "
    "It matches the autumn recession low used earlier to within a few centimetres.",
    f"Across {RES['n']} winters it averaged {RES['start_level_mean']:.2f} m (standard deviation "
    f"{RES['start_level_sd']:.2f} m), from {RES['start_level_min']:.2f} m (1976/77, after the 1976 drought) to "
    f"{RES['start_level_max']:.2f} m (2008/09).",
    f"It is unrelated to that winter's rainfall (r = {RES['corr_start_rain']:.2f}), so it adds independent information. "
    f"On its own it correlates with the peak at r = {RES['corr_start_peak']:.2f}."])

s.append(P("2. How the finding has developed", H2))
rows = [["Analysis", "Data", "Without start", "With start", "Start effect"],
        ["v1, v2 (7 Sep)", "Broughton Oct–Jan / Oct–Dec, first-pass peaks", "0.52 / 0.43", "0.56 / 0.49", "weak, not significant"],
        ["v3 (7 Sep)", "Broughton Oct–Mar, corrected peaks, 25 winters", "0.74", "0.83", "≈ +5 m per m"],
        ["20 Oct, first issue", "HadUK Oct–Mar, peaks later found too low, 25 winters", "0.80", "0.85", "+3.6 m per m, p 0.02"],
        ["This report", f"HadUK Oct–Mar, full record, logger era ({RL['n']})",
         f"{ML['octmar']['r2']:.2f}", f"{ML['octmar_start']['r2']:.2f}",
         f"+{ML['octmar_start']['coef'][2]:.1f} m per m, p {ML['octmar_start']['p'][2]:.3f}"],
        ["This report", f"HadUK Oct–Mar, full record, all winters ({RES['n']})", f"{m1['r2']:.2f}", f"{m2['r2']:.2f}",
         f"+{k_start:.1f} m per m, p &lt; 0.001"]]
rows = [[_P(c, ParagraphStyle("c", fontName="Helvetica-Bold" if i in (0, 5) else "Helvetica", fontSize=8, leading=10))
         for c in r] for i, r in enumerate(rows)]
s.append(table(rows, [26 * mm, 62 * mm, 22 * mm, 20 * mm, 44 * mm], font=8))
s.append(P("Columns 3–4 are R² (share of variation in winter peak explained).", SMALL))
s += bullets([
    "The early analyses saw little effect because their rainfall window missed Feb–Mar recharge and several peaks were "
    "truncated. Fixing those made the effect clear.",
    "This morning's version understated it because the peaks it used were too low in several winters that had started "
    "high — 2024/25 (start 79.04 m; peak 95.04 m, not 90.31 m) and 2012/13 (start 79.04 m; peak 95.73 m, not 94.42 m). "
    "With the full record the effect is larger and much more certain.",
    f"Using Oct–Jan rain instead: R² {M['octjan']['r2']:.2f} → {M['octjan_start']['r2']:.2f}, start effect "
    f"+{M['octjan_start']['coef'][2]:.1f} m per m — the same picture."])

s.append(P(f"3. Current model (all {RES['n']} winters)", H2))
rows = [["Model", "Term", "Coefficient", "Std error", "p-value"]]
for key, name in (("octmar", "Rain only"), ("octmar_start", "Rain + start level")):
    m = M[key]
    for i, term in enumerate(m["names"]):
        t = {"intercept": "Intercept", "oct_mar_mm": "Oct–Mar rain (per mm)", "start_level": "Start level (per m)"}[term]
        rows.append([name if i == 0 else "", t, f"{m['coef'][i]:.3f}", f"{m['se'][i]:.3f}", pv(m["p"][i])])
rows = [[_P(c, ParagraphStyle("c", fontName="Helvetica-Bold" if i == 0 else "Helvetica", fontSize=8, leading=10))
         for c in r] for i, r in enumerate(rows)]
s.append(table(rows, [38 * mm, 46 * mm, 28 * mm, 28 * mm, 28 * mm], font=8))
f, fp = RES["f_test_octmar"]
s.append(P(f"Fit: peak ≈ {m2['coef'][0]:.1f} + {k_rain:.3f} × Oct–Mar rain + {k_start:.2f} × 1 October level. "
           f"F-test for adding the start level: F = {f:.1f}, p {pv(fp)}. Partial correlation of start level with the "
           f"peak after allowing for rain: r = {RES['partial_r_start']:.2f}. 95% range for the start effect: about "
           f"{k_start - 2 * m2['se'][2]:.1f}–{k_start + 2 * m2['se'][2]:.1f} m per m.", BODY))
s.append(P(f"<b>In practical terms:</b> a start one standard deviation ({RES['start_level_sd']:.2f} m) above average raises "
           f"the expected peak by about {k_start * RES['start_level_sd']:.1f} m. By comparison, 100 mm more Oct–Mar rain "
           f"raises it by about {k_rain * 100:.1f} m, and one standard deviation of Oct–Mar rain (127 mm) by about "
           f"{k_rain * 127:.1f} m. So rainfall matters roughly two to three times as much, but a high start is worth "
           "about 50 mm of extra winter rain.", BODY))

s.append(PageBreak())
s.append(P("4. Where the start level helps — and where it doesn't", H2))
s += bullets([
    "<b>Helps most:</b> 1976/77 (start 77.15 m; residual −6.4 → −0.6 m), 2008/09 (79.39 m; +7.4 → +3.2 m), "
    "1997/98 (77.64 m; −4.8 → −1.2 m), 2005/06 (77.70 m; −5.1 → −1.7 m), 1974/75 (79.08 m; +5.6 → +2.7 m) and "
    "2024/25 (79.04 m; +6.2 → +3.6 m) — the very low and very high starts.",
    "<b>Makes it worse:</b> 1989/90 and 2019/20 (low starts, but a very wet February drove a high peak), and 2023/24 "
    "and 2007/08 (high starts that peaked lower than the model expects).",
    "<b>Still unexplained:</b> 1965/66 (+8.7 m), 1981/82 (+5.8 m), 2018/19 (−5.2 m), 1968/69 (+4.7 m) and "
    "1999/2000 (+4.3 m) — pointing to rainfall timing within the winter as the next missing factor.",
    "<b>Flood-threshold calls:</b> both models flag four of the six flood winters with rainfall data and give no false "
    "alarms. Rain alone misses 1994/95 and 2002/03; with the start level it catches 1994/95 but misses 2019/20 "
    "(low start, intense February rain). 2002/03 is missed by both."])

s.append(P("5. Caveats and next steps", H2))
s += bullets([
    "Before 1999 the start level and peak come from roughly weekly manual dips, so both can be slightly smoothed.",
    "Winter 2025/26 (peak 99.02 m) is not included because HadUK-Grid rainfall currently ends in December 2025.",
    "Three winters have no reading close enough to 1 October (1973/74, 1986/87, 1995/96) and are left out.",
    "Next: add a rainfall-timing term (for example February rain or the wettest 30 days) using the monthly HadUK-Grid "
    "data, and use the start level in the month-by-month flood-probability model."])
s.append(P("Reproduce: <font face='Courier'>python scripts/winter_summary.py</font>, then "
           "<font face='Courier'>python scripts/start_level_analysis.py</font> (all winters) and "
           "<font face='Courier'>--first-winter 2000 --tag _logger</font> (logger era). Outputs in output/haduk/.", SMALL))

s.append(P("Appendix — winter by winter (all winters)", H2))
rows = [["Winter", "Oct–Mar mm", "Start m", "Peak m", "Pred: rain", "Pred: + start", "Resid: rain", "Resid: + start"]]
bold = []
for i, r in D.iterrows():
    y = int(r.winter_end_year)
    rows.append([lab(y), f"{r.oct_mar_mm:.0f}", f"{r.start_level_mAOD:.2f}", f"{r.peak_level_mAOD:.2f}",
                 f"{r.pred_rain_only:.1f}", f"{r.pred_rain_start:.1f}", f"{r.resid_rain_only:+.1f}",
                 f"{r.resid_rain_start:+.1f}"])
    if r.peak_level_mAOD >= 97:
        bold.append(i + 1)
s.append(table(rows, [20 * mm, 20 * mm, 18 * mm, 18 * mm, 22 * mm, 24 * mm, 24 * mm, 26 * mm], font=7.2, bold_rows=bold))
s.append(P("Bold rows reached 97 m. Residual = actual peak minus predicted.", SMALL))

s.append(PageBreak())
from PIL import Image as PILImage
pw, ph = PILImage.open(PNG).size
iw = 172 * mm
ih = min(iw * ph / pw, 255 * mm)
s.append(Image(PNG, width=ih * pw / ph, height=ih))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=14 * mm,
                        bottomMargin=17 * mm, title="Lopcombe Corner — start-of-winter level analysis",
                        author="Keith Sloan / Claude")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print(OUT)
