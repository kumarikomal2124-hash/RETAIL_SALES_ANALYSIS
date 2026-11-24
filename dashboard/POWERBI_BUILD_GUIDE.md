# Power BI Dashboard: Step-by-Step Build Guide

**Output file:** `dashboard/powerbi_dashboard.pbix`
**Tool:** Power BI Desktop (free, Windows). Download it from the Microsoft Store or from powerbi.microsoft.com.
**Time needed:** about 60–90 minutes the first time.

> **Why there is no ready-made `.pbix` in this folder.** A `.pbix` file can only be created inside
> Power BI Desktop. Everything else is prepared for you here: the data model, every DAX measure, the
> colour theme and a layout preview of each page. Follow the steps below to build the dashboard
> yourself. This is also the best preparation for viva questions about it.

The previews in `dashboard/preview/` show the target layout. They were drawn in Python from the
same data, so your numbers in Power BI must match them exactly.

---

## Step 0 · Prepare the data (already done if you ran the pipeline)
```bash
python scripts/prepare_powerbi_data.py
```
This creates five CSV files in `dashboard/powerbi_data/`.

## Step 1 · Load the data
1. Open Power BI Desktop → **Get data → Text/CSV**.
2. Load each file: `fact_sales.csv`, `dim_customer.csv`, `dim_product.csv`, `dim_location.csv`, `dim_date.csv`.
3. On each preview click **Transform Data** and check the column types:
   * `order_date`, `ship_date`, `date`, `first_order`, `last_order` → **Date**
   * `sales`, `profit`, `unit_price`, `shipping_cost`, `gross_sales`, `discount` → **Decimal number**
   * `order_id`, `quantity`, all `*_key` columns → **Whole number**
4. **Close & Apply**.

## Step 2 · Build the relationships (Model view)
Drag the following fields. Each relationship is **many-to-one (\*:1)** with a **single** cross-filter direction.

| From (many side) | To (one side) |
|---|---|
| `fact_sales[customer_key]` | `dim_customer[customer_key]` |
| `fact_sales[product_key]` | `dim_product[product_key]` |
| `fact_sales[location_key]` | `dim_location[location_key]` |
| `fact_sales[order_date]` | `dim_date[date]` |

Then:
* Select `dim_date` → **Table tools → Mark as date table** → column `date`.
* `dim_date[month_name]` → **Sort by column** → `month_number`.
* `dim_customer[rfm_segment]` → **Sort by column** → `rfm_segment_order`.
* `dim_location[province]` → **Data category → State or Province**; `dim_location[country]` → **Country/Region**.
  This lets the map visual place provinces correctly.
* Hide all `*_key` columns from the report view (right-click → Hide in report view).

The resulting star schema:
```
 dim_date ──┐
            │
 dim_customer ── fact_sales ── dim_product
            │
 dim_location┘
```

## Step 3 · Apply the theme
**View → Themes → Browse for themes →** `dashboard/retail_theme.json`.
This sets the colour palette (colour-blind safe), the fonts and the card style.

## Step 4 · Create the measures
Create the table `_Measures` and add every measure from **`DAX_measures.md`**.
Check the card values against the "expected" numbers listed there.

## Step 5 · Build the pages
Page size: **16:9 (1280 × 720)**. On every page:
* add a **title text box** at the top left,
* put the **slicer row** directly below the title,
* sync the slicers across pages (**View → Sync slicers**), so a filter chosen on one page applies to all pages.

### Slicers (all pages)
| Slicer | Field | Style |
|---|---|---|
| Date | `dim_date[date]` | Between (date range) |
| Category | `dim_product[category]` | Dropdown |
| Region | `dim_location[region]` | Dropdown |
| Customer segment | `dim_customer[rfm_segment]` | Dropdown |
| Business segment *(optional)* | `fact_sales[business_segment]` | Dropdown |

### Page 1 · Executive Overview  (`preview/page1_executive_overview.png`)
| Visual | Fields |
|---|---|
| 4 × **Card** | Total Revenue · Total Profit · Total Orders · Average Order Value |
| Card *(optional)* | Profit Margin % |
| **Line chart**: Revenue trend | X: `dim_date[year_month]` · Y: Total Revenue (+ Revenue 3M Rolling) |
| **Clustered bar**: Revenue by category | Y: `dim_product[category]` · X: Total Revenue |
| **Clustered column**: Revenue & profit by year | X: `dim_date[year]` · Y: Total Revenue; *duplicate the visual for profit, and do not use a dual axis* |

### Page 2 · Product Analysis  (`preview/page2_product_analysis.png`)
| Visual | Fields |
|---|---|
| **Bar**: Top 10 products | `product_name`, Total Revenue · *Filter: Top N = 10 by Total Revenue* |
| **Bar**: Bottom 10 products | `product_name`, Total Revenue · *Filter: Bottom N = 10* |
| **Bar**: Profit by sub-category | `sub_category`, Total Profit · colour via `Margin Color` measure |
| **Matrix**: Category profitability | Rows: category → sub_category · Values: Revenue, Profit, Profit Margin %, Units Sold |
| **Scatter** *(optional)* | X: Avg Discount % · Y: Profit Margin % · Details: sub_category |

### Page 3 · Customer Analysis  (`preview/page3_customer_analysis.png`)
| Visual | Fields |
|---|---|
| Cards | Total Customers · Repeat Customer Rate % · Orders per Customer |
| **Bar**: Customers by RFM segment | `rfm_segment`, Customers (in context) |
| **Bar**: Revenue by RFM segment | `rfm_segment`, Total Revenue |
| **Table**: Top 10 customers | `customer_name`, Total Revenue, Total Orders, Total Profit · *Top N = 10* |
| **Line**: Purchasing trend by business segment | X: `year`, Legend: `business_segment`, Y: Total Revenue |

### Page 4 · Regional Analysis  (`preview/page4_regional_analysis.png`)
| Visual | Fields |
|---|---|
| **Filled map** (or Map) | Location: `province` · Colour saturation: Total Revenue |
| **Bar**: Revenue by province | `province`, Total Revenue |
| **Bar**: Profit margin by province | `province`, Profit Margin % · colour via `Margin Color` |
| **Matrix**: Region × Category | Rows: region · Columns: category · Values: Total Profit (conditional-format background) |

> **About "store performance".** The dataset has no store IDs. Each **province** is treated as a
> sales territory, so the province visuals provide the store-level comparison. State this
> assumption on the page with a small text box.

## Step 6 · Interactivity and polish
* **Edit interactions** (Format → Edit interactions): clicking a category bar should filter the other visuals.
* Add **tooltips** to bar charts: drag Profit Margin % and Units Sold into the *Tooltips* field well.
* Add **page navigation buttons** (Insert → Buttons → Navigator → Page navigator).
* Align visuals with **Format → Align** and keep equal spacing.

## Step 7 · Validate
With no slicers selected, the cards must show:
**Revenue $14.92M · Profit $1.52M · Orders 5,496 · AOV $2,713.90 · Margin 10.2%**.
Select *Year = 2012* → Revenue should be **$3.72M**.

## Step 8 · Save and export
* **File → Save as** → `dashboard/powerbi_dashboard.pbix`
* Export screenshots of each page (or **File → Export → PDF**) into `dashboard/screenshots/` and
  paste them into the report in place of the preview images (Chapter 21).
