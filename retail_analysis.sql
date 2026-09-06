-- =====================================================================
-- Retail Business Performance & Profitability Analysis
-- SQL Queries for Data Exploration and Segmentation
-- Table: transactions (loaded from retail_transactions.csv)
-- =====================================================================

-- 1. Data cleaning check: identify missing/null records
SELECT
    SUM(CASE WHEN region IS NULL THEN 1 ELSE 0 END)          AS missing_region,
    SUM(CASE WHEN inventory_days IS NULL THEN 1 ELSE 0 END)  AS missing_inventory_days
FROM transactions;

-- 2. Remove/flag incomplete records for a clean analysis view
-- (create a cleaned view rather than deleting raw data)
CREATE VIEW IF NOT EXISTS clean_transactions AS
SELECT *
FROM transactions
WHERE region IS NOT NULL
  AND inventory_days IS NOT NULL;

-- 3. Overall business performance summary
SELECT
    COUNT(*)                         AS total_transactions,
    ROUND(SUM(revenue), 2)           AS total_revenue,
    ROUND(SUM(cost), 2)              AS total_cost,
    ROUND(SUM(profit), 2)            AS total_profit,
    ROUND(AVG(profit_margin_pct), 2) AS avg_profit_margin_pct
FROM clean_transactions;

-- 4. Profit margin by category
SELECT
    category,
    COUNT(*)                          AS num_transactions,
    ROUND(SUM(revenue), 2)            AS total_revenue,
    ROUND(SUM(profit), 2)             AS total_profit,
    ROUND(AVG(profit_margin_pct), 2)  AS avg_profit_margin_pct
FROM clean_transactions
GROUP BY category
ORDER BY total_profit DESC;

-- 5. Profit margin by category and sub-category (identify profit-draining sub-categories)
SELECT
    category,
    subcategory,
    COUNT(*)                          AS num_transactions,
    ROUND(SUM(revenue), 2)            AS total_revenue,
    ROUND(SUM(profit), 2)             AS total_profit,
    ROUND(AVG(profit_margin_pct), 2)  AS avg_profit_margin_pct
FROM clean_transactions
GROUP BY category, subcategory
ORDER BY avg_profit_margin_pct ASC
LIMIT 10;  -- lowest-margin sub-categories -> profit-draining areas

-- 6. Performance by region
SELECT
    region,
    ROUND(SUM(revenue), 2)            AS total_revenue,
    ROUND(SUM(profit), 2)             AS total_profit,
    ROUND(AVG(profit_margin_pct), 2)  AS avg_profit_margin_pct
FROM clean_transactions
GROUP BY region
ORDER BY total_profit DESC;

-- 7. Seasonal product behavior
SELECT
    season,
    category,
    ROUND(SUM(revenue), 2)            AS total_revenue,
    ROUND(AVG(profit_margin_pct), 2)  AS avg_profit_margin_pct
FROM clean_transactions
GROUP BY season, category
ORDER BY season, total_revenue DESC;

-- 8. Inventory turnover buckets vs. profitability
SELECT
    CASE
        WHEN inventory_days <= 20 THEN 'Fast-moving (<=20 days)'
        WHEN inventory_days <= 50 THEN 'Moderate (21-50 days)'
        WHEN inventory_days <= 80 THEN 'Slow-moving (51-80 days)'
        ELSE 'Overstocked (>80 days)'
    END AS inventory_bucket,
    COUNT(*)                          AS num_transactions,
    ROUND(AVG(profit_margin_pct), 2)  AS avg_profit_margin_pct,
    ROUND(SUM(profit), 2)             AS total_profit
FROM clean_transactions
GROUP BY inventory_bucket
ORDER BY avg_profit_margin_pct DESC;

-- 9. Top 10 highest-profit sub-categories
SELECT
    category,
    subcategory,
    ROUND(SUM(profit), 2) AS total_profit
FROM clean_transactions
GROUP BY category, subcategory
ORDER BY total_profit DESC
LIMIT 10;

-- 10. Overstocked / slow-moving items requiring strategic action
-- (long inventory days AND margin below their own category's average --
--  i.e. underperforming relative to peers in the same category)
WITH segment AS (
    SELECT category, subcategory, region,
           AVG(inventory_days) AS avg_inventory_days,
           AVG(profit_margin_pct) AS avg_profit_margin_pct,
           COUNT(*) AS num_transactions
    FROM clean_transactions
    GROUP BY category, subcategory, region
),
cat_avg AS (
    SELECT category, AVG(profit_margin_pct) AS cat_avg_margin
    FROM clean_transactions
    GROUP BY category
)
SELECT s.category, s.subcategory, s.region,
       ROUND(s.avg_inventory_days,1)    AS avg_inventory_days,
       ROUND(s.avg_profit_margin_pct,2) AS avg_profit_margin_pct,
       ROUND(c.cat_avg_margin,2)        AS category_avg_margin,
       s.num_transactions
FROM segment s
JOIN cat_avg c ON s.category = c.category
WHERE s.avg_inventory_days > 60
  AND s.avg_profit_margin_pct < c.cat_avg_margin
ORDER BY s.avg_inventory_days DESC;

-- 11. Ranking sub-categories within each category by profit contribution
SELECT
    category,
    subcategory,
    ROUND(SUM(profit), 2) AS total_profit,
    RANK() OVER (PARTITION BY category ORDER BY SUM(profit) DESC) AS profit_rank
FROM clean_transactions
GROUP BY category, subcategory
ORDER BY category, profit_rank;
