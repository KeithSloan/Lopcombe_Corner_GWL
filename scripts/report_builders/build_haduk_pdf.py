"""Build Lopcombe_HadUK_Rainfall_Cyclicity.pdf from the analysis outputs."""
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph as _P, Spacer, Table, TableStyle, Image, PageBreak

BASE = "."
RES = json.load(open(f"{BASE}/output/haduk/haduk_results.json"))
PNG = f"{BASE}/output/haduk/Lopcombe_HadUK_rainfall_cyclicity.png"
OUT = f"{BASE}/docs/reports/Lopcombe_HadUK_Rainfall_Cyclicity.pdf"
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
    return [_P(t, BUL, bulletText="•") for t in items]


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
    canvas.drawString(18 * mm, 10 * mm, "Lopcombe Corner borehole (EA E14150) · HadUK-Grid rainfall analysis · 20 Oct 2026")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


rl = RES["rain_level"]
import pandas as _pd
_ws = _pd.read_csv(f"{BASE}/output/levels/winter_summary.csv")
PK = dict(zip(_ws.winter_end_year, _ws.peak_mAOD))
w = lambda y: f"{y - 1}/{str(y)[2:]}"
s = [P("Lopcombe Corner — HadUK-Grid Rainfall: Validation, Cycles and Trend", H1),
     P("Rainfall: Met Office HadUK-Grid v1.3.2.ceda (release v20260512), 1 km monthly, 1963–2025, cell centred "
       "E 425500 / N 135500 containing borehole E14150 (E 425007 / N 135427) · Levels: winter peaks (highest level "
       "October–May) from the full EA record — manual dips to 1998/99, daily logger from 1999/2000 · updated 20 Oct 2026", SUB),
     P("<b>Bottom line.</b> Over 62 winters there is <b>no regular cycle</b> in rainfall or water levels. Oct–Mar "
       f"rainfall explains winter peaks well (r = {rl['all_r']:.2f} over {rl['all_n']} winters), every winter that "
       "reached the 97 m Pitton flood threshold had at least about 670 mm of Oct–Mar rain, and winter rainfall has "
       "risen by about 1.4 mm a year — a trend that falls just short of statistical significance. "
       "<i>Updated 20 Oct 2026: winter peaks now come from the full daily EA record, which corrected several "
       "logger-era peaks that had been read too low; the conclusions are unchanged.</i>", NOTE),
     P("1. Rainfall source and validation", H2)]
s += bullets([
    "The single 1 km cell matches the mean of its 3×3 neighbourhood to within 1.25 mm a month, so the exact cell choice "
    "does not matter. Mean annual rainfall at the cell is 844 mm (range 548–1155 mm).",
    "Against the Broughton gauge (E13580, about 10 km away): Oct–Dec totals agree with r = 0.96 and within 2% overall.",
    "Against Tim Vaughan's Broughton Oct–Jan figures, HadUK-Grid is within −1% to +8% (table below), so the borehole "
    "cell is slightly wetter than Broughton.",
    "The earlier API-summed Broughton Oct–Jan totals were flawed — in 2001, 2006, 2022 and 2024 they were smaller than "
    "the Oct–Dec totals, which is impossible. HadUK-Grid replaces them."])
s.append(table([["Winter", "Tim (Broughton) Oct–Jan mm", "HadUK-Grid Oct–Jan mm", "Difference"],
                ["2000/01", "534", "578", "+8%"], ["2002/03", "557", "603", "+8%"],
                ["2013/14", "605", "634", "+5%"], ["2019/20", "484", "496", "+2%"],
                ["2023/24", "509", "505", "−1%"]], [28 * mm, 50 * mm, 46 * mm, 26 * mm]))

s.append(P("2. Rainfall vs winter peak level", H2))
k, b = rl["fit"]
s += bullets([
    f"Oct–Mar rainfall vs winter peak: <b>r = {rl['all_r']:.2f}</b> over {rl['all_n']} winters; manual-dip era "
    f"1963/64–1998/99 r = {rl['dip_r']:.2f}; logger era 1999/2000–2024/25 <b>r = {rl['log_r']:.2f}</b> "
    "(slightly better than 0.86 using Broughton).",
    f"Fit: peak ≈ {k:.3f} × rain + {b:.1f}, i.e. about +{k * 100:.1f} m of peak per +100 mm of Oct–Mar rain.",
    "The dip-era correlation is lower partly because sparse manual dips can miss the true peak."])
rows = [["Winter", "Oct–Mar rain (mm)", "Peak (mAOD)", "Reached 97 m?"]]
lst = sorted([(y, r, p, "Yes") for y, r, p in rl["breach"]] +
             [(y, round(r), PK[y], "No") for y, r in rl["wet_no_breach"]], key=lambda z: -z[1])
for y, r, p, yes in lst:
    rows.append([w(y), str(r), f"{p:.2f}", yes])
