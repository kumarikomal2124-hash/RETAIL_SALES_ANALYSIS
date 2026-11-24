# SQL Query Results

Generated automatically by `scripts/build_database.py` from `sql/retail_analysis.sql`.


## Data-load check: row counts in each table

`00_row_counts.csv` · 4 rows

| table_name   |   row_count |
|:-------------|------------:|
| fact_sales   |        8399 |
| dim_customer |         795 |
| dim_product  |        1263 |
| dim_location |          13 |



## Q1. Overall business KPIs

`01_total_sales_profit.csv` · 1 rows

|   total_revenue |   total_profit |   profit_margin_pct |   total_orders |   total_units |   total_customers |   avg_order_value |
|----------------:|---------------:|--------------------:|---------------:|--------------:|------------------:|------------------:|
|   14,915,600.82 |   1,521,767.98 |               10.20 |       5,496.00 |    214,777.00 |            795.00 |          2,713.90 |



## Q2. Top 10 products by revenue

`02_top10_products_revenue.csv` · 10 rows

| product_name                                                  | category        |    revenue |     profit |   units_sold |   margin_pct |
|:--------------------------------------------------------------|:----------------|-----------:|-----------:|-------------:|-------------:|
| Global Troy™ Executive Leather Low-Back Tilter                | Furniture       | 275,941.52 |  79,284.78 |          550 |        28.73 |
| Polycom ViewStation™ ISDN Videoconferencing Unit              | Technology      | 255,303.97 | -17,771.27 |           41 |        -6.96 |
| Canon PC940 Copier                                            | Technology      | 210,910.68 |  47,705.85 |          474 |        22.62 |
| Riverside Palais Royal Lawyers Bookcase, Royale Cherry Finish | Furniture       | 206,494.13 |  14,291.57 |          236 |         6.92 |
| Hewlett Packard LaserJet 3310 Copier                          | Technology      | 194,880.35 |  73,299.61 |          334 |        37.61 |
| Bretford CR8500 Series Meeting Room Furniture                 | Furniture       | 147,412.21 |  -1,989.87 |          407 |        -1.35 |
| Sharp AL-1530CS Digital Copier                                | Technology      | 130,046.81 |  11,770.30 |          260 |         9.05 |
| Hewlett-Packard cp1700 [D, PS] Series Color Inkjet Printers   | Technology      | 128,100.43 |  55,281.39 |          269 |        43.15 |
| GBC DocuBind 200 Manual Binding Machine                       | Office Supplies | 120,342.74 |  50,462.53 |          286 |        41.93 |
| Canon imageCLASS 2200 Advanced Copier                         | Technology      | 114,173.41 | -31,885.68 |           32 |       -27.93 |



## Q3. Top 10 customers by total spending

`03_top10_customers.csv` · 10 rows

| customer_name     |   orders |   total_spent |   profit_generated |   avg_order_value | last_order_date   |
|:------------------|---------:|--------------:|-------------------:|------------------:|:------------------|
| Emily Phan        |        8 |    117,124.44 |          34,005.44 |         14,640.55 | 2012-11-26        |
| Deborah Brumfield |       12 |     97,433.14 |          31,121.22 |          8,119.43 | 2012-01-03        |
| Roy Skaria        |       18 |     92,542.15 |           1,343.94 |          5,141.23 | 2012-12-04        |
| Sylvia Foulston   |       18 |     88,875.76 |           5,141.90 |          4,937.54 | 2012-10-12        |
| Grant Carroll     |       17 |     88,417.00 |          27,977.29 |          5,201.00 | 2012-11-11        |
| Alejandro Grove   |        9 |     83,561.93 |          20,588.92 |          9,284.66 | 2012-09-01        |
| Darren Budd       |       26 |     81,577.34 |           1,857.66 |          3,137.59 | 2012-11-14        |
| Julia Barnett     |       12 |     80,044.45 |          -1,956.09 |          6,670.37 | 2012-12-12        |
| John Lucas        |       14 |     79,696.19 |          12,725.08 |          5,692.58 | 2012-12-02        |
| Liz MacKendrick   |       14 |     76,306.43 |          20,397.24 |          5,450.46 | 2012-07-02        |



## Q4. Monthly revenue, profit and orders

`04_monthly_sales_trend.csv` · 48 rows

