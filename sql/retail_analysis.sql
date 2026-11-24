/* =====================================================================
   Retail Shop Analysis Using Data Analytics - SQL Implementation
   ---------------------------------------------------------------------
   Database : SQLite 3 (file: dataset/retail.db)
   Run with : python scripts/build_database.py
              (loads dataset/cleaned_data.csv into the staging table
               stg_sales, then executes this whole file)

   Design   : STAR SCHEMA
              fact_sales      - one row per order line (8,399 rows)
              dim_customer    - one row per customer
              dim_product     - one row per product
              dim_location    - one row per province (with its region)

   Why a star schema? The fact table holds the numbers (sales, profit,
   quantity), and the dimension tables hold descriptions (who, what,
   where). This is the standard layout for analytics and for Power BI.

   Note: in this dataset a few order_ids are linked to more than one
   customer, so customer and location are stored per line, not per order.

   Each analysis query starts with a marker line of the form
       -- @query <name> | <description>
   which the Python runner uses to export each result to CSV.
   ===================================================================== */

PRAGMA foreign_keys = ON;

/* ---------------------------------------------------------------------
   PART A - SCHEMA CREATION (DDL)
   --------------------------------------------------------------------- */
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_location;

CREATE TABLE dim_customer (
    customer_id     INTEGER PRIMARY KEY,
    customer_name   TEXT    NOT NULL UNIQUE
);

CREATE TABLE dim_product (
    product_id          INTEGER PRIMARY KEY,
    product_name        TEXT NOT NULL UNIQUE,
    category            TEXT NOT NULL,
    sub_category        TEXT NOT NULL,
    product_container   TEXT,
    product_base_margin REAL CHECK (product_base_margin BETWEEN 0 AND 1)
);

CREATE TABLE dim_location (
    location_id INTEGER PRIMARY KEY,
    province    TEXT NOT NULL UNIQUE,
    region      TEXT NOT NULL
);

CREATE TABLE fact_sales (
    row_id          INTEGER PRIMARY KEY,
    order_id        INTEGER NOT NULL,
    order_date      TEXT    NOT NULL,          -- ISO format YYYY-MM-DD
    ship_date       TEXT    NOT NULL,
    order_priority  TEXT,
    ship_mode       TEXT,
    segment         TEXT,
    customer_id     INTEGER NOT NULL REFERENCES dim_customer(customer_id),
    product_id      INTEGER NOT NULL REFERENCES dim_product(product_id),
    location_id     INTEGER NOT NULL REFERENCES dim_location(location_id),
    unit_price      REAL    NOT NULL CHECK (unit_price > 0),
    quantity        INTEGER NOT NULL CHECK (quantity > 0),
    discount        REAL    NOT NULL CHECK (discount BETWEEN 0 AND 1),
    sales           REAL    NOT NULL CHECK (sales > 0),
    shipping_cost   REAL    NOT NULL CHECK (shipping_cost >= 0),
    profit          REAL    NOT NULL
);

/* ---------------------------------------------------------------------
   PART B - LOAD (normalise the staging table into the star schema)
   --------------------------------------------------------------------- */
INSERT INTO dim_customer (customer_name)
SELECT DISTINCT customer_name FROM stg_sales ORDER BY customer_name;

INSERT INTO dim_product (product_name, category, sub_category, product_container, product_base_margin)
SELECT product_name,
       MIN(category), MIN(sub_category), MIN(product_container), MIN(product_base_margin)
FROM stg_sales
GROUP BY product_name
ORDER BY product_name;

INSERT INTO dim_location (province, region)
SELECT DISTINCT province, region FROM stg_sales ORDER BY region, province;

INSERT INTO fact_sales
SELECT s.row_id, s.order_id, s.order_date, s.ship_date, s.order_priority, s.ship_mode,
       s.segment, c.customer_id, p.product_id, l.location_id,
       s.unit_price, s.quantity, s.discount, s.sales, s.shipping_cost, s.profit
FROM stg_sales s
JOIN dim_customer c ON c.customer_name = s.customer_name
JOIN dim_product  p ON p.product_name  = s.product_name
JOIN dim_location l ON l.province      = s.province;

-- Indexes speed up the joins and the date filters used below
CREATE INDEX idx_fact_order_date ON fact_sales(order_date);
CREATE INDEX idx_fact_customer   ON fact_sales(customer_id);
CREATE INDEX idx_fact_product    ON fact_sales(product_id);
CREATE INDEX idx_fact_location   ON fact_sales(location_id);

-- A reusable view that joins the fact table to all dimensions
DROP VIEW IF EXISTS v_sales;
CREATE VIEW v_sales AS
SELECT f.*, c.customer_name, p.product_name, p.category, p.sub_category,
       l.province, l.region,
       CAST(strftime('%Y', f.order_date) AS INTEGER) AS order_year,
       strftime('%Y-%m', f.order_date)               AS year_month
