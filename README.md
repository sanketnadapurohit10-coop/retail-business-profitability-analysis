# Retail Business Performance & Profitability Analysis

Analysis of retail transaction data to identify profit-draining categories, evaluate the relationship between inventory turnover and profitability, and surface seasonal product behavior.

## 📋 Overview

- **Objective:** Analyze transactional retail data to uncover profit-draining categories, optimize inventory turnover, and identify seasonal product behavior
- **Dataset:** 5,821 cleaned transactions (6,000 total, 2.4% removed for missing values), 5 categories, 5 regions, 5 seasons
- **Status:** ✅ Complete

## 📊 Key Results

| Metric | Value |
|---|---|
| Total Revenue | $26.87M |
| Total Profit | $2.24M |
| Overall Profit Margin | 11.66% |
| Inventory Days ↔ Margin Correlation | -0.54 to -0.63 (within category) |

### Top Findings
- **Beauty & Personal Care (20.67%)** and **Apparel (17.84%)** are the highest-margin categories
- **Grocery (2.59%)** and **Electronics (5.08%)** drain margin the most — despite Electronics generating the highest revenue ($14.9M)
- **Longer inventory holding time predicts lower margin in every category** (correlation -0.54 to -0.63), driven by markdown pricing on aging stock
- **Regional performance is fairly even** (11.4%–11.9% margin across all 5 regions) — profitability issues are category-driven, not geography-driven

### Profit-Draining Sub-Categories (Lowest Margin)
| Category | Sub-Category | Avg Margin |
|---|---|---|
| Grocery | Beverages | 2.12% |
| Grocery | Staples | 2.53% |
| Grocery | Snacks | 2.57% |
| Electronics | Smartphones | 4.71% |
| Electronics | Cameras | 4.89% |

## 🎯 Business Recommendations

1. **Renegotiate supplier costs or bundle margin-accretive add-ons** for Grocery and Electronics rather than competing on price alone
2. **Tighten reorder cycles** for Apparel and Home & Kitchen sub-categories, which show the longest average holding times (75–80 days)
3. **Prioritize 10 identified segments** (mostly Apparel — Women's Wear, Footwear, Men's Wear — plus Home & Kitchen Furniture) for clearance pricing due to long holding times + below-category-average margins
4. **Expand catalog depth in Beauty & Personal Care**, the highest-margin category, to capture more revenue at strong margins

## 🛠️ Technical Stack

- **SQL (SQLite):** Data cleaning, profit margin aggregation, inventory-bucket segmentation, window functions
- **Python (Pandas, NumPy):** Correlation analysis between inventory days and profitability
- **Matplotlib/Seaborn:** 9-panel visual dashboard

## 📁 Repository Contents
![image alt](https://github.com/sanketnadapurohit10-coop/retail-business-profitability-analysis/blob/33b59d4ee5b0d7a356bfbee4ef75110263cfb464/retail_performance_dashboard.png)
- `RETAIL_ANALYSIS_REPORT.pdf` — Full 2-page report: introduction, abstract, tools used, methodology, findings, and conclusion
- `retail_analysis.sql` — 11 SQL queries for data exploration and segmentation
- `retail_performance_dashboard.png` — 9-panel dashboard of revenue, margin, regional, seasonal, and inventory-turnover views
- `retail_transactions.csv` — The 6,000-row transactional dataset used
- `generate_retail_data.py` — Script to generate the synthetic dataset
- `run_analysis.py` — Script to run the full SQL + Python analysis

## 📖 How to Use This Repo

- **Quick review:** Start with `RETAIL_ANALYSIS_REPORT.pdf` (~5 min read)
- **Reproduce the analysis:** Run `generate_retail_data.py` then `run_analysis.py`
- **Visual summary:** See `retail_performance_dashboard.png`