s.append(P("<b>97 m Pitton threshold.</b> Six of these winters reached it, all with Oct–Mar ≥ about 670 mm. Of the seven winters "
           "above that amount, six breached; the exception was 2022/23. Five of the six breaches have come since 2000. "
           "1976/77 (669 mm, 89.1 m) just missed the band, after the 1976 drought left the aquifer very low. A seventh "
           "winter, 2025/26, reached 99.02 m; its rainfall is not yet in HadUK-Grid.", BODY))
s.append(table(rows, [28 * mm, 40 * mm, 32 * mm, 32 * mm], bold_rows=[i + 1 for i, z in enumerate(lst) if z[3] == "No"]))

s.append(PageBreak())
s.append(P("3. Cyclicity", H2))
s.append(P("Same tests as the September cyclicity check: Lomb–Scargle periodogram over 2–30 years, significance from "
           "5,000 Monte Carlo runs against white noise (shuffled data) and red noise (fitted AR(1)), autocorrelation to "
           "lag 15, a split-half stability check and a runs test about the median.", BODY))
rows = [["Series", "n", "Strongest period", "p (white)", "p (red)", "Halves", "Runs (obs/exp)"]]
for key in ("rain", "annual", "level"):
    d = RES[key]
    rows.append([d["name"], str(d["n"]), f"{d['ls_peaks'][0][0]} yr", f"{d['p_white']:.2f}", f"{d['p_red']:.2f}",
                 f"{d['half1'][2]} / {d['half2'][2]} yr", f"{d['runs']} / {d['runs_expected']:.0f}"])
s.append(table(rows, [40 * mm, 10 * mm, 28 * mm, 18 * mm, 16 * mm, 28 * mm, 26 * mm], font=8))
s.append(Spacer(1, 6))
s += bullets([
    "<b>No significant cycle.</b> No periodogram peak comes close to the 95% noise threshold (p ≈ 0.4–0.75).",
    "The water level's ~6–7 year tendency has no counterpart in Oct–Mar rainfall, whose strongest period is 3.3 years, "
    "and neither series keeps the same dominant period in its first and second halves.",
    "Autocorrelation of both rainfall and peak level stays inside the ±0.25 noise band at every lag up to 15 years. "
    "Runs tests show wet and dry winters alternating at random.",
    "High-rainfall winters (top 20%): " + ", ".join(w(y) for y in RES["rain"]["high_years"]) + "."])

s.append(P("4. Trend", H2))
d = RES["rain"]
s += bullets([
    f"Oct–Mar rainfall: Sen slope <b>+{d['sen_slope_per_yr']:.1f} mm/yr</b> (about +87 mm over 62 winters, roughly 18% "
    f"of the mean), Mann–Kendall p = {d['mk_p']:.3f} — suggestive but not significant at the 5% level. Eight of the 13 "
    "wettest-quintile winters fall in 2000/01 or later.",
    f"Calendar-year rainfall: +{RES['annual']['sen_slope_per_yr']:.1f} mm/yr, p = {RES['annual']['mk_p']:.2f}.",
    f"Winter peak level: no trend (Sen {RES['level']['sen_slope_per_yr']:+.2f} m/yr, p = {RES['level']['mk_p']:.2f}). "
    "Dip-era peaks may under-read where dips were sparse, which would mute any level trend."])

s.append(P("5. Files and how to reproduce", H2))
s.append(table([["File (repo-relative)", "What it is"],
                ["scripts/get_haduk_1km.sh", "Downloads the 63 NetCDF files from CEDA (needs a free CEDA account)"],
                ["scripts/haduk_extract_cell.py", "Extracts the borehole cell from the NetCDF files to CSV"],
                ["scripts/haduk_rainfall_analysis.py", "Rainfall vs peak, cycles, trend and chart"],
                ["data/haduk/lopcombe_haduk1km_monthly_rainfall.csv", "Monthly rainfall, cell and 3×3 mean, 1963–2025"],
                ["output/haduk/lopcombe_winter_rain_vs_peak.csv", "Winter totals and peak level per winter"],
                ["output/haduk/haduk_results.json", "All statistics"],
                ["output/levels/winter_summary.csv", "Winter peaks from the full EA record (scripts/winter_summary.py)"],
                ["output/haduk/Lopcombe_HadUK_rainfall_cyclicity.png", "The chart on the next page"]],
               [80 * mm, 94 * mm], font=8, left=True))
s.append(Spacer(1, 4))
s.append(P("The 2.6 GB of NetCDF files are kept on the external SSD (/Volumes/Crucial X9 Pro for Mac/HadUK-Grid), "
           "not in the repo. The start-of-winter level is analysed in Lopcombe_Start_of_Winter_Level.pdf; it "
           "explains part of why wet winters such as 2022/23 stayed below the threshold.", SMALL))

s.append(PageBreak())
iw = 172 * mm
from PIL import Image as PILImage
pw, ph = PILImage.open(PNG).size
ih = min(iw * ph / pw, 255 * mm)
s.append(Image(PNG, width=ih * pw / ph, height=ih))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=14 * mm,
                        bottomMargin=17 * mm, title="Lopcombe Corner — HadUK-Grid rainfall analysis",
                        author="Keith Sloan / Claude")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print(OUT)
