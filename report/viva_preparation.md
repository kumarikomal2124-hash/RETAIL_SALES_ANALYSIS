# Viva Preparation: Retail Shop Analysis Using Data Analytics

Answers use this project's **actual numbers**. Learn the reasoning, not the wording.

## A. 60-second project summary (memorise this)
> "I analysed 8,399 order lines from a public retail dataset, Superstore Sales, covering 2009 to 2012. I cleaned
> the data in Python, explored it with Pandas and Matplotlib, built a star-schema SQL database, segmented customers
> with RFM analysis, and designed a four-page Power BI dashboard. The shop made $14.9 million in revenue at a
> 10.2% margin, but about half of all order lines lost money. The biggest cause is shipping cheap items: when
> shipping cost is high relative to price, the margin is minus 50%. Furniture brings 35% of revenue but only 8% of
> profit. 31% of customers, the Champions and Loyal segments, generate 49% of revenue. My recommendations are a
> shipping-cost policy, Furniture repricing, discount caps, ABC-based inventory control and RFM-based retention.
> I cross-checked the Python and SQL results, and they match to the cent."

---

## B. Dataset and cleaning

**Q1. Where did your data come from? Is it real?**
It is the Superstore Sales sample dataset, originally from Tableau and widely used on Kaggle. I used a public copy
on GitHub (curran/data). It is realistic teaching data, not one named company's confidential data, so I present my
findings as findings *about this dataset*.

**Q2. Why not use the more common US Superstore dataset?**
This edition includes **Unit Price** and **Shipping Cost**, which the brief needed (Total Sales = Quantity × Unit
Price) and which revealed the main loss driver. It also has more than 5,000 records (8,399), all three categories, and dates, discounts and profit.

**Q3. What problems did you find in the raw data?**
(1) Old Mac encoding and carriage-return line endings, which I fixed by reading with `encoding="mac_roman"`,
`lineterminator="\r"`. (2) One empty trailing row. (3) Spelling errors "Saskachewan" and "Prarie". (4) 63 missing
Product Base Margin values. (5) Dates stored as text. (6) 21 order IDs linked to more than one customer.

**Q4. How did you handle missing values? Why not just drop the rows?**
Base margin is a product attribute, so I imputed the **median of the product's sub-category** and added a flag
column. Dropping the rows would have removed valid sales and profit data.

**Q5. You found 1,042 outliers. Why didn't you remove them?**
They make up **63.4% of revenue**. They are large business orders, not errors, and removing them would remove most of
the business. I kept and flagged them, and used log scales or medians where they would distort charts.
**Removing outliers is a decision, not a rule.**

**Q6. Explain the IQR method.**
IQR = Q3 − Q1 (the middle 50% of the data). Values below Q1 − 1.5×IQR or above Q3 + 1.5×IQR are flagged as outliers.
It is robust because quartiles are not affected by extreme values, unlike the mean and standard deviation.

**Q7. Sales ≠ Quantity × Unit Price. Why? Which did you use?**
The provider recorded Sales after adjustments such as discount. The median ratio is 1.004, so the two are close but not
identical. I used the **original Sales column** for revenue and kept Quantity × Unit Price as a derived field,
`gross_sales`, so that I never altered the original data.

**Q8. About half of all lines have negative profit. Isn't that a data error?**
No. Selling at a loss is a real outcome, for example a heavy discount or expensive shipping on a cheap item. I
investigated *why* in the EDA instead of deleting the rows.

## C. EDA and findings

**Q9. What is AOV and how did you calculate it?**
Average Order Value = total revenue ÷ number of distinct orders = $14,915,601 ÷ 5,496 = **$2,713.90**. Count distinct
order IDs, not rows, because one order has several lines.

**Q10. Why is the mean order value larger than the median?**
The distribution is right-skewed: a few very large orders pull the mean up. That is why I report both.

**Q11. Which category is best? Which is worst?**
Technology: 40% of revenue, 58% of profit, 14.8% margin. Furniture: 35% of revenue but 8% of profit, 2.3% margin,
because Tables (−$99K) and Bookcases (−$34K) lose money.

**Q12. What is the most important finding?**
Shipping cost relative to item price. In the top quartile the margin is **−50%** and 96% of lines lose money. Budget
items under $20 have a −13.5% margin. Discount matters too (margin falls from 12.4% to 7.5%), but less.

**Q13. Does correlation prove that discounts cause losses?**
No. Correlation shows association, not causation. To prove the effect, the business should run a controlled test (an
A/B test) on its discount policy. I say this in the limitations.

**Q14. Why Spearman and not Pearson correlation?**
The data is skewed and has outliers. Spearman uses ranks, so it is robust to them and captures monotonic, not just
linear, relationships.

**Q15. What is the trend over time?**
Revenue peaked in 2009 ($4.21M), fell in 2010 (−15.7%) and 2011 (−3.2%), and recovered in 2012 (+8.2%). But 2012 had the
lowest profit and margin (9.19%), so the growth was "bought" with lower profitability.

**Q16. Seasonality?**
December is the strongest month and June the weakest. Q4 (26.9%) and Q1 (26.1%) are the strongest quarters.

**Q17. Which regions need improvement?**
Nunavut (2.4% margin), Newfoundland (6.7%), and British Columbia (7.7%, the second-largest by revenue) are all below the
10.2% average. New Brunswick has the best margin (16.9%).

**Q18. The brief asked for store performance. Your data has no stores. What did you do?**
I treated each **province as a sales territory** and stated this assumption clearly. I did not invent store IDs.

