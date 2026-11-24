"""
prepare_powerbi_data.py - export a Power BI-ready star schema.

Usage (from the project root, after running notebooks 01-03):
    python scripts/prepare_powerbi_data.py

Creates in dashboard/powerbi_data/:
    fact_sales.csv     one row per order line, with foreign keys
    dim_customer.csv   customer + RFM scores and RFM segment
    dim_product.csv    product hierarchy + ABC class
    dim_location.csv   province, region, country (for the map visual)
    dim_date.csv       continuous calendar 2009-01-01 .. 2012-12-31
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dashboard" / "powerbi_data"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(ROOT / "dataset" / "cleaned_data.csv", parse_dates=["order_date", "ship_date"])
rfm = pd.read_csv(ROOT / "results" / "rfm_segments.csv")
prod_summary = pd.read_csv(ROOT / "results" / "product_summary.csv")

# ---- Dimensions -------------------------------------------------------------
dim_customer = (rfm[["customer_name", "recency", "frequency", "monetary", "R", "F", "M",
                     "RFM_score", "segment", "main_business_segment", "first_order", "last_order"]]
                .rename(columns={"segment": "rfm_segment", "monetary": "lifetime_sales"})
                .sort_values("customer_name").reset_index(drop=True))
dim_customer.insert(0, "customer_key", dim_customer.index + 1)
seg_order = {s: i for i, s in enumerate(["High-Value (Champions)", "Loyal Customers", "Potential Loyalists",
                                         "New Customers", "Need Attention", "At-Risk Customers",
                                         "Hibernating / Lost"], start=1)}
dim_customer["rfm_segment_order"] = dim_customer["rfm_segment"].map(seg_order)

dim_product = (df.groupby("product_name")
               .agg(category=("category", "first"), sub_category=("sub_category", "first"),
                    product_container=("product_container", "first"),
                    product_base_margin=("product_base_margin", "first"))
               .reset_index())
dim_product = dim_product.merge(prod_summary[["product_name", "abc_class"]], on="product_name", how="left")
dim_product.insert(0, "product_key", dim_product.index + 1)

dim_location = df[["province", "region"]].drop_duplicates().sort_values(["region", "province"]).reset_index(drop=True)
dim_location["country"] = "Canada"
dim_location.insert(0, "location_key", dim_location.index + 1)

dates = pd.date_range(df["order_date"].min().replace(month=1, day=1), df["order_date"].max().replace(month=12, day=31))
dim_date = pd.DataFrame({"date": dates})
dim_date["year"] = dim_date["date"].dt.year
dim_date["quarter"] = "Q" + dim_date["date"].dt.quarter.astype(str)
dim_date["month_number"] = dim_date["date"].dt.month
dim_date["month_name"] = dim_date["date"].dt.strftime("%b")
dim_date["year_month"] = dim_date["date"].dt.strftime("%Y-%m")
dim_date["weekday"] = dim_date["date"].dt.strftime("%a")
dim_date["weekday_number"] = dim_date["date"].dt.weekday + 1

# ---- Fact -------------------------------------------------------------------
fact = (df.merge(dim_customer[["customer_key", "customer_name"]], on="customer_name")
          .merge(dim_product[["product_key", "product_name"]], on="product_name")
          .merge(dim_location[["location_key", "province"]], on="province"))
fact = fact[["row_id", "order_id", "order_date", "ship_date", "ship_days", "customer_key", "product_key",
             "location_key", "segment", "order_priority", "ship_mode", "unit_price", "quantity",
             "gross_sales", "discount", "discount_band", "sales", "shipping_cost", "profit",
             "profit_status", "price_band"]].rename(columns={"segment": "business_segment"})
assert len(fact) == len(df), "Join must not add or drop rows"

for name, table in [("fact_sales", fact), ("dim_customer", dim_customer), ("dim_product", dim_product),
                    ("dim_location", dim_location), ("dim_date", dim_date)]:
    table.to_csv(OUT / f"{name}.csv", index=False, date_format="%Y-%m-%d")
    print(f"{name:<14} {len(table):>6,} rows  {table.shape[1]:>2} cols")
