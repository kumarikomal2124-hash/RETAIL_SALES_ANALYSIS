"""
build_database.py - create the SQLite database and run every SQL analysis query.

Usage (from the project root folder):
    python scripts/build_database.py

What it does:
 1. Loads dataset/cleaned_data.csv into a staging table (stg_sales).
 2. Executes sql/retail_analysis.sql, which builds the star schema
    (dim_customer, dim_product, dim_location, fact_sales) and the view v_sales.
 3. Runs every query marked with "-- @query" and saves each result to
    sql/query_results/<name>.csv, plus a combined Markdown summary.
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "dataset" / "retail.db"
CSV_PATH = ROOT / "dataset" / "cleaned_data.csv"
SQL_PATH = ROOT / "sql" / "retail_analysis.sql"
OUT_DIR = ROOT / "sql" / "query_results"

STAGING_COLS = ["row_id", "order_id", "order_date", "ship_date", "order_priority", "ship_mode",
                "customer_name", "segment", "province", "region", "category", "sub_category",
                "product_name", "product_container", "product_base_margin", "unit_price",
                "quantity", "discount", "sales", "shipping_cost", "profit"]


def split_sql(text):
    """Split the SQL file into the setup part and the list of named queries."""
    parts = re.split(r"^-- @query ", text, flags=re.M)
    setup, queries = parts[0], []
    for block in parts[1:]:
        header, _, body = block.partition("\n")
        name, _, desc = header.partition("|")
        queries.append((name.strip(), desc.strip(), body.strip()))
    return setup, queries


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()                       # rebuild from scratch every time (reproducible)

    con = sqlite3.connect(DB_PATH)
    df = pd.read_csv(CSV_PATH)[STAGING_COLS]
    df.to_sql("stg_sales", con, index=False)   # staging table = cleaned CSV as-is
    print(f"Loaded {len(df):,} rows into stg_sales")

    setup, queries = split_sql(SQL_PATH.read_text(encoding="utf-8"))
    con.executescript(setup)                   # DDL + load into star schema
    con.execute("DROP TABLE stg_sales")        # staging no longer needed
    con.commit()

    md = ["# SQL Query Results\n",
          "Generated automatically by `scripts/build_database.py` from `sql/retail_analysis.sql`.\n"]
    for name, desc, sql in queries:
        result = pd.read_sql_query(sql, con)
        result.to_csv(OUT_DIR / f"{name}.csv", index=False)
        md += [f"\n## {desc}\n", f"`{name}.csv` · {len(result)} rows\n",
               result.head(20).to_markdown(index=False, floatfmt=",.2f"), "\n"]
        print(f"  ✓ {name:<32} {len(result):>4} rows")
    (OUT_DIR / "ALL_RESULTS.md").write_text("\n".join(md), encoding="utf-8")

    con.execute("VACUUM")
    con.close()
    print(f"Database: {DB_PATH.relative_to(ROOT)}   Results: {OUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