| year_month   |    revenue |    profit |   orders |
|:-------------|-----------:|----------:|---------:|
| 2009-01      | 516,302.96 | 62,326.40 |      133 |
| 2009-02      | 332,480.64 | 30,422.68 |      101 |
| 2009-03      | 411,628.73 | 22,802.96 |      124 |
| 2009-04      | 393,276.48 | 39,132.73 |      118 |
| 2009-05      | 230,145.54 | 18,035.35 |      119 |
| 2009-06      | 263,456.07 | 34,640.55 |      105 |
| 2009-07      | 380,503.97 | 41,749.43 |      120 |
| 2009-08      | 329,754.72 | 14,682.84 |      127 |
| 2009-09      | 325,292.31 | 46,652.05 |      123 |
| 2009-10      | 361,555.27 | 55,228.01 |      100 |
| 2009-11      | 248,933.43 | 16,222.22 |      106 |
| 2009-12      | 415,809.35 | 52,643.51 |      118 |
| 2010-01      | 336,526.68 | 48,177.27 |      108 |
| 2010-02      | 271,580.51 | 25,999.13 |      109 |
| 2010-03      | 217,808.01 |  1,116.68 |      110 |
| 2010-04      | 266,968.59 | 17,306.51 |       95 |
| 2010-05      | 283,534.28 | 42,636.66 |      129 |
| 2010-06      | 293,080.66 | 36,130.26 |      108 |
| 2010-07      | 229,885.50 | 15,918.45 |      109 |
| 2010-08      | 207,937.01 | 21,862.78 |      125 |



## Q5. Year-over-year revenue growth (window function LAG)

`05_yearly_growth.csv` · 4 rows

|   order_year |      revenue |     profit |   revenue_growth_pct |
|-------------:|-------------:|-----------:|---------------------:|
|         2009 | 4,209,139.46 | 434,538.73 |               nan    |
|         2010 | 3,549,680.80 | 363,871.48 |               -15.67 |
|         2011 | 3,436,816.70 | 381,455.99 |                -3.18 |
|         2012 | 3,719,963.86 | 341,901.78 |                 8.24 |



## Q6. Category-wise performance and share of revenue

`06_category_performance.csv` · 3 rows

| category        |      revenue |     profit |   units_sold |   revenue_share_pct |   margin_pct |
|:----------------|-------------:|-----------:|-------------:|--------------------:|-------------:|
| Technology      | 5,984,248.18 | 886,313.52 |        52175 |               40.12 |        14.81 |
| Furniture       | 5,178,590.54 | 117,433.03 |        44324 |               34.72 |         2.27 |
| Office Supplies | 3,752,762.10 | 518,021.43 |       118278 |               25.16 |        13.80 |



## Q7. Region and province sales with ranking (window function RANK)

`07_region_sales.csv` · 13 rows

| region                | province              |      revenue |     profit |   margin_pct |   revenue_rank |   margin_rank |
|:----------------------|:----------------------|-------------:|-----------:|-------------:|---------------:|--------------:|
| Ontario               | Ontario               | 3,063,212.48 | 346,868.54 |        11.32 |              1 |             4 |
| West                  | British Columbia      | 1,892,757.78 | 145,062.13 |         7.66 |              2 |             9 |
| West                  | Alberta               | 1,704,791.49 | 151,946.48 |         8.91 |              3 |             8 |
| Quebec                | Quebec                | 1,510,195.08 | 140,426.65 |         9.30 |              4 |             7 |
| Prairie               | Saskatchewan          | 1,464,455.82 | 184,732.96 |        12.61 |              5 |             2 |
| Prairie               | Manitoba              | 1,372,848.78 | 136,427.16 |         9.94 |              6 |             6 |
| Yukon                 | Yukon                 |   975,867.37 |  73,849.21 |         7.57 |              7 |            11 |
| Atlantic              | Nova Scotia           |   817,729.36 |  85,361.87 |        10.44 |              8 |             5 |
| Northwest Territories | Northwest Territories |   800,847.33 | 100,653.08 |        12.57 |              9 |             3 |
| Atlantic              | New Brunswick         |   684,211.52 | 115,351.94 |        16.86 |             10 |             1 |
| Atlantic              | Prince Edward Island  |   409,383.25 |  31,361.71 |         7.66 |             11 |            10 |
| Nunavut               | Nunavut               |   116,376.48 |   2,841.11 |         2.44 |             12 |            13 |
| Atlantic              | Newfoundland          |   102,924.07 |   6,885.14 |         6.69 |             13 |            12 |



## Q8. Low-performing products: bottom 15 by revenue (with units and orders)

`08_low_sales_products.csv` · 15 rows

