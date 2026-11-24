# DAX Measures: Retail Shop Analysis Dashboard

Create a blank table named **`_Measures`** (*Home → Enter data → name it `_Measures` → Load*),
then add each measure with *Modeling → New measure*. Keeping all measures in one table makes
them easy to find and explain.

Expected values with **no filters applied** are shown, so you can check that each measure is correct.
(They come from `results/eda_metrics.json` and `sql/query_results/`.)

## 1. Core KPIs

```DAX
Total Revenue = SUM ( fact_sales[sales] )                                   -- 14,915,600.82

Total Profit = SUM ( fact_sales[profit] )                                   -- 1,521,767.98

Profit Margin % = DIVIDE ( [Total Profit], [Total Revenue] )                -- 10.20 %  (format as %)

Total Orders = DISTINCTCOUNT ( fact_sales[order_id] )                       -- 5,496

Average Order Value = DIVIDE ( [Total Revenue], [Total Orders] )            -- 2,713.90

Units Sold = SUM ( fact_sales[quantity] )                                   -- 214,777

Total Customers = DISTINCTCOUNT ( fact_sales[customer_key] )                -- 795

Avg Discount % = AVERAGE ( fact_sales[discount] )                           -- 4.97 %

Total Shipping Cost = SUM ( fact_sales[shipping_cost] )

Loss Line Items % =
DIVIDE (
    CALCULATE ( COUNTROWS ( fact_sales ), fact_sales[profit] < 0 ),
    COUNTROWS ( fact_sales )
)                                                                           -- 50.8 %
```

## 2. Time intelligence
These require `dim_date` to be marked as the date table (*Table tools → Mark as date table → `date`*).

```DAX
Revenue PY = CALCULATE ( [Total Revenue], SAMEPERIODLASTYEAR ( dim_date[date] ) )

Revenue YoY % = DIVIDE ( [Total Revenue] - [Revenue PY], [Revenue PY] )     -- 2012: +8.24 %

Profit PY = CALCULATE ( [Total Profit], SAMEPERIODLASTYEAR ( dim_date[date] ) )

Revenue YTD = TOTALYTD ( [Total Revenue], dim_date[date] )

Revenue 3M Rolling =
CALCULATE (
    [Total Revenue],
    DATESINPERIOD ( dim_date[date], MAX ( dim_date[date] ), -3, MONTH )
) / 3                                                    -- average monthly revenue of the last 3 months
```

> **Tip:** plot `Revenue 3M Rolling` against `dim_date[year_month]` on the same line chart as
> `Total Revenue` to show the smoothed trend. Both lines share one axis because both are revenue.

## 3. Product analysis

```DAX
Product Revenue Rank =
RANKX ( ALL ( dim_product[product_name] ), [Total Revenue], , DESC, DENSE )

Is Loss Making = IF ( [Total Profit] < 0, "Loss", "Profit" )

Revenue Share % = DIVIDE ( [Total Revenue], CALCULATE ( [Total Revenue], ALL ( dim_product ) ) )
```

Use **Top N filters** in the visual's filter pane (*Filter type → Top N → 10 → by Total Revenue*)
for the Top 10 and Bottom 10 product charts. This is simpler than writing ranking measures.

## 4. Customer analysis

```DAX
Customers (in context) = DISTINCTCOUNT ( fact_sales[customer_key] )

Orders per Customer = DIVIDE ( [Total Orders], [Customers (in context)] )   -- 6.91 overall
-- (the notebook reports 6.94 = average of each customer's own order count; it is slightly higher
--  because 21 order IDs are shared by two customers and are counted once per customer there)

Repeat Customers =
COUNTROWS (
    FILTER (
        VALUES ( fact_sales[customer_key] ),
        CALCULATE ( DISTINCTCOUNT ( fact_sales[order_id] ) ) > 1
    )
)                                                                           -- 784

Repeat Customer Rate % = DIVIDE ( [Repeat Customers], [Customers (in context)] )   -- 98.6 %

Revenue per Customer = DIVIDE ( [Total Revenue], [Customers (in context)] )
```

## 5. Regional analysis

```DAX
Province Revenue Rank =
RANKX ( ALL ( dim_location[province] ), [Total Revenue], , DESC, DENSE )

Margin vs Company Avg (pp) =
( [Profit Margin %] - CALCULATE ( [Profit Margin %], ALL ( dim_location ) ) ) * 100
```

## 6. Conditional formatting helper

```DAX
Margin Color =
SWITCH (
    TRUE (),
    [Profit Margin %] < 0,    "#e34948",   -- loss: red
    [Profit Margin %] < 0.05, "#eda100",   -- weak: amber
    "#2a78d6"                              -- healthy: blue
)
```
Apply it via *Format → Bars/Columns → Colors → fx → Format style: Field value → Margin Color*.

## Formatting checklist
| Measure | Format |
|---|---|
| Total Revenue, Total Profit, Average Order Value | Currency, 0 decimals; cards display **Millions/Thousands** |
| Profit Margin %, Revenue YoY %, Repeat Customer Rate %, Loss Line Items % | Percentage, 1 decimal |
| Total Orders, Units Sold, Total Customers | Whole number, thousands separator |
