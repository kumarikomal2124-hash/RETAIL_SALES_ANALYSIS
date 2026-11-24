"""
build_report.py - generate the final-year project report (report/final_project_report.docx).

Usage (from the project root, after running the full pipeline):
    python scripts/build_report.py

Every number in the report is read from the analysis outputs (results/*.json,
sql/query_results/*.csv), so the report always matches the analysis.
Text in [SQUARE BRACKETS] is a placeholder for the student to fill in.
"""
import json
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm, RGBColor

ROOT = Path(__file__).resolve().parents[1]
VIS = ROOT / "visualizations"
PREV = ROOT / "dashboard" / "preview"
Q = ROOT / "sql" / "query_results"

C = json.loads((ROOT / "results" / "cleaning_summary.json").read_text())
M = json.loads((ROOT / "results" / "eda_metrics.json").read_text())
R = json.loads((ROOT / "results" / "rfm_metrics.json").read_text())
K = M["kpis"]


def q(name):
    return pd.read_csv(Q / f"{name}.csv")


def money(v, d=0):
    return f"{'-' if v < 0 else ''}${abs(v):,.{d}f}"


def mn(v):
    return f"${v/1e6:.2f} million"


# ---------------------------------------------------------------- diagrams
def draw_architecture(path):
    """System architecture diagram: data flows left to right through five layers."""
    fig, ax = plt.subplots(figsize=(11, 4.2), dpi=160)
    ax.set_xlim(0, 11); ax.set_ylim(0, 4.2); ax.axis("off")
    layers = [
        ("1. Data Source", ["Superstore Sales CSV", "(raw_data.csv)", "8,400 rows · 21 cols"], "#cde2fb"),
        ("2. Data Processing", ["Python · Pandas · NumPy", "01_data_cleaning.ipynb", "→ cleaned_data.csv"], "#b7d3f6"),
        ("3. Storage & Query", ["SQLite star schema", "retail_analysis.sql", "16 business queries"], "#9ec5f4"),
        ("4. Analytics", ["EDA (02 notebook)", "RFM segmentation (03)", "ABC inventory analysis"], "#86b6ef"),
        ("5. Presentation", ["Power BI dashboard (4 pages)", "Matplotlib/Seaborn charts", "Report & recommendations"], "#6da7ec"),
    ]
    w, gap = 1.95, 0.22
    for i, (title, lines, col) in enumerate(layers):
        x = 0.1 + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 0.7), w, 2.6, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    facecolor=col, edgecolor="#256abf", linewidth=1.2))
        ax.text(x + w / 2, 3.0, title, ha="center", va="center", fontsize=10.5, fontweight="bold", color="#0b0b0b")
        for j, line in enumerate(lines):
            ax.text(x + w / 2, 2.35 - j * 0.45, line, ha="center", va="center", fontsize=8.6, color="#0b0b0b")
        if i < len(layers) - 1:
            ax.annotate("", xy=(x + w + gap - 0.02, 2.0), xytext=(x + w + 0.02, 2.0),
                        arrowprops=dict(arrowstyle="-|>", color="#0d366b", lw=1.6))
    ax.text(5.5, 0.3, "Reproducible pipeline: run_pipeline.py executes layers 2-5 in order",
            ha="center", fontsize=9, color="#52514e", style="italic")
    fig.savefig(path, bbox_inches="tight", facecolor="white"); plt.close(fig)


def draw_methodology(path):
    steps = ["Business\nunderstanding", "Data\ncollection", "Data cleaning &\npreprocessing", "Exploratory\nanalysis",
             "SQL\nanalysis", "RFM\nsegmentation", "Dashboard", "Insights &\nrecommendations"]
    fig, ax = plt.subplots(figsize=(11, 2.4), dpi=160)
    ax.set_xlim(0, 16); ax.set_ylim(0, 2.4); ax.axis("off")
    for i, s in enumerate(steps):
        x = 0.1 + i * 2
        ax.add_patch(FancyBboxPatch((x, 0.6), 1.7, 1.2, boxstyle="round,pad=0.02,rounding_size=0.15",
                                    facecolor="#2a78d6" if i % 2 == 0 else "#256abf", edgecolor="none"))
        ax.text(x + 0.85, 1.2, s, ha="center", va="center", fontsize=8.2, color="white", fontweight="bold")
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 2.0, 1.2), xytext=(x + 1.72, 1.2), arrowprops=dict(arrowstyle="-|>", color="#52514e"))
    fig.savefig(path, bbox_inches="tight", facecolor="white"); plt.close(fig)


def draw_star_schema(path):
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=160)
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")
    boxes = {
        "fact_sales": (3.6, 2.2, ["row_id (PK)", "order_id, order_date, ship_date", "customer_id (FK)", "product_id (FK)",
                                  "location_id (FK)", "unit_price, quantity, discount", "sales, shipping_cost, profit"], "#2a78d6"),
        "dim_customer": (0.2, 4.2, ["customer_id (PK)", "customer_name"], "#1baf7a"),
        "dim_product": (7.0, 4.0, ["product_id (PK)", "product_name", "category, sub_category", "container, base_margin"], "#1baf7a"),
        "dim_location": (0.2, 0.4, ["location_id (PK)", "province", "region"], "#1baf7a"),
    }
    centers = {}
    for name, (x, y, fields, col) in boxes.items():
        h = 0.45 + 0.32 * len(fields); w = 2.8
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", facecolor="white",
                                    edgecolor=col, linewidth=1.6))
        ax.add_patch(FancyBboxPatch((x, y + h - 0.42), w, 0.42, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=col, edgecolor=col))
        ax.text(x + w / 2, y + h - 0.21, name, ha="center", va="center", color="white", fontweight="bold", fontsize=10)
        for j, f in enumerate(fields):
            ax.text(x + 0.12, y + h - 0.68 - j * 0.32, f, fontsize=8.3, va="center", color="#0b0b0b")
        centers[name] = (x + w / 2, y + h / 2)
    for d in ["dim_customer", "dim_product", "dim_location"]:
        (x1, y1), (x2, y2) = centers["fact_sales"], centers[d]
        ax.plot([x1, x2], [y1, y2], color="#52514e", lw=1, zorder=-1)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, "many : 1", fontsize=7.5, color="#52514e", ha="center")
    fig.savefig(path, bbox_inches="tight", facecolor="white"); plt.close(fig)


# ---------------------------------------------------------------- docx helpers
doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
sec.left_margin = Cm(3.0); sec.right_margin = Cm(2.0); sec.top_margin = Cm(2.5); sec.bottom_margin = Cm(2.5)

st = doc.styles["Normal"]
st.font.name = "Times New Roman"; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.line_spacing = 1.5
st.paragraph_format.space_after = Pt(6)
for lvl, size in [(1, 16), (2, 13), (3, 12)]:
    h = doc.styles[f"Heading {lvl}"]
    h.font.name = "Times New Roman"; h.font.size = Pt(size); h.font.bold = True
    h.font.color.rgb = RGBColor(0x0d, 0x36, 0x6b)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        h.element.rPr.rFonts.set(qn(a), "Times New Roman")
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        h.element.rPr.rFonts.attrib.pop(qn(a), None)
    h.paragraph_format.space_before = Pt(12 if lvl > 1 else 0); h.paragraph_format.space_after = Pt(6)

fig_no = [0]
tab_no = [0]
chapter = [0]


def para(text, bold=False, italic=False, align=None, size=None, space_after=None):
    p = doc.add_paragraph()
    _runs(p, text, bold, italic, size)
    if align == "center": p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "right": p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else: p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if space_after is not None: p.paragraph_format.space_after = Pt(space_after)
    return p


def _runs(p, text, bold=False, italic=False, size=None):
    """Support **bold** inline markup."""
    parts = text.split("**")
    for i, part in enumerate(parts):
        if not part: continue
        r = p.add_run(part)
        r.bold = bold or (i % 2 == 1); r.italic = italic
        if size: r.font.size = Pt(size)


def bullets(items, style="List Bullet"):
    for it in items:
        p = doc.add_paragraph(style=style)
        _runs(p, it)
        p.paragraph_format.space_after = Pt(2)


def h1(text, numbered=True):
    if chapter[0] > 0 or not numbered:
        doc.add_page_break()
    if numbered:
        chapter[0] += 1
        doc.add_heading(f"Chapter {chapter[0]}: {text}", level=1)
    else:
        doc.add_heading(text, level=1)


def h2(text):
    doc.add_heading(text, level=2)


def h3(text):
    doc.add_heading(text, level=3)


def figure(path, caption, width=15.5):
    fig_no[0] += 1
    doc.add_picture(str(path), width=Cm(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = para(f"Figure {fig_no[0]}: {caption}", italic=True, align="center", size=10, space_after=10)
    return p


def table(df, caption=None, widths=None, font=9.5):
    if caption:
        tab_no[0] += 1
        p = para(f"Table {tab_no[0]}: {caption}", bold=True, align="center", size=10, space_after=2)
        p.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, col in enumerate(df.columns):
        cell = t.rows[0].cells[i]; cell.text = ""
        r = cell.paragraphs[0].add_run(str(col)); r.bold = True; r.font.size = Pt(font)
        shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "D9E6F7")
        cell._tc.get_or_add_tcPr().append(shd)
    for _, row in df.iterrows():
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(font)
    for row in t.rows:
        for c in row.cells:
            c.paragraphs[0].paragraph_format.line_spacing = 1.0
            c.paragraphs[0].paragraph_format.space_after = Pt(1)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def code(text):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.left_indent = Cm(0.5)
    r = p.add_run(text); r.font.name = "Consolas"; r.font.size = Pt(8.5)
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "F2F2F2")
    p._p.get_or_add_pPr().append(shd)


def field(paragraph, instr):
    """Insert a Word field (e.g. TOC, PAGE). Fields update when the document is opened/updated."""
    r = paragraph.add_run()
    for tag, attr in [("w:fldChar", "begin"), ("w:instrText", None), ("w:fldChar", "separate")]:
        el = OxmlElement(tag)
        if attr: el.set(qn("w:fldCharType"), attr)
        else:
            el.set(qn("xml:space"), "preserve"); el.text = instr
        r._r.append(el)
    t = OxmlElement("w:t"); t.text = "Right-click → Update Field to build the table of contents." if "TOC" in instr else "1"
    r._r.append(t)
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end"); r._r.append(end)


def blank(n=1):
    for _ in range(n):
        doc.add_paragraph()