**Q19. The brief asked for inventory analysis without stock data. How did you do it?**
I analysed stock *movement*: units sold per quarter, **ABC classification** (A = top 80% of revenue), sales velocity
and demand variability (coefficient of variation). 291 products (23%) generate 80% of revenue. Class-C products lose
$107K. 140 high-volume products lose money.

## D. SQL

**Q20. What is a star schema? Why did you use it?**
One central **fact table** (fact_sales: the measurable events) linked to **dimension tables** (customer, product,
location: the descriptions). It is simple to query, avoids repeating descriptive data, and is the model Power BI recommends.

**Q21. Primary key vs foreign key?**
A primary key uniquely identifies a row (e.g. `product_id` in dim_product). A foreign key in another table
references it (`fact_sales.product_id`), enforcing that every sale points to a real product.

**Q22. WHERE vs HAVING?**
WHERE filters rows **before** grouping. HAVING filters groups **after** aggregation. My query 12 uses
`HAVING SUM(profit) < 0` to find loss-making sub-categories.

**Q23. What is a CTE?**
A Common Table Expression (`WITH name AS (...)`) is a named temporary result that makes complex queries readable. I
used one to total orders before averaging (AOV), and one to compute yearly totals before LAG().

**Q24. Explain the window functions you used.**
`LAG()` reads the previous row's value (last year's revenue for YoY growth). `RANK()` ranks provinces.
`ROW_NUMBER() OVER (PARTITION BY category …)` numbers products within each category to find each category's best seller.
Unlike GROUP BY, window functions keep every row.

**Q25. Why SQLite and not MySQL?**
SQLite is built into Python, so there is no server to install and anyone can reproduce the project. The SQL is
standard; only the date functions (`strftime`, `julianday`) would change in MySQL.

**Q26. How do you know your results are correct?**
I computed the same KPIs independently in Python and SQL, and they match exactly ($14,915,600.82, 5,496 orders). RFM values match
for all 795 customers. The pipeline also asserts no missing values, unique keys and expected row counts.

## E. RFM segmentation

**Q27. Explain RFM.**
Recency: days since the last order (lower is better). Frequency: number of orders. Monetary: total spend. Each is scored 1–5 by
quintile, and segments are assigned by rules, e.g. Champions = R≥4, F≥4, M≥4.

**Q28. Why quintiles? Why rank before cutting?**
Quintiles create 5 equal-sized groups, relative to this customer base. Many customers share the same order count, so
ranking first breaks ties and keeps the groups equal.

**Q29. Why did you use 31 Dec 2012 as the reference date and not today?**
The data ends on 30 Dec 2012. Using today would make every customer look inactive for over ten years.

**Q30. What did RFM show?**
Champions: 127 customers (16%), 32.8% of revenue. Champions + Loyal: 31% of customers, 49% of revenue. At-Risk: 133
customers who used to buy often (8 orders on average) but have been inactive for about a year, $2.80M of past revenue, the best
win-back target. Only 5 new customers, so retention matters more than acquisition.

**Q31. Why rules instead of K-Means clustering?**
Rules are transparent: a manager can understand why a customer is "At-Risk". K-Means is listed as future work, to
compare against the rule-based segments.

## F. Power BI

**Q32. Why is there no .pbix generated by code?**
.pbix files can only be authored in Power BI Desktop. I prepared the star-schema data, all DAX measures, the theme and
page designs, then built the dashboard in Power BI Desktop. *(Make sure you have built it before the viva.)*

**Q33. What is DAX? Give an example.**
Data Analysis Expressions, Power BI's formula language. `Average Order Value = DIVIDE([Total Revenue], [Total Orders])`.
DIVIDE is safer than "/" because it handles division by zero.

**Q34. Measure vs calculated column?**
A calculated column is computed once per row and stored. A measure is computed at query time in the current filter
context (e.g. responding to slicers). KPIs should be measures.

**Q35. What does "Mark as date table" do?**
It tells Power BI that `dim_date` is a continuous calendar, which enables time-intelligence functions like
SAMEPERIODLASTYEAR for year-over-year comparison.

**Q36. Why no dual-axis charts?**
Two y-scales on one chart can mislead, because the visual crossing points depend on arbitrary scaling. I show revenue and profit in
separate charts instead.

## G. Recommendations and limitations

**Q37. Give your top three recommendations with evidence.**
1. **Shipping policy for low-price items** (top relative-shipping-cost quartile: −50% margin).
2. **Reprice Furniture, especially Tables and Bookcases** (2.3% category margin; −$99K and −$34K).
3. **RFM retention**: a VIP programme for Champions and a win-back campaign for 133 At-Risk customers ($2.80M of past revenue).

**Q38. What are the limitations?**
Sample dataset; no store or stock-level data; no cost breakdown; data ends in 2012; correlation is not causation;
RFM scores are relative.

**Q39. Future scope?**
Sales forecasting (ARIMA/Prophet), K-Means segmentation, CLV prediction, market-basket analysis, connecting
real inventory data, and scheduled Power BI refresh.

**Q40. What did you learn?**
Revenue alone can mislead: the #2 product by revenue (Polycom videoconferencing unit, $255K) has a −7% margin. Always
analyse profit, validate across tools, and document assumptions.

---

## H. Live demo plan (5 minutes)
1. Open `01_data_cleaning.ipynb` and show the cleaning log and validation table.
2. Open `02_exploratory_analysis.ipynb` and show the discount/shipping charts (the key insight).
3. Open `04_sql_analysis.ipynb` and run one window-function query.
4. Open the Power BI dashboard, apply the **Category = Furniture** slicer, and watch the margin drop.
5. Close with the recommendations slide or chapter.