| product_name                                              | category        | sub_category                   |   orders |   units_sold |   revenue |   profit |
|:----------------------------------------------------------|:----------------|:-------------------------------|---------:|-------------:|----------:|---------:|
| Alliance Rubber Bands                                     | Office Supplies | Rubber Bands                   |        1 |            6 |     14.85 |    -2.79 |
| Sony IBM Color Diskettes, 25/Pack                         | Technology      | Computer Peripherals           |        2 |           26 |     31.29 |   -65.33 |
| *Staples* Packaging Labels                                | Office Supplies | Labels                         |        2 |           12 |     34.94 |     4.32 |
| Avery 482                                                 | Office Supplies | Labels                         |        1 |           16 |     44.46 |     5.27 |
| Blackstonian Pencils                                      | Office Supplies | Pens & Art Supplies            |        1 |           19 |     50.07 |    -0.53 |
| Colorific® Watercolor Pencils                             | Office Supplies | Pens & Art Supplies            |        1 |           10 |     50.97 |     4.45 |
| Avery 516                                                 | Office Supplies | Labels                         |        1 |           10 |     70.02 |    22.62 |
| Computer Printout Index Tabs                              | Office Supplies | Binders and Binder Accessories |        1 |           46 |     75.60 |  -225.25 |
| Newell 332                                                | Office Supplies | Pens & Art Supplies            |        1 |           26 |     78.03 |     0.51 |
| Rogers Handheld Barrel Pencil Sharpener                   | Office Supplies | Pens & Art Supplies            |        3 |           30 |     93.44 |   -75.67 |
| Wilson Jones Standard D-Ring Binders                      | Office Supplies | Binders and Binder Accessories |        1 |           19 |     97.06 |    -7.36 |
| Xerox 1972                                                | Office Supplies | Paper                          |        1 |           19 |    103.68 |   -58.16 |
| Accohide Poly Flexible Ring Binders                       | Office Supplies | Binders and Binder Accessories |        3 |           25 |    104.82 |   -77.74 |
| Sanford Uni-Blazer™ View Highlighters, Chisel Tip, Yellow | Office Supplies | Pens & Art Supplies            |        1 |           48 |    109.78 |     4.48 |
| Newell 321                                                | Office Supplies | Pens & Art Supplies            |        2 |           35 |    112.83 |   -45.43 |



## Q9. Average order value overall and by customer segment

`09_average_order_value.csv` · 5 rows

| segment        |   orders |   avg_order_value |
|:---------------|---------:|------------------:|
| All segments   |     5496 |          2,713.90 |
| Consumer       |     1076 |          2,847.22 |
| Corporate      |     2002 |          2,746.71 |
| Home Office    |     1341 |          2,658.29 |
| Small Business |     1077 |          2,588.97 |



## Q10. Repeat vs one-time customers

`10_repeat_customers.csv` · 4 rows

| customer_type      |   customers |   pct_of_customers |
|:-------------------|------------:|-------------------:|
| 1 order (one-time) |          11 |               1.38 |
| 2-4 orders         |         215 |              27.04 |
| 5-9 orders         |         410 |              51.57 |
| 10+ orders         |         159 |              20.00 |



## Q11. Profit margin by category and sub-category

`11_profit_margin_by_category.csv` · 17 rows

| category        | sub_category                   |      revenue |     profit |   margin_pct |
|:----------------|:-------------------------------|-------------:|-----------:|-------------:|
| Furniture       | Office Furnishings             |   698,093.81 | 100,427.93 |        14.39 |
| Furniture       | Chairs & Chairmats             | 1,761,836.55 | 149,649.73 |         8.49 |
| Furniture       | Bookcases                      |   822,652.04 | -33,582.13 |        -4.08 |
| Furniture       | Tables                         | 1,896,008.14 | -99,062.50 |        -5.22 |
| Office Supplies | Labels                         |    38,981.55 |  13,677.17 |        35.09 |
| Office Supplies | Binders and Binder Accessories | 1,022,957.59 | 307,413.39 |        30.05 |
| Office Supplies | Envelopes                      |   174,085.80 |  48,182.60 |        27.68 |
| Office Supplies | Appliances                     |   736,991.54 |  97,158.06 |        13.18 |
| Office Supplies | Paper                          |   446,452.86 |  45,263.20 |        10.14 |
| Office Supplies | Pens & Art Supplies            |   167,107.22 |   7,564.78 |         4.53 |
| Office Supplies | Storage & Organization         | 1,070,182.60 |   6,664.15 |         0.62 |
| Office Supplies | Rubber Bands                   |    15,006.63 |    -102.67 |        -0.68 |
| Office Supplies | Scissors, Rulers and Trimmers  |    80,996.31 |  -7,799.25 |        -9.63 |
| Technology      | Telephones and Communication   | 1,889,313.80 | 316,951.62 |        16.78 |
| Technology      | Copiers and Fax                | 1,130,361.30 | 167,361.49 |        14.81 |
| Technology      | Office Machines                | 2,168,697.14 | 307,712.93 |        14.19 |
| Technology      | Computer Peripherals           |   795,875.94 |  94,287.48 |        11.85 |



