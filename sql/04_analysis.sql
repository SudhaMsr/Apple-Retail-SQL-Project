-- ============================================================
-- Apple Retail Sales: 20 business questions (PostgreSQL)
--
-- Revenue = quantity * list price. "Today" is pinned to the last day in the data,
-- DATE '2024-12-31', so every result is reproducible.
-- Each question starts with a "-- Qnn:" header; run_analysis.py uses these to split the file.
-- ============================================================


-- ─────────────────────────── Foundations ───────────────────────────

-- Q01: How many stores are there in each country?
SELECT country, COUNT(*) AS stores
FROM stores
GROUP BY country
ORDER BY stores DESC, country;

-- Q02: Which 10 stores sold the most units overall?
SELECT st.store_name, st.country, SUM(s.quantity) AS units
FROM sales s
JOIN stores st ON st.store_id = s.store_id
GROUP BY st.store_name, st.country
ORDER BY units DESC
LIMIT 10;

-- Q03: How many sales transactions happened in December 2023?
SELECT COUNT(*) AS transactions, SUM(quantity) AS units
FROM sales
WHERE sale_date >= DATE '2023-12-01' AND sale_date < DATE '2024-01-01';

-- Q04: What share of warranty claims ended as "Warranty Void"?
SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE repair_status = 'Warranty Void') / COUNT(*), 2) AS pct_void
FROM warranty;

-- Q05: What is the average list price in each category?
SELECT c.category_name, ROUND(AVG(p.price), 2) AS avg_price, COUNT(*) AS products
FROM products p
JOIN category c ON c.category_id = p.category_id
GROUP BY c.category_name
ORDER BY avg_price DESC;


-- ─────────────────────────── Sales performance ───────────────────────────

-- Q06: Which categories generate the most revenue, and what share of the total?
SELECT c.category_name,
       ROUND(SUM(s.quantity * p.price) / 1e6, 1) AS revenue_musd,
       ROUND(100.0 * SUM(s.quantity * p.price) / SUM(SUM(s.quantity * p.price)) OVER (), 1) AS pct_of_total
FROM sales s
JOIN products p ON p.product_id = s.product_id
JOIN category c ON c.category_id = p.category_id
GROUP BY c.category_name
ORDER BY revenue_musd DESC;

-- Q07: How did revenue move quarter by quarter?
SELECT EXTRACT(YEAR FROM s.sale_date)::int    AS year,
       EXTRACT(QUARTER FROM s.sale_date)::int AS quarter,
       ROUND(SUM(s.quantity * p.price) / 1e6, 1) AS revenue_musd
FROM sales s
JOIN products p ON p.product_id = s.product_id
GROUP BY 1, 2
ORDER BY 1, 2;

-- Q08: For each store, which day of the week sells the most units?
WITH by_day AS (
    SELECT store_id,
           EXTRACT(DOW FROM sale_date)::int AS dow,
           SUM(quantity) AS units,
           RANK() OVER (PARTITION BY store_id ORDER BY SUM(quantity) DESC) AS rnk
    FROM sales
    GROUP BY store_id, EXTRACT(DOW FROM sale_date)
)
SELECT st.store_name,
       CASE d.dow WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday' WHEN 3 THEN 'Wednesday'
                  WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday' ELSE 'Saturday' END AS best_day,
       d.units
FROM by_day d
JOIN stores st ON st.store_id = d.store_id
WHERE d.rnk = 1
ORDER BY d.units DESC
LIMIT 10;

-- Q09: What is each country's least-selling product in 2024?
WITH ranked AS (
    SELECT st.country, p.product_name, SUM(s.quantity) AS units,
           RANK() OVER (PARTITION BY st.country ORDER BY SUM(s.quantity) ASC) AS rnk
    FROM sales s
    JOIN stores st ON st.store_id = s.store_id
    JOIN products p ON p.product_id = s.product_id
    WHERE s.sale_date >= DATE '2024-01-01'
    GROUP BY st.country, p.product_name
)
SELECT country, product_name, units
FROM ranked
WHERE rnk = 1
ORDER BY country;

-- Q10: In which months of the last 3 years did US stores sell more than 9,000 units?
SELECT DATE_TRUNC('month', s.sale_date)::date AS month, SUM(s.quantity) AS units
FROM sales s
JOIN stores st ON st.store_id = s.store_id
WHERE st.country = 'United States'
  AND s.sale_date > DATE '2024-12-31' - INTERVAL '3 years'
GROUP BY 1
HAVING SUM(s.quantity) > 9000
ORDER BY 1;

-- Q11: How does a product sell over its lifecycle (months after launch)?
SELECT CASE
           WHEN s.sale_date - p.launch_date < 183 THEN '0-6 months'
           WHEN s.sale_date - p.launch_date < 365 THEN '6-12 months'
           WHEN s.sale_date - p.launch_date < 548 THEN '12-18 months'
           ELSE '18+ months'
       END AS lifecycle_stage,
       ROUND(AVG(s.quantity * p.price), 2) AS avg_revenue_per_sale,
       COUNT(*) AS transactions
FROM sales s
JOIN products p ON p.product_id = s.product_id
WHERE p.launch_date >= DATE '2021-01-01'  -- full lifecycles only
GROUP BY 1
ORDER BY MIN(s.sale_date - p.launch_date);


-- ─────────────────────────── Warranty & risk ───────────────────────────

