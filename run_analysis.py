import sqlite3
import pandas as pd
import numpy as np

pd.set_option("display.width", 120)

conn = sqlite3.connect("retail.db")

# recreate the clean view (in case not run via .sql file)
conn.execute("""
CREATE VIEW IF NOT EXISTS clean_transactions AS
SELECT * FROM transactions
WHERE region IS NOT NULL AND inventory_days IS NOT NULL
""")

print("="*70)
print("1. OVERALL PERFORMANCE SUMMARY")
print("="*70)
q1 = pd.read_sql("""
SELECT
    COUNT(*) AS total_transactions,
    ROUND(SUM(revenue),2) AS total_revenue,
    ROUND(SUM(cost),2) AS total_cost,
    ROUND(SUM(profit),2) AS total_profit,
    ROUND(AVG(profit_margin_pct),2) AS avg_profit_margin_pct
FROM clean_transactions
""", conn)
print(q1.to_string(index=False))

print("\n" + "="*70)
print("2. PROFIT MARGIN BY CATEGORY")
print("="*70)
q2 = pd.read_sql("""
SELECT category, COUNT(*) AS num_transactions,
       ROUND(SUM(revenue),2) AS total_revenue,
       ROUND(SUM(profit),2) AS total_profit,
       ROUND(AVG(profit_margin_pct),2) AS avg_profit_margin_pct
FROM clean_transactions
GROUP BY category
ORDER BY total_profit DESC
""", conn)
print(q2.to_string(index=False))

print("\n" + "="*70)
print("3. LOWEST-MARGIN SUB-CATEGORIES (profit-draining)")
print("="*70)
q3 = pd.read_sql("""
SELECT category, subcategory, COUNT(*) AS num_transactions,
       ROUND(SUM(revenue),2) AS total_revenue,
       ROUND(SUM(profit),2) AS total_profit,
       ROUND(AVG(profit_margin_pct),2) AS avg_profit_margin_pct
FROM clean_transactions
GROUP BY category, subcategory
ORDER BY avg_profit_margin_pct ASC
LIMIT 10
""", conn)
print(q3.to_string(index=False))

print("\n" + "="*70)
print("4. PERFORMANCE BY REGION")
print("="*70)
q4 = pd.read_sql("""
SELECT region, ROUND(SUM(revenue),2) AS total_revenue,
       ROUND(SUM(profit),2) AS total_profit,
       ROUND(AVG(profit_margin_pct),2) AS avg_profit_margin_pct
FROM clean_transactions
GROUP BY region
ORDER BY total_profit DESC
""", conn)
print(q4.to_string(index=False))

print("\n" + "="*70)
print("5. INVENTORY TURNOVER BUCKETS VS PROFITABILITY")
print("="*70)
q5 = pd.read_sql("""
SELECT
    CASE
        WHEN inventory_days <= 20 THEN 'Fast-moving (<=20 days)'
        WHEN inventory_days <= 50 THEN 'Moderate (21-50 days)'
        WHEN inventory_days <= 80 THEN 'Slow-moving (51-80 days)'
        ELSE 'Overstocked (>80 days)'
    END AS inventory_bucket,
    COUNT(*) AS num_transactions,
    ROUND(AVG(profit_margin_pct),2) AS avg_profit_margin_pct,
    ROUND(SUM(profit),2) AS total_profit
FROM clean_transactions
GROUP BY inventory_bucket
ORDER BY avg_profit_margin_pct DESC
""", conn)
print(q5.to_string(index=False))

print("\n" + "="*70)
print("6. OVERSTOCKED / SLOW-MOVING ITEMS (ACTION NEEDED)")
print("   (high inventory days AND margin below their own category's average)")
print("="*70)
q6 = pd.read_sql("""
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
       ROUND(s.avg_inventory_days,1) AS avg_inventory_days,
       ROUND(s.avg_profit_margin_pct,2) AS avg_profit_margin_pct,
       ROUND(c.cat_avg_margin,2) AS category_avg_margin,
       s.num_transactions
FROM segment s
JOIN cat_avg c ON s.category = c.category
WHERE s.avg_inventory_days > 60
  AND s.avg_profit_margin_pct < c.cat_avg_margin
ORDER BY s.avg_inventory_days DESC
LIMIT 10
""", conn)
print(q6.to_string(index=False))
print(f"\n{len(q6)} overstocked/slow-moving segments identified requiring action.")

print("\n" + "="*70)
print("7. PYTHON: CORRELATION - INVENTORY DAYS vs PROFITABILITY")
print("="*70)
df = pd.read_sql("SELECT * FROM clean_transactions", conn)
overall_corr = df["inventory_days"].corr(df["profit_margin_pct"])
print(f"Overall correlation (inventory_days vs profit_margin_pct): {overall_corr:.3f}")

print("\nCorrelation by category:")
cat_corr = df.groupby("category").apply(
    lambda g: g["inventory_days"].corr(g["profit_margin_pct"])
).round(3)
print(cat_corr.to_string())

# Save summary stats for the report/dashboard
summary = {
    "total_transactions": int(q1["total_transactions"][0]),
    "total_revenue": float(q1["total_revenue"][0]),
    "total_profit": float(q1["total_profit"][0]),
    "avg_profit_margin_pct": float(q1["avg_profit_margin_pct"][0]),
    "overall_corr_inventory_margin": round(overall_corr, 3),
}
import json
with open("summary_stats.json", "w") as f:
    json.dump(summary, f, indent=2)

q2.to_csv("category_performance.csv", index=False)
q3.to_csv("lowest_margin_subcategories.csv", index=False)
q4.to_csv("region_performance.csv", index=False)
q5.to_csv("inventory_bucket_performance.csv", index=False)
q6.to_csv("overstocked_slow_moving_items.csv", index=False)

print("\nSaved: summary_stats.json, category_performance.csv, lowest_margin_subcategories.csv,")
print("       region_performance.csv, inventory_bucket_performance.csv, overstocked_slow_moving_items.csv")

conn.close()
