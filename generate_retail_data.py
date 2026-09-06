"""
Generate a realistic retail transactional dataset for the
Retail Business Performance & Profitability Analysis project.
"""
import numpy as np
import pandas as pd

np.random.seed(42)

N = 6000

categories = {
    "Electronics": ["Headphones", "Smartphones", "Laptops", "Cameras", "Accessories"],
    "Apparel": ["Men's Wear", "Women's Wear", "Kids Wear", "Footwear", "Winter Wear"],
    "Home & Kitchen": ["Cookware", "Furniture", "Decor", "Appliances", "Storage"],
    "Grocery": ["Snacks", "Beverages", "Dairy", "Staples", "Frozen Foods"],
    "Beauty & Personal Care": ["Skincare", "Haircare", "Makeup", "Fragrances", "Grooming"],
}

regions = ["North", "South", "East", "West", "Central"]
seasons = ["Winter", "Spring", "Summer", "Monsoon", "Festive"]

# Baseline profit margin ranges (%) and inventory turnover behavior differ by category
category_margin_profile = {
    "Electronics": (0.06, 0.14),           # thin margins
    "Apparel": (0.18, 0.35),               # fashion, seasonal discounts
    "Home & Kitchen": (0.15, 0.28),
    "Grocery": (0.04, 0.10),               # very thin margins, fast turnover
    "Beauty & Personal Care": (0.22, 0.40),  # high margin
}

category_inventory_days_profile = {
    "Electronics": (25, 70),
    "Apparel": (30, 120),
    "Home & Kitchen": (40, 100),
    "Grocery": (3, 20),
    "Beauty & Personal Care": (20, 60),
}

rows = []
for i in range(N):
    category = np.random.choice(list(categories.keys()), p=[0.22, 0.24, 0.20, 0.20, 0.14])
    subcategory = np.random.choice(categories[category])
    region = np.random.choice(regions)
    season = np.random.choice(seasons, p=[0.2, 0.2, 0.2, 0.2, 0.2])

    unit_cost = np.round(np.random.uniform(50, 3000) if category == "Electronics" else
                          np.random.uniform(10, 500), 2)

    lo, hi = category_margin_profile[category]
    margin_pct = np.random.uniform(lo, hi)

    # Festive season boosts margin slightly for Apparel/Beauty, discounts hurt Electronics
    if season == "Festive":
        if category in ["Apparel", "Beauty & Personal Care"]:
            margin_pct += np.random.uniform(0.0, 0.05)
        elif category == "Electronics":
            margin_pct -= np.random.uniform(0.01, 0.04)
    margin_pct = max(margin_pct, 0.01)

    unit_price = np.round(unit_cost * (1 + margin_pct), 2)

    inv_lo, inv_hi = category_inventory_days_profile[category]
    inventory_days = int(np.random.uniform(inv_lo, inv_hi))
    # Slow-moving stock tends to correlate with lower realized margin due to markdowns
    if inventory_days > (inv_lo + inv_hi) / 2:
        markdown = np.random.uniform(0.0, 0.15)
        unit_price = np.round(unit_price * (1 - markdown), 2)

    quantity_sold = int(np.random.poisson(lam=15 if category == "Grocery" else 6) + 1)

    revenue = np.round(unit_price * quantity_sold, 2)
    cost = np.round(unit_cost * quantity_sold, 2)
    profit = np.round(revenue - cost, 2)
    profit_margin_pct = np.round((profit / revenue) * 100, 2) if revenue > 0 else 0

    # occasional missing/null values to simulate real-world messiness
    if np.random.rand() < 0.02:
        inventory_days = np.nan
    if np.random.rand() < 0.01:
        region = None

    rows.append({
        "transaction_id": f"TXN{100000+i}",
        "category": category,
        "subcategory": subcategory,
        "region": region,
        "season": season,
        "unit_cost": unit_cost,
        "unit_price": unit_price,
        "quantity_sold": quantity_sold,
        "inventory_days": inventory_days,
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "profit_margin_pct": profit_margin_pct,
    })

df = pd.DataFrame(rows)
df.to_csv("retail_transactions.csv", index=False)
print(df.shape)
print(df.head())
print("\nNulls:\n", df.isna().sum())
