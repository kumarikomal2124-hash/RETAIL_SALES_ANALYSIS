"""
run_pipeline.py - reproduce the entire project with one command.

Usage (from the project root folder):
    python run_pipeline.py

Steps (each step only reads files produced by earlier steps):
  1. notebooks/01_data_cleaning.ipynb          raw_data.csv  -> cleaned_data.csv
  2. notebooks/02_exploratory_analysis.ipynb   charts + results/eda_metrics.json
  3. notebooks/03_customer_segmentation.ipynb  RFM segments + results/rfm_metrics.json
  4. scripts/build_database.py                 dataset/retail.db + sql/query_results/
  5. notebooks/04_sql_analysis.ipynb           SQL demo + SQL-vs-Python cross-check
  6. scripts/prepare_powerbi_data.py           dashboard/powerbi_data/*.csv
  7. scripts/render_dashboard_preview.py       dashboard/preview/*.png
     scripts/build_interactive_dashboard.py    dashboard/interactive_dashboard.html
  8. scripts/build_report.py                   report/final_project_report.docx
  9. validation checks
Notebooks are executed in place, so they are saved with fresh outputs.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

ROOT = Path(__file__).resolve().parent


def run_notebook(name):
    path = ROOT / "notebooks" / name
    nb = nbformat.read(path, as_version=4)
    ExecutePreprocessor(timeout=900, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(path.parent)}})
    nbformat.write(nb, path)


def run_script(name):
    subprocess.run([sys.executable, str(ROOT / "scripts" / name)], check=True, cwd=ROOT)


def validate():
    """Cross-check key results produced by different tools."""
    import pandas as pd
    clean = pd.read_csv(ROOT / "dataset" / "cleaned_data.csv")
    eda = json.loads((ROOT / "results" / "eda_metrics.json").read_text())["kpis"]
    sql = pd.read_csv(ROOT / "sql" / "query_results" / "01_total_sales_profit.csv").iloc[0]
    pbi = pd.read_csv(ROOT / "dashboard" / "powerbi_data" / "fact_sales.csv")
    checks = {
        "cleaned rows = 8,399": len(clean) == 8399,
        "no missing values in cleaned data": int(clean.isna().sum().sum()) == 0,
        "row_id unique": clean["row_id"].is_unique,
        "Python revenue = SQL revenue": abs(eda["total_revenue"] - sql["total_revenue"]) < 0.01,
        "Python profit = SQL profit": abs(eda["total_profit"] - sql["total_profit"]) < 0.01,
        "Python orders = SQL orders": eda["total_orders"] == sql["total_orders"],
        "Power BI revenue = Python revenue": abs(pbi["sales"].sum() - eda["total_revenue"]) < 0.01,
        "report generated": (ROOT / "report" / "final_project_report.docx").exists(),
    }
    for name, ok in checks.items():
        print(f"   {'PASS' if ok else 'FAIL'}  {name}")
    return all(checks.values())


STEPS = [
    ("Data cleaning", lambda: run_notebook("01_data_cleaning.ipynb")),
    ("Exploratory analysis", lambda: run_notebook("02_exploratory_analysis.ipynb")),
    ("Customer segmentation", lambda: run_notebook("03_customer_segmentation.ipynb")),
    ("SQL database + queries", lambda: run_script("build_database.py")),
    ("SQL demo notebook", lambda: run_notebook("04_sql_analysis.ipynb")),
    ("Power BI data export", lambda: run_script("prepare_powerbi_data.py")),
    ("Dashboard previews", lambda: run_script("render_dashboard_preview.py")),
    ("Interactive HTML dashboard", lambda: run_script("build_interactive_dashboard.py")),
    ("Project report", lambda: run_script("build_report.py")),
]

if __name__ == "__main__":
    start = time.time()
    for i, (label, fn) in enumerate(STEPS, 1):
        t = time.time()
        print(f"[{i}/{len(STEPS)}] {label} ...", flush=True)
        fn()
        print(f"      done in {time.time() - t:.1f}s")
    print("[validation]")
    ok = validate()
    print(f"\nPipeline finished in {time.time() - start:.0f}s - {'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}")
    sys.exit(0 if ok else 1)
