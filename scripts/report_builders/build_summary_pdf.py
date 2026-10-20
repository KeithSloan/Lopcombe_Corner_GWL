"""Build Lopcombe_Summary.pdf from the analysis outputs."""
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph as _P, Spacer, Table, TableStyle, Image, PageBreak

BASE = "."
RES = json.load(open(f"{BASE}/output/flood/flood_prob_results.json"))
PNG = f"{BASE}/output/levels/Lopcombe_winter_peaks.png"
OUT = f"{BASE}/docs/reports/Lopcombe_Summary.pdf"
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
    canvas.drawString(18 * mm, 10 * mm, "Lopcombe Corner borehole (EA E14150) · Summary of findings · 20 Oct 2026")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


import pandas as pd
H = json.load(open(f"{BASE}/output/haduk/haduk_results.json"))
SL = json.load(open(f"{BASE}/output/haduk/start_level_results.json"))
WS = pd.read_csv(f"{BASE}/output/levels/winter_summary.csv")
H1.fontSize, H1.leading = 15, 18
H2.fontSize, H2.leading, H2.spaceBefore, H2.spaceAfter = 10.5, 13, 5, 2
BODY.fontSize, BODY.leading, BODY.spaceAfter = 8.6, 11, 2
BUL.fontSize, BUL.leading, BUL.spaceAfter = 8.6, 11, 1.5
NOTE.fontSize, NOTE.leading = 8.8, 11.5
rl, m1, m2 = H["rain_level"], SL["models"]["octmar"], SL["models"]["octmar_start"]
fm = RES["months"]
lt = RES["latest"]
s = [P("Lopcombe Corner Borehole — Summary of Findings", H1),
     P("EA station E14150 (Chalk, near Winterslow) · levels: full EA record 1963–2026 (manual dips and daily logger) · "
       "rainfall: Met Office HadUK-Grid 1 km for the borehole's cell · 20 Oct 2026", SUB),
     P(f"<b>Record:</b> 102.01 mAOD on 13 Feb 2014. <b>Floods:</b> {RES['n_flood']} of {RES['n_winters']} winters reached "
       f"the 97 m Pitton groundwater-flood threshold — {', '.join(RES['flood_winters'])} — five of them since 2000 and "
       f"four since 2013. <b>Now:</b> {lt['level']:.2f} m on {lt['date']}, a normal autumn level (the well drains back "
       f"to about {SL['start_level_mean']:.1f} ± {SL['start_level_sd']:.1f} m every autumn).", NOTE)]
pw, ph = 3070, 920
from PIL import Image as PILImage
pw, ph = PILImage.open(PNG).size
iw = 174 * mm
s.append(Image(PNG, width=iw, height=iw * ph / pw))
s.append(P("What drives the winter peak", H2))
s += bullets([
    f"<b>Winter rainfall, mainly.</b> October–March rainfall explains most of the peak (r = {rl['all_r']:.2f} over "
    f"{rl['all_n']} winters): about <b>+{rl['fit'][0] * 100:.1f} m of peak per extra 100 mm</b>. Every flood winter with "
    "rainfall data had at least about 670 mm October–March; of the seven winters above that, six flooded (not 2022/23).",
    f"<b>The starting level matters too.</b> Adding the 1 October level lifts the share explained from {m1['r2']:.2f} to "
    f"{m2['r2']:.2f}: each extra metre at the start adds about <b>{m2['coef'][2]:.1f} m</b> to the peak (p &lt; 0.001). "
    "A high autumn start is worth roughly 50 mm of extra winter rain.",
    "<b>Timing within the winter</b> explains much of what is left — intense February rain (2019/20, 1989/90) or an "
    "early-January spike followed by a dry spell (2022/23)."])
s.append(P("Cycles and trends", H2))
s += bullets([
    f"<b>No regular cycle.</b> Neither rainfall nor peak level shows a significant periodicity (strongest periods "
    f"{H['rain']['ls_peaks'][0][0]} and {H['level']['ls_peaks'][0][0]} years, p ≈ 0.4–0.5); wet winters come in short, "
    "irregular clusters.",
    f"<b>Winter rainfall has crept up</b> by about {H['rain']['sen_slope_per_yr']:.1f} mm a year since 1963 "
    f"(≈ +87 mm), but this just misses statistical significance (p = {H['rain']['mk_p']:.2f}). Winter peak levels show no "
    f"trend (p = {H['level']['mk_p']:.2f}), even though floods have clustered since 2000."])
s.append(P("Early warning: chance of reaching 97 m later in the winter", H2))
rows = [["Level at end of …", "Oct", "Nov", "Dec", "Jan", "Feb"],
        ["50:50 chance at about", "not useful", "88–89 m", "92–93 m", "93–95.5 m", "~96 m"],
        ["Lowest level that still went on to flood", *[f"{fm[m]['min_level_flood']:.1f} m" for m in
                                                       ("Oct", "Nov", "Dec", "Jan", "Feb")]]]
s.append(table(rows, [58 * mm, 23 * mm, 23 * mm, 23 * mm, 24 * mm, 23 * mm], font=8.2))
s += bullets([
    "At the end of October the chance is about the long-run 1 in 10 whatever the level. From November the level is a "
    "strong guide. Every flood winter was at least 89.6 m by the end of January, and none first reached 97 m after the "
    "end of February. Percentages carry about ±10–20 points of uncertainty (only seven flood winters)."])
s.append(P("Data notes", H2))
s.append(P("HadUK-Grid rainfall is an estimate interpolated from surrounding gauges, not a reading at the borehole; it "
           "agrees closely with Broughton (E13580) and has no gaps. On 20 Oct 2026 the full EA level record showed that "
           "several logger-era winter peaks used earlier had been read too low (e.g. 2023/24 is 99.11 m, not 97.54 m); "
           "all current reports use the corrected record. Details, methods and scripts: docs/reports and docs/notes in "
           "the Lopcombe_Corner_GWL repository.", BODY))
doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=12 * mm,
                        bottomMargin=15 * mm, title="Lopcombe Corner — summary of findings",
                        author="Keith Sloan / Claude")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print(OUT)
