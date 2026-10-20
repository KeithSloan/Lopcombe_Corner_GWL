"""Build Lopcombe_Flood_Probability.pdf from the analysis outputs."""
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph as _P, Spacer, Table, TableStyle, Image, PageBreak

BASE = "."
RES = json.load(open(f"{BASE}/output/flood/flood_prob_results.json"))
PNG = f"{BASE}/output/flood/Lopcombe_flood_probability.png"
OUT = f"{BASE}/docs/reports/Lopcombe_Flood_Probability.pdf"
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
    canvas.drawString(18 * mm, 10 * mm, "Lopcombe Corner borehole (EA E14150) · Flood probability by month-end level · 20 Oct 2026")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


import pandas as pd
T = pd.read_csv(f"{BASE}/output/flood/flood_prob_table.csv")
W = pd.read_csv(f"{BASE}/output/flood/flood_prob_winters.csv")
MS = ["Oct", "Nov", "Dec", "Jan", "Feb"]
Mo = RES["months"]
lt = RES["latest"]
pct = lambda v: f"{v * 100:.0f}%"


def lvl(v, hi=97.0):
    return "—" if v != v or v >= hi else f"{v:.1f} m"


s = [P("Lopcombe Corner — Chance of Reaching the 97 m Flood Threshold", H1),
     P("Probability that the borehole level is at or above 97 mAOD (the Pitton groundwater-flood threshold) at some time "
       f"later in the winter, given the level at the end of each month from October to February · EA E14150, {RES['n_winters']} winters 1963/64–2025/26 · "
       "levels from the full EA record (manual dips and daily logger) · rainfall HadUK-Grid 1 km · 20 Oct 2026", SUB),
     P(f"<b>In short.</b> {RES['n_flood']} of {RES['n_winters']} winters reached 97 m (about 1 in 9): "
       f"{', '.join(RES['flood_winters'])}. The October level tells you little — the well starts nearly every winter "
       "at about 78–79 m — so at the end of October the chance is roughly the long-run 1 in 10. From the end of November "
       "the level becomes a strong guide: a 50:50 chance corresponds to about <b>88–89 m at the end of November</b>, "
       "<b>92–93 m at the end of December</b>, <b>93–95.5 m at the end of January</b> and <b>about 96 m at the end of "
       "February</b>. Every flood winter was at least 89.6 m by the end of January, and no winter has first reached "
       f"97 m after the end of February. On {lt['date']} the level was {lt['level']:.2f} m, an ordinary autumn level.", NOTE),
     P("1. Probability table", H2),
     P("Chance (%) that the level is at or above 97 m at some time after that month end (up to 31 May), by the level "
       "at the month end. Each cell gives the "
       "rainfall-scenario estimate, then the history estimate in brackets. A dash means that level has never been seen "
       "at that time of year, so no estimate is given.", BODY)]
levels = [79, 80, 82, 84, 86, 88, 90, 92, 93, 94, 95, 96]
rows = [["Level at month end"] + [f"End {m}" for m in MS]]
for v in levels:
    r = [f"{v:g} m"]
    for m in MS:
        x = T[(T.month_end == m) & (T.level_mAOD == v)].iloc[0]
        r.append(f"{x.p_scenario * 100:.0f}  ({x.p_history * 100:.0f})" if x.within_observed_range else "—")
    rows.append(r)
s.append(table(rows, [34 * mm, 28 * mm, 28 * mm, 28 * mm, 28 * mm, 28 * mm], font=8.5))
s.append(Spacer(1, 4))
rows = [["", *[f"End {m}" for m in MS]],
        ["50:50 level (scenario)", *[lvl(Mo[m]["p50_scenario"], Mo[m]["plot_range"][1]) for m in MS]],
        ["50:50 level (history)", *[lvl(Mo[m]["p50_history"], Mo[m]["plot_range"][1]) for m in MS]],
        ["Highest level, no flood", *[f"{Mo[m]['max_level_no_flood']:.1f} m" for m in MS]],
        ["Lowest level, then flooded", *[f"{Mo[m]['min_level_flood']:.1f} m" for m in MS]]]