-- Q12: Which 10 products have the highest warranty claim rate?
SELECT p.product_name,
       COUNT(s.sale_id) AS sales,
       COUNT(w.claim_id) AS claims,
       ROUND(100.0 * COUNT(w.claim_id) / COUNT(s.sale_id), 2) AS claim_rate_pct
FROM sales s
JOIN products p ON p.product_id = s.product_id
LEFT JOIN warranty w ON w.sale_id = s.sale_id
GROUP BY p.product_name
HAVING COUNT(s.sale_id) > 5000
ORDER BY claim_rate_pct DESC
LIMIT 10;

-- Q13: Are premium products associated with more post-sale issues?
SELECT CASE WHEN p.price < 200 THEN '< $200'
            WHEN p.price < 500 THEN '$200-499'
            WHEN p.price < 1000 THEN '$500-999'
            ELSE '$1,000+' END AS price_band,
       COUNT(s.sale_id) AS sales,
       ROUND(100.0 * COUNT(w.claim_id) / COUNT(s.sale_id), 2) AS claim_rate_pct
FROM sales s
JOIN products p ON p.product_id = s.product_id
LEFT JOIN warranty w ON w.sale_id = s.sale_id
WHERE p.category_id <> 'CAT-10'  -- services cannot fail
GROUP BY 1
ORDER BY MIN(p.price);

-- Q14: What share of claims are filed within 180 days of purchase?
SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE w.claim_date - s.sale_date <= 180) / COUNT(*), 1) AS pct_within_180d,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY w.claim_date - s.sale_date) AS median_days_to_claim
FROM warranty w
JOIN sales s ON s.sale_id = w.sale_id;

-- Q15: Which category had the most claims in the last 2 years?
SELECT c.category_name, COUNT(*) AS claims
FROM warranty w
JOIN sales s ON s.sale_id = w.sale_id
JOIN products p ON p.product_id = s.product_id
JOIN category c ON c.category_id = p.category_id
WHERE w.claim_date > DATE '2024-12-31' - INTERVAL '2 years'
GROUP BY c.category_name
ORDER BY claims DESC;

-- Q16: Per country, what is the chance that a sale turns into a claim?
SELECT st.country,
       COUNT(s.sale_id) AS sales,
       COUNT(w.claim_id) AS claims,
       ROUND(100.0 * COUNT(w.claim_id) / COUNT(s.sale_id), 2) AS claim_chance_pct
FROM sales s
JOIN stores st ON st.store_id = s.store_id
LEFT JOIN warranty w ON w.sale_id = s.sale_id
GROUP BY st.country
ORDER BY claim_chance_pct DESC;

-- Q17: Which stores have no warranty claims at all? (data-quality check)
SELECT st.store_name
FROM stores st
WHERE NOT EXISTS (
    SELECT 1 FROM sales s JOIN warranty w ON w.sale_id = s.sale_id WHERE s.store_id = st.store_id
);


-- ─────────────────────────── Advanced (window functions) ───────────────────────────

-- Q18: Year-over-year revenue growth for the 10 fastest-growing stores (LAG).
WITH yearly AS (
    SELECT st.store_name,
           EXTRACT(YEAR FROM s.sale_date)::int AS year,
           SUM(s.quantity * p.price) AS revenue
    FROM sales s
    JOIN stores st ON st.store_id = s.store_id
    JOIN products p ON p.product_id = s.product_id
    GROUP BY st.store_name, EXTRACT(YEAR FROM s.sale_date)
), growth AS (
    SELECT store_name, year, revenue,
           LAG(revenue) OVER (PARTITION BY store_name ORDER BY year) AS prev_revenue
    FROM yearly
)
SELECT store_name, year,
       ROUND(revenue / 1e6, 2) AS revenue_musd,
       ROUND(100.0 * (revenue - prev_revenue) / prev_revenue, 1) AS yoy_growth_pct
FROM growth
WHERE year = 2024
ORDER BY yoy_growth_pct DESC
LIMIT 10;

-- Q19: Rank products within each category by 2024 revenue (top 3 per category).
WITH ranked AS (
    SELECT c.category_name, p.product_name,
           SUM(s.quantity * p.price) AS revenue,
           DENSE_RANK() OVER (PARTITION BY c.category_name ORDER BY SUM(s.quantity * p.price) DESC) AS rnk
    FROM sales s
    JOIN products p ON p.product_id = s.product_id
    JOIN category c ON c.category_id = p.category_id
    WHERE s.sale_date >= DATE '2024-01-01'
    GROUP BY c.category_name, p.product_name
)
SELECT category_name, rnk, product_name, ROUND(revenue / 1e6, 2) AS revenue_musd
FROM ranked
WHERE rnk <= 3
ORDER BY category_name, rnk;

-- Q20: Rolling 3-month revenue and month-over-month change in 2024.
WITH monthly AS (
    SELECT DATE_TRUNC('month', s.sale_date)::date AS month,
           SUM(s.quantity * p.price) AS revenue
    FROM sales s
    JOIN products p ON p.product_id = s.product_id
    GROUP BY 1
)
SELECT month,
       ROUND(revenue / 1e6, 1) AS revenue_musd,
       ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) / 1e6, 1) AS rolling_3m_musd,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month), 1) AS mom_pct
FROM monthly
WHERE month >= DATE '2024-01-01'
ORDER BY month;
