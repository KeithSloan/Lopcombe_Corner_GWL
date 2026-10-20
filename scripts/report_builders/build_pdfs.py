"""Recreate the three Lopcombe Corner PDF reports from the project docs.

Data are transcribed from the claude.ai project docs (lopcombe-annual-max.md,
lopcombe-instrumented-annual-max.md, lopcombe-highest-levels.md,
lopcombe-rainfall-correlation-v2-octdec.md, lopcombe-rainfall-correlation-v3-octmar.md,
lopcombe-correction-truncation.md) and the HadUK-Grid winter table of 2026-10-20.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether)

OUT = "docs/reports"
os.makedirs(OUT, exist_ok=True)
HADUK_CSV = "./output/haduk/lopcombe_winter_rain_vs_peak.csv"

BLUE, ORANGE, INK, INK2, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False})

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=17, leading=21, spaceAfter=4, alignment=0)
SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontSize=9, textColor=colors.HexColor(INK2), spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12, leading=15, spaceBefore=10, spaceAfter=4)
BODY = ParagraphStyle("BODY", parent=ss["Normal"], fontSize=9.5, leading=13, spaceAfter=4)
BUL = ParagraphStyle("BUL", parent=BODY, leftIndent=12, bulletIndent=2)
NOTE = ParagraphStyle("NOTE", parent=BODY, backColor=colors.HexColor("#fdf1e8"),
                      borderColor=colors.HexColor(ORANGE), borderWidth=0.8, borderPadding=6,
                      spaceBefore=6, spaceAfter=10)
SMALL = ParagraphStyle("SMALL", parent=BODY, fontSize=8, leading=10, textColor=colors.HexColor(INK2))


_P = Paragraph
def Paragraph(text, style, **kw):
    return _P(text.replace("²", "<super>2</super>"), style, **kw)


def bullets(items):
    return [Paragraph(t, BUL, bulletText="•") for t in items]


def _cell(v, bold, font):
    if isinstance(v, str) and "²" in v:
        st = ParagraphStyle("c", fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=font, leading=font + 2,
                            alignment=2 if v[:1].isdigit() or v[:1] in "rR" else 0)
        return Paragraph(v.replace("²", "<super>2</super>"), st)
    return v


def table(rows, widths, header_rows=1, font=8.5, bold_rows=()):
    rows = [[_cell(v, i < header_rows or i in bold_rows, font) for v in row] for i, row in enumerate(rows)]
    t = Table(rows, colWidths=widths, repeatRows=header_rows)
    st = [("FONT", (0, 0), (-1, -1), "Helvetica", font),
          ("FONT", (0, 0), (-1, header_rows - 1), "Helvetica-Bold", font),
          ("LINEBELOW", (0, header_rows - 1), (-1, header_rows - 1), 0.8, colors.HexColor(INK2)),
          ("ROWBACKGROUNDS", (0, header_rows), (-1, -1), [colors.white, colors.HexColor("#f4f4f1")]),
          ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
          ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    for r in bold_rows:
        st.append(("FONT", (0, r), (-1, r), "Helvetica-Bold", font))
    t.setStyle(TableStyle(st))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor(INK2))
    canvas.drawString(18 * mm, 10 * mm, "Lopcombe Corner borehole (EA E14150) · recreated 20 Oct 2026; peaks from full EA record")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build(name, story, title):
    path = os.path.join(OUT, name)
    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=16 * mm, bottomMargin=18 * mm, title=title,
                            author="Keith Sloan / Claude")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return path


def img(fig, name, width_mm=174):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=200, bbox_inches="tight")
    plt.close(fig)
    w, h = fig.get_size_inches()
    return Image(p, width=width_mm * mm, height=width_mm * mm * h / w)


# ===================================================================== data
DIP = {1963: (84.19, "30 May"), 1964: (84.76, "1 Jan"), 1965: (80.18, "30 Apr"), 1966: (93.73, "5 Mar"),
       1967: (94.44, "26 Mar"), 1968: (87.78, "8 Feb"), 1969: (92.38, "5 Feb"), 1970: (87.01, "2 Apr"),
       1971: (89.48, "19 Feb"), 1972: (92.30, "26 Mar"), 1973: (81.97, "12 Feb"), 1974: (90.85, "5 Mar"),
       1975: (95.12, "12 Feb"), 1976: (79.12, "24 Dec"), 1977: (89.05, "12 Mar"), 1978: (89.37, "19 Mar"),
       1979: (90.22, "23 Apr"), 1980: (89.69, "16 Apr"), 1981: (87.71, "23 Apr"), 1982: (92.84, "31 Mar"),
       1983: (89.07, "29 Jan"), 1984: (83.85, "9 Mar"), 1985: (86.84, "26 Feb"), 1986: (87.11, "19 Feb"),
       1987: (89.41, "27 Apr"), 1988: (87.92, "4 Mar"), 1989: (82.78, "30 Apr"), 1990: (93.30, "28 Feb"),
       1991: (80.06, "30 Apr"), 1992: (79.24, "22 May"), 1993: (87.02, "12 Feb"), 1994: (94.20, "28 Jan"),
       1995: (98.26, "23 Feb"), 1996: (84.75, "19 Mar"), 1997: (79.84, "2 Apr"), 1998: (84.38, "5 Feb"),
       1999: (92.59, "3 Feb"), 2000: (101.17, "21 Dec"), 2001: (98.38, "21 Feb"), 2002: (94.64, "9 Dec"),
       2003: (100.07, "5 Jan"), 2004: (82.42, "16 Mar"), 2005: (80.20, "21 Feb"), 2006: (79.30, "8 May"),
       2007: (90.53, "22 Mar"), 2008: (85.62, "4 Feb"), 2009: (92.60, "26 Feb"), 2010: (88.06, "24 Mar"),
       2011: (81.04, "21 Mar"), 2012: (80.45, "14 Aug"), 2013: (94.39, "11 Jan"), 2014: (94.90, "2 Apr"),
       2015: (78.69, "3 Nov"), 2016: (88.14, "11 Mar"), 2017: (78.59, "14 Jul"), 2018: (89.58, "18 Apr"),
       2019: (80.71, "15 Mar"), 2020: (92.04, "6 Feb"), 2021: (None, "no dip"), 2022: (78.62, "30 Nov"),
       2023: (87.67, "9 May"), 2024: (92.29, "7 Feb"), 2025: (80.39, "9 Jun")}

# Winter peaks from the full EA record (output/levels/winter_summary.csv), winter ending in year Y
_WS = pd.read_csv("./output/levels/winter_summary.csv")
CORR = {int(r.winter_end_year): (float(r.peak_mAOD), pd.Timestamp(r.peak_date).strftime("%-d %b %Y"))
        for r in _WS.itertuples() if r.winter_end_year >= 2000}
_OLD_CORR = {2001: (101.39, ""), 2002: (85.33, ""), 2003: (100.79, ""), 2004: (82.72, ""), 2005: (80.05, ""),
        2006: (79.33, ""), 2007: (90.76, ""), 2008: (85.76, ""), 2009: (92.62, ""), 2010: (88.15, ""),
        2011: (81.05, ""), 2012: (78.4, "approx."), 2013: (94.42, ""), 2014: (102.01, "13 Feb 2014"),
        2015: (83.13, ""), 2016: (88.15, ""), 2017: (78.86, ""), 2018: (89.54, ""), 2019: (80.66, ""),
        2020: (97.25, "24 Feb 2020"), 2021: (91.72, "13 Feb 2021"), 2022: (79.61, ""),
        2023: (92.62, "21 Jan 2023"), 2024: (97.54, "12 Jan 2024"), 2025: (90.31, "9 Dec 2024")}
# Logger annual maxima as first extracted (some truncated) - kept for the dip-vs-logger comparison
LOG_ORIG = {2000: 101.39, 2001: 98.46, 2002: 94.90, 2003: 100.79, 2004: 82.48, 2005: 80.05, 2006: 79.33,
            2007: 90.76, 2008: 85.76, 2009: 92.62, 2010: 88.15, 2011: 81.05, 2012: 80.48, 2013: 94.35,
            2014: 101.89, 2015: 83.00, 2016: 88.15, 2017: 78.88, 2018: 89.98, 2019: 80.66, 2020: 92.81,
            2021: 87.24, 2022: 79.96, 2023: 91.35, 2024: 92.97, 2025: 90.28}

# v2 table: winter | Oct-Dec | Oct-Jan | peak (pre-correction) | antecedent min
V2 = """2001|511|507|101.39|78.65 2002|192|245|85.05|78.55 2003|489|528|100.79|78.71 2004|284|315|82.48|78.30
2005|273|362|80.05|78.10 2006|233|217|79.33|77.70 2007|328|372|90.76|77.58 2008|175|367|85.76|78.92
2009|160|237|92.62|79.36 2010|372|396|88.15|78.17 2011|158|273|81.05|78.25 2012|184|239|77.99|77.99
2013|433|522|94.35|79.02 2014|329|539|101.89|78.58 2015|329|379|83.00|78.86 2016|198|294|88.15|78.56
2017|164|185|78.88|78.70 2018|186|243|89.98|78.47 2019|246|280|80.66|78.40 2020|355|385|92.81|77.93
2021|427|549|87.24|78.66 2022|273|252|79.96|78.67 2023|377|501|91.35|78.07 2024|443|367|92.97|78.92
2025|328|433|90.28|79.08"""
v2 = pd.DataFrame([list(map(float, r.split("|"))) for r in V2.split()],
                  columns=["winter", "octdec", "octjan", "peak", "antemin"])
v2["winter"] = v2.winter.astype(int)

hk = pd.read_csv(HADUK_CSV)

# ============================================================ PDF 1: annual maxima
def pdf1():
    s = [Paragraph("Lopcombe Corner Borehole — Highest Groundwater Levels", H1),
         Paragraph("EA station E14150 · Chalk aquifer · borehole depth 54.30 m · datum 126.61 mAOD · "
                   "records from 23 April 1963 · source: EA Hydrology API (retrieved 7 Sep 2026)", SUB),
         Paragraph("<b>Recreated and updated 20 Oct 2026.</b> This report rebuilds the September 2026 annual-maximum "
                   "PDF. Logger-era winter peaks now come from the full daily EA record (downloaded 20 Oct 2026), which "
                   "showed the earlier extractions had missed several later peaks. The all-time record is "
                   "<b>102.01 mAOD on 13 Feb 2014</b>; 2023/24 reached <b>99.11 m</b> (12 Apr 2024) and 2025/26 "
                   "<b>99.02 m</b> (27 Feb 2026).", NOTE)]

    # chart
    yrs = np.array(sorted(DIP)); dv = np.array([DIP[y][0] if DIP[y][0] else np.nan for y in yrs])
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.bar(yrs, dv - 76, bottom=76, width=0.75, color=BLUE, label="Manual dip annual maximum")
    cy = np.array(sorted(CORR)); cv = np.array([CORR[y][0] for y in cy])
    ax.plot(cy, cv, "o-", color=ORANGE, ms=4, lw=1.5, label="Logger winter peak (full daily record), winter ending in year")
    ax.axhline(97, color=INK2, ls=":", lw=1); ax.text(1963.5, 97.4, "97 m Pitton flood threshold", fontsize=7.5, color=INK2)
    ax.set_ylim(76, 104); ax.set_ylabel("mAOD"); ax.grid(axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper left", fontsize=8)
    ax.set_title("Annual maximum level, 1963–2026 (dip of 105.08 m in May 2025 excluded as erroneous)",
                 loc="left", fontsize=9.5, color=INK)
    s.append(img(fig, "fig1.png"))

    s.append(Paragraph("Highest credible levels since 1963", H2))
    rows = [["Rank", "Level (mAOD)", "Date", "Series"],
            ["1", "102.01", "13 Feb 2014", "Logger (15-min) — record"],
            ["2", "101.39", "17 Dec 2000", "Logger"],
            ["3", "101.17", "21 Dec 2000", "Dipped (same event)"],
            ["4", "100.75", "8 Jan 2003", "Logger"],
            ["5", "99.11", "12 Apr 2024", "Logger"],
            ["6", "99.02", "27 Feb 2026", "Logger"],
            ["7", "98.26", "23 Feb 1995", "Dipped"],
            ["8", "97.25", "25 Feb 2020", "Logger"]]
    s.append(table(rows, [14 * mm, 28 * mm, 30 * mm, 70 * mm], bold_rows=(1,)))
    s.append(Spacer(1, 6))
    s += bullets([
        "Seven winters have reached the 97 m Pitton flood threshold: 1994/95, 2000/01, 2002/03, 2013/14, 2019/20, "
        "2023/24 and 2025/26 — four of them since 2013.",
        "Manual dips undersample sharp peaks once dipping became sparse (from about 2013); the 2014 dip maximum was only 94.90 m.",
        "<b>Data-quality flag:</b> a dip of 105.08 mAOD on 15 May 2025 is erroneous despite a ‘Good’ flag — neighbouring dips "
        "were 84.32 m (25 Nov 2024) and 80.39 m (9 Jun 2025), and the logger read about 82.8 m at that moment. It is excluded."])

    s.append(PageBreak())
    s.append(Paragraph("Annual maxima — manual dip record (cleaned)", H2))
    yrs = sorted(DIP); half = (len(yrs) + 1) // 2
    rows = [["Year", "mAOD", "Date", "", "Year", "mAOD", "Date"]]
    for i in range(half):
        a = yrs[i]; b = yrs[i + half] if i + half < len(yrs) else None
        fa = lambda y: [str(y), f"{DIP[y][0]:.2f}" if DIP[y][0] else "—", DIP[y][1]]
        rows.append(fa(a) + [""] + (fa(b) if b else ["", "", ""]))
    s.append(table(rows, [16 * mm, 18 * mm, 20 * mm, 10 * mm, 16 * mm, 18 * mm, 20 * mm], font=8))
    s.append(Paragraph("2021 has no dip reading. 2025 shows the cleaned value (next dip after the erroneous 105.08 m).", SMALL))

    s.append(PageBreak())
    s.append(Paragraph("Logger era: dips vs 15-minute logger", H2))
    s.append(Paragraph("Dips agree with the logger to within ±0.3 m while dipping was about weekly (2000–2012). From 2013 "
                       "dips thinned to a few a year and miss the true peak. The last column is the highest daily "
                       "logger reading from October to May of the winter ending that year, from the full EA record; "
                       "the first-pass column shows the September 2026 extraction for comparison.", BODY))
    rows = [["Year / winter end", "Dip max (calendar yr)", "Logger first pass", "Winter peak (full record)", "Peak date"]]
    for y in range(2000, 2027):
        d = DIP.get(y, (None, ""))[0]
        c = CORR.get(y)
        rows.append([str(y), f"{d:.2f}" if d else "—", f"{LOG_ORIG[y]:.2f}" if y in LOG_ORIG else "—",
                     f"{c[0]:.2f}" if c else "—", c[1] if c else ""])
    s.append(table(rows, [26 * mm, 32 * mm, 30 * mm, 40 * mm, 36 * mm], font=8,
                   bold_rows=[i + 1 for i, y in enumerate(range(2000, 2027)) if CORR.get(y, (0,))[0] >= 97]))
    s.append(Paragraph("Quality flags on the logger series: 2000–03 ‘Unchecked’, 2005 ‘Suspect’, 2021 and 2023–25 "
                       "‘Edited/provisional’.", SMALL))
    return build("Lopcombe_Corner_Annual_Max_Levels.pdf", s, "Lopcombe Corner — Annual maximum levels")


# ============================================================ PDF 2: Oct-Dec + antecedent min
def pdf2():
    s = [Paragraph("Lopcombe Corner — Rainfall vs Peak Level (Oct–Dec & antecedent minimum)", H1),
         Paragraph("25 winters 2000/01–2024/25 · levels: EA logger E14150 (winter peak = max Oct–Apr) · "
                   "rainfall: Broughton E13580 daily totals summed (±few %) · analysis 7 Sep 2026", SUB),
         Paragraph("<b>Recreated 20 Oct 2026 — superseded.</b> These results used the first-pass winter peaks, three "
                   "of which were later found to be truncated (2019/20, 2020/21, 2023/24, each ~4.5 m too low), and "
                   "Broughton totals that under-read in wet winters. See the Oct–Mar report and the HadUK-Grid "
                   "analysis of 20 Oct 2026 for the current figures. The conclusion here — keep a window that "
                   "includes January or later — still holds.", NOTE),
         Paragraph("Headline", H2)]
    s += bullets([
        "<b>Oct–Dec does not beat Oct–Jan.</b> Peak vs Oct–Jan r = 0.72 (r² 0.52); vs Oct–Dec r = 0.65 (r² 0.43); both p &lt; 0.001. "
        "Most winter peaks occur Feb–Apr, so January rain genuinely feeds them. The Feb-2014 record grew from a Dec 2013 / Jan 2014 "
        "deluge, and Oct–Dec alone under-predicts it by about 13 m.",
        "<b>Antecedent recession minimum helps only slightly here.</b> Adding it to Oct–Dec lifts R² from 0.43 to 0.49 "
        "(partial r ≈ 0.32, p &gt; 0.05, n = 25). The direction supports the buffer idea — 2009 peaked at 92.6 m on only 160 mm "
        "Oct–Dec from the highest autumn start (79.4 m) — but the well recedes to a near-constant autumn baseline "
        "(78.5 ± 0.4 m), so it carries little multi-year memory."])

    s.append(Paragraph("Model comparison", H2))
    s.append(table([["Model", "r / R²", "adj R²", "Note"],
                    ["peak ~ Oct–Jan rain", "r 0.72 / 0.52", "0.50", "best single predictor"],
                    ["peak ~ Oct–Dec rain", "r 0.65 / 0.43", "0.40", "weaker"],
                    ["peak ~ Oct–Dec + antecedent min", "0.49", "0.44", "antecedent not significant"],
                    ["peak ~ Oct–Jan + antecedent min", "0.56", "0.52", "best overall"]],
                   [62 * mm, 30 * mm, 20 * mm, 50 * mm]))

    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
    for ax, col, lab in ((axs[0], "octdec", "Oct–Dec"), (axs[1], "octjan", "Oct–Jan")):
        r = np.corrcoef(v2[col], v2.peak)[0, 1]
        ax.scatter(v2[col], v2.peak, s=28, color=BLUE, edgecolor="white", lw=0.8)
        k, b = np.polyfit(v2[col], v2.peak, 1); xx = np.array([140, 570]); ax.plot(xx, k * xx + b, ls="--", color=INK2, lw=1)
        ax.axhline(97, color=INK2, ls=":", lw=1)
        ax.set_title(f"Peak vs {lab} rainfall (r = {r:.2f})", loc="left", fontsize=9.5, color=INK)
        ax.set_xlabel(f"{lab} rainfall, Broughton (mm)"); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
    axs[0].set_ylabel("Winter peak (mAOD, first pass)")
    s.append(Spacer(1, 6)); s.append(img(fig, "fig2.png"))

    s.append(Paragraph("97 m Pitton threshold", H2))
    s.append(Paragraph("Breaches in this dataset (2001, 2003, 2014) all needed a very wet winter, but the Oct–Dec total is a poor "
                       "trigger: 2014 breached on only 329 mm Oct–Dec, while 2024, 2013 and 2021 had more Oct–Dec rain "
                       "(443/433/427 mm) and did not breach. Timing within the winter and antecedent state gate the threshold, "
                       "so a single autumn rainfall total should not be used as the flood trigger.", BODY))

    s.append(PageBreak())
    s.append(Paragraph("Data (as used in September 2026)", H2))
    rows = [["Winter ending", "Oct–Dec mm", "Oct–Jan mm", "Peak mAOD", "Antecedent min mAOD"]]
    for _, r in v2.iterrows():
        rows.append([str(int(r.winter)), f"{r.octdec:.0f}", f"{r.octjan:.0f}", f"{r.peak:.2f}", f"{r.antemin:.2f}"])
    s.append(table(rows, [28 * mm, 26 * mm, 26 * mm, 26 * mm, 36 * mm], font=8))
    s.append(Paragraph("Known issues found later: in 2001, 2006, 2022 and 2024 the Oct–Jan sum is smaller than Oct–Dec, "
                       "which is impossible and shows the fetch dropped days; the 2020, 2021 and 2024 peaks are truncated "
                       "(corrected 97.25, 91.72 and 97.54 m).", SMALL))
    return build("Lopcombe_Rainfall_Correlation_OctDec_SummerMin.pdf", s, "Lopcombe Corner — Oct–Dec rainfall analysis")


# ============================================================ PDF 3: Oct-Mar
def pdf3():
    s = [Paragraph("Lopcombe Corner — Peak Level vs Winter Rainfall (Oct–Mar, corrected)", H1),
         Paragraph("25 winters 2000/01–2024/25 · September statistics: corrected peaks and Broughton rainfall re-summed by month from "
                   "Broughton E13580 and validated against Tim Vaughan's Broughton figures · analysis 7 Sep 2026", SUB),
         Paragraph("<b>Recreated and updated 20 Oct 2026.</b> Statistics in sections 1–3 are those from the September "
                   "analysis, which used Broughton rainfall and winter peaks that were later found to be too low in "
                   "several years. The chart and data table use <b>HadUK-Grid 1 km rainfall</b> and winter peaks from "
                   "the <b>full daily EA record</b>. On that basis peak vs Oct–Mar is r = 0.87 for the logger era and "
                   "r = 0.83 over 62 winters back to 1963/64.", NOTE),
         Paragraph("Headline — Oct–Mar is the right window; antecedent low matters too", H2),
         table([["Window", "r", "r²", "+ antecedent low"],
                ["Oct–Dec", "0.72", "0.52", "—"],
                ["Oct–Jan", "0.80", "0.64", "R² 0.73"],
                ["Oct–Mar", "0.86", "0.74", "R² 0.83"]], [40 * mm, 20 * mm, 20 * mm, 40 * mm], bold_rows=(3,)),
         Spacer(1, 6)]
    s += bullets([
        "Extending the window from Oct to Mar lifts r from 0.80 to 0.86: the recharge that sets the peak runs into Feb–Mar.",
        "Adding the antecedent recession low lifts Oct–Mar R² to 0.83 — about +5 m of peak per +1 m of antecedent level — "
        "so the buffer effect is a clear contributor once the rainfall window is right.",
        "Oct–Mar fit (Broughton): peak ≈ 0.047 × rain + 64.4, about +4.7 m per +100 mm.",
        "Why Oct–Jan fell short: most peaks occur Feb–Mar, fed by late-winter rain — Feb 2020 (148 mm) drove the 24 Feb 2020 "
        "peak of 97.25 m; Feb 2014 (141 mm) the 13 Feb record of 102.0 m."])

    w = hk[hk.winter_end_year >= 2001].copy()
    w["peak"] = [CORR[int(y)][0] for y in w.winter_end_year]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    br = w.peak >= 97
    ax.scatter(w.oct_mar_mm[~br], w.peak[~br], s=30, color=BLUE, edgecolor="white", lw=0.8, label="Below 97 m")
    ax.scatter(w.oct_mar_mm[br], w.peak[br], s=34, color=ORANGE, edgecolor="white", lw=0.8, label="Reached 97 m")
    for _, r in w[br | (w.winter_end_year == 2023)].iterrows():
        y = int(r.winter_end_year)
        off = {2001: (-40, 4), 2020: (6, -11)}.get(y, (5, -3))
        ax.annotate(f"{y-1}/{str(y)[2:]}", (r.oct_mar_mm, r.peak), xytext=off, textcoords="offset points", fontsize=7.5)
    k, b = np.polyfit(w.oct_mar_mm, w.peak, 1); xx = np.array([200, 900]); ax.plot(xx, k * xx + b, ls="--", color=INK2, lw=1)
    ax.axhline(97, color=INK2, ls=":", lw=1)
    r = np.corrcoef(w.oct_mar_mm, w.peak)[0, 1]
    ax.set_title(f"Winter peak (full record) vs Oct–Mar rainfall, HadUK-Grid 1 km, 2000/01–2024/25 (r = {r:.2f})",
                 loc="left", fontsize=9.5, color=INK)
    ax.set_xlabel("Oct–Mar rainfall (mm)"); ax.set_ylabel("Winter peak (mAOD)")
    ax.legend(frameon=False, loc="upper left", fontsize=8); ax.grid(color=GRID, lw=0.6); ax.set_axisbelow(True)
    s.append(Spacer(1, 4)); s.append(img(fig, "fig3.png"))

    s.append(Paragraph("97 m Pitton threshold (revised)", H2))
    s.append(Paragraph("Five of 25 logger-era winters reached 97 m (about 1 in 5): 2000/01, 2002/03, 2013/14, 2019/20 and 2023/24. "
                       "On the Broughton sums all had Oct–Mar ≥ ~615 mm and none below ~565 mm reached it; on HadUK-Grid all "
                       "had ≥ ~670 mm. An Oct–Mar running total is a better early indicator than Oct–Jan, but timing and "
                       "antecedent state still shift the exact peak — 2022/23 was very wet yet peaked at only 93.1 m. "
                       "A sixth winter, 2025/26 (99.02 m), is not in this table because HadUK-Grid rainfall currently "
                       "ends in December 2025.", BODY))
    s.append(Paragraph("Validation and caveats", H2))
    s += bullets([
        "Broughton monthly Oct–Jan sums vs Tim Vaughan: 2001 529 vs 534, 2003 555 vs 557 (~1%), but 2014 565 vs 605, 2020 445 vs 484, "
        "2024 456 vs 509 (7–11% low) — the fetch under-added the wettest months. HadUK-Grid gives 578, 603, 634, 496 and 505 mm.",
        "Winter 2018/19 Broughton totals under-read (12-day data gap in January 2019).",
        "Broughton is about 10 km from the borehole; HadUK-Grid uses the borehole's own 1 km cell."])

    s.append(PageBreak())
    s.append(Paragraph("Data: winter peaks (full EA record) and HadUK-Grid 1 km rainfall", H2))
    rows = [["Winter", "Oct–Dec mm", "Oct–Jan mm", "Oct–Mar mm", "Peak mAOD", "Peak date"]]
    for _, r in w.iterrows():
        y = int(r.winter_end_year)
        rows.append([f"{y-1}/{str(y)[2:]}", f"{r.oct_dec_mm:.0f}", f"{r.oct_jan_mm:.0f}", f"{r.oct_mar_mm:.0f}",
                     f"{CORR[y][0]:.2f}", CORR[y][1]])
    s.append(table(rows, [22 * mm, 24 * mm, 24 * mm, 24 * mm, 24 * mm, 30 * mm], font=8,
                   bold_rows=[i + 1 for i, y in enumerate(w.winter_end_year) if CORR[int(y)][0] >= 97]))
    s.append(Paragraph("Bold rows reached the 97 m threshold. Rainfall: Met Office HadUK-Grid v1.3.2.ceda (release v20260512), "
                       "cell centred E 425500 / N 135500. Peaks: highest daily logger reading October–May.", SMALL))
    return build("Lopcombe_Rainfall_Correlation_OctMar.pdf", s, "Lopcombe Corner — Oct–Mar rainfall analysis")


for f in (pdf1, pdf3):
    print(f())
