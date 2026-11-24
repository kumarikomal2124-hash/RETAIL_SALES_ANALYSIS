"""
render_dashboard_preview.py - draw a layout preview of each Power BI page from the real data.

Usage (from the project root, after prepare_powerbi_data.py):
    python scripts/render_dashboard_preview.py

These PNGs are DESIGN PREVIEWS rendered with matplotlib, not Power BI screenshots. They show
the target layout and the numbers the finished Power BI dashboard must reproduce.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "notebooks"))
import viz_style as vs  # noqa: E402

vs.apply_style()
DATA = ROOT / "dashboard" / "powerbi_data"
OUT = ROOT / "dashboard" / "preview"
OUT.mkdir(parents=True, exist_ok=True)
PAGE_BG, PANEL = "#f4f3f0", "#ffffff"

fact = pd.read_csv(DATA / "fact_sales.csv", parse_dates=["order_date"])
cust = pd.read_csv(DATA / "dim_customer.csv")
prod = pd.read_csv(DATA / "dim_product.csv")
loc = pd.read_csv(DATA / "dim_location.csv")
f = fact.merge(cust, on="customer_key").merge(prod, on="product_key").merge(loc, on="location_key")
f["year"] = f["order_date"].dt.year
f["year_month"] = f["order_date"].dt.to_period("M").dt.to_timestamp()
CATS = ["Technology", "Furniture", "Office Supplies"]


def short(s, n=34):
    return s if len(s) <= n else s[: n - 1] + "…"


def fmt_money(v):
    return f"${v/1e6:.2f}M" if abs(v) >= 1e6 else f"${v/1e3:,.0f}K" if abs(v) >= 1e4 else f"${v:,.2f}"


def new_page(title, subtitle):
    fig = plt.figure(figsize=(12.8, 7.2), dpi=150, facecolor=PAGE_BG)
    fig.text(0.015, 0.955, title, fontsize=17, fontweight="bold", color=vs.TEXT)
    fig.text(0.015, 0.925, subtitle, fontsize=9, color=vs.TEXT_2)
    # slicer row
    for i, s in enumerate(["Date: 01/01/2009 – 31/12/2012", "Category: All", "Region: All", "Customer segment: All"]):
        x = 0.015 + i * 0.165
        fig.patches.append(FancyBboxPatch((x, 0.862), 0.155, 0.04, boxstyle="round,pad=0,rounding_size=0.006",
                                          transform=fig.transFigure, facecolor=PANEL, edgecolor=vs.GRID))
        fig.text(x + 0.008, 0.882, s + "  ▾", fontsize=8.5, color=vs.TEXT_2, va="center")
    fig.text(0.985, 0.955, "Design preview rendered from project data (not a Power BI screenshot)",
             fontsize=7.5, color=vs.GRAY, ha="right")
    return fig


def panel(fig, rect, title=None, lpad=0.0):
    """Add an axes on a white rounded card; lpad widens the card leftwards to hold axis labels."""
    ax = fig.add_axes(rect)
    fig.patches.append(FancyBboxPatch((rect[0] - 0.008 - lpad, rect[1] - 0.035), rect[2] + 0.016 + lpad, rect[3] + 0.075,
                                      boxstyle="round,pad=0,rounding_size=0.008", transform=fig.transFigure,
                                      facecolor=PANEL, edgecolor=vs.GRID, zorder=-1))
    ax.set_facecolor(PANEL)
    if title:
        ax.set_title(title, fontsize=10.5, pad=8)
    ax.tick_params(labelsize=8)
    return ax


def card(fig, x, y, w, h, label, value, note=None):
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.008",
                                      transform=fig.transFigure, facecolor=PANEL, edgecolor=vs.GRID))
    fig.text(x + 0.012, y + h - 0.035, label, fontsize=9, color=vs.TEXT_2)
    fig.text(x + 0.012, y + 0.035 if note else y + 0.025, value, fontsize=21, fontweight="bold", color=vs.TEXT)
    if note:
        fig.text(x + 0.012, y + 0.012, note, fontsize=7.5, color=vs.TEXT_2)


def label_bars(ax, values, fmt, inside=False):
    for y, v in enumerate(values):
        ax.text(v, y, " " + fmt(v), va="center", fontsize=7.5, color=vs.TEXT_2,
                ha="left" if v >= 0 else "right")


# ------------------------------------------------------------------ Page 1
rev, prof = f["sales"].sum(), f["profit"].sum()
orders = f["order_id"].nunique()
fig = new_page("Executive Overview", "Retail Shop Analysis · Superstore Sales 2009–2012 · all values in USD")
cw = 0.233
for i, (lab, val, note) in enumerate([("Total Revenue", fmt_money(rev), None),
                                      ("Total Profit", fmt_money(prof), f"Margin {prof/rev*100:.1f}%"),
                                      ("Total Orders", f"{orders:,}", f"{len(f):,} line items"),
                                      ("Average Order Value", f"${rev/orders:,.0f}", None)]):
    card(fig, 0.015 + i * (cw + 0.01), 0.71, cw, 0.13, lab, val, note)

m = f.groupby("year_month")["sales"].sum()
ax = panel(fig, [0.055, 0.095, 0.53, 0.53], "Monthly revenue trend", lpad=0.035)
ax.plot(m.index, m.values, color="#9ec5f4", lw=1.3, label="Monthly revenue")
ax.plot(m.index, m.rolling(3).mean(), color=vs.BLUE, lw=2.2, label="3-month rolling avg")
vs.money_axis(ax); ax.legend(fontsize=8, loc="upper right")

c = f.groupby("category")["sales"].sum().reindex(CATS[::-1])
ax = panel(fig, [0.72, 0.4, 0.26, 0.195], "Revenue by category", lpad=0.075)
ax.barh(c.index, c.values, color=[vs.CATEGORY_COLORS[k] for k in c.index], height=0.6)
label_bars(ax, c.values, lambda v: f"${v/1e6:.2f}M"); ax.set_xlim(0, c.max() * 1.35); ax.set_xticks([])
ax.grid(False)

y = f.groupby("year")[["sales", "profit"]].sum()
ax = panel(fig, [0.645, 0.095, 0.15, 0.2], "Revenue by year", lpad=0.035)
ax.bar(y.index.astype(str), y["sales"], color=vs.BLUE, width=0.6); vs.money_axis(ax)
ax = panel(fig, [0.835, 0.095, 0.145, 0.2], "Profit by year", lpad=0.035)
ax.bar(y.index.astype(str), y["profit"], color=vs.AQUA, width=0.6); vs.money_axis(ax)
fig.savefig(OUT / "page1_executive_overview.png", facecolor=PAGE_BG); plt.close(fig)

# ------------------------------------------------------------------ Page 2
fig = new_page("Product Analysis", "Which products and categories drive revenue and profit?")
p = f.groupby(["product_name", "category"]).agg(revenue=("sales", "sum"), profit=("profit", "sum")).reset_index()
top = p.nlargest(10, "revenue").iloc[::-1]
ax = panel(fig, [0.19, 0.47, 0.27, 0.34], "Top 10 products by revenue", lpad=0.17)
ax.barh(top["product_name"].map(short), top["revenue"], color=[vs.CATEGORY_COLORS[k] for k in top["category"]], height=0.65)
vs.money_axis(ax, "x"); ax.tick_params(axis="y", labelsize=6.8)

low = p.nsmallest(10, "revenue")
ax = panel(fig, [0.19, 0.07, 0.27, 0.31], "Bottom 10 products by revenue", lpad=0.17)
ax.barh(low["product_name"].map(short), low["revenue"], color=vs.GRAY, height=0.65)
ax.tick_params(axis="y", labelsize=6.8); vs.money_axis(ax, "x")

s = f.groupby("sub_category").agg(profit=("profit", "sum"), revenue=("sales", "sum")).sort_values("profit")
ax = panel(fig, [0.645, 0.07, 0.15, 0.74], "Profit by sub-category", lpad=0.115)
ax.barh([short(i, 24) for i in s.index], s["profit"], color=np.where(s["profit"] >= 0, vs.POS, vs.NEG), height=0.65)
ax.axvline(0, color=vs.TEXT_2, lw=0.7); vs.money_axis(ax, "x"); ax.tick_params(axis="y", labelsize=7)

cat = f.groupby("category").agg(revenue=("sales", "sum"), profit=("profit", "sum"), units=("quantity", "sum")).loc[CATS]
cat["margin"] = cat["profit"] / cat["revenue"] * 100
ax = panel(fig, [0.83, 0.07, 0.15, 0.74], "Category profitability")
ax.axis("off")
for i, (k, r) in enumerate(cat.iterrows()):
    yy = 0.93 - i * 0.33
    ax.add_patch(plt.Rectangle((0, yy - 0.012), 0.05, 0.05, color=vs.CATEGORY_COLORS[k], transform=ax.transAxes))
    ax.text(0.09, yy, k, fontsize=9.5, fontweight="bold", color=vs.TEXT, transform=ax.transAxes)
    for j, (lab, val) in enumerate([("Revenue", fmt_money(r["revenue"])), ("Profit", fmt_money(r["profit"])),
                                    ("Margin", f"{r['margin']:.1f}%"), ("Units", f"{r['units']:,.0f}")]):
        ax.text(0.09, yy - 0.06 - j * 0.055, lab, fontsize=8, color=vs.TEXT_2, transform=ax.transAxes)
        ax.text(0.95, yy - 0.06 - j * 0.055, val, fontsize=8, color=vs.TEXT, ha="right", transform=ax.transAxes)
fig.savefig(OUT / "page2_product_analysis.png", facecolor=PAGE_BG); plt.close(fig)

# ------------------------------------------------------------------ Page 3
fig = new_page("Customer Analysis", "Who buys, how often, and which RFM segments matter most?")
co = f.groupby("customer_name")["order_id"].nunique()
for i, (lab, val) in enumerate([("Total Customers", f"{len(co):,}"),
                                ("Repeat Customer Rate", f"{(co > 1).mean()*100:.1f}%"),
                                ("Orders per Customer", f"{co.mean():.2f}"),
                                ("Revenue per Customer", f"${rev/len(co):,.0f}")]):
    card(fig, 0.015 + i * (cw + 0.01), 0.71, cw, 0.13, lab, val)
order = ["High-Value (Champions)", "Loyal Customers", "Potential Loyalists", "New Customers",
         "Need Attention", "At-Risk Customers", "Hibernating / Lost"]
seg_c = cust["rfm_segment"].value_counts().reindex(order).iloc[::-1]
seg_r = f.groupby("rfm_segment")["sales"].sum().reindex(order).iloc[::-1]
ax = panel(fig, [0.15, 0.37, 0.16, 0.25], "Customers by RFM segment", lpad=0.13)
ax.barh(seg_c.index, seg_c.values, color=vs.GRAY, height=0.6); ax.tick_params(axis="y", labelsize=7.2)
label_bars(ax, seg_c.values, lambda v: f"{v:.0f}"); ax.set_xlim(0, seg_c.max() * 1.25)
ax = panel(fig, [0.15, 0.07, 0.16, 0.22], "Revenue by RFM segment", lpad=0.13)
ax.barh(seg_r.index, seg_r.values, color=vs.BLUE, height=0.6); ax.tick_params(axis="y", labelsize=7.2)
vs.money_axis(ax, "x"); ax.set_xlim(0, seg_r.max() * 1.15)

t = f.groupby("customer_name").agg(revenue=("sales", "sum"), orders=("order_id", "nunique"),
                                   profit=("profit", "sum")).nlargest(10, "revenue")
ax = panel(fig, [0.365, 0.07, 0.27, 0.55], "Top 10 customers")
ax.axis("off")
cols = [("Customer", 0.0, "left"), ("Revenue", 0.62, "right"), ("Orders", 0.79, "right"), ("Profit", 1.0, "right")]
for name, x, ha in cols:
    ax.text(x, 0.97, name, fontsize=8.5, fontweight="bold", color=vs.TEXT, ha=ha, transform=ax.transAxes)
for i, (n, r) in enumerate(t.iterrows()):
    yy = 0.88 - i * 0.088
    for (val, (_, x, ha)) in zip([short(n, 22), f"${r['revenue']:,.0f}", f"{r['orders']:.0f}", ("-" if r["profit"] < 0 else "") + f"${abs(r['profit']):,.0f}"], cols):
        ax.text(x, yy, val, fontsize=8, color=vs.TEXT if x == 0 else vs.TEXT_2, ha=ha, transform=ax.transAxes)
    ax.axhline(yy - 0.03, color=vs.GRID, lw=0.6)

bs = f.pivot_table(index="year", columns="business_segment", values="sales", aggfunc="sum")
ax = panel(fig, [0.69, 0.07, 0.29, 0.55], "Revenue by business segment and year", lpad=0.04)
for k, col in zip(["Corporate", "Home Office", "Consumer", "Small Business"], [vs.BLUE, vs.ORANGE, vs.AQUA, vs.VIOLET]):
    ax.plot(bs.index.astype(str), bs[k], color=col, marker="o", ms=4, label=k)
vs.money_axis(ax); ax.legend(fontsize=7.5, ncol=2, loc="upper right")
fig.savefig(OUT / "page3_customer_analysis.png", facecolor=PAGE_BG); plt.close(fig)

# ------------------------------------------------------------------ Page 4
fig = new_page("Regional Analysis", "Province = sales territory (dataset has no store IDs) · 13 provinces in 8 regions")
pv = f.groupby(["province", "region"]).agg(revenue=("sales", "sum"), profit=("profit", "sum")).reset_index()
pv["margin"] = pv["profit"] / pv["revenue"] * 100
overall = prof / rev * 100
a = pv.sort_values("revenue")
ax = panel(fig, [0.14, 0.07, 0.22, 0.74], "Revenue by province", lpad=0.115)
ax.barh(a["province"], a["revenue"], color=vs.BLUE, height=0.65); vs.money_axis(ax, "x")
ax.tick_params(axis="y", labelsize=7.5)
b = pv.sort_values("margin")
ax = panel(fig, [0.49, 0.07, 0.2, 0.74], "Profit margin by province (amber = below 5%)", lpad=0.12)
cols_m = np.where(b["margin"] < 5, vs.YELLOW, vs.BLUE)
ax.barh(b["province"], b["margin"], color=cols_m, height=0.65)
ax.axvline(overall, color=vs.TEXT_2, ls="--", lw=0.9)
ax.text(overall, len(b) - 0.4, f" company {overall:.1f}%", fontsize=7, color=vs.TEXT_2)
label_bars(ax, b["margin"].values, lambda v: f"{v:.1f}%"); ax.set_xlim(0, b["margin"].max() * 1.25)
ax.tick_params(axis="y", labelsize=7.5)

rc = f.pivot_table(index="region", columns="category", values="profit", aggfunc="sum")[CATS]
rc = rc.loc[f.groupby("region")["sales"].sum().sort_values(ascending=False).index]
ax = panel(fig, [0.80, 0.07, 0.18, 0.74], "Profit: region × category ($K)", lpad=0.065)
lim = np.abs(rc.values).max()
ax.imshow(rc.values, cmap="RdBu", vmin=-lim, vmax=lim, aspect="auto")
ax.set_xticks(range(3)); ax.set_xticklabels(["Tech", "Furn", "Office"], fontsize=7.5)
ax.set_yticks(range(len(rc))); ax.set_yticklabels([short(r, 14) for r in rc.index], fontsize=7.5)
ax.grid(False)
for i in range(rc.shape[0]):
    for j in range(3):
        v = rc.values[i, j]
        ax.text(j, i, f"{v/1e3:.0f}", ha="center", va="center", fontsize=7.5,
                color="white" if abs(v) > lim * 0.55 else vs.TEXT)
fig.savefig(OUT / "page4_regional_analysis.png", facecolor=PAGE_BG); plt.close(fig)

print("Saved 4 preview pages to", OUT.relative_to(ROOT))