## Q12. Sub-categories with a net loss (HAVING clause)

`12_loss_making_subcategories.csv` · 4 rows

| category        | sub_category                  |      revenue |     profit |
|:----------------|:------------------------------|-------------:|-----------:|
| Furniture       | Tables                        | 1,896,008.14 | -99,062.50 |
| Furniture       | Bookcases                     |   822,652.04 | -33,582.13 |
| Office Supplies | Scissors, Rulers and Trimmers |    80,996.31 |  -7,799.25 |
| Office Supplies | Rubber Bands                  |    15,006.63 |    -102.67 |



## Q13. Impact of discount level on profitability (CASE banding)

`13_discount_impact.csv` · 4 rows

| discount_band   |   line_items |      revenue |   margin_pct |   loss_line_pct |
|:----------------|-------------:|-------------:|-------------:|----------------:|
| 1) 0-2%         |         2327 | 4,344,048.33 |        12.36 |           47.19 |
| 2) 3-5%         |         2335 | 4,082,476.70 |        11.74 |           48.78 |
| 3) 6-8%         |         2209 | 3,983,044.76 |         7.97 |           52.97 |
| 4) 9%+          |         1528 | 2,506,031.03 |         7.50 |           56.09 |



## Q14. Shipping mode: volume, cost and margin

`14_ship_mode_performance.csv` · 3 rows

| ship_mode      |   line_items |      revenue |   shipping_cost |   margin_pct |   avg_ship_days |
|:---------------|-------------:|-------------:|----------------:|-------------:|----------------:|
| Regular Air    |         6270 | 7,506,303.21 |       48,008.19 |        14.72 |            2.04 |
| Delivery Truck |         1146 | 6,224,878.72 |       51,971.94 |         4.33 |            2.04 |
| Express Air    |          983 | 1,184,418.90 |        7,850.91 |        12.45 |            2.00 |



## Q15. Best-selling product in each category (ROW_NUMBER)

`15_top_product_per_category.csv` · 3 rows

| category        | product_name                                     |    revenue |
|:----------------|:-------------------------------------------------|-----------:|
| Furniture       | Global Troy™ Executive Leather Low-Back Tilter   | 275,941.52 |
| Technology      | Polycom ViewStation™ ISDN Videoconferencing Unit | 255,303.97 |
| Office Supplies | GBC DocuBind 200 Manual Binding Machine          | 120,342.74 |



## Q16. RFM base table per customer (input to customer segmentation)

`16_rfm_base.csv` · 795 rows

| customer_name     |   recency_days |   frequency |   monetary |
|:------------------|---------------:|------------:|-----------:|
| Emily Phan        |             35 |           8 | 117,124.44 |
| Deborah Brumfield |            363 |          12 |  97,433.14 |
| Roy Skaria        |             27 |          18 |  92,542.15 |
| Sylvia Foulston   |             80 |          18 |  88,875.76 |
| Grant Carroll     |             50 |          17 |  88,417.00 |
| Alejandro Grove   |            121 |           9 |  83,561.93 |
| Darren Budd       |             47 |          26 |  81,577.34 |
| Julia Barnett     |             19 |          12 |  80,044.45 |
| John Lucas        |             29 |          14 |  79,696.19 |
| Liz MacKendrick   |            182 |          14 |  76,306.43 |
| Dennis Kane       |             30 |          13 |  75,967.59 |
| Ed Braxton        |             24 |          22 |  75,802.76 |
| Mark Cousins      |            165 |          18 |  70,579.73 |
| Raymond Book      |             59 |          11 |  70,426.59 |
| Lisa DeCherney    |             11 |          13 |  67,914.00 |
| Philip Brown      |             70 |          12 |  64,716.80 |
| Clytie Kelty      |            247 |          10 |  63,189.95 |
| Muhammed Yedwab   |             35 |          16 |  62,544.02 |
| Jasper Cacioppo   |            168 |           7 |  61,350.09 |
| Matt Abelman      |            141 |          12 |  60,962.35 |