FROM fact_sales f
JOIN dim_customer c USING (customer_id)
JOIN dim_product  p USING (product_id)
JOIN dim_location l USING (location_id);


/* =====================================================================
   PART C - BUSINESS ANALYSIS QUERIES
   ===================================================================== */

-- @query 00_row_counts | Data-load check: row counts in each table
SELECT 'fact_sales'   AS table_name, COUNT(*) AS row_count FROM fact_sales   UNION ALL
SELECT 'dim_customer',               COUNT(*)              FROM dim_customer UNION ALL
SELECT 'dim_product',                COUNT(*)              FROM dim_product  UNION ALL
SELECT 'dim_location',               COUNT(*)              FROM dim_location;

-- @query 01_total_sales_profit | Q1. Overall business KPIs
SELECT ROUND(SUM(sales), 2)                                 AS total_revenue,
       ROUND(SUM(profit), 2)                                AS total_profit,
       ROUND(100.0 * SUM(profit) / SUM(sales), 2)           AS profit_margin_pct,
       COUNT(DISTINCT order_id)                             AS total_orders,
       SUM(quantity)                                        AS total_units,
       COUNT(DISTINCT customer_id)                          AS total_customers,
       ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2)      AS avg_order_value
FROM fact_sales;

-- @query 02_top10_products_revenue | Q2. Top 10 products by revenue
SELECT p.product_name,
       p.category,
       ROUND(SUM(f.sales), 2)                        AS revenue,
       ROUND(SUM(f.profit), 2)                       AS profit,
       SUM(f.quantity)                               AS units_sold,
       ROUND(100.0 * SUM(f.profit) / SUM(f.sales), 2) AS margin_pct
FROM fact_sales f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;

-- @query 03_top10_customers | Q3. Top 10 customers by total spending
SELECT c.customer_name,
       COUNT(DISTINCT f.order_id)                    AS orders,
       ROUND(SUM(f.sales), 2)                        AS total_spent,
       ROUND(SUM(f.profit), 2)                       AS profit_generated,
       ROUND(SUM(f.sales) / COUNT(DISTINCT f.order_id), 2) AS avg_order_value,
       MAX(f.order_date)                             AS last_order_date
FROM fact_sales f
JOIN dim_customer c ON c.customer_id = f.customer_id
GROUP BY c.customer_id
ORDER BY total_spent DESC
LIMIT 10;

-- @query 04_monthly_sales_trend | Q4. Monthly revenue, profit and orders
SELECT strftime('%Y-%m', order_date)        AS year_month,
       ROUND(SUM(sales), 2)                 AS revenue,
       ROUND(SUM(profit), 2)                AS profit,
       COUNT(DISTINCT order_id)             AS orders
FROM fact_sales
GROUP BY year_month
ORDER BY year_month;

-- @query 05_yearly_growth | Q5. Year-over-year revenue growth (window function LAG)
WITH yearly AS (
    SELECT strftime('%Y', order_date) AS order_year,
           SUM(sales)  AS revenue,
           SUM(profit) AS profit
    FROM fact_sales
    GROUP BY order_year
)
SELECT order_year,
       ROUND(revenue, 2)                                            AS revenue,
       ROUND(profit, 2)                                             AS profit,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY order_year))
             / LAG(revenue) OVER (ORDER BY order_year), 2)          AS revenue_growth_pct
FROM yearly
ORDER BY order_year;

-- @query 06_category_performance | Q6. Category-wise performance and share of revenue
SELECT p.category,
       ROUND(SUM(f.sales), 2)                                       AS revenue,
       ROUND(SUM(f.profit), 2)                                      AS profit,
       SUM(f.quantity)                                              AS units_sold,
       ROUND(100.0 * SUM(f.sales) / (SELECT SUM(sales) FROM fact_sales), 2) AS revenue_share_pct,
       ROUND(100.0 * SUM(f.profit) / SUM(f.sales), 2)               AS margin_pct
FROM fact_sales f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- @query 07_region_sales | Q7. Region and province sales with ranking (window function RANK)
SELECT l.region,
       l.province,
       ROUND(SUM(f.sales), 2)                               AS revenue,
       ROUND(SUM(f.profit), 2)                              AS profit,
       ROUND(100.0 * SUM(f.profit) / SUM(f.sales), 2)       AS margin_pct,
       RANK() OVER (ORDER BY SUM(f.sales) DESC)             AS revenue_rank,
       RANK() OVER (ORDER BY SUM(f.profit) / SUM(f.sales) DESC) AS margin_rank
FROM fact_sales f
JOIN dim_location l ON l.location_id = f.location_id
GROUP BY l.location_id
ORDER BY revenue DESC;

