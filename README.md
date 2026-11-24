# Retail Shop Analysis Using Data Analytics

A complete, reproducible data analytics project that analyses four years of retail transactions to find
what drives revenue and profit, who the valuable customers are, and which products and regions need attention.
It ends with evidence-based business recommendations.

**Stack:** Python (Pandas, NumPy, Matplotlib, Seaborn) · SQL (SQLite) · Jupyter · Power BI · CSV/Excel

---

## Key results (from the actual data)

| Metric | Value |
|---|---|
| Total revenue | **$14,915,600.82** |
| Total profit | **$1,521,767.98** (10.2% margin) |
| Orders / customers / products | 5,496 / 795 / 1,263 |
| Average order value | $2,713.90 |
| Order lines sold at a loss | 50.8% |

* **Technology** = 40% of revenue but **58% of profit**. **Furniture** = 35% of revenue but only **8% of profit**
  (Tables and Bookcases lose money).
* **Main loss driver:** shipping cost that is high relative to item price. The top quartile has a **−50% margin**.
  Higher discounts also reduce margin (12.4% → 7.5%).
* **Customers:** 98.6% are repeat buyers. Champions + Loyal (31% of customers) bring **49% of revenue**.
  At-Risk customers represent **$2.80M** of past revenue.
* **Inventory:** 23% of products (class A) generate 80% of revenue. Class-C products make a net loss.
* Python, SQL and Power BI-export totals are **cross-validated** and match to the cent.

## Dataset

**Superstore Sales (Canadian edition)**, a public sample retail dataset originally distributed by Tableau Software.
Copy used: <https://github.com/curran/data/tree/gh-pages/superstoreSales> (file `superstoreSales.csv`).
8,399 order lines · 21 columns · Jan 2009 – Dec 2012 · 3 categories, 17 sub-categories, 13 provinces.

No fields were simulated. Derived fields (gross sales, margin %, date parts, bands, flags) are calculated
from original columns and listed in notebook 01 and in the report. The data has **no store IDs or stock levels**,
so provinces are treated as sales territories and inventory is analysed through stock *movement*.

## Folder structure

```
Retail-Shop-Analysis/
├── dataset/
│   ├── raw_data.csv                 original file, unchanged (Mac Roman encoding, CR line endings)
│   ├── cleaned_data.csv             output of notebook 01 (8,399 × 38)
│   └── retail.db                    SQLite star-schema database (built by scripts/build_database.py)
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_exploratory_analysis.ipynb
│   ├── 03_customer_segmentation.ipynb
│   ├── 04_sql_analysis.ipynb        runs and explains every SQL query
│   └── viz_style.py                 shared chart style (colour-blind-safe palette)
├── sql/
│   ├── retail_analysis.sql          schema (DDL) + load + 16 analysis queries
│   └── query_results/               one CSV per query + ALL_RESULTS.md
├── visualizations/                  all charts (PNG, 160 dpi)
├── dashboard/
│   ├── interactive_dashboard.html   ★ interactive dashboard - double-click to open in a browser
│   ├── POWERBI_BUILD_GUIDE.md       step-by-step instructions to build the .pbix
│   ├── DAX_measures.md              every measure, with expected values for checking
│   ├── retail_theme.json            Power BI theme
│   ├── powerbi_data/                star-schema CSVs to load into Power BI
│   └── preview/                     4 page-layout previews rendered from the data
├── results/                         metrics JSON, cleaning log, RFM and product summaries
├── report/
│   ├── final_project_report.docx    full academic report (27 sections, generated from results)
│   ├── final_project_report.pdf     PDF copy of the report
│   └── viva_preparation.md          likely viva questions with answers
├── scripts/                         build_database, prepare_powerbi_data, render_dashboard_preview, build_report
├── run_pipeline.py                  runs everything in order + validation checks
├── requirements.txt
└── README.md
```

## How to run

### 1. Install
```bash
python -m venv venv
venv\Scripts\activate            # Windows   (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

### 2. Run everything (about 20 seconds)
```bash
python run_pipeline.py
```
This re-executes all notebooks, rebuilds the database, re-exports the Power BI data, redraws the dashboard
previews, regenerates the report, and prints PASS/FAIL validation checks.

### 3. Or run each component yourself
| Step | Command | Output |
|---|---|---|
| Cleaning | open `notebooks/01_data_cleaning.ipynb` in Jupyter → *Run All* | `dataset/cleaned_data.csv` |
| EDA | `notebooks/02_exploratory_analysis.ipynb` → *Run All* | `visualizations/`, `results/eda_metrics.json` |
| RFM | `notebooks/03_customer_segmentation.ipynb` → *Run All* | `results/rfm_segments.csv` |
| SQL | `python scripts/build_database.py` | `dataset/retail.db`, `sql/query_results/` |
| SQL demo | `notebooks/04_sql_analysis.ipynb` → *Run All* | query explanations |
| Power BI data | `python scripts/prepare_powerbi_data.py` | `dashboard/powerbi_data/` |
| Report | `python scripts/build_report.py` | `report/final_project_report.docx` |

Start Jupyter with `jupyter notebook` from the project folder. Run notebooks in order 01 → 02 → 03.

### 4. Query the database directly (optional)
Open `dataset/retail.db` in **DB Browser for SQLite** (free) and run any query from `sql/retail_analysis.sql`.
The SQL uses standard syntax (CTEs, window functions); only the date functions `strftime`/`julianday` are
SQLite-specific. In MySQL use `DATE_FORMAT`/`DATEDIFF` instead.

### 5. Interactive dashboard (no Power BI needed)
Double-click `dashboard/interactive_dashboard.html`. It opens in your browser and works offline. It has 4 pages, slicers for date,
category, region, RFM segment and business segment, hover tooltips, and click-to-filter on bars and heatmap cells.
Every number is computed live from the 8,399 order lines and matches the notebooks and SQL.

### 6. Build the Power BI dashboard
The `.pbix` file must be created in **Power BI Desktop** (Windows). Follow `dashboard/POWERBI_BUILD_GUIDE.md`
(about 60–90 minutes). Save it as `dashboard/powerbi_dashboard.pbix`, then replace the four preview figures in the
report (Chapter 15) with screenshots of your pages.

## Before you submit: checklist
- [ ] Fill every `[PLACEHOLDER]` in the report (university, college, department, names, roll number, guide, dates).
- [ ] In Word: right-click the table of contents → *Update Field → Update entire table*.
- [ ] Build `powerbi_dashboard.pbix` and paste its screenshots into Chapter 15.
- [ ] Format the references in your college's required citation style.
- [ ] Read `report/viva_preparation.md`.

## Honest limitations
Sample (teaching) dataset · no store IDs or stock-on-hand data · no cost breakdown · data ends in 2012 ·
some order IDs map to more than one customer (documented in notebook 01). See Chapter 18 of the report.