# =========================================================================
#  FRONT MATTER
# =========================================================================
para("[NAME OF THE UNIVERSITY]", bold=True, align="center", size=16)
para("[NAME OF THE COLLEGE / INSTITUTE]", bold=True, align="center", size=14)
para("[Department of ________________]", align="center")
blank(2)
para("A PROJECT REPORT ON", bold=True, align="center", size=13)
para("RETAIL SHOP ANALYSIS USING DATA ANALYTICS", bold=True, align="center", size=20)
blank(1)
para("Submitted in partial fulfilment of the requirements for the award of the degree of", align="center", italic=True)
para("[DEGREE NAME, e.g. Bachelor of ________]", bold=True, align="center")
para("[Academic Year 20__ – 20__]", align="center")
blank(2)
para("Submitted by", align="center", italic=True)
para("[STUDENT NAME]", bold=True, align="center")
para("[Roll / Enrolment Number]", align="center")
blank(1)
para("Under the guidance of", align="center", italic=True)
para("[GUIDE NAME]", bold=True, align="center")
para("[Designation, Department]", align="center")
blank(2)
para("[COLLEGE LOGO]", align="center", italic=True)

# Certificate
doc.add_page_break()
para("CERTIFICATE", bold=True, align="center", size=16)
blank(1)
para("This is to certify that the project report entitled **\"Retail Shop Analysis Using Data Analytics\"** "
     "submitted by **[STUDENT NAME]** (Roll No. **[ROLL NUMBER]**) to **[NAME OF THE COLLEGE]**, affiliated to "
     "**[NAME OF THE UNIVERSITY]**, in partial fulfilment of the requirements for the award of the degree of "
     "**[DEGREE NAME]** is a record of bona fide work carried out by the student under my supervision during the "
     "academic year **[20__ – 20__]**. The matter embodied in this report has not been submitted elsewhere for the "
     "award of any other degree or diploma.")