-- @query 08_low_sales_products | Q8. Low-performing products: bottom 15 by revenue (with units and orders)
SELECT p.product_name,
       p.category,
       p.sub_category,
       COUNT(DISTINCT f.order_id)    AS orders,
       SUM(f.quantity)               AS units_sold,
       ROUND(SUM(f.sales), 2)        AS revenue,
       ROUND(SUM(f.profit), 2)       AS profit
FROM fact_sales f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY p.product_id
ORDER BY revenue ASC
LIMIT 15;

-- @query 09_average_order_value | Q9. Average order value overall and by customer segment
WITH order_totals AS (
    SELECT order_id, segment, SUM(sales) AS order_value
    FROM fact_sales
    GROUP BY order_id, segment
)
SELECT 'All segments'                AS segment,
       COUNT(*)                      AS orders,
       ROUND(AVG(order_value), 2)    AS avg_order_value
FROM (SELECT order_id, SUM(sales) AS order_value FROM fact_sales GROUP BY order_id)
UNION ALL
SELECT segment, COUNT(*), ROUND(AVG(order_value), 2)
FROM order_totals
GROUP BY segment;

-- @query 10_repeat_customers | Q10. Repeat vs one-time customers
WITH customer_orders AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS n_orders
    FROM fact_sales
    GROUP BY customer_id
)
SELECT CASE WHEN n_orders = 1              THEN '1 order (one-time)'
            WHEN n_orders BETWEEN 2 AND 4  THEN '2-4 orders'
            WHEN n_orders BETWEEN 5 AND 9  THEN '5-9 orders'
            ELSE '10+ orders' END                                  AS customer_type,
       COUNT(*)                                                    AS customers,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customer_orders), 2) AS pct_of_customers
FROM customer_orders
GROUP BY customer_type
ORDER BY MIN(n_orders);

-- @query 11_profit_margin_by_category | Q11. Profit margin by category and sub-category
SELECT p.category,
       p.sub_category,
       ROUND(SUM(f.sales), 2)                           AS revenue,
       ROUND(SUM(f.profit), 2)                          AS profit,
       ROUND(100.0 * SUM(f.profit) / SUM(f.sales), 2)   AS margin_pct
FROM fact_sales f
JOIN dim_product p ON p.product_id = f.product_id
GROUP BY p.category, p.sub_category
ORDER BY p.category, margin_pct DESC;

-- @query 12_loss_making_subcategories | Q12. Sub-categories with a net loss (HAVING clause)
SELECT category, sub_category,
       ROUND(SUM(sales), 2)  AS revenue,
       ROUND(SUM(profit), 2) AS profit
FROM v_sales
GROUP BY category, sub_category
HAVING SUM(profit) < 0
ORDER BY profit;

-- @query 13_discount_impact | Q13. Impact of discount level on profitability (CASE banding)
SELECT CASE WHEN discount <= 0.02 THEN '1) 0-2%'
            WHEN discount <= 0.05 THEN '2) 3-5%'
            WHEN discount <= 0.08 THEN '3) 6-8%'
            ELSE '4) 9%+' END                                          AS discount_band,
       COUNT(*)                                                        AS line_items,
       ROUND(SUM(sales), 2)                                            AS revenue,
       ROUND(100.0 * SUM(profit) / SUM(sales), 2)                      AS margin_pct,
       ROUND(100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS loss_line_pct
FROM fact_sales
GROUP BY discount_band
ORDER BY discount_band;

-- @query 14_ship_mode_performance | Q14. Shipping mode: volume, cost and margin
SELECT ship_mode,
       COUNT(*)                                          AS line_items,
       ROUND(SUM(sales), 2)                              AS revenue,
       ROUND(SUM(shipping_cost), 2)                      AS shipping_cost,
       ROUND(100.0 * SUM(profit) / SUM(sales), 2)        AS margin_pct,
       ROUND(AVG(julianday(ship_date) - julianday(order_date)), 2) AS avg_ship_days
FROM fact_sales
GROUP BY ship_mode
ORDER BY revenue DESC;

-- @query 15_top_product_per_category | Q15. Best-selling product in each category (ROW_NUMBER)
WITH ranked AS (
    SELECT category, product_name, SUM(sales) AS revenue,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY SUM(sales) DESC) AS rn
    FROM v_sales
    GROUP BY category, product_name
)
SELECT category, product_name, ROUND(revenue, 2) AS revenue
FROM ranked
WHERE rn = 1
ORDER BY revenue DESC;

-- @query 16_rfm_base | Q16. RFM base table per customer (input to customer segmentation)
SELECT c.customer_name,
       CAST(julianday((SELECT MAX(order_date) FROM fact_sales)) - julianday(MAX(f.order_date)) + 1
            AS INTEGER)                    AS recency_days,
       COUNT(DISTINCT f.order_id)          AS frequency,
       ROUND(SUM(f.sales), 2)              AS monetary
FROM fact_sales f
JOIN dim_customer c ON c.customer_id = f.customer_id
GROUP BY c.customer_id
ORDER BY monetary DESC;
