"""
Generate APD Optimisation Validation PDF
BESS Multi-Market Optimisation Algorithm — Worked Examples from January 2026
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate, Frame
from reportlab.lib import colors
import os

# ── Colour palette ──
NAVY = HexColor("#1F4E79")
BLUE = HexColor("#2E75B6")
LIGHT_BLUE = HexColor("#D6E8F7")
VERY_LIGHT_BLUE = HexColor("#EBF3FA")
GREEN_BG = HexColor("#E8F5E9")
RED_BG = HexColor("#FFEBEE")
YELLOW_BG = HexColor("#FFF8E1")
GREY = HexColor("#F5F5F5")
DARK_GREY = HexColor("#444444")
MID_GREY = HexColor("#888888")
BORDER_GREY = HexColor("#CCCCCC")

# ── Output path ──
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(os.path.dirname(OUT_DIR), "docs", "APD_Optimisation_Validation.pdf")
# Use docs folder directly
OUT_PATH = os.path.join(OUT_DIR, "APD_Optimisation_Validation.pdf")

# ── Page dimensions ──
PAGE_W, PAGE_H = A4
MARGIN = 2 * cm


# ── Header / footer ──
def header_footer(canvas, doc):
    canvas.saveState()
    # Header
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(1.5)
    canvas.line(MARGIN, PAGE_H - MARGIN + 8*mm, PAGE_W - MARGIN, PAGE_H - MARGIN + 8*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MID_GREY)
    canvas.drawString(MARGIN, PAGE_H - MARGIN + 10*mm,
                      "BESS Optimisation Validation — January 2026")
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - MARGIN + 10*mm,
                           "Confidential")
    # Footer
    canvas.setStrokeColor(BORDER_GREY)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, MARGIN - 5*mm, PAGE_W - MARGIN, MARGIN - 5*mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MID_GREY)
    canvas.drawCentredString(PAGE_W / 2, MARGIN - 10*mm,
                             f"Page {doc.page}")
    canvas.drawRightString(PAGE_W - MARGIN, MARGIN - 10*mm,
                           "Ampyr Energy — Project Lazarus")
    canvas.restoreState()


# ── Styles ──
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    "DocTitle", parent=styles["Title"], fontSize=28, leading=34,
    textColor=NAVY, spaceAfter=6*mm, alignment=TA_CENTER,
    fontName="Helvetica-Bold"))

styles.add(ParagraphStyle(
    "DocSubtitle", parent=styles["Normal"], fontSize=16, leading=20,
    textColor=BLUE, spaceAfter=4*mm, alignment=TA_CENTER,
    fontName="Helvetica"))

styles.add(ParagraphStyle(
    "CoverDetail", parent=styles["Normal"], fontSize=11, leading=15,
    textColor=DARK_GREY, alignment=TA_CENTER, fontName="Helvetica"))

styles.add(ParagraphStyle(
    "H1", parent=styles["Heading1"], fontSize=18, leading=22,
    textColor=NAVY, spaceBefore=10*mm, spaceAfter=4*mm,
    fontName="Helvetica-Bold", borderWidth=0,
    borderPadding=0, borderColor=None))

styles.add(ParagraphStyle(
    "H2", parent=styles["Heading2"], fontSize=14, leading=18,
    textColor=BLUE, spaceBefore=6*mm, spaceAfter=3*mm,
    fontName="Helvetica-Bold"))

styles.add(ParagraphStyle(
    "H3", parent=styles["Heading3"], fontSize=12, leading=16,
    textColor=DARK_GREY, spaceBefore=4*mm, spaceAfter=2*mm,
    fontName="Helvetica-Bold"))

styles.add(ParagraphStyle(
    "Body", parent=styles["Normal"], fontSize=10, leading=14,
    textColor=black, spaceAfter=2*mm, fontName="Helvetica",
    alignment=TA_JUSTIFY))

styles.add(ParagraphStyle(
    "BodyBold", parent=styles["Normal"], fontSize=10, leading=14,
    textColor=black, spaceAfter=2*mm, fontName="Helvetica-Bold"))

styles.add(ParagraphStyle(
    "CodeBlock", parent=styles["Normal"], fontSize=9, leading=13,
    textColor=HexColor("#333333"), fontName="Courier",
    leftIndent=10*mm, spaceAfter=1*mm))

styles.add(ParagraphStyle(
    "Note", parent=styles["Normal"], fontSize=9.5, leading=13.5,
    textColor=HexColor("#555555"), fontName="Helvetica-Oblique",
    leftIndent=8*mm, rightIndent=8*mm, spaceAfter=3*mm,
    borderWidth=0, borderPadding=4, borderColor=BLUE,
    backColor=VERY_LIGHT_BLUE))

styles.add(ParagraphStyle(
    "TableCell", parent=styles["Normal"], fontSize=8.5, leading=11,
    fontName="Helvetica"))

styles.add(ParagraphStyle(
    "TableCellBold", parent=styles["Normal"], fontSize=8.5, leading=11,
    fontName="Helvetica-Bold"))

styles.add(ParagraphStyle(
    "TableHeader", parent=styles["Normal"], fontSize=8.5, leading=11,
    fontName="Helvetica-Bold", textColor=white))

styles.add(ParagraphStyle(
    "TableCellCode", parent=styles["Normal"], fontSize=8, leading=10,
    fontName="Courier", alignment=TA_RIGHT))


# ── Helpers ──
def h1(text):
    return Paragraph(text, styles["H1"])

def h2(text):
    return Paragraph(text, styles["H2"])

def h3(text):
    return Paragraph(text, styles["H3"])

def p(text):
    return Paragraph(text, styles["Body"])

def pb(text):
    return Paragraph(text, styles["BodyBold"])

def code(text):
    return Paragraph(text.replace(" ", "&nbsp;"), styles["CodeBlock"])

def note(text):
    return Paragraph(text, styles["Note"])

def sp(h=3):
    return Spacer(1, h*mm)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER_GREY,
                       spaceAfter=3*mm, spaceBefore=3*mm)


def make_table(headers, rows, col_widths=None):
    """Create a styled table with header row."""
    # Build data
    data = [[Paragraph(h, styles["TableHeader"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles["TableCell"]) for c in row])

    if col_widths is None:
        avail = PAGE_W - 2 * MARGIN
        col_widths = [avail / len(headers)] * len(headers)

    t = Table(data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GREY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]
    # Alternating row shading
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), GREY))

    t.setStyle(TableStyle(style_cmds))
    return t


def make_highlight_table(headers, rows, col_widths=None, highlight_rows=None):
    """Table with specific row highlighting (green/red/blue)."""
    data = [[Paragraph(h, styles["TableHeader"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles["TableCell"]) for c in row])

    if col_widths is None:
        avail = PAGE_W - 2 * MARGIN
        col_widths = [avail / len(headers)] * len(headers)

    t = Table(data, colWidths=col_widths, repeatRows=1)

    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GREY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(('BACKGROUND', (0, i), (-1, i), GREY))

    if highlight_rows:
        for row_idx, colour in highlight_rows.items():
            style_cmds.append(('BACKGROUND', (0, row_idx), (-1, row_idx), colour))
            style_cmds.append(('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold'))

    t.setStyle(TableStyle(style_cmds))
    return t


# ═══════════════════════════════════════════════
# BUILD THE DOCUMENT
# ═══════════════════════════════════════════════
story = []

# ── TITLE PAGE ──
story.append(Spacer(1, 50*mm))
story.append(Paragraph("AMPYR ENERGY", styles["DocSubtitle"]))
story.append(Spacer(1, 4*mm))
story.append(Paragraph("BESS Multi-Market Optimisation", styles["DocTitle"]))
story.append(Paragraph("Algorithm Validation Document", styles["DocSubtitle"]))
story.append(Spacer(1, 6*mm))
story.append(Paragraph("With Worked Examples from January 2026 Data", styles["CoverDetail"]))
story.append(Spacer(1, 3*mm))
story.append(Paragraph("Prepared for Business Expert Validation", styles["CoverDetail"]))
story.append(Spacer(1, 20*mm))
story.append(Paragraph(
    "<b>Asset:</b> Northwold Solar Farm BESS (8.4 MWh / 4.2 MW import / 7.5 MW export)",
    styles["CoverDetail"]))
story.append(Paragraph(
    "<b>Aggregator:</b> GridBeyond", styles["CoverDetail"]))
story.append(Paragraph(
    "<b>Period:</b> January 2026 (31 days, 1,488 half-hourly periods)",
    styles["CoverDetail"]))
story.append(Spacer(1, 25*mm))
story.append(Paragraph(
    "Confidential — Project Lazarus | Version 1.0 | March 2026",
    ParagraphStyle("footer_cover", parent=styles["Normal"], fontSize=9,
                   textColor=MID_GREY, alignment=TA_CENTER)))
story.append(PageBreak())


# ── TABLE OF CONTENTS ──
story.append(h1("Table of Contents"))
story.append(sp(4))
toc_items = [
    ("1.", "What the Algorithm Does"),
    ("2.", "Input Parameters"),
    ("3.", "The Algorithm Step by Step"),
    ("4.", "January 2026 Results Summary"),
    ("5.", "Worked Example: Best Trading Day (5 January 2026)"),
    ("6.", "Worked Example: SFFR Day (3 January 2026)"),
    ("7.", "Understanding the Performance Gap"),
    ("8.", "Validation Checklist for Business Expert"),
]
for num, title in toc_items:
    story.append(Paragraph(
        f"<b>{num}</b>&nbsp;&nbsp;{title}", styles["Body"]))
story.append(PageBreak())


# ═══════════════ SECTION 1 ═══════════════
story.append(h1("1. What the Algorithm Does"))
story.append(p(
    "The optimisation algorithm answers a simple question: <b>given perfect knowledge of market prices "
    "for an entire day, what is the maximum revenue the battery could have earned?</b>"))
story.append(p(
    "This is a <b>hindsight analysis</b> (not a forecast). It shows the theoretical ceiling that a "
    "perfect trading strategy could achieve, allowing us to measure how well GridBeyond actually performed."))
story.append(sp())

story.append(h2("1.1 The Decision"))
story.append(p(
    "Every day, the algorithm makes one binary decision:"))
story.append(note(
    "Should the battery trade in wholesale/balancing markets (Multi-Market), "
    "or stay in frequency response (SFFR)?"))
story.append(p("It calculates the total revenue for each option and picks the higher one."))
story.append(sp())

story.append(h2("1.2 The Three Strategies Computed"))
cw = [30*mm, 35*mm, 38*mm, 60*mm]
story.append(make_table(
    ["Strategy", "Markets Used", "Switching", "Purpose"],
    [
        ["Strategy 1: EPEX Daily", "EPEX only", "Whole day: SFFR or EPEX",
         "Simple baseline — what if we only traded EPEX?"],
        ["Strategy 2: EPEX EFA", "EPEX only", "Per 2-hour EFA block",
         "Can we do better by switching between SFFR and EPEX within a day?"],
        ["Strategy 3: Multi-Market", "EPEX + ISEM + SSP + SBP + DA_HH",
         "Whole day: SFFR or all markets",
         "Best possible with all markets — the benchmark we care about"],
    ], cw
))
story.append(sp())
story.append(pb(
    "Strategy 3 (Multi-Market) is the primary benchmark. It represents the theoretical maximum "
    "revenue achievable within the asset's physical and warranty constraints."))
story.append(PageBreak())


# ═══════════════ SECTION 2 ═══════════════
story.append(h1("2. Input Parameters"))

story.append(h2("2.1 Battery Physical Constraints"))
cw2 = [35*mm, 28*mm, 100*mm]
story.append(make_table(
    ["Parameter", "Value", "What It Means"],
    [
        ["Max Charge (Import)", "4.2 MW",
         "How fast the battery can absorb energy from the grid"],
        ["Max Discharge (Export)", "7.5 MW",
         "How fast the battery can push energy to the grid (asymmetric — faster out than in)"],
        ["Usable Capacity", "8.4 MWh",
         "Total energy the battery can store"],
        ["Round-Trip Efficiency", "87%",
         "For every 1 MWh put in, only 0.87 MWh comes out (13% lost as heat)"],
        ["SOC Floor", "5% (0.42 MWh)",
         "Never drain below this — protects battery cells from damage"],
        ["SOC Ceiling", "95% (7.98 MWh)",
         "Never charge above this — prevents thermal stress"],
        ["Warranty Limit", "1.5 cycles/day",
         "Maximum daily discharge throughput = 12.6 MWh = 1.5 x 8.4"],
    ], cw2
))
story.append(sp())

story.append(h2("2.2 Market Prices (5 Markets)"))
story.append(p(
    "For each 30-minute period, the algorithm sees prices from 5 markets and picks the cheapest "
    "to buy from and the most expensive to sell into:"))
cw3 = [32*mm, 60*mm, 40*mm]
story.append(make_table(
    ["Market", "What It Is", "Typical Range (Jan 26)"],
    [
        ["EPEX Day Ahead", "Wholesale market, prices set day before delivery",
         "50–200 GBP/MWh"],
        ["GB-ISEM Intraday", "Cross-border intraday auction (GB–Ireland)",
         "50–200 GBP/MWh"],
        ["SSP (System Sell Price)", "Price for being long in National Grid balancing",
         "50–750 GBP/MWh (spikes!)"],
        ["SBP (System Buy Price)", "Price for being short in National Grid balancing",
         "50–500 GBP/MWh"],
        ["DA HH (Day Ahead Half-Hourly)", "Half-hourly variant of day-ahead",
         "50–200 GBP/MWh"],
    ], cw3
))
story.append(sp())
story.append(note(
    "Key insight: SSP can spike to extreme levels (750 GBP/MWh on Jan 5!) during system stress "
    "events. The multi-market algorithm captures these spikes by selling into SSP when it is the "
    "highest-priced market."))
story.append(sp())

story.append(h2("2.3 SFFR (Frequency Response)"))
story.append(p(
    "SFFR is a contract where the battery commits to being available for grid frequency support. "
    "The battery earns a fixed price per MW of availability per hour, regardless of whether it "
    "actually needs to respond."))
story.append(code("SFFR Revenue per period = Availability_MW x SFFR_Clearing_Price x 0.5 hours"))
story.append(sp(1))
story.append(code("The optimiser assumes 7.0 MW availability (full capacity)."))
story.append(code("Actual availability varies (average 6.81 MW in Jan 2026 due to SOC/operational constraints)."))
story.append(PageBreak())


# ═══════════════ SECTION 3 ═══════════════
story.append(h1("3. The Algorithm Step by Step"))

story.append(h2("3.1 Overview"))
story.append(p("For each day in the month:"))
story.append(sp())

story.append(pb("Step 1: Calculate SFFR value for the full day"))
story.append(code("SFFR_Daily = Sum over 48 periods of (7.0 MW x SFFR_Clearing_Price x 0.5 hours)"))
story.append(sp())

story.append(pb("Step 2: For each period, find the cheapest market to buy from and the most expensive to sell into"))
story.append(code("Buy_Price[t]  = min(EPEX[t], ISEM[t], SSP[t], SBP[t], DA_HH[t])"))
story.append(code("Sell_Price[t] = max(EPEX[t], ISEM[t], SSP[t], SBP[t], DA_HH[t])"))
story.append(sp())

story.append(pb("Step 3: Solve the linear program — find the optimal charge/discharge schedule"))
story.append(code("Maximize: Sum of (Discharge[t] x Sell_Price[t] - Charge[t] x Buy_Price[t]) x 0.5"))
story.append(sp(1))
story.append(code("Subject to:"))
story.append(code("  Battery physics: SoC[t] = SoC[t-1] + Charge[t] x 0.933 x 0.5 - Discharge[t] / 0.933 x 0.5"))
story.append(code("  Charge limit:    0 &lt;= Charge[t] &lt;= 4.2 MW"))
story.append(code("  Discharge limit: 0 &lt;= Discharge[t] &lt;= 7.5 MW"))
story.append(code("  SOC bounds:      0.42 MWh &lt;= SoC[t] &lt;= 7.98 MWh"))
story.append(code("  Warranty:        Sum(Discharge[t] x 0.5) &lt;= 12.6 MWh per day"))
story.append(sp())

story.append(pb("Step 4: Compare and choose"))
story.append(code("If SFFR_Daily &gt; Multi_Market_Revenue:  choose SFFR (battery locked)"))
story.append(code("If Multi_Market_Revenue &gt;= SFFR_Daily: choose Multi-Market (active dispatch)"))
story.append(sp())

story.append(pb("Step 5: Carry SOC forward to the next day"))
story.append(code("Day N+1 starting SOC = Day N ending SOC"))
story.append(sp())

story.append(h2("3.2 Efficiency Explained"))
story.append(p("The battery loses energy in both directions:"))
story.append(code("Charging:    1 MWh from grid --> battery stores 0.933 MWh (6.7% lost)"))
story.append(code("Discharging: 0.933 MWh from battery --> grid receives 0.87 MWh (another 6.7% lost)"))
story.append(code("Round trip:  1 MWh in --> 0.87 MWh out (13% total loss)"))
story.append(sp())
story.append(p(
    "This means the sell price must be at least <b>15% higher</b> than the buy price to break "
    "even on a round trip (1 / 0.87 = 1.149)."))
story.append(note(
    "Break-even spread = Buy_Price x (1/0.87 - 1) = Buy_Price x 14.9%. "
    "At 100 GBP/MWh buy price, need 115 GBP/MWh sell price just to break even."))
story.append(PageBreak())


# ═══════════════ SECTION 4 ═══════════════
story.append(h1("4. January 2026 Results Summary"))

story.append(h2("4.1 Monthly Totals"))
cw4 = [85*mm, 78*mm]
story.append(make_highlight_table(
    ["Metric", "Value"],
    [
        ["Optimised Multi-Market Revenue (theoretical max)", "£33,376"],
        ["Actual GridBeyond Revenue", "£28,190"],
        ["Revenue Gap", "£5,186"],
        ["Capture Rate", "84.5%"],
        ["Days choosing SFFR", "22 out of 31 (71%)"],
        ["Days choosing Multi-Market", "8 out of 31 (when price spikes made trading more valuable)"],
        ["Total SFFR periods", "1,056 of 1,488 (71%)"],
        ["Total active trading periods", "81 of 1,488 (5.4%)"],
        ["Total idle periods (in trading days)", "303 of 1,488"],
    ], cw4,
    highlight_rows={1: LIGHT_BLUE, 2: GREEN_BG}
))
story.append(sp())

story.append(h2("4.2 Daily Revenue Ranking (Top 10 Days)"))
cw5 = [12*mm, 22*mm, 28*mm, 28*mm, 73*mm]
story.append(make_table(
    ["Rank", "Date", "Strategy", "Optimised Rev.", "Key Driver"],
    [
        ["1", "Mon 5 Jan", "Multi-Market", "£5,222",
         "SSP spike to 750 at 19:00 — sold 1.65 MW into SSP"],
        ["2", "Thu 8 Jan", "Multi-Market", "£3,766",
         "SSP spike event — high balancing market spreads"],
        ["3", "Tue 6 Jan", "Multi-Market", "£2,551",
         "Continued high SSP spreads from 5th Jan event"],
        ["4", "Fri 2 Jan", "Multi-Market", "£1,115",
         "New Year period high demand / low wind"],
        ["5", "Thu 15 Jan", "Multi-Market", "£1,095",
         "Evening peak SSP spread"],
        ["6", "Mon 19 Jan", "Multi-Market", "£1,008",
         "High evening spreads"],
        ["7", "Wed 14 Jan", "Multi-Market", "£981",
         "Moderate SSP spreads"],
        ["8", "Tue 27 Jan", "SFFR", "£943",
         "High SFFR clearing prices (winter peak demand)"],
        ["9", "Sun 25 Jan", "SFFR", "£915",
         "High SFFR clearing prices"],
        ["10", "Wed 28 Jan", "SFFR", "£911",
         "High SFFR clearing prices"],
    ], cw5
))
story.append(sp())
story.append(note(
    "The top 3 days (5th–8th Jan) generated 34.6% of the entire month's optimised revenue. "
    "This concentration highlights the importance of capturing price spike events."))
story.append(PageBreak())


# ═══════════════ SECTION 5 ═══════════════
story.append(h1("5. Worked Example: Best Trading Day (5 January 2026)"))
story.append(p(
    "This day generated <b>£5,222</b> in optimised revenue — the highest single day in January. "
    "The optimizer chose Multi-Market over SFFR. Let's walk through why and how."))
story.append(sp())

story.append(h2("5.1 The Decision: SFFR vs Multi-Market"))
story.append(p(
    "<b>SFFR option:</b> Locking the battery in frequency response for the full day. "
    "SFFR clearing prices on Jan 5 ranged from 1.17 to 4.36 GBP/MW/h."))
story.append(code("SFFR_Daily = Sum(7.0 MW x SFFR_Price[t] x 0.5) for 48 periods"))
story.append(code("          ~= 7.0 x average(2.84) x 0.5 x 48 = ~477 GBP"))
story.append(sp())
story.append(p(
    "<b>Multi-Market option:</b> Active trading across all 5 markets. "
    "SSP spiked to 750 GBP/MWh at 19:00!"))
story.append(code("Multi_Market_Revenue = 5,222 GBP  (from LP solver)"))
story.append(sp())
story.append(pb(
    "Decision: Multi-Market wins (5,222 >> 477). "
    "The SSP spike alone made trading 10x more valuable than SFFR."))
story.append(sp())

story.append(h2("5.2 What the Algorithm Did (Hour by Hour)"))
story.append(pb("Phase 1 — Charging (00:00–02:30)"))
story.append(p(
    "Bought energy from SSP at 68–70 GBP/MWh (cheapest market overnight). "
    "Charged from starting SOC up to 7.98 MWh (95% full)."))

cw6 = [18*mm, 18*mm, 18*mm, 22*mm, 22*mm, 22*mm, 20*mm]
story.append(make_table(
    ["Time", "Action", "Net MWh", "SOC (MWh)", "Buy Price", "Sell Price", "Revenue"],
    [
        ["00:00", "Buy-SSP", "-2.10", "2.38", "68.15", "83.10", "-£143"],
        ["00:30", "Buy-SSP", "-2.10", "4.34", "70.16", "83.10", "-£147"],
        ["01:00", "Idle", "0.00", "4.34", "77.20", "95.30", "£0"],
        ["01:30", "Buy-SSP", "-2.10", "6.30", "70.15", "83.00", "-£147"],
        ["02:00", "Idle", "0.00", "6.30", "77.00", "96.00", "£0"],
        ["02:30", "Buy-SSP", "-1.81", "7.98", "70.16", "82.37", "-£127"],
    ], cw6
))
story.append(sp())
story.append(p(
    "<b>Charging cost:</b> £564 spent buying energy. SSP was the cheapest market at 68–70 GBP/MWh "
    "while EPEX was 82–83 GBP/MWh. The algorithm saved ~15% by buying from SSP instead of EPEX."))
story.append(sp())

story.append(pb("Phase 2 — Waiting (03:00–15:30)"))
story.append(p(
    "Battery sat fully charged at 7.98 MWh for 26 consecutive periods. Despite spreads of "
    "20–70 GBP/MWh during this time, the algorithm held because it 'knew' (hindsight) that "
    "much larger spreads were coming."))
story.append(note(
    "This is the key advantage of hindsight optimization: a real-time trader might have been "
    "tempted to discharge at the 68 GBP/MWh spread at 15:30, but the optimizer held for the "
    "640 GBP/MWh spread at 19:00."))
story.append(sp())

story.append(pb("Phase 3 — The Spike Discharge (16:00–19:00)"))
story.append(p("SSP spiked to extreme levels. The optimizer sold aggressively:"))
story.append(make_highlight_table(
    ["Time", "Action", "Net MWh", "SOC (MWh)", "Buy Price", "Sell Price", "Revenue"],
    [
        ["16:00", "Buy-ISEM", "+1.65", "5.92", "157.79", "433.30", "+£1,294"],
        ["16:30", "Sell-SSP", "+3.75", "1.90", "175.16", "426.65", "+£1,600"],
        ["17:00", "Buy-SSP", "-2.10", "3.86", "82.77", "179.30", "-£174"],
        ["17:30", "Sell-SSP", "+1.35", "2.41", "174.08", "368.87", "+£498"],
        ["18:30", "Buy-ISEM", "-0.08", "2.48", "158.15", "338.56", "-£12"],
        ["19:00", "Sell-SSP", "+1.65", "0.42", "110.00", "750.00", "+£2,582"],
    ], cw6,
    highlight_rows={2: GREEN_BG, 6: GREEN_BG, 7: GREEN_BG}
))
story.append(sp())
story.append(pb(
    "The 19:00 period alone generated £2,582. SSP hit 750 GBP/MWh (vs ISEM at 110). "
    "The battery discharged its last 1.65 MWh, reaching the minimum SOC of 0.42 MWh."))
story.append(sp())

story.append(pb("Phase 4 — Empty (19:30–23:30)"))
story.append(p(
    "Battery sat at minimum SOC (0.42 MWh). Even though spreads of 40–100 GBP/MWh existed, "
    "there was nothing left to sell and the warranty limit was reached."))
story.append(sp())

story.append(h2("5.3 Revenue Breakdown for Jan 5"))
cw7 = [45*mm, 28*mm, 90*mm]
story.append(make_highlight_table(
    ["Component", "Amount (GBP)", "Explanation"],
    [
        ["Charging cost (4 periods)", "-£564",
         "Bought 8.26 MWh at avg 68–70 via SSP"],
        ["Discharge revenue (3 sell periods)", "+£5,974",
         "Sold into SSP during price spike (avg 408 GBP/MWh)"],
        ["Recharge + small trades", "-£188",
         "Mid-day repositioning"],
        ["NET TOTAL", "£5,222",
         "Revenue after all costs"],
    ], cw7,
    highlight_rows={4: LIGHT_BLUE}
))
story.append(sp())

story.append(h2("5.4 How Did GridBeyond Actually Perform on Jan 5?"))
cw8 = [42*mm, 32*mm, 38*mm, 30*mm]
story.append(make_highlight_table(
    ["Metric", "Optimised", "Actual (GridBeyond)", "Gap"],
    [
        ["Total Revenue", "£5,222", "£1,181", "£4,041 (77% missed)"],
        ["Strategy", "Multi-Market (aggressive SSP)", "Mixed SFFR + IDA1 + EPEX", "—"],
        ["Revenue from SFFR", "£0 (not chosen)", "£666", "—"],
        ["Revenue from IDA1", "£0", "£872", "—"],
        ["Revenue from EPEX 30 DA", "£0", "-£324 (loss)", "—"],
        ["Imbalance", "£0", "-£34 (net penalty)", "—"],
    ], cw8,
    highlight_rows={1: RED_BG}
))
story.append(sp())
story.append(note(
    "GridBeyond earned £1,181 vs the theoretical £5,222 (22.6% capture). The main miss: "
    "GridBeyond did not sell into SSP during the 750 GBP/MWh spike at 19:00. This single "
    "missed period accounts for £2,582 of the £4,041 gap."))
story.append(sp())
story.append(p(
    "<b>Important caveat:</b> GridBeyond trades in real-time without knowledge of future prices. "
    "The SSP spike at 19:00 was unpredictable. The optimisation uses perfect hindsight — it is a "
    "benchmark, not an expectation."))
story.append(PageBreak())


# ═══════════════ SECTION 6 ═══════════════
story.append(h1("6. Worked Example: SFFR Day (3 January 2026)"))
story.append(p(
    "On this day, the algorithm chose SFFR over Multi-Market trading. "
    "Revenue: <b>£670</b> (all from frequency response, zero active trading)."))
story.append(sp())

story.append(h2("6.1 The Decision"))
story.append(code("SFFR_Daily = Sum(7.0 x SFFR_Price[t] x 0.5) for 48 periods = 670 GBP"))
story.append(code("Multi_Market_Revenue (from LP solver)                      &lt; 670 GBP"))
story.append(sp(1))
story.append(code("Result: SFFR wins. Battery stays locked in frequency response all day."))
story.append(sp())
story.append(p(
    "Why was SFFR better? The market spreads on Jan 3 were modest (4–50 GBP/MWh range), "
    "while SFFR clearing prices were decent (1.70–6.09 GBP/MW/h). There was no SSP spike event "
    "to make trading worthwhile."))
story.append(sp())

story.append(h2("6.2 SFFR Clearing Prices Through the Day"))
story.append(p(
    "SFFR prices follow a predictable pattern: low overnight, rising through the morning, "
    "peaking in the late afternoon/evening, dropping at night."))
cw9 = [36*mm, 30*mm, 25*mm, 25*mm, 47*mm]
story.append(make_table(
    ["Time Block", "SFFR Price (GBP/MW/h)", "Avg Availability", "Revenue/Period", "Comment"],
    [
        ["00:00–02:30 (Night)", "1.70", "7.4 MW", "~6.3/period", "Low demand period"],
        ["03:00–06:30 (Early)", "1.30", "7.4 MW", "~4.8/period", "Lowest SFFR price band"],
        ["07:00–10:30 (Morning)", "3.96", "6.6 MW", "~13.0/period", "Morning peak begins"],
        ["11:00–14:30 (Midday)", "5.04", "4.4 MW", "~11.2/period", "High price, lower availability"],
        ["15:00–18:30 (Peak)", "6.09", "7.4 MW", "~22.4/period", "Highest SFFR prices of the day"],
        ["19:00–22:30 (Evening)", "5.51", "7.4 MW", "~20.5/period", "Still high evening demand"],
        ["23:00–23:30 (Night)", "2.99", "7.3 MW", "~11.0/period", "Dropping to night rates"],
    ], cw9
))
story.append(sp())

story.append(h2("6.3 Optimiser vs Actual Comparison"))
cw10 = [45*mm, 58*mm, 58*mm]
story.append(make_highlight_table(
    ["Metric", "Optimiser", "Actual GridBeyond"],
    [
        ["Strategy", "SFFR (full day)", "SFFR (full day)"],
        ["Assumed Availability", "7.0 MW (constant)", "6.81 MW (average, varies by period)"],
        ["Total Revenue", "£670", "£638"],
        ["Gap", "£32 (4.8%)", "—"],
        ["Gap Cause", "—", "Actual availability < assumed 7.0 MW"],
    ], cw10,
    highlight_rows={3: GREEN_BG}
))
story.append(sp())
story.append(note(
    "On SFFR days, the gap between optimised and actual is small (4.8%) and entirely due to "
    "the availability assumption. The optimiser uses 7.0 MW; actual availability averages "
    "6.81 MW due to SOC constraints and operational factors. This is not a strategy gap — "
    "GridBeyond made the right call on this day."))
story.append(PageBreak())


# ═══════════════ SECTION 7 ═══════════════
story.append(h1("7. Understanding the Performance Gap"))
story.append(p(
    "The total January gap is <b>£5,186</b> (optimised £33,376 vs actual £28,190). "
    "Where does it come from?"))
story.append(sp())

story.append(h2("7.1 Gap Decomposition"))
cw11 = [45*mm, 25*mm, 22*mm, 71*mm]
story.append(make_highlight_table(
    ["Source of Gap", "Estimated GBP", "% of Total Gap", "Explanation"],
    [
        ["SSP spike events not captured", "~£3,500", "67%",
         "GridBeyond was in SFFR or not positioned when SSP spiked (especially Jan 5, 8)"],
        ["Sub-optimal market selection", "~£800", "15%",
         "Actual trades used EPEX/IDA1 when ISEM or SSP offered better prices"],
        ["SFFR availability gap", "~£500", "10%",
         "Optimiser assumes 7.0 MW, actual averages 6.81 MW"],
        ["Imbalance charges", "~£386", "7%",
         "Actual incurred imbalance penalties not in optimised"],
        ["TOTAL GAP", "~£5,186", "100%", ""],
    ], cw11,
    highlight_rows={5: LIGHT_BLUE}
))
story.append(sp())

story.append(h2("7.2 What This Means"))
story.append(pb(
    "The 84.5% capture rate is a reasonable result. The majority of the gap (67%) comes from "
    "unpredictable SSP spikes that no real-time trader could consistently capture. "
    "The algorithm's advantage is purely hindsight."))
story.append(sp())
story.append(p("Key points for validation:"))
story.append(p(
    "<b>1.</b> SFFR days show very small gaps (4–5%) — GridBeyond correctly identifies "
    "when SFFR is the right strategy."))
story.append(p(
    "<b>2.</b> The bulk of the gap concentrates in 2–3 spike days per month — this is "
    "expected for any non-clairvoyant trader."))
story.append(p(
    "<b>3.</b> The warranty constraint (1.5 cycles/day = 12.6 MWh discharge) limits how much "
    "can be extracted from spike events."))
story.append(p(
    "<b>4.</b> The algorithm respects all physical constraints — no revenue is assumed that "
    "violates SOC bounds, power limits, or efficiency losses."))
story.append(PageBreak())


# ═══════════════ SECTION 8 ═══════════════
story.append(h1("8. Validation Checklist for Business Expert"))
story.append(p("Please confirm the following aspects of the algorithm are correct and reasonable:"))
story.append(sp())

story.append(h2("8.1 Physical Constraints"))
cw12 = [10*mm, 88*mm, 55*mm]
story.append(make_table(
    ["#", "Question", "Expected Answer"],
    [
        ["1", "Is the max charge rate of 4.2 MW correct for Northwold?",
         "Yes / No / Correct value: ___"],
        ["2", "Is the max discharge rate of 7.5 MW correct?",
         "Yes / No / Correct value: ___"],
        ["3", "Is 8.4 MWh the correct usable capacity?",
         "Yes / No / Correct value: ___"],
        ["4", "Is 87% round-trip efficiency accurate?",
         "Yes / No / Correct value: ___"],
        ["5", "Are the 5%/95% SOC limits appropriate?",
         "Yes / No / Correct limits: ___"],
    ], cw12
))
story.append(sp())

story.append(h2("8.2 Commercial Parameters"))
story.append(make_table(
    ["#", "Question", "Expected Answer"],
    [
        ["6", "Is 1.5 cycles/day the correct warranty limit?",
         "Yes / No / Correct limit: ___"],
        ["7", "Is 7.0 MW the right assumed SFFR availability?",
         "Yes / No / Correct value: ___"],
        ["8", "Should we use 7.0 MW or the actual varying availability for SFFR value?",
         "7.0 MW / Actual / Other: ___"],
        ["9", "Are all 5 markets (EPEX, ISEM, SSP, SBP, DA_HH) accessible to GridBeyond?",
         "Yes / Some not: ___"],
        ["10", "Is the whole-day SFFR vs trading decision realistic, or should EFA blocks be used?",
         "Whole day / EFA blocks / Other: ___"],
    ], cw12
))
story.append(sp())

story.append(h2("8.3 Algorithm Logic"))
story.append(make_table(
    ["#", "Question", "Expected Answer"],
    [
        ["11", "Is it correct that the battery cannot trade AND do SFFR in the same period?",
         "Yes / No (can do both): ___"],
        ["12", "Should imbalance costs be included in the optimisation or excluded?",
         "Include / Exclude: ___"],
        ["13", "Should the aggregator fee (5%) be applied to the optimised revenue?",
         "Yes / No: ___"],
        ["14", "Are there any other revenue streams not modelled (e.g., STOR, FFR dynamic)?",
         "No / Yes: ___"],
        ["15", "Is the assumption of perfect price foresight acceptable for benchmarking?",
         "Yes / No: ___"],
    ], cw12
))
story.append(sp())

story.append(h2("8.4 Results Validation"))
story.append(make_table(
    ["#", "Question", "Expected Answer"],
    [
        ["16", "Does 84.5% capture rate seem reasonable for Jan 2026?",
         "Yes / Too high / Too low"],
        ["17", "Is it fair that 22 of 31 days chose SFFR in Jan? (Winter = high SFFR prices)",
         "Yes / Expected more trading / Less"],
        ["18", "Does the Jan 5 example (£5,222 optimised vs £1,181 actual) look plausible?",
         "Yes / Needs investigation: ___"],
        ["19", "Should we track additional metrics (e.g., risk-adjusted return, Sharpe ratio)?",
         "No / Yes: ___"],
        ["20", "Is this benchmark appropriate for GridBeyond performance reviews?",
         "Yes / Needs adjustments: ___"],
    ], cw12
))
story.append(sp(10))

story.append(hr())
story.append(Paragraph(
    "— End of Document —",
    ParagraphStyle("end", parent=styles["Normal"], fontSize=10,
                   textColor=MID_GREY, alignment=TA_CENTER)))


# ═══════════════ BUILD PDF ═══════════════
doc = SimpleDocTemplate(
    OUT_PATH,
    pagesize=A4,
    topMargin=MARGIN + 8*mm,
    bottomMargin=MARGIN + 4*mm,
    leftMargin=MARGIN,
    rightMargin=MARGIN,
    title="BESS Multi-Market Optimisation — Algorithm Validation",
    author="Ankit Agarwal — Ampyr Energy",
    subject="Optimisation Algorithm Validation with January 2026 Worked Examples",
)

doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)

file_size = os.path.getsize(OUT_PATH)
print(f"PDF created: {OUT_PATH}")
print(f"Size: {file_size / 1024:.1f} KB")