s.append(table(rows, [44 * mm, 26 * mm, 26 * mm, 26 * mm, 26 * mm, 26 * mm], font=8.5))
s.append(P("“Lowest level, then flooded”: the lowest month-end level from which the level later reached 97 m. "
           "2013/14 was only 80.3 m at the end of December and peaked at 102.0 m in February; 2025/26 was 89.6 m at the "
           "end of January and reached 99.0 m; 2023/24 had fallen back to 93.7 m by the end of February and rose again "
           "to 99.1 m in April.", SMALL))

s.append(P("2. How to read it", H2))
s += bullets([
    "<b>End of October:</b> the level barely varies between winters (77.6–82.9 m), so it says little. Both methods put the "
    "chance near the long-run 1 in 10 at ordinary levels. Above about 80 m the two methods disagree sharply (see §4), so "
    "treat October estimates above 80 m as very uncertain.",
    "<b>End of November and December:</b> the most useful early warning. A rise to the high 80s by late November "
    "(as in 2000/01, 2002/03 and 2023/24) roughly halves the odds against a flood; but a low December level does not rule "
    "one out if January and February are very wet (2013/14).",
    "<b>End of January and February:</b> the curves steepen — the outcome depends on whether the level is already within "
    "a few metres of 97 m. Only three winters first crossed 97 m after the end of January (1994/95, 2019/20, 2025/26), "
    "none after the end of February. Late-season exceedances came from winters already near or above 97 m, such as "
    "2023/24's return to 99.1 m in April 2024.",
    "Probabilities above the 97 m line are 100% by definition: the threshold has already been reached."])

s.append(PageBreak())
s.append(P("3. Methods", H2))
s += bullets([
    "<b>Data.</b> All manual dips (1963 onwards) and the daily 09:00 logger reading (1999 onwards) from the EA Hydrology "
    "API, downloaded 20 Oct 2026 (scripts/export_levels.py). One spurious dip (105.08 m, 15 May 2025) was removed. The "
    "month-end level is interpolated between the readings either side, which must be within 21 days. The outcome for "
    "each month is whether any reading after that month end, up to 31 May, is at or above 97 m.",
    "<b>History method.</b> For each month, a logistic regression of “reached 97 m later” on the month-end level, using "
    "Firth's penalised estimator because there are only seven flood winters. It answers: among past winters at this level "
    "on this date, how often did a flood follow?",
    "<b>Rainfall-scenario method.</b> For each month, a regression of the highest level after the month end on the "
    "month-end level and the "
    "HadUK-Grid rainfall still to come (from the next month to April). For a given level, the peak is then predicted "
    "under each of the 62 historical rainfall sequences, with the model's residual scatter, and the chances averaged. It "
    "answers: starting from this level, what fraction of plausible rest-of-winter weather leads to 97 m?",
    "Curves are drawn only across the range of levels seen at that time of year (plus a small margin)."])
rows = [["Month end", "Winters", "Level coef (m per m)", "Rain coef (m per 100 mm)", "Fit R²", "Scatter (m)"]]
for m in MS:
    d = Mo[m]
    rows.append([m, str(d["n_scenario"]), f"{d['scen_level_coef']:.2f} ± {d['scen_level_se']:.2f}",
                 f"{d['scen_rain_coef'] * 100:.1f} ± {d['scen_rain_se'] * 100:.1f}", f"{d['scen_r2']:.2f}",
                 f"{d['scen_sigma']:.1f}"])
rows = [[_P(c.replace("²", "<super>2</super>"), ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=8, leading=10))
         if i == 0 and "²" in c else c for c in r] for i, r in enumerate(rows)]
