"""Build HadUK-Grid_Rainfall_Method.pdf from the analysis outputs."""
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph as _P, Spacer, Table, TableStyle, Image, PageBreak

BASE = "."
RES = json.load(open(f"{BASE}/output/haduk/start_level_results.json"))
OUT = f"{BASE}/docs/reports/HadUK-Grid_Rainfall_Method.pdf"
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
    canvas.drawString(18 * mm, 10 * mm, "Lopcombe Corner borehole (EA E14150) · How HadUK-Grid rainfall is produced · 20 Oct 2026")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


s = [P("HadUK-Grid — How the Rainfall Figures Are Produced", H1),
     P("Background note for the Lopcombe Corner analyses that use HadUK-Grid 1 km monthly rainfall "
       "(v1.3.2.ceda, release v20260512) · written 20 Oct 2026", SUB),
     P("<b>In short.</b> HadUK-Grid does not measure rainfall itself. It takes readings from the UK rain-gauge network "
       "and spreads them onto a regular 1 km grid by statistical regression and interpolation. The value for the "
       "Lopcombe Corner cell is therefore an <b>estimate</b> built from surrounding gauges and the local geography, "
       "not a reading from a gauge at the borehole.", NOTE),
     P("1. Where the data come from", H2)]
s += bullets([
    "The input is the Met Office archive of UK weather observations from land-based surface stations — a network of "
    "thousands of rain gauges whose membership changes over time as stations open and close.",
    "Monthly rainfall before 1961 was added through the <b>Rainfall Rescue</b> project, which digitised historical "
    "handwritten gauge records.",
    "Because every month is gridded afresh from whichever gauges were reporting, the grid smooths over the routine "
    "opening and closing of individual stations."])
s.append(P("2. How the gauge readings become a grid", H2))
s += bullets([
    "<b>Regression on geography.</b> Gauges are irregularly placed, so the gaps are filled by a process of regression "
    "and interpolation onto a 1 km × 1 km grid. The regression accounts for latitude and longitude, altitude, terrain "
    "shape, coastal influence and urban land use.",
    "<b>Interpolation of what geography doesn't explain.</b> The Met Office cites a 2005 <i>International Journal of "
    "Climatology</i> paper for the monthly method. As we understand it, each month is treated as a departure from the "
    "long-term average (for rainfall, a percentage of normal), and the part not explained by geography is interpolated "
    "between nearby gauges with weights that fall off with distance. The Met Office methods page does not spell these "
    "details out, so they are our understanding of the published method rather than confirmed here.",
    "<b>Coarser products.</b> The 5, 12, 25 and 60 km grids are averages of the 1 km cells within each larger box. "
    "Country, administrative-region and river-basin series are averages of the 1 km cells within each area.",
    "<b>Long-term averages</b> (1961–1990, 1981–2010, 1991–2020) are calculated by averaging or summing the monthly or "
    "annual grids."])
s.append(P("3. What this means for the Lopcombe Corner figures", H2))
rows = [["Aspect", "Implication"],
        ["Nature of the value", "A weighted estimate for the 1 km cell (centre E 425500 / N 135500) from nearby gauges, "
                                "adjusted for terrain — not a direct measurement."],
        ["Independence from Broughton", "Broughton (EA E13580) is very likely one of the gauges feeding the estimate, "
                                        "so HadUK-Grid and Broughton are not fully independent. Their close agreement "
                                        "(Oct–Dec r = 0.96) partly reflects this."],
        ["Strengths", "No gaps; no jumps when stations close; quality-controlled and consistent from 1963 (and earlier). "
                      "This is why it gave cleaner winter totals than summing daily Broughton data from the EA API, "
                      "which had dropped days."],
        ["Cell choice", "Neighbouring cells differ by at most 1.25 mm a month, so small errors in locating the borehole "
                        "do not matter."],
        ["Limitations", "Smooths out very local downpours; more uncertain in earlier decades and where gauges are sparse; "
                        "monthly totals hide the timing of rain within a month."],
        ["Fitness for this work", "Seasonal totals (Oct–Mar) drive the chalk aquifer, and these are what HadUK-Grid does "
                                  "best. The limitations matter little for the winter-peak and cyclicity analyses."]]
cs = ParagraphStyle("cs", fontName="Helvetica", fontSize=8.5, leading=11)
rows = [[_P(c, ParagraphStyle("hb", parent=cs, fontName="Helvetica-Bold")) if i == 0 or j == 0 else _P(c, cs)
         for j, c in enumerate(r)] for i, r in enumerate(rows)]
t = Table(rows, colWidths=[40 * mm, 134 * mm], repeatRows=1)
t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                       ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor(INK2)),
                       ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f4f1")]),
                       ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
s.append(t)
s.append(P("4. Data used in this project", H2))
s += bullets([
    "Product: HadUK-Grid gridded climate observations, 1 km, monthly rainfall, version v1.3.2.ceda, release v20260512, "
    "from the CEDA archive (<font face='Courier'>badc/ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid/</font>).",
    "Files: 63 yearly NetCDF files, 1963–2025, about 42 MB each, kept on the external SSD at "
    "/Volumes/Crucial X9 Pro for Mac/HadUK-Grid. Downloading needs a free CEDA account and an access token "
    "(scripts/get_haduk_1km.sh handles this).",
    "Extracted series: data/haduk/lopcombe_haduk1km_monthly_rainfall.csv (cell value and 3×3 mean)."])
s.append(P("Sources", H2))
s += bullets([
    "Met Office, <i>HadUK-Grid Methods</i>: https://www.metoffice.gov.uk/research/climate/maps-and-data/data/haduk-grid/methods",
    "CEDA, <i>Using Archive Access Tokens</i>: https://help.ceda.ac.uk/article/5100-archive-access-tokens",
    "Monthly gridding method: 2005 <i>International Journal of Climatology</i> paper cited on the Met Office methods page; "
    "HadUK-Grid science paper also linked there. Not read directly for this note."])

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=14 * mm,
                        bottomMargin=17 * mm, title="HadUK-Grid — how the rainfall figures are produced",
                        author="Keith Sloan / Claude")
doc.build(s, onFirstPage=footer, onLaterPages=footer)
print(OUT)