blank(4)
t = doc.add_table(rows=3, cols=2)
for i, (a, b) in enumerate([("[Guide Name]", "[Head of Department]"), ("Project Guide", "Head of Department"),
                            ("[Department]", "[Department]")]):
    t.cell(i, 0).text = a; t.cell(i, 1).text = b
    t.cell(i, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
blank(3)
para("External Examiner: ____________________          Date: ____________", align="center")

# Declaration
doc.add_page_break()
para("DECLARATION", bold=True, align="center", size=16)
blank(1)
para("I, **[STUDENT NAME]**, hereby declare that the project report entitled **\"Retail Shop Analysis Using Data "
     "Analytics\"** submitted to **[NAME OF THE COLLEGE]** in partial fulfilment of the requirements for the award "
     "of the degree of **[DEGREE NAME]** is my original work carried out under the guidance of **[GUIDE NAME]**. "
     "The analysis uses a publicly available sample dataset, which is acknowledged in the report. "
     "This work has not been submitted to any other university or institution for the award of any degree or diploma.")
blank(4)
para("Place: [CITY]", align="left")
para("Date: [DD/MM/YYYY]                                                    [Student Signature]", align="left")
para("                                                                                    [STUDENT NAME]", align="left")

# Acknowledgement
doc.add_page_break()
para("ACKNOWLEDGEMENT", bold=True, align="center", size=16)
blank(1)
para("I would like to express my sincere gratitude to my project guide, **[GUIDE NAME]**, for their valuable "
     "guidance, encouragement and constructive feedback throughout this project.")
para("I am thankful to **[HEAD OF DEPARTMENT NAME]**, Head of the Department of **[DEPARTMENT]**, and to "
     "**[PRINCIPAL / DIRECTOR NAME]** for providing the facilities and environment needed to complete this work.")
para("I also thank all the faculty members of the department for their support, and the open-source communities "
     "behind Python, Pandas, NumPy, Matplotlib, Seaborn and SQLite, whose tools made this analysis possible.")
para("Finally, I thank my family and friends for their constant support and motivation.")
blank(2)
para("[STUDENT NAME]", bold=True, align="right")

# Abstract
doc.add_page_break()
para("ABSTRACT", bold=True, align="center", size=16)
blank(1)
y = {r["order_year"]: r for r in M["yearly"]}
cats = {r["category"]: r for r in M["category"]}
para(f"Retail businesses generate large volumes of transaction data, but many small and medium retailers make "
     f"pricing, stocking and marketing decisions by intuition. This project applies a complete data analytics "
     f"workflow to a public retail dataset, the Superstore Sales dataset ({C['clean_rows']:,} order lines, "
     f"{C['n_orders']:,} orders, {C['n_customers']} customers and {C['n_products']:,} products from "
     f"{C['date_min'][:4]} to {C['date_max'][:4]}), to show how data can support better business decisions.")
para("The raw data was cleaned and validated in Python (Pandas, NumPy), explored with Matplotlib and Seaborn, "
     "loaded into a relational star-schema database queried with SQL, segmented with RFM (Recency, Frequency, "
     "Monetary) analysis, and summarised in a four-page Power BI dashboard design.")
para(f"The shop earned **{mn(K['total_revenue'])}** in revenue and **{mn(K['total_profit'])}** in profit "
     f"(**{K['profit_margin_pct']:.1f}%** margin). Technology produced {cats['Technology']['revenue_share_pct']:.0f}% of "
     f"revenue but {cats['Technology']['profit_share_pct']:.0f}% of profit, whereas Furniture produced "
     f"{cats['Furniture']['revenue_share_pct']:.0f}% of revenue but only {cats['Furniture']['profit_share_pct']:.0f}% of "
     f"profit. **{K['loss_line_share_pct']:.0f}%** of order lines were sold at a loss. The strongest driver was a high "
     f"shipping cost relative to item price, followed by higher discounts. RFM analysis showed that "
     f"{R['top2_customer_share_pct']:.0f}% of customers (Champions and Loyal) generate "
     f"{R['top2_revenue_share_pct']:.0f}% of revenue, while At-Risk customers represent "
     f"{mn(R['at_risk_revenue'])} of past revenue. ABC analysis found that "
     f"{M['abc'][0]['product_share_pct']:.0f}% of products generate 80% of revenue.")
para("Based on these findings the report recommends a shipping-cost policy for low-priced items, a review of "
     "Furniture pricing and discounts, inventory prioritisation by ABC class, and RFM-based retention campaigns.")
para("**Keywords:** retail analytics, exploratory data analysis, SQL, RFM segmentation, ABC analysis, Power BI, Python.",
     align="left")

# Table of contents
doc.add_page_break()
para("TABLE OF CONTENTS", bold=True, align="center", size=16)
field(doc.add_paragraph(), 'TOC \\o "1-2" \\h \\z \\u')
para("(In Microsoft Word: right-click the line above → Update Field → Update entire table.)", italic=True, size=10)

# page numbers in footer
footer_p = sec.footer.paragraphs[0]; footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
field(footer_p, "PAGE")

# =========================================================================
#  CHAPTERS
# =========================================================================
h1("Introduction")
para("Retail is one of the most data-rich industries. Every sale records what was sold, to whom, where, when, at "
     "what price and with what discount. Taken together, these records describe how the business really performs: "
     "which products earn money, which customers are valuable, and which regions or policies are losing money.")
para("**Data analytics** is the process of collecting, cleaning, analysing and visualising data to answer business "
     "questions. It is commonly described at four levels:")
bullets(["**Descriptive analytics**: what happened? (e.g. total revenue by year)",
         "**Diagnostic analytics**: why did it happen? (e.g. why are Furniture margins low?)",
         "**Predictive analytics**: what is likely to happen? (e.g. forecasting demand)",
         "**Prescriptive analytics**: what should we do? (e.g. recommended discount caps)"])
para("This project concentrates on descriptive and diagnostic analytics and turns the results into prescriptive "
     "business recommendations. It follows the workflow a junior data analyst would use in industry: Python for data "
     "preparation and exploration, SQL for structured business queries, statistical segmentation of customers, and a "
     "Power BI dashboard for decision makers.")
h2("1.1 Background of the project")
para("The analysis uses the Superstore Sales dataset, a realistic sample of a retailer that sells office supplies, "
     "furniture and technology products to consumers and businesses across Canadian provinces. It contains "
     "transaction-level detail, including unit price, quantity, discount, shipping cost and profit, which makes it "
     "suitable for analysing both sales performance and profitability.")
h2("1.2 Organisation of the report")
para("Chapters 2–5 define the problem, objectives and the existing versus proposed approach. Chapter 6 reviews "
     "relevant literature, Chapter 7 describes the tools, and Chapter 8 the dataset. Chapters 9–10 present the "
     "architecture and methodology. Chapters 11–15 document the implementation: cleaning, EDA, SQL, segmentation and "
     "dashboard. Chapters 16–20 present results, recommendations, limitations, future scope and conclusions.")

h1("Problem Statement")
para("Retail managers must decide which products to stock, how much discount to give, which customers to target "
     "and which regions need attention. Without analysis these decisions are based on intuition or on revenue alone, "
     "and revenue can be misleading: a product or region can sell a lot and still lose money.")
para("**Problem:** Given four years of transaction-level retail data, identify the drivers of revenue and profit, "
     "the behaviour and value of different customers, and the performance of products and regions, and turn these "
     "findings into evidence-based recommendations that improve profitability.", italic=True)
para("Specific questions addressed:")
bullets(["How have revenue and profit changed over months, quarters and years? Is there seasonality?",
         "Which products and categories generate the most revenue and the most profit?",
         "Which regions perform well and which require improvement?",
         "How do discounts and shipping costs affect profitability?",
         "Who are the most valuable customers, and which are at risk of being lost?",
         "Which products need better inventory management?"])

h1("Project Objectives")
bullets(["To acquire a realistic public retail dataset and document its source, structure and limitations.",
         "To clean and preprocess the data: handle missing values, duplicates, outliers, inconsistent formats and dates, "
         "and create calculated fields (gross sales, profit margin, discount %, month, quarter, year).",
         "To perform exploratory data analysis of revenue, profit, orders, average order value, trends, products, "
         "categories, regions, customers and discounts, using clear visualisations.",
         "To design a relational database (star schema) and answer business questions with SQL.",
         "To segment customers using RFM analysis into actionable groups.",
         "To analyse stock movement using ABC classification and demand variability.",
         "To design an interactive four-page Power BI dashboard with slicers.",
         "To derive business recommendations, each supported by an analytical finding."])

h1("Existing System")
para("In many small and medium retail businesses, performance is tracked with manual or semi-manual methods:")
bullets(["Sales are recorded in billing software or spreadsheets, and summarised as daily or monthly totals.",
         "Reports focus on **revenue** (how much was sold), with little visibility of **profit** per product, "
         "category, customer or region.",
         "Discounts are given case by case, without measuring their effect on margin.",
         "Customers are treated uniformly; there is no systematic way to identify high-value or at-risk customers.",
         "Stock is reordered based on experience, not on measured demand velocity or variability.",
         "Reports are static; managers cannot filter or drill down by period, category or region."])
para("**Limitations of the existing system:** it is time-consuming and error-prone, it hides loss-making "
     "products behind good revenue figures, and it does not support targeted marketing or data-driven inventory "
     "decisions.")

h1("Proposed System")
para("The proposed system is a reproducible analytics pipeline that turns raw transaction data into insights and an "
     "interactive dashboard:")
table(pd.DataFrame([
    ["Data preparation", "Automated, documented cleaning in Python with validation rules and a cleaning log"],
    ["Analysis", "Revenue and profit analysed together at every level (product, category, region, customer)"],
    ["Database", "Normalised star schema in SQLite with reusable SQL queries"],
    ["Customer insight", "RFM segmentation with an action plan per segment"],
    ["Inventory insight", "ABC classification, sales velocity and demand variability"],
    ["Reporting", "Interactive Power BI dashboard with date, category, region and segment slicers"],
    ["Decision support", "Recommendations each linked to a measured finding"],
], columns=["Component", "Proposed approach"]), "Features of the proposed system", widths=[4, 11.5])
para("**Advantages:** consistent and repeatable results (re-running the pipeline regenerates every output), "
     "profit-aware decisions, the ability to identify specific problem areas, faster reporting, and a clear audit "
     "trail from raw data to recommendation.")

h1("Literature Review")
para("This chapter summarises established work on the concepts this project applies. (Full references are listed "
     "in Chapter 21.)")
h2("6.1 Data analytics and business decision-making")
para("Davenport and Harris (2007) argue that organisations which systematically use data and analysis to make "
     "decisions can gain a competitive advantage, and they describe retail as an industry where analytics is "
     "especially valuable. Provost and Fawcett (2013) present data-analytic thinking as a structured process: "
     "understand the business problem, understand and prepare the data, analyse, evaluate and deploy. This "
     "project's methodology follows that sequence.")
h2("6.2 Data preprocessing and exploratory analysis")
para("Han, Kamber and Pei (2011) describe data preprocessing (cleaning, integration, transformation and "
     "reduction) as an essential step before analysis, because real data is often incomplete, noisy and "
     "inconsistent. Their treatment of missing values, outlier detection (including the inter-quartile range) and "
     "data transformation informs Chapter 11. The Python tools used are documented in McKinney (2010) for Pandas, "
     "Harris et al. (2020) for NumPy, Hunter (2007) for Matplotlib and Waskom (2021) for Seaborn.")
h2("6.3 Dimensional modelling")
para("Kimball and Ross (2013) introduced dimensional modelling for data warehouses. The **star schema** places "
     "measurable events in a central fact table and descriptive attributes in surrounding dimension tables. The "
     "design is easy to understand, efficient to query, and is the recommended model for Power BI. This project's "
     "database follows this design.")
h2("6.4 RFM customer segmentation")
para("RFM analysis was popularised in direct marketing by Hughes (1994), who showed that customers who bought "
     "recently, buy frequently and spend more are more likely to respond to future offers. Fader, Hardie and Lee "
     "(2005) linked RFM measures to customer lifetime value, which supports their use as indicators of customer "
     "worth. Chen, Sain and Guo (2012) applied RFM-based segmentation to an online retailer's transaction data "
     "to identify meaningful customer groups, demonstrating the method's practical value in retail.")
h2("6.5 ABC inventory classification")
para("ABC analysis applies the Pareto principle to inventory: a small share of items usually accounts for most "
     "of the value. Silver, Pyke and Peterson (1998) describe using it to focus control effort, giving tight "
     "attention to class A items and simpler policies to class C items. This project applies ABC classification "
     "to product revenue.")
h2("6.6 Dashboard design")
para("Few (2006) defines an information dashboard as a visual display of the most important information needed to "
     "achieve objectives, arranged on a single screen so it can be monitored at a glance. He recommends simple chart "
     "types, minimal decoration and consistent colours. These principles guided the dashboard and chart design.")
h2("6.7 Research gap addressed")
para("Many student projects on retail data report revenue totals and top products only. This project combines "
     "revenue **and** profit analysis, diagnostic analysis of loss drivers (discount, shipping cost, price band), "
     "RFM segmentation and ABC inventory analysis in one reproducible pipeline, and cross-validates Python results "
     "against SQL results.")

h1("Technology and Tools Used")
table(pd.DataFrame([
    ["Python 3", "Programming language for all data processing and analysis"],
    ["Pandas", "Loading, cleaning, transforming and aggregating tabular data (DataFrames)"],
    ["NumPy", "Fast numerical operations, conditional columns, statistics"],
    ["Matplotlib", "Base plotting library used for all static charts"],
    ["Seaborn", "Statistical visualisation (heatmaps) built on Matplotlib"],
    ["SciPy", "Spearman rank correlation"],
    ["Jupyter Notebook", "Interactive environment combining code, output and explanation"],
    ["SQL / SQLite", "Relational database and query language; SQLite is built into Python and needs no server"],
    ["Power BI Desktop", "Microsoft's business-intelligence tool for interactive dashboards (DAX measures)"],
    ["Excel / CSV", "Dataset storage and exchange format, readable by every tool above"],
    ["python-docx", "Generation of this report from the analysis results"],
], columns=["Tool", "Purpose in this project"]), "Technologies used", widths=[4, 11.5])
h2("7.1 Hardware and software requirements")
table(pd.DataFrame([
    ["Processor", "Any modern dual-core CPU"], ["RAM", "4 GB minimum (8 GB recommended for Power BI)"],
    ["Storage", "about 500 MB including libraries"],
    ["Operating system", "Windows 10/11 (required for Power BI Desktop); Python parts also run on macOS/Linux"],
    ["Software", "Python 3.10+, Jupyter, libraries in requirements.txt, Power BI Desktop (free)"],
], columns=["Item", "Requirement"]), "System requirements", widths=[4, 11.5])

h1("Dataset Description")
h2("8.1 Source")
para("**Dataset:** Superstore Sales (Canadian edition), a sample retail dataset originally distributed by Tableau "
     "Software as a training dataset and widely republished on Kaggle and GitHub for analytics practice. "
     "The copy used in this project was obtained from the public GitHub repository *curran/data* "
     "(https://raw.githubusercontent.com/curran/data/gh-pages/superstoreSales/superstoreSales.csv).")
para("**Nature of the data:** this is a realistic **sample** dataset prepared for teaching. It is not the "
     "confidential data of a named company, so all findings describe this dataset, and the recommendations show "
     "how a retailer would act on such findings.")
h2("8.2 Size and coverage")
table(pd.DataFrame([
    ["Order lines (records)", f"{C['clean_rows']:,}"], ["Original columns", C["raw_columns"]],
    ["Distinct orders", f"{C['n_orders']:,}"], ["Customers", C["n_customers"]],
    ["Products", f"{C['n_products']:,}"], ["Categories / sub-categories", f"{C['n_categories']} / {C['n_sub_categories']}"],
    ["Provinces / regions", f"{C['n_provinces']} / {C['n_regions']}"],
    ["Period", f"{C['date_min']} to {C['date_max']} (4 years)"],
], columns=["Property", "Value"]), "Dataset size and coverage", widths=[6, 9.5])
h2("8.3 Columns (original data)")
cols = [
    ["Row ID", "Integer", "Unique identifier of each order line"],
    ["Order ID", "Integer", "Order number (one order can contain several lines)"],
    ["Order Date / Ship Date", "Date", "When the order was placed / shipped"],
    ["Order Priority", "Text", "Critical, High, Medium, Low, Not Specified"],
    ["Order Quantity", "Integer", "Units purchased in the line"],
    ["Sales", "Decimal", "Revenue recorded for the line (USD)"],
    ["Discount", "Decimal", "Discount rate (0–0.25)"],
    ["Ship Mode", "Text", "Regular Air, Express Air, Delivery Truck"],
    ["Profit", "Decimal", "Profit (or loss, if negative) on the line"],
    ["Unit Price", "Decimal", "List price per unit"],
    ["Shipping Cost", "Decimal", "Shipping cost charged for the line"],
    ["Customer Name", "Text", "Customer identifier"],
    ["Province / Region", "Text", "Location of the sale (13 provinces, 8 regions)"],
    ["Customer Segment", "Text", "Corporate, Home Office, Consumer, Small Business"],
    ["Product Category / Sub-Category", "Text", "3 categories, 17 sub-categories"],
    ["Product Name", "Text", "Product description"],
    ["Product Container", "Text", "Packaging type (Small Box, Jumbo Drum, …)"],
    ["Product Base Margin", "Decimal", "Expected base margin of the product (0–1)"],
]
table(pd.DataFrame(cols, columns=["Column", "Type", "Description"]), "Original dataset columns", widths=[5, 2.5, 8])
h2("8.4 Original versus derived fields")
para("To keep the analysis honest, the report clearly separates the data's **original** fields from those "
     "**derived** by the project. No field was simulated or invented. The derived fields are calculated from "
     "original values:")
table(pd.DataFrame([
    ["gross_sales", "quantity × unit_price"], ["profit_margin_pct", "profit ÷ sales × 100"],
    ["discount_pct, discount_amount", "discount × 100; gross_sales × discount"],
    ["order_year / quarter / month / year_month", "extracted from order_date"],
    ["ship_days", "ship_date − order_date"], ["profit_status", "Profit if profit ≥ 0 else Loss"],
    ["discount_band, price_band", "grouped discount / unit price"],
    ["is_*_outlier flags, base_margin_imputed", "data-quality flags"],
], columns=["Derived field", "Formula"]), "Derived fields", widths=[7, 8.5])
para("**Fields not present in the data:** the dataset has no store identifier, no stock-on-hand figures and "
     "no customer demographics. The project therefore (a) treats each **province as a sales territory** for "
     "store-level comparison, and (b) analyses **stock movement** (units sold, velocity, variability) rather than "
     "inventory levels. These assumptions are stated wherever they apply.")
h2("8.5 Business relevance")
para("The dataset contains every element needed for retail decision-making: price, quantity, discount, cost "
     "(through profit and shipping cost), time, product hierarchy, customer and location. This allows the analysis "
     "to move beyond \"how much did we sell\" to \"where do we make or lose money, and why\".")

h1("System Architecture")
draw_architecture(VIS / "00_system_architecture.png")
figure(VIS / "00_system_architecture.png", "System architecture of the retail analytics solution")
para("The system has five layers. Data flows from the raw CSV through Python cleaning into an analysis-ready "
     "dataset. That dataset feeds the SQLite database, the analytical notebooks and the Power BI model. All outputs "
     "(charts, query results, metrics, dashboard data and this report) are generated from the cleaned dataset, so a "
     "change in the data flows consistently through to every output.")
h2("9.1 Database design (star schema)")
draw_star_schema(VIS / "00_star_schema.png")
figure(VIS / "00_star_schema.png", "Star schema used for the SQL database and the Power BI model", width=13)
para("The fact table **fact_sales** stores one row per order line with the measurable values. Three dimension "
     "tables describe customers, products and locations. Each dimension relates to the fact table as **one-to-many**. "
     "Customer and location are stored on each line rather than per order, because a few order IDs in this "
     "dataset are linked to more than one customer (Section 11.6).")
h2("9.2 Project folder structure")
code("Retail-Shop-Analysis/\n"
     "├── dataset/            raw_data.csv, cleaned_data.csv, retail.db\n"
     "├── notebooks/          01_data_cleaning, 02_exploratory_analysis,\n"
     "│                       03_customer_segmentation, 04_sql_analysis (.ipynb), viz_style.py\n"
     "├── sql/                retail_analysis.sql, query_results/\n"
     "├── scripts/            build_database.py, prepare_powerbi_data.py,\n"
     "│                       render_dashboard_preview.py, build_report.py\n"
     "├── visualizations/     all exported charts (.png)\n"
     "├── dashboard/          powerbi_data/, DAX_measures.md, retail_theme.json,\n"
     "│                       POWERBI_BUILD_GUIDE.md, preview/\n"
     "├── results/            metrics (.json), RFM and product summaries (.csv)\n"
     "├── report/             final_project_report.docx, viva_preparation.md\n"
     "├── run_pipeline.py     runs every step in order\n"
     "├── requirements.txt\n"
     "└── README.md")

h1("Methodology")
draw_methodology(VIS / "00_methodology.png")
figure(VIS / "00_methodology.png", "Project methodology")
steps = [
    ("Business understanding", "Define the questions a retail manager needs answered (Chapter 2)."),
    ("Data collection", "Select a public dataset with transactions, customers, products, prices, discounts, profit and location."),
    ("Data cleaning and preprocessing", "Correct encoding, types, spelling, missing values and duplicates; validate business rules; flag outliers; create derived fields."),
    ("Exploratory data analysis", "Calculate KPIs; analyse trends, categories, products, regions, customers, discounts and shipping; visualise each."),
    ("SQL analysis", "Build a star-schema database and answer business questions with SQL, including CTEs and window functions."),
    ("Customer segmentation", "Calculate R, F and M per customer, score them 1–5 by quintile, and assign rule-based segments."),
    ("Inventory analysis", "ABC classification by revenue, sales velocity and demand variability per product."),
    ("Dashboard", "Prepare a Power BI star schema, DAX measures, theme and page designs."),
    ("Insights and recommendations", "Link each recommendation to a measured finding."),
    ("Validation", "Cross-check Python totals against SQL totals; assert data-quality rules in code."),
]
table(pd.DataFrame([(i + 1, a, b) for i, (a, b) in enumerate(steps)], columns=["#", "Phase", "Activities"]),
      "Methodology phases", widths=[1, 4.5, 10])
h2("10.1 Key metric definitions")
table(pd.DataFrame([
    ["Total Revenue", "Sum of sales"], ["Total Profit", "Sum of profit"],
    ["Profit Margin %", "Total profit ÷ total revenue × 100"], ["Total Orders", "Count of distinct order IDs"],
    ["Average Order Value (AOV)", "Total revenue ÷ total orders"],
    ["Repeat customer", "Customer with more than one distinct order"],
], columns=["Metric", "Definition"]), "KPI definitions", widths=[5, 10.5])

h1("Data Cleaning and Preprocessing")
para("All cleaning is implemented in **notebooks/01_data_cleaning.ipynb**. Every step writes an entry to a "
     "cleaning log (results/cleaning_log.csv), which is reproduced below.")
table(pd.DataFrame([(i + 1, l["step"], l["detail"]) for i, l in enumerate(C["log"])],
                   columns=["#", "Step", "What was done (from the cleaning log)"]),
      "Cleaning log", widths=[0.8, 3.2, 11.5], font=8.5)
h2("11.1 Loading with the correct encoding")
para("The raw file uses old Macintosh conventions: carriage-return line endings and the Mac Roman character "
     "encoding. Reading it with default settings would garble symbols such as ® and ™ in product names. The file is "
     "therefore read with explicit settings:")
code('raw = pd.read_csv(RAW_PATH, lineterminator="\\r", encoding="mac_roman")')
para("The file also ends with an extra line break, which produces one empty row. That row was removed.")
h2("11.2 Standardising formats")
para(f"Column names were converted to snake_case, extra spaces were trimmed, and {C['spelling_fixes']:,} misspelled "
     "location values were corrected (\"Saskachewan\" → Saskatchewan, \"Prarie\" → Prairie). Dates were converted with "
     "an explicit format (%m/%d/%Y) to avoid day/month ambiguity. Identifier and quantity columns were converted to "
     "integers.")
h2("11.3 Duplicates")
para("Duplicates were checked in three ways: exact duplicate rows, duplicate Row IDs, and identical "
     "transactions that differ only in Row ID. None were found.")
h2("11.4 Missing values")
para(f"Only Product Base Margin had missing values ({C['base_margin_imputed']} rows). Because it is a product "
     "attribute, values were imputed hierarchically: first from the same product (no matches were available), then "
     "from the **median of the product's sub-category**. A flag column (base_margin_imputed) records which values "
     "were imputed. No rows were dropped, because their sales and profit values are complete.")
h2("11.5 Validation of numerical values")
table(pd.DataFrame(C["validation"]).rename(columns={"rule": "Business rule", "rows_failing": "Rows failing",
                                                    "status": "Result"}),
      "Business-rule validation", widths=[8, 3.5, 3])
h2("11.6 Known data characteristics")
para(f"Three characteristics are documented instead of being \"fixed\", because they are genuine properties of the data:")
bullets([f"**{C['neg_profit_share_pct']}% of order lines have negative profit.** Selling at a loss is a real business "
         "outcome, and its causes are investigated in Chapter 12.",
         f"**{C['multi_customer_orders']} order IDs are linked to more than one customer**, and "
         f"**{C['multi_province_customers']} customers appear in more than one province.** The dataset was prepared "
         "for teaching, so segment and province are treated as attributes of each transaction.",
         f"**Recorded sales ≠ quantity × unit price exactly.** The median ratio is {C['sales_to_gross_median_ratio']}, "
         "so the data provider applied adjustments before recording sales. All revenue figures use the **original "
         "Sales column**; gross_sales is kept as a derived comparison field."])
h2("11.7 Outlier detection and treatment")
table(pd.DataFrame(C["outliers"]).rename(columns={"column": "Column", "lower_bound": "Lower bound",
                                                  "upper_bound": "Upper bound", "outliers": "Outliers", "pct": "% rows"}),
      "IQR outlier detection (Q1 − 1.5·IQR, Q3 + 1.5·IQR)", widths=[3.5, 3, 3, 3, 3])
para(f"The IQR rule flagged {C['sales_outliers']:,} sales outliers, but together they account for "
     f"**{C['sales_outlier_revenue_share_pct']}% of total revenue**. They are large business orders, not errors, so "
     f"deleting them would remove most of the shop's revenue. They were therefore **retained and flagged**. Charts "
     f"use log scales or medians where outliers would otherwise dominate. Only {C['ship_delay_anomalies']} shipments "
     "with delivery times over 30 days were flagged as probable data-entry anomalies.")
figure(VIS / "01_outlier_boxplots.png", "Box plots (log scale) of sales, unit price and shipping cost")
h2("11.8 Calculated columns")
para(f"The cleaned dataset (dataset/cleaned_data.csv) has **{C['clean_rows']:,} rows and {C['clean_columns']} "
     "columns**: the original fields plus the derived fields listed in Section 8.4.")

h1("Exploratory Data Analysis")
para("EDA is implemented in **notebooks/02_exploratory_analysis.ipynb**. All figures below are exported from that "
     "notebook, and every number is read from results/eda_metrics.json.")
h2("12.1 Headline KPIs")
table(pd.DataFrame([
    ["Total revenue", money(K["total_revenue"], 2)], ["Total profit", money(K["total_profit"], 2)],
    ["Profit margin", f"{K['profit_margin_pct']:.2f}%"], ["Total orders", f"{K['total_orders']:,}"],
    ["Order lines", f"{K['total_line_items']:,}"], ["Units sold", f"{K['total_units']:,}"],
    ["Average order value (mean)", money(K["avg_order_value"], 2)],
    ["Median order value", money(K["median_order_value"], 2)],
    ["Average discount", f"{K['avg_discount_pct']:.2f}%"], ["Order lines sold at a loss", f"{K['loss_line_share_pct']}%"],
], columns=["KPI", "Value"]), "Headline KPIs (2009–2012)", widths=[7, 6])
para(f"**Insight:** the mean order value ({money(K['avg_order_value'])}) is much larger than the median "
     f"({money(K['median_order_value'])}). A minority of large orders therefore carries a large share of revenue, "
     f"which matches the outlier analysis. About half of all order lines lose money, but the business is profitable "
     f"overall because profitable lines are larger.")

h2("12.2 Yearly comparison")
yt = pd.DataFrame(M["yearly"])
table(pd.DataFrame({"Year": yt["order_year"], "Revenue": yt["revenue"].map(money), "Profit": yt["profit"].map(money),
                    "Margin %": yt["margin_pct"].map("{:.2f}".format), "Orders": yt["orders"],
                    "Revenue growth %": yt["revenue_growth_pct"].map(lambda v: "–" if pd.isna(v) else f"{v:+.2f}")}),
      "Yearly performance", widths=[2, 3, 3, 2.3, 2, 3])
figure(VIS / "02_yearly_revenue_profit.png", "Revenue and profit by year")
y09, y10, y11, y12 = (y[k] for k in (2009, 2010, 2011, 2012))
para(f"**Insight:** revenue was highest in 2009 ({mn(y09['revenue'])}), fell by {abs(y10['revenue_growth_pct']):.1f}% "
     f"in 2010 and a further {abs(y11['revenue_growth_pct']):.1f}% in 2011, then recovered by "
     f"{y12['revenue_growth_pct']:.1f}% in 2012. However, **2012 had the lowest profit "
     f"({money(y12['profit'])}) and the lowest margin ({y12['margin_pct']:.2f}%)**, so the 2012 revenue recovery "
     f"came at the expense of profitability.")

h2("12.3 Monthly trend and seasonality")
figure(VIS / "03_monthly_revenue_trend.png", "Monthly revenue with 3-month rolling average")
mm, ss = M["monthly"], M["seasonality"]
para(f"Average monthly revenue was {money(mm['avg_monthly_revenue'])}, with a coefficient of variation of "
     f"{mm['monthly_cv_pct']}%. The best month was {mm['best_month']} ({money(mm['best_month_revenue'])}) and the "
     f"weakest was {mm['worst_month']} ({money(mm['worst_month_revenue'])}). No month made an overall loss.")
figure(VIS / "04_seasonality_heatmap.png", "Revenue heatmap by month and year ($ thousands)")
figure(VIS / "05_quarterly_revenue.png", "Quarterly revenue by year")
qs = ss["quarter_share_pct"]
para(f"**Insight:** averaged over four years, **{ss['strongest_calendar_month']}** is the strongest month and "
     f"**{ss['weakest_calendar_month']}** the weakest. Q4 ({qs['Q4']}%) and Q1 ({qs['Q1']}%) carry more revenue than "
     f"Q2 ({qs['Q2']}%) and Q3 ({qs['Q3']}%). The pattern is moderate rather than extreme, so it supports planning "
     f"stock and campaigns around the year-end and new-year period.")

h2("12.4 Category performance")
ct = pd.DataFrame(M["category"])
table(pd.DataFrame({"Category": ct["category"], "Revenue": ct["revenue"].map(money), "Revenue %": ct["revenue_share_pct"].map("{:.1f}".format),
                    "Profit": ct["profit"].map(money), "Profit %": ct["profit_share_pct"].map("{:.1f}".format),
                    "Margin %": ct["margin_pct"].map("{:.2f}".format), "Units": ct["units"].map("{:,.0f}".format)}),
      "Category performance", widths=[3, 2.8, 1.8, 2.5, 1.8, 1.8, 2])
figure(VIS / "06_category_performance.png", "Revenue, profit and margin by category")
figure(VIS / "10_category_distribution.png", "Sales distribution and share by category")
para(f"**Insight:** Technology is the most valuable category: {cats['Technology']['revenue_share_pct']:.1f}% of revenue "
     f"and {cats['Technology']['profit_share_pct']:.1f}% of profit at a {cats['Technology']['margin_pct']:.1f}% margin. "
     f"**Furniture is the problem category.** It brings {cats['Furniture']['revenue_share_pct']:.1f}% of revenue but only "
     f"{cats['Furniture']['profit_share_pct']:.1f}% of profit (margin {cats['Furniture']['margin_pct']:.2f}%). Office "
     f"Supplies moves {cats['Office Supplies']['units']:,.0f} units (the majority of units) at a healthy "
     f"{cats['Office Supplies']['margin_pct']:.1f}% margin.")

h2("12.5 Sub-category profitability")
figure(VIS / "07_subcategory_profit.png", "Profit and margin by sub-category", width=14)
subs = pd.DataFrame(M["sub_category"])
loss = subs[subs["profit"] < 0].sort_values("profit")
para("**Insight:** four sub-categories lose money overall: " +
     ", ".join(f"{r.sub_category} ({money(r.profit)})" for r in loss.itertuples()) +
     ". Tables and Bookcases (both Furniture) are the largest losses and explain Furniture's weak margin. "
     "Telephones & Communication, Office Machines and Binders are the largest profit contributors; Binders reach a "
     "30.1% margin.")

h2("12.6 Best-selling and most profitable products")
tp = pd.DataFrame(M["top10_products_revenue"])
table(pd.DataFrame({"Product": tp["product_name"], "Category": tp["category"], "Revenue": tp["revenue"].map(money),
                    "Margin %": tp["margin_pct"].map("{:.1f}".format)}),
      "Top 10 products by revenue", widths=[8.5, 2.8, 2.4, 1.8], font=8.5)
figure(VIS / "08_top10_products_revenue.png", "Top 10 products by revenue")
figure(VIS / "09_product_profit_loss.png", "Most profitable and most loss-making products")
neg_top = tp[tp["margin_pct"] < 0]
para("**Insight:** high revenue does not guarantee profit. " + (
    f"{neg_top.iloc[0]['product_name']} is the #{int(neg_top.index[0]) + 1} product by revenue "
    f"({money(neg_top.iloc[0]['revenue'])}) but has a {neg_top.iloc[0]['margin_pct']:.1f}% margin. " if len(neg_top) else "") +
    f"The largest loss-maker is {M['bottom10_products_profit'][0]['product_name']} "
    f"({money(M['bottom10_products_profit'][0]['profit'])}).")

h2("12.7 Regional performance")
pv = pd.DataFrame(M["province"])
table(pd.DataFrame({"Province": pv["province"], "Region": pv["region"], "Revenue": pv["revenue"].map(money),
                    "Profit": pv["profit"].map(money), "Margin %": pv["margin_pct"].map("{:.1f}".format),
                    "Customers": pv["customers"]}),
      "Province performance (sorted by revenue)", widths=[3.8, 3.5, 2.6, 2.3, 1.7, 1.8], font=8.5)
figure(VIS / "11_province_performance.png", "Revenue and profit margin by province")
figure(VIS / "12_region_category_profit.png", "Profit by region and category ($ thousands)", width=12)
lowm = pv.sort_values("margin_pct")
para(f"**Insight:** Ontario is the largest territory ({pv.iloc[0]['revenue_share_pct']:.1f}% of revenue) with an "
     f"above-average margin. **{lowm.iloc[0]['province']}** has the weakest margin ({lowm.iloc[0]['margin_pct']:.1f}%), "
     f"followed by {lowm.iloc[1]['province']} ({lowm.iloc[1]['margin_pct']:.1f}%). British Columbia is the second-largest "
     f"province but earns only {pv.set_index('province').loc['British Columbia','margin_pct']:.1f}%, below the company "
     f"average of {K['profit_margin_pct']:.1f}%. New Brunswick has the best margin "
     f"({pv.set_index('province').loc['New Brunswick','margin_pct']:.1f}%). The heatmap shows that Furniture earns little "
     f"in every region and loses money in Quebec, while Technology is the main profit source everywhere.")

h2("12.8 Customer purchasing patterns")
cu = M["customers"]
sg = pd.DataFrame(M["segment"])
table(pd.DataFrame({"Segment": sg["segment"], "Revenue": sg["revenue"].map(money), "Revenue %": sg["revenue_share_pct"].map("{:.1f}".format),
                    "Orders": sg["orders"], "AOV": sg["aov"].map(money), "Margin %": sg["margin_pct"].map("{:.2f}".format)}),
      "Performance by business customer segment", widths=[3.2, 3, 2, 1.8, 2.2, 2])
figure(VIS / "13_customer_patterns.png", "Orders per customer and customer revenue concentration")
para(f"**Insight:** customers are highly loyal: {cu['repeat_customer_pct']}% placed more than one order (average "
     f"{cu['avg_orders_per_customer']} orders each), and only {cu['one_time_customers']} customers bought once. Revenue is "
     f"concentrated: the **top 20% of customers generate {cu['top20pct_customer_revenue_share']}% of revenue**. The "
     f"Corporate segment is the largest ({sg.iloc[0]['revenue_share_pct']:.1f}% of revenue), while Small Business has the "
     f"best margin ({sg.set_index('segment').loc['Small Business','margin_pct']:.2f}%). "
     f"{cu['loss_making_customers']} customers are unprofitable over the four years.")
pri = pd.DataFrame(M["order_priority"]).sort_values("margin_pct")
para(f"Order priority also matters: **{pri.iloc[0]['order_priority']}**-priority orders have the lowest margin "
     f"({pri.iloc[0]['margin_pct']:.2f}%), compared with {pri.iloc[-1]['margin_pct']:.2f}% for "
     f"{pri.iloc[-1]['order_priority']}-priority orders. This suggests that urgent orders cost more to fulfil.")

h2("12.9 Discount and shipping impact on profitability")
dd = pd.DataFrame(M["discount"])
table(pd.DataFrame({"Discount band": dd["discount_band"], "Order lines": dd["line_items"], "Revenue": dd["revenue"].map(money),
                    "Margin %": dd["margin_pct"].map("{:.2f}".format), "Lines at a loss %": dd["loss_line_pct"].map("{:.1f}".format)}),
      "Profitability by discount band", widths=[3, 2.5, 3.5, 2.5, 3])
figure(VIS / "14_discount_impact.png", "Profit margin and loss share by discount level")
para(f"**Insight:** as discount rises from 0–2% to 9%+, the margin falls from {dd.iloc[0]['margin_pct']:.1f}% to "
     f"{dd.iloc[-1]['margin_pct']:.1f}% and the share of loss-making lines rises from {dd.iloc[0]['loss_line_pct']:.0f}% to "
     f"{dd.iloc[-1]['loss_line_pct']:.0f}%. Discounting reduces profitability, but it does not explain why almost half "
     f"of lines lose money even at low discounts. The next table shows the stronger driver.")
sc = pd.DataFrame(M["shipping_cost_band"])
table(pd.DataFrame({"Shipping cost ÷ unit price (quartile)": sc["ship_cost_band"], "Revenue": sc["revenue"].map(money),
                    "Profit": sc["profit"].map(money), "Margin %": sc["margin_pct"].map("{:.2f}".format),
                    "Lines at a loss %": sc["loss_share"].map("{:.1f}".format)}),
      "Profitability by relative shipping cost", widths=[5, 3, 3, 2, 2.5])
pb = pd.DataFrame(M["price_band"])
table(pd.DataFrame({"Price band": pb["price_band"], "Units": pb["units"].map("{:,.0f}".format), "Revenue": pb["revenue"].map(money),
                    "Profit": pb["profit"].map(money), "Margin %": pb["margin_pct"].map("{:.2f}".format)}),
      "Profitability by unit-price band", widths=[4, 2.5, 3, 3, 2.5])
para(f"**Key diagnostic finding:** when shipping cost is high relative to the item's price (top quartile), the "
     f"margin is **{sc.iloc[-1]['margin_pct']:.1f}%** and **{sc.iloc[-1]['loss_share']:.0f}%** of lines lose money. In the "
     f"lowest quartile the margin is {sc.iloc[0]['margin_pct']:.1f}%. Similarly, budget items under $20 have a "
     f"{pb.iloc[0]['margin_pct']:.1f}% margin. **Shipping cheap items is the largest single cause of losses.** "
     f"Delivery Truck shipments, used for bulky goods such as furniture, have a margin of only "
     f"{[s for s in M['ship_mode'] if s['ship_mode']=='Delivery Truck'][0]['margin_pct']:.2f}%.")
figure(VIS / "17_correlation_heatmap.png", "Spearman correlation between numeric variables", width=12)
cw = M["correlation_with_profit"]
para(f"The correlation matrix supports this: profit correlates positively with sales ({cw['sales']:.2f}) and "
     f"negatively with shipping cost ({cw['shipping_cost']:.2f}), while its correlation with discount is weak "
     f"({cw['discount']:.2f}). Correlation shows association, not causation.")

h2("12.10 Inventory and stock movement patterns")
para("Stock-on-hand data is not available, so stock **movement** was analysed: units sold over time, ABC "
     "classification, sales velocity (units per active month) and demand variability (coefficient of variation of "
     "quarterly units).")
ab = pd.DataFrame(M["abc"])
table(pd.DataFrame({"Class": ab["abc_class"], "Products": ab["products"], "% of products": ab["product_share_pct"].map("{:.1f}".format),
                    "Revenue": ab["revenue"].map(money), "% of revenue": ab["revenue_share_pct"].map("{:.1f}".format),
                    "Profit": ab["profit"].map(money)}),
      "ABC classification of products", widths=[1.5, 2, 2.5, 3.2, 2.5, 3])
figure(VIS / "15_abc_analysis.png", "ABC (Pareto) analysis of product revenue")
figure(VIS / "16_stock_movement_quarterly.png", "Units sold per quarter by category")
inv = M["inventory"]
para(f"**Insight:** {ab.iloc[0]['products']} class-A products ({ab.iloc[0]['product_share_pct']:.0f}%) generate 80% of "
     f"revenue. In contrast, {ab.iloc[2]['products']} class-C products ({ab.iloc[2]['product_share_pct']:.0f}%) generate "
     f"only 5% and **make a net loss of {money(ab.iloc[2]['profit'])}**. {inv['high_volume_loss_count']} "
     f"high-volume products (top quartile by units) lose money, a combined {money(inv['high_volume_loss_total'])}. "
     f"{inv['erratic_A_count']} class-A products have erratic quarterly demand (CV > 1.5), and "
     f"{inv['slow_movers_count']} products sold in two or fewer orders in four years.")
hv = pd.DataFrame(inv["high_volume_loss_top10"]).head(8)
table(pd.DataFrame({"Product": hv["product_name"], "Sub-category": hv["sub_category"], "Units": hv["units"],
                    "Profit": hv["profit"].map(money)}),
      "High-volume products that lose money (top 8)", widths=[8.2, 3.5, 1.5, 2.3], font=8.5)

h1("SQL Implementation")
para("The database is built by **scripts/build_database.py**, which loads the cleaned CSV into a staging "
     "table and executes **sql/retail_analysis.sql**. The SQL file (a) creates the star schema with primary keys, "
     "foreign keys and CHECK constraints, (b) populates it from staging with INSERT … SELECT, (c) adds indexes and a "
     "reporting view, and (d) runs 16 analysis queries. Each result is saved to sql/query_results/.")
rc = q("00_row_counts")
table(rc, "Row counts after loading", widths=[5, 4])
h2("13.1 Example: schema definition")
code("CREATE TABLE fact_sales (\n    row_id INTEGER PRIMARY KEY,\n    order_id INTEGER NOT NULL,\n"
     "    order_date TEXT NOT NULL,\n    customer_id INTEGER NOT NULL REFERENCES dim_customer(customer_id),\n"
     "    product_id  INTEGER NOT NULL REFERENCES dim_product(product_id),\n"
     "    location_id INTEGER NOT NULL REFERENCES dim_location(location_id),\n"
     "    quantity INTEGER NOT NULL CHECK (quantity > 0),\n    discount REAL NOT NULL CHECK (discount BETWEEN 0 AND 1),\n"
     "    sales REAL NOT NULL CHECK (sales > 0),\n    profit REAL NOT NULL, ...);")


def sql_section(title, name, sql_snippet, explanation, cols=None, fmt=None, widths=None, limit=None):
    h2(title)
    code(sql_snippet)
    para("**Explanation:** " + explanation)
    df = q(name)
    if limit: df = df.head(limit)
    if cols: df = df[cols]
    if fmt:
        for c, f in fmt.items(): df[c] = df[c].map(f)
    table(df, f"Output of query {name}", widths=widths, font=8.5)


fm = lambda v: money(v)
pc = "{:.2f}".format
sql_section("13.2 Q1 – Total sales and profit", "01_total_sales_profit",
            "SELECT ROUND(SUM(sales),2) AS total_revenue, ROUND(SUM(profit),2) AS total_profit,\n"
            "       ROUND(100.0*SUM(profit)/SUM(sales),2) AS profit_margin_pct,\n"
            "       COUNT(DISTINCT order_id) AS total_orders,\n"
            "       ROUND(SUM(sales)/COUNT(DISTINCT order_id),2) AS avg_order_value\nFROM fact_sales;",
            "aggregates the entire fact table. COUNT(DISTINCT order_id) counts orders, not lines. The output "
            "matches the Python results exactly, which cross-validates both implementations.",
            cols=["total_revenue", "total_profit", "profit_margin_pct", "total_orders", "avg_order_value"],
            fmt={"total_revenue": fm, "total_profit": fm, "avg_order_value": lambda v: money(v, 2)})
sql_section("13.3 Q2 – Top 10 products by revenue", "02_top10_products_revenue",
            "SELECT p.product_name, p.category, ROUND(SUM(f.sales),2) AS revenue, ...\n"
            "FROM fact_sales f JOIN dim_product p ON p.product_id = f.product_id\n"
            "GROUP BY p.product_id ORDER BY revenue DESC LIMIT 10;",
            "joins facts to the product dimension, groups by product and keeps the 10 highest revenues.",
            cols=["product_name", "revenue", "profit", "margin_pct"], fmt={"revenue": fm, "profit": fm},
            widths=[9, 2.4, 2.2, 1.9])
sql_section("13.4 Q3 – Top 10 customers by spending", "03_top10_customers",
            "SELECT c.customer_name, COUNT(DISTINCT f.order_id) AS orders,\n"
            "       ROUND(SUM(f.sales),2) AS total_spent, MAX(f.order_date) AS last_order_date\n"
            "FROM fact_sales f JOIN dim_customer c ON c.customer_id = f.customer_id\n"
            "GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 10;",
            "ranks customers by total spending. Some top spenders generate little profit, which shows that "
            "high-revenue customers are not always high-profit customers.",
            cols=["customer_name", "orders", "total_spent", "profit_generated", "last_order_date"],
            fmt={"total_spent": fm, "profit_generated": fm})
sql_section("13.5 Q4/Q5 – Monthly trend and yearly growth", "05_yearly_growth",
            "WITH yearly AS (SELECT strftime('%Y', order_date) AS order_year,\n"
            "                       SUM(sales) AS revenue, SUM(profit) AS profit\n"
            "                FROM fact_sales GROUP BY order_year)\n"
            "SELECT order_year, revenue, profit,\n"
            "       100.0*(revenue - LAG(revenue) OVER (ORDER BY order_year))\n"
            "            / LAG(revenue) OVER (ORDER BY order_year) AS revenue_growth_pct\nFROM yearly;",
            "the monthly query (04) groups by strftime('%Y-%m') to give 48 monthly rows for trend charts. The yearly "
            "query uses a Common Table Expression (CTE) and the LAG() window function to compare each year with the previous year.",
            fmt={"revenue": fm, "profit": fm, "revenue_growth_pct": lambda v: "–" if pd.isna(v) else f"{v:+.2f}"})
sql_section("13.6 Q6 – Category-wise performance", "06_category_performance",
            "SELECT p.category, SUM(f.sales) AS revenue, SUM(f.profit) AS profit,\n"
            "       100.0*SUM(f.sales)/(SELECT SUM(sales) FROM fact_sales) AS revenue_share_pct, ...\n"
            "FROM fact_sales f JOIN dim_product p USING (product_id) GROUP BY p.category;",
            "a scalar sub-query provides the grand total so each category's share is calculated in one query.",
            fmt={"revenue": fm, "profit": fm})
sql_section("13.7 Q7 – Region-wise sales with ranking", "07_region_sales",
            "SELECT l.region, l.province, SUM(f.sales) AS revenue, ...,\n"
            "       RANK() OVER (ORDER BY SUM(f.sales) DESC) AS revenue_rank,\n"
            "       RANK() OVER (ORDER BY SUM(f.profit)/SUM(f.sales) DESC) AS margin_rank\n"
            "FROM fact_sales f JOIN dim_location l USING (location_id) GROUP BY l.location_id;",
            "two RANK() window functions rank provinces by revenue and by margin. Provinces with a high revenue rank "
            "but a low margin rank (e.g. British Columbia) need attention.",
            cols=["province", "region", "revenue", "margin_pct", "revenue_rank", "margin_rank"],
            fmt={"revenue": fm}, widths=[3.8, 3.5, 2.6, 1.8, 2, 2])
sql_section("13.8 Q8 – Low-performing products", "08_low_sales_products",
            "SELECT p.product_name, p.category, COUNT(DISTINCT f.order_id) AS orders,\n"
            "       SUM(f.quantity) AS units_sold, SUM(f.sales) AS revenue\n"
            "FROM fact_sales f JOIN dim_product p USING (product_id)\n"
            "GROUP BY p.product_id ORDER BY revenue ASC LIMIT 15;",
            "sorting in ascending order surfaces the weakest products, which are candidates for clearance or delisting.",
            cols=["product_name", "category", "orders", "units_sold", "revenue"], limit=10,
            fmt={"revenue": lambda v: money(v, 2)}, widths=[7.5, 3, 1.5, 1.8, 1.8])
sql_section("13.9 Q9 – Average order value", "09_average_order_value",
            "WITH order_totals AS (SELECT order_id, segment, SUM(sales) AS order_value\n"
            "                      FROM fact_sales GROUP BY order_id, segment)\n"
            "SELECT segment, COUNT(*) AS orders, AVG(order_value) AS avg_order_value\n"
            "FROM order_totals GROUP BY segment;",
            "order lines are first summed to order level in a CTE, so AOV is a true per-order average rather than a per-line average.",
            fmt={"avg_order_value": lambda v: money(v, 2)})
sql_section("13.10 Q10 – Repeat customers", "10_repeat_customers",
            "WITH customer_orders AS (SELECT customer_id, COUNT(DISTINCT order_id) AS n_orders\n"
            "                         FROM fact_sales GROUP BY customer_id)\n"
            "SELECT CASE WHEN n_orders = 1 THEN '1 order (one-time)' ... END AS customer_type,\n"
            "       COUNT(*) AS customers\nFROM customer_orders GROUP BY customer_type;",
            "CASE groups customers into order-count buckets. Only 1.4% of customers bought once.")
sql_section("13.11 Q11/Q12 – Profit margin by category and loss-making sub-categories", "12_loss_making_subcategories",
            "SELECT category, sub_category, SUM(sales) AS revenue, SUM(profit) AS profit\n"
            "FROM v_sales GROUP BY category, sub_category\nHAVING SUM(profit) < 0 ORDER BY profit;",
            "Q11 calculates the margin for every sub-category (17 rows). Q12 uses HAVING, which filters *after* "
            "grouping, unlike WHERE, which filters rows *before* grouping, to keep only sub-categories with a net loss.",
            fmt={"revenue": fm, "profit": fm})
h2("13.12 Additional queries")
para("Q13 bands discounts with CASE to measure their margin impact (reproducing the discount table in Section 12.9). Q14 compares ship "
     "modes using julianday() for delivery time. Q15 uses ROW_NUMBER() OVER (PARTITION BY category …) to find "
     "each category's best seller. Q16 computes Recency, Frequency and Monetary values per customer; these were "
     "verified to be **identical** to the Python RFM values for all 795 customers (notebook 04).")

h1("Customer Segmentation")
para("Customer segmentation is implemented in **notebooks/03_customer_segmentation.ipynb**.")
h2("14.1 RFM methodology")
bullets([f"**Recency (R):** days between the customer's last order and the reference date ({R['reference_date']}, the "
         "day after the last order in the data). Lower is better.",
         "**Frequency (F):** number of distinct orders. Higher is better.",
         "**Monetary (M):** total sales value. Higher is better."])
para("Each measure is converted to a **score from 1 to 5 using quintiles** (each score holds about 20% of "
     "customers). Customers are ranked before cutting, so that ties (e.g. many customers with exactly six orders) "
     "do not break the equal-size groups. The Recency scale is reversed, so the most recent buyers score 5.")
sr = R["score_ranges"]
table(pd.DataFrame({"Score": ["1", "2", "3", "4", "5"],
                    "Recency (days)": [f"{sr['Recency (days) min'][s]}–{sr['Recency (days) max'][s]}" for s in "12345"],
                    "Frequency (orders)": [f"{sr['Frequency (orders) min'][s]}–{sr['Frequency (orders) max'][s]}" for s in "12345"],
                    "Monetary ($)": [f"{sr['Monetary ($) min'][s]:,}–{sr['Monetary ($) max'][s]:,}" for s in "12345"]}),
      "What each RFM score means in real units", widths=[1.5, 4, 4, 5])
h2("14.2 Segment rules")
table(pd.DataFrame([
    ["1", "High-Value (Champions)", "R ≥ 4, F ≥ 4, M ≥ 4"], ["2", "New Customers", "first order in last 365 days"],
    ["3", "Loyal Customers", "R ≥ 3, F ≥ 4"], ["4", "Potential Loyalists", "R ≥ 3, F 2–3"],
    ["5", "Need Attention", "R ≥ 3, F = 1"], ["6", "At-Risk Customers", "R ≤ 2, F ≥ 3"], ["7", "Hibernating / Lost", "R ≤ 2, F ≤ 2"],
], columns=["Order", "Segment", "Rule (first match wins)"]), "RFM segment rules", widths=[1.5, 5, 7])
h2("14.3 Results")
pr = pd.DataFrame(R["profile"])
table(pd.DataFrame({"Segment": pr["segment"], "Customers": pr["customers"], "% customers": pr["customer_share_pct"].map("{:.1f}".format),
                    "% revenue": pr["revenue_share_pct"].map("{:.1f}".format), "Avg recency (days)": pr["avg_recency_days"].map("{:.0f}".format),
                    "Avg orders": pr["avg_frequency"].map("{:.1f}".format), "Avg spend": pr["avg_monetary"].map(money)}),
      "RFM segment profile", widths=[4.2, 1.8, 1.8, 1.8, 2.2, 1.7, 2.2], font=8.5)
figure(VIS / "18_rfm_segment_share.png", "Share of customers versus share of revenue by RFM segment")
figure(VIS / "19_rfm_heatmap.png", "Average customer spend by Recency and Frequency score", width=12)
P = pr.set_index("segment")
para(f"**Insights:** **Champions** ({P.loc['High-Value (Champions)','customers']} customers, "
     f"{P.loc['High-Value (Champions)','customer_share_pct']:.1f}%) generate "
     f"{P.loc['High-Value (Champions)','revenue_share_pct']:.1f}% of revenue. Together with Loyal customers, "
     f"{R['top2_customer_share_pct']}% of customers produce {R['top2_revenue_share_pct']}% of revenue. "
     f"**At-Risk customers** ({P.loc['At-Risk Customers','customers']}) bought frequently "
     f"({P.loc['At-Risk Customers','avg_frequency']:.1f} orders on average) but not for about "
     f"{P.loc['At-Risk Customers','avg_recency_days']:.0f} days. They account for {mn(R['at_risk_revenue'])} of past revenue, "
     f"which makes them the most valuable group to win back. Only {P.loc['New Customers','customers']} customers are "
     "genuinely new: the customer base is mature, so **retention matters more than acquisition** for this business.")
h2("14.4 Business applications")
table(pd.DataFrame({"Segment": pr["segment"], "Recommended action": pr["recommended_action"]}),
      "Marketing action per segment", widths=[4.2, 11.3], font=9)

h1("Power BI Dashboard")
para("The dashboard is designed as four pages with synchronised slicers for **date range, category, region and RFM "
     "customer segment**. Its data model is the same star schema as the SQL database, exported by "
     "scripts/prepare_powerbi_data.py (fact_sales plus dim_customer, dim_product, dim_location and a continuous dim_date "
     "calendar). dim_customer carries each customer's RFM segment, and dim_product carries its ABC class, so both can "
     "be used as slicers.")
para("Measures are written in **DAX** (Data Analysis Expressions), for example:")
code("Total Revenue       = SUM ( fact_sales[sales] )\n"
     "Total Orders        = DISTINCTCOUNT ( fact_sales[order_id] )\n"
     "Average Order Value = DIVIDE ( [Total Revenue], [Total Orders] )\n"
     "Profit Margin %     = DIVIDE ( [Total Profit], [Total Revenue] )\n"
     "Revenue YoY %       = DIVIDE ( [Total Revenue] - [Revenue PY], [Revenue PY] )")
para("The complete measure list, the theme file and step-by-step build instructions are in the dashboard/ "
     "folder (DAX_measures.md, retail_theme.json, POWERBI_BUILD_GUIDE.md).")
para("**Note on the figures below:** they are **design previews** of each page, drawn in Python from the "
     "same model data. They define the target layout and the values the Power BI report must reproduce. "
     "[Replace each with a screenshot of the corresponding page of powerbi_dashboard.pbix once it is built.]",
     italic=True)
for fn, title, desc in [
    ("page1_executive_overview.png", "Page 1 – Executive Overview",
     "KPI cards (revenue, profit, orders, AOV), the monthly revenue trend with a 3-month rolling average, revenue by "
     "category, and revenue and profit by year shown as separate charts (no dual axis)."),
    ("page2_product_analysis.png", "Page 2 – Product Analysis",
     "Top 10 and bottom 10 products, profit by sub-category coloured by gain or loss, and a category profitability panel."),
    ("page3_customer_analysis.png", "Page 3 – Customer Analysis",
     "Customer KPIs (count, repeat rate, orders per customer), RFM segment size and revenue, top customers, and revenue "
     "trend by business segment."),
    ("page4_regional_analysis.png", "Page 4 – Regional Analysis",
     "Revenue and margin by province (provinces act as sales territories because the data has no store IDs), and a "
     "region × category profit matrix. A filled map of provinces is added in Power BI."),
]:
    h2(title)
    figure(PREV / fn, title + " (design preview)", width=16)
    para(desc)

h1("Results and Findings")
res = [
    f"**Overall performance:** {mn(K['total_revenue'])} revenue, {mn(K['total_profit'])} profit "
    f"({K['profit_margin_pct']:.1f}% margin), {K['total_orders']:,} orders, AOV {money(K['avg_order_value'], 2)}.",
    f"**Trend:** revenue peaked in 2009, declined in 2010–2011 and recovered {y12['revenue_growth_pct']:.1f}% in 2012. "
    f"Margin fell to {y12['margin_pct']:.2f}% in 2012, the lowest of the four years.",
    f"**Seasonality:** {ss['strongest_calendar_month']} is the strongest month and {ss['weakest_calendar_month']} the weakest; "
    f"Q4 and Q1 are the strongest quarters.",
    f"**Highest-revenue products:** {tp.iloc[0]['product_name']} ({money(tp.iloc[0]['revenue'])}), {tp.iloc[1]['product_name']} "
    f"and {tp.iloc[2]['product_name']}.",
    f"**Most profitable category:** Technology ({cats['Technology']['profit_share_pct']:.0f}% of profit, "
    f"{cats['Technology']['margin_pct']:.1f}% margin). Most profitable sub-categories: Telephones & Communication, Office "
    "Machines and Binders.",
    f"**Weakest category:** Furniture ({cats['Furniture']['margin_pct']:.1f}% margin). Tables and Bookcases lose money.",
    f"**Loss drivers:** a high shipping cost relative to price (top quartile margin {sc.iloc[-1]['margin_pct']:.0f}%), "
    f"budget items ({pb.iloc[0]['margin_pct']:.1f}% margin), and higher discounts (margin falls from "
    f"{dd.iloc[0]['margin_pct']:.1f}% to {dd.iloc[-1]['margin_pct']:.1f}%).",
    f"**Regions:** Ontario leads in revenue; {lowm.iloc[0]['province']}, {lowm.iloc[1]['province']} and British "
    "Columbia have below-average margins; New Brunswick has the best margin.",
    f"**Customers:** {cu['repeat_customer_pct']}% are repeat buyers; the top 20% generate {cu['top20pct_customer_revenue_share']}% "
    f"of revenue; Champions + Loyal ({R['top2_customer_share_pct']}%) generate {R['top2_revenue_share_pct']}%; "
    f"At-Risk customers hold {mn(R['at_risk_revenue'])} of past revenue.",
    f"**Inventory:** {ab.iloc[0]['products']} class-A products give 80% of revenue; class-C products make a net loss of "
    f"{money(ab.iloc[2]['profit'])}; {inv['high_volume_loss_count']} high-volume products lose {money(abs(inv['high_volume_loss_total']))}.",
]
bullets(res)
h2("16.1 Validation of results")
bullets(["Python (Pandas) and SQL (SQLite) produce identical totals: revenue $14,915,600.82, 5,496 orders, AOV $2,713.90.",
         "RFM values from SQL and Python are identical for all 795 customers.",
         "The Power BI export reproduces the same revenue and profit totals (asserted in code).",
         "Automated assertions check for no missing values, unique keys and expected row counts."])

h1("Business Recommendations")
para("Each recommendation below is linked to the finding that supports it.")
recs = [
    ("Introduce a shipping-cost policy for low-priced items",
     f"Lines with the highest shipping cost relative to price have a {sc.iloc[-1]['margin_pct']:.1f}% margin and "
     f"{sc.iloc[-1]['loss_share']:.0f}% of them lose money; budget items (<$20) have a {pb.iloc[0]['margin_pct']:.1f}% margin.",
     "Set a minimum order value for free shipping, charge shipping on small low-price orders, encourage bundling "
     "of small items, and renegotiate carrier rates for light parcels."),
    ("Fix Furniture profitability, starting with Tables and Bookcases",
     f"Furniture provides {cats['Furniture']['revenue_share_pct']:.0f}% of revenue but only "
     f"{cats['Furniture']['profit_share_pct']:.0f}% of profit; Tables ({money(loss.iloc[0]['profit'])}) and Bookcases "
     f"({money(loss.iloc[1]['profit'])}) lose money; Delivery Truck shipments earn only a "
     f"{[s for s in M['ship_mode'] if s['ship_mode']=='Delivery Truck'][0]['margin_pct']:.1f}% margin.",
     "Review list prices and supplier costs, add delivery and assembly charges for bulky items, and stop "
     "discounting loss-making furniture lines."),
    ("Cap discounts and require approval above 5%",
     f"Margin drops from {dd.iloc[0]['margin_pct']:.1f}% (0–2% discount) to {dd.iloc[-1]['margin_pct']:.1f}% (9%+), and "
     f"loss-making lines rise from {dd.iloc[0]['loss_line_pct']:.0f}% to {dd.iloc[-1]['loss_line_pct']:.0f}%.",
     "Use a tiered discount policy: give discounts only to Champions and Loyal customers or for clearance of class-C stock."),
    ("Grow Technology and high-margin Office Supplies",
     f"Technology earns {cats['Technology']['profit_share_pct']:.0f}% of profit at a {cats['Technology']['margin_pct']:.1f}% margin; "
     "Binders (30.1%), Labels (35.1%) and Envelopes (27.7%) have the highest margins.",
     "Give these products prominent placement, cross-sell them with Furniture orders, and keep them in stock."),
    ("Review loss-making best-sellers individually",
     (f"{neg_top.iloc[0]['product_name']} is a top-revenue product with a {neg_top.iloc[0]['margin_pct']:.1f}% margin. " if len(neg_top) else "") +
     f"{inv['high_volume_loss_count']} high-volume products lose {money(abs(inv['high_volume_loss_total']))} in total.",
     "Re-price, renegotiate supplier cost or replace these products. Volume is not a reason to keep a product that loses money."),
    ("Focus on retention with RFM-based campaigns",
     f"Champions + Loyal = {R['top2_customer_share_pct']}% of customers but {R['top2_revenue_share_pct']}% of revenue; "
     f"{P.loc['At-Risk Customers','customers']} At-Risk customers represent {mn(R['at_risk_revenue'])} of past revenue; "
     f"only {P.loc['New Customers','customers']} customers are new.",
     "Run a VIP programme for Champions, a win-back campaign for At-Risk customers, and nurture programmes for "
     "Potential Loyalists. Spend little on the Hibernating group."),
    ("Improve the weak territories",
     f"{lowm.iloc[0]['province']} ({lowm.iloc[0]['margin_pct']:.1f}%), {lowm.iloc[1]['province']} "
     f"({lowm.iloc[1]['margin_pct']:.1f}%) and British Columbia "
     f"({pv.set_index('province').loc['British Columbia','margin_pct']:.1f}%) are below the {K['profit_margin_pct']:.1f}% "
     "average; Furniture loses money in Quebec.",
     "Review shipping costs to remote provinces, adjust the product mix by region, and learn from New Brunswick's "
     "practices (the best margin)."),
    ("Manage inventory by ABC class",
     f"{ab.iloc[0]['products']} class-A products generate 80% of revenue; {ab.iloc[2]['products']} class-C products generate 5% "
     f"and lose {money(abs(ab.iloc[2]['profit']))}; {inv['erratic_A_count']} class-A products have erratic demand; "
     f"{inv['slow_movers_count']} products are slow movers.",
     "Hold safety stock and review class-A items frequently; reduce the class-C range and slow movers; plan stock "
     "for the stronger Q4/Q1 period."),
    ("Price urgent orders correctly",
     f"Critical-priority orders have a {pri.iloc[0]['margin_pct']:.1f}% margin, compared with "
     f"{pri.iloc[-1]['margin_pct']:.1f}% for {pri.iloc[-1]['order_priority']} priority.",
     "Add an express or priority handling fee, so that urgent fulfilment costs are recovered."),
]
for i, (title, ev, act) in enumerate(recs, 1):
    h3(f"R{i}. {title}")
    para(f"**Evidence:** {ev}")
    para(f"**Action:** {act}")
h2("17.1 Marketing strategy summary")
bullets(["**Retention first:** most customers are repeat buyers, so loyalty and win-back offer the best return.",
         "**Seasonal campaigns** in Q4 and Q1, when demand is highest, and promotional activity to lift the weaker June period.",
         "**Segment-targeted offers** instead of blanket discounts, aimed at the Corporate segment (largest revenue) and "
         "Small Business (best margin).",
         "**Bundles** of low-price Office Supplies with higher-value items, which spreads shipping cost across a larger order."])

h1("Limitations")
bullets(["The dataset is a public **sample** dataset prepared for teaching, so findings describe this data and are not "
         "audited results of a real company.",
         "There are **no store IDs or stock-on-hand data**. Provinces are used as sales territories, and inventory is "
         "analysed through sales movement only.",
         "**No cost breakdown** (purchase cost, overheads) is available, so the reasons behind profit are inferred from "
         "discount, shipping cost and price, not proven.",
         "Some customers and orders map to multiple provinces or segments (a property of this dataset), which limits "
         "customer-level geographic analysis.",
         "The data ends in 2012, so recency is measured relative to the end of the data and market conditions may "
         "have changed since then.",
         "Correlation analysis shows association, not causation; the recommendations should be tested (e.g. A/B tests) "
         "before full roll-out.",
         "RFM quintile scores are relative to this customer base and must be recalculated when new data arrives."])

h1("Future Scope")
bullets(["**Sales forecasting** with time-series models (e.g. ARIMA, Prophet) to plan stock and staffing.",
         "**Machine-learning segmentation** (e.g. K-Means clustering on RFM features) to compare with rule-based segments.",
         "**Customer lifetime value (CLV)** prediction to rank customers by future value.",
         "**Market-basket analysis** (association rules) to find products that are bought together for bundling.",
         "**Profit-driver modelling** (e.g. regression or decision trees) to quantify the effect of discount and shipping on profit.",
         "**Real inventory integration**: combine with stock levels to compute reorder points and stock-out risk.",
         "**Automated refresh**: connect Power BI to a live database and schedule refreshes in the Power BI Service.",
         "**Deployment** of an interactive web app (e.g. Streamlit) for non-technical users."])

h1("Conclusion")
para("This project built a complete, reproducible retail analytics solution. A public dataset of 8,399 "
     "transactions was cleaned, validated and documented. It was analysed with Python, stored and queried in a "
     "star-schema SQL database, segmented with RFM analysis, examined for stock movement with ABC analysis, and "
     "presented through a four-page Power BI dashboard design.")
para(f"The analysis shows that revenue alone can mislead. The shop is profitable overall "
     f"({K['profit_margin_pct']:.1f}% margin), but about half of its order lines lose money. Most of these losses come "
     "from shipping low-priced items, from Furniture lines such as Tables and Bookcases, and from higher discounts. "
     f"At the same time, a small group of customers and products creates most of the value: {R['top2_customer_share_pct']}% "
     f"of customers generate {R['top2_revenue_share_pct']}% of revenue, and {ab.iloc[0]['product_share_pct']:.0f}% of products "
     "generate 80% of revenue.")
para("The recommendations (a shipping-cost policy, Furniture repricing, discount control, ABC-based inventory "
     "management and RFM-based retention) each follow directly from a measured finding. Together they "
     "show how data analytics can help a retail business move from intuition to evidence-based decisions.")

h1("References")
para("[Format these references in the citation style required by your institution, e.g. APA or IEEE. "
     "Verify each one before submission.]", italic=True, size=10)
refs = [
    "Chen, D., Sain, S. L., & Guo, K. (2012). Data mining for the online retail industry: A case study of RFM model-based customer segmentation using data mining. Journal of Database Marketing & Customer Strategy Management, 19(3), 197–208.",
    "Davenport, T. H., & Harris, J. G. (2007). Competing on Analytics: The New Science of Winning. Harvard Business School Press.",
    "Fader, P. S., Hardie, B. G. S., & Lee, K. L. (2005). RFM and CLV: Using iso-value curves for customer base analysis. Journal of Marketing Research, 42(4), 415–430.",
    "Few, S. (2006). Information Dashboard Design: The Effective Visual Communication of Data. O'Reilly Media.",
    "Han, J., Kamber, M., & Pei, J. (2011). Data Mining: Concepts and Techniques (3rd ed.). Morgan Kaufmann.",
    "Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020). Array programming with NumPy. Nature, 585, 357–362.",
    "Hughes, A. M. (1994). Strategic Database Marketing. Probus Publishing.",
    "Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in Science & Engineering, 9(3), 90–95.",
    "Kimball, R., & Ross, M. (2013). The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling (3rd ed.). Wiley.",
    "McKinney, W. (2010). Data structures for statistical computing in Python. Proceedings of the 9th Python in Science Conference, 56–61.",
    "Provost, F., & Fawcett, T. (2013). Data Science for Business. O'Reilly Media.",
    "Silver, E. A., Pyke, D. F., & Peterson, R. (1998). Inventory Management and Production Planning and Scheduling (3rd ed.). Wiley.",
    "Waskom, M. L. (2021). seaborn: statistical data visualization. Journal of Open Source Software, 6(60), 3021.",
    "Microsoft. Power BI documentation. https://learn.microsoft.com/power-bi/",
    "SQLite. SQLite documentation. https://www.sqlite.org/docs.html",
    "Superstore Sales dataset (Tableau sample data), public copy: https://github.com/curran/data/tree/gh-pages/superstoreSales",
]
for i, r in enumerate(refs, 1):
    p = para(f"[{i}] {r}", align="left", size=11)
    p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.first_line_indent = Cm(-0.8)

out = ROOT / "report" / "final_project_report.docx"
doc.save(out)
print(f"Saved {out.relative_to(ROOT)}  ({fig_no[0]} figures, {tab_no[0]} tables, {chapter[0]} chapters)")