s.append(table(rows, [22 * mm, 18 * mm, 36 * mm, 40 * mm, 18 * mm, 22 * mm], font=8))
s.append(P("Scenario-model regression for each month end. The scenario fit excludes 2025/26, because HadUK-Grid rainfall "
           "currently ends in December 2025.", SMALL))

s.append(P("4. Checks and caveats", H2))
cal = RES["calibration"]
s += bullets([
    f"<b>Calibration.</b> Added over all winters, the history method expects {cal['Dec']['expected_history']:.1f} "
    f"flood winters against {cal['Dec']['observed']} observed (end-December case). The rainfall-scenario method expects "
    f"{cal['Dec']['expected_scenario']:.1f} against {cal['Dec']['observed_scenario_set']} in the winters it covers, so it "
    "runs about 20% low — read it as the lower and the history method as the upper estimate.",
    "<b>The two methods agree well from November to February</b> (50:50 levels within about 2 m). In October they diverge "
    "above 80 m: the scenario model extrapolates a steep level effect, while history has only three winters above 81 m "
    "at the end of October (1966/67, 1993/94, 2024/25) — all peaked at 94–95 m but none reached 97 m.",
    "<b>Only seven flood winters.</b> Individual percentages carry wide uncertainty — think of them as ±10–20 points.",
    "<b>Rainfall scenarios</b> treat the rest of the winter's rain as unrelated to what has fallen so far, and give "
    "every historical winter equal weight; any shift toward wetter winters (the Oct–Mar trend is +1.4 mm/yr, not "
    "significant) is not included.",
    "<b>Before 1999</b> the record is manual dips (roughly weekly), so early peaks and month-end levels can be slightly "
    "low or smoothed."])
s.append(P("5. Data note — earlier winter peaks", H2))
s.append(P("The full daily logger record shows that several winter peaks used in the earlier HadUK-Grid, start-of-winter "
           "and Oct–Mar reports were too low, because the earlier extraction still missed later peaks. Notable "
           "differences: 2023/24 99.11 m (12 Apr 2024, not 97.54 m); 2024/25 95.04 m (not 90.31 m); 2014/15 87.78 m "
           "(not 83.13 m); 2021/22 82.68 m (not 79.61 m); 2012/13 95.73 m (not 94.42 m). Winter 2025/26 (99.02 m, "
           "27 Feb 2026) is new. This report uses the full record, and the HadUK-Grid, start-of-winter, annual-maximum and Oct–Mar reports have since been re-run with it.", BODY))
s.append(P("Reproduce: <font face='Courier'>python scripts/export_levels.py</font> then "
           "<font face='Courier'>python scripts/flood_probability.py</font> (outputs in output/flood/).", SMALL))

s.append(PageBreak())
from PIL import Image as PILImage
pw, ph = PILImage.open(PNG).size
iw = 172 * mm
ih = min(iw * ph / pw, 250 * mm)
s.append(Image(PNG, width=ih * pw / ph, height=ih))

s.append(PageBreak())
s.append(P("Appendix — month-end levels and winter peaks (mAOD)", H2))
rows = [["Winter", "End Oct", "End Nov", "End Dec", "End Jan", "End Feb", "Peak", "Peak date"]]
bold = []
f = lambda v: "—" if v != v else f"{v:.2f}"
for i, r in W.iterrows():
    rows.append([r.winter, f(r.L_Oct), f(r.L_Nov), f(r.L_Dec), f(r.L_Jan), f(r.L_Feb), f"{r.peak:.2f}", r.peak_date])
    if r.flood:
        bold.append(i + 1)
s.append(table(rows, [20 * mm, 20 * mm, 20 * mm, 20 * mm, 20 * mm, 20 * mm, 20 * mm, 26 * mm], font=7.2, bold_rows=bold))
s.append(P("Bold: reached 97 m. “—”: no readings within 21 days of that month end.", SMALL))

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=14 * mm,
                        bottomMargin=17 * mm, title="Lopcombe Corner — flood probability by month-end level",
                        author="Keith Sloan / Claude")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print(OUT)
