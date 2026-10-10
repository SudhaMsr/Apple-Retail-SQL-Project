"""
Generate a synthetic Apple-style retail dataset (~1M sales rows) with the same files and
columns as the Kaggle "Apple Retail Sales" dataset:

    category.csv  products.csv  stores.csv  sales.csv  warranty.csv

The data is fake but deliberately realistic so the SQL analysis has something to find:
holiday peaks, launch-month spikes, flagship stores, and products that fail more often.

    python data/generate.py              # writes data/raw/*.csv
    python data/generate.py --rows 200000

If you have the real Kaggle CSVs, put them in data/raw/ instead and skip this script.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
START, END = np.datetime64("2020-01-01"), np.datetime64("2024-12-31")
OUT = Path(__file__).parent / "raw"

CATEGORIES = [
    ("CAT-1", "Smartphone"),
    ("CAT-2", "Laptop"),
    ("CAT-3", "Tablet"),
    ("CAT-4", "Smartwatch"),
    ("CAT-5", "Audio"),
    ("CAT-6", "Desktop"),
    ("CAT-7", "Accessories"),
    ("CAT-8", "Streaming Device"),
    ("CAT-9", "Smart Speaker"),
    ("CAT-10", "Subscription Service"),
]

# (name, category, launch date, price in USD, popularity weight, failure rate multiplier)
PRODUCTS = [
    ("iPhone 11", "CAT-1", "2019-09-20", 699, 10, 1.0), ("iPhone 11 Pro", "CAT-1", "2019-09-20", 999, 7, 1.1),
    ("MacBook Pro 16 (2019)", "CAT-2", "2019-11-13", 2399, 3, 1.2), ("MacBook Air (2020)", "CAT-2", "2020-03-18", 999, 6, 0.9),
    ("iPad (8th gen)", "CAT-3", "2020-09-18", 329, 6, 0.9), ("iPad Pro 11 (2020)", "CAT-3", "2020-03-25", 799, 3, 1.1),
    ("Apple Watch Series 5", "CAT-4", "2019-09-20", 399, 6, 1.0), ("AirPods Pro (1st gen)", "CAT-5", "2019-10-30", 249, 8, 1.7),
    ("iPhone 12", "CAT-1", "2020-10-23", 799, 9, 1.1), ("iPhone 12 Pro", "CAT-1", "2020-10-23", 999, 7, 1.0),
    ("iPhone 13", "CAT-1", "2021-09-24", 799, 10, 0.9), ("iPhone 13 Pro", "CAT-1", "2021-09-24", 999, 8, 0.9),
    ("iPhone SE (3rd gen)", "CAT-1", "2022-03-18", 429, 6, 0.8), ("iPhone 14", "CAT-1", "2022-09-16", 799, 10, 1.0),
    ("iPhone 14 Pro", "CAT-1", "2022-09-16", 999, 9, 1.2), ("iPhone 15", "CAT-1", "2023-09-22", 799, 11, 1.0),
    ("iPhone 15 Pro", "CAT-1", "2023-09-22", 999, 10, 1.4), ("iPhone 16", "CAT-1", "2024-09-20", 799, 11, 0.9),
    ("iPhone 16 Pro", "CAT-1", "2024-09-20", 999, 10, 1.0),
    ("MacBook Air (M1)", "CAT-2", "2020-11-17", 999, 7, 0.7), ("MacBook Pro 13 (M1)", "CAT-2", "2020-11-17", 1299, 4, 0.8),
    ("MacBook Pro 14", "CAT-2", "2021-10-26", 1999, 4, 1.1), ("MacBook Air (M2)", "CAT-2", "2022-07-15", 1199, 6, 0.8),
    ("MacBook Pro 16", "CAT-2", "2023-01-24", 2499, 3, 1.3), ("MacBook Air 15", "CAT-2", "2023-06-13", 1299, 5, 0.7),
    ("MacBook Air (M3)", "CAT-2", "2024-03-08", 1099, 6, 0.7),
    ("iPad (9th gen)", "CAT-3", "2021-09-24", 329, 7, 0.9), ("iPad Air (5th gen)", "CAT-3", "2022-03-18", 599, 5, 0.9),
    ("iPad Pro 11", "CAT-3", "2021-05-21", 799, 4, 1.2), ("iPad Pro 12.9", "CAT-3", "2022-10-26", 1099, 3, 1.5),
    ("iPad mini (6th gen)", "CAT-3", "2021-09-24", 499, 4, 0.8), ("iPad (10th gen)", "CAT-3", "2022-10-26", 449, 6, 1.0),
    ("Apple Watch Series 6", "CAT-4", "2020-09-18", 399, 5, 1.0), ("Apple Watch SE", "CAT-4", "2020-09-18", 279, 6, 0.9),
    ("Apple Watch Series 7", "CAT-4", "2021-10-15", 399, 6, 1.1), ("Apple Watch Series 8", "CAT-4", "2022-09-16", 399, 6, 1.0),
    ("Apple Watch Ultra", "CAT-4", "2022-09-23", 799, 3, 1.3), ("Apple Watch Series 9", "CAT-4", "2023-09-22", 399, 6, 0.9),
    ("AirPods (3rd gen)", "CAT-5", "2021-10-26", 179, 8, 1.2), ("AirPods Pro (2nd gen)", "CAT-5", "2022-09-23", 249, 9, 1.6),
    ("AirPods Max", "CAT-5", "2020-12-15", 549, 3, 1.8), ("Beats Studio Buds", "CAT-5", "2021-06-24", 149, 5, 1.3),
    ("iMac 24", "CAT-6", "2021-05-21", 1299, 3, 0.8), ("Mac mini (M2)", "CAT-6", "2023-01-24", 599, 3, 0.6),
    ("Mac Studio", "CAT-6", "2022-03-18", 1999, 1.5, 0.9), ("Mac Pro", "CAT-6", "2023-06-13", 6999, 0.4, 1.0),
    ("MagSafe Charger", "CAT-7", "2020-10-23", 39, 9, 0.5), ("Magic Keyboard", "CAT-7", "2021-05-21", 99, 5, 0.4),
    ("Apple Pencil (2nd gen)", "CAT-7", "2019-09-20", 129, 6, 0.7), ("AirTag", "CAT-7", "2021-04-30", 29, 9, 0.3),
    ("USB-C to Lightning Cable", "CAT-7", "2019-09-20", 19, 10, 0.4), ("Magic Mouse", "CAT-7", "2021-05-21", 79, 5, 0.5),
    ("Apple TV 4K", "CAT-8", "2021-05-21", 179, 4, 0.6), ("Apple TV HD", "CAT-8", "2019-09-20", 149, 2, 0.6),
    ("HomePod mini", "CAT-9", "2020-11-16", 99, 5, 0.7), ("HomePod (2nd gen)", "CAT-9", "2023-02-03", 299, 3, 0.8),
    ("AppleCare+ (1 year)", "CAT-10", "2019-09-20", 199, 4, 0.0), ("Apple One Bundle", "CAT-10", "2020-10-30", 195, 3, 0.0),
]

# (store name, city, country, size weight)
STORES = [
    ("Apple Fifth Avenue", "New York", "United States", 3.2), ("Apple Union Square", "San Francisco", "United States", 2.4),
    ("Apple Michigan Avenue", "Chicago", "United States", 2.0), ("Apple The Grove", "Los Angeles", "United States", 2.1),
    ("Apple Lincoln Road", "Miami", "United States", 1.5), ("Apple Bellevue Square", "Seattle", "United States", 1.4),
    ("Apple Boylston Street", "Boston", "United States", 1.4), ("Apple Georgetown", "Washington", "United States", 1.3),
    ("Apple Regent Street", "London", "United Kingdom", 2.8), ("Apple Covent Garden", "London", "United Kingdom", 2.0),
    ("Apple Cabot Circus", "Bristol", "United Kingdom", 1.1), ("Apple Trafford Centre", "Manchester", "United Kingdom", 1.2),
    ("Apple Princes Street", "Edinburgh", "United Kingdom", 0.9), ("Apple Champs-Élysées", "Paris", "France", 2.2),
    ("Apple Opéra", "Paris", "France", 1.6), ("Apple Kurfürstendamm", "Berlin", "Germany", 1.6),
    ("Apple Rosenstraße", "Munich", "Germany", 1.4), ("Apple Via del Corso", "Rome", "Italy", 1.3),
    ("Apple Piazza Liberty", "Milan", "Italy", 1.5), ("Apple Passeig de Gràcia", "Barcelona", "Spain", 1.4),
    ("Apple Puerta del Sol", "Madrid", "Spain", 1.4), ("Apple Amsterdam", "Amsterdam", "Netherlands", 1.2),
    ("Apple Ginza", "Tokyo", "Japan", 2.6), ("Apple Shibuya", "Tokyo", "Japan", 2.0), ("Apple Shinsaibashi", "Osaka", "Japan", 1.5),
    ("Apple Sanlitun", "Beijing", "China", 2.5), ("Apple Nanjing East", "Shanghai", "China", 2.7),
    ("Apple Tianhe Road", "Guangzhou", "China", 1.8), ("Apple Orchard Road", "Singapore", "Singapore", 1.9),
    ("Apple Marina Bay Sands", "Singapore", "Singapore", 1.7), ("Apple Myeongdong", "Seoul", "South Korea", 1.6),
    ("Apple Garosugil", "Seoul", "South Korea", 1.4), ("Apple Central World", "Bangkok", "Thailand", 1.3),
    ("Apple BKC", "Mumbai", "India", 1.5), ("Apple Saket", "New Delhi", "India", 1.3),
    ("Apple Dubai Mall", "Dubai", "UAE", 2.0), ("Apple Yas Mall", "Abu Dhabi", "UAE", 1.2),
    ("Apple Sydney", "Sydney", "Australia", 2.1), ("Apple Chadstone", "Melbourne", "Australia", 1.5),
    ("Apple Eaton Centre", "Toronto", "Canada", 1.7), ("Apple Pacific Centre", "Vancouver", "Canada", 1.3),
    ("Apple Antara", "Mexico City", "Mexico", 1.2), ("Apple Morumbi", "São Paulo", "Brazil", 1.1),
]

REPAIR_STATUS = np.array(["Completed", "Pending", "Rejected", "Warranty Void"])


def main(rows: int) -> None:
    rng = np.random.default_rng(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    category = pd.DataFrame(CATEGORIES, columns=["category_id", "category_name"])

    products = pd.DataFrame(PRODUCTS, columns=["product_name", "category_id", "launch_date", "price", "pop", "fail"])
    products.insert(0, "product_id", [f"P-{i + 1}" for i in range(len(products))])
    products["launch_date"] = pd.to_datetime(products["launch_date"])

    stores = pd.DataFrame(STORES, columns=["store_name", "city", "country", "size"])
    stores.insert(0, "store_id", [f"ST-{i + 1}" for i in range(len(stores))])

    # ── sales: pick a store and a day, then a product that existed on that day
    days = np.arange(START, END + np.timedelta64(1, "D"))
    d = pd.DatetimeIndex(days)
    day_w = np.ones(len(days))
    day_w *= np.where(d.month == 12, 1.9, 1.0) * np.where(d.month == 11, 1.35, 1.0)  # holidays
    day_w *= np.where(d.month.isin([8, 9]), 1.15, 1.0)  # back to school
    day_w *= np.where(d.dayofweek >= 5, 1.3, 1.0)  # weekends
    day_w *= 1 + 0.07 * (d.year - 2020)  # steady growth
    sale_day = rng.choice(len(days), size=rows, p=day_w / day_w.sum())

    store_w = stores["size"].to_numpy()
    sale_store = rng.choice(len(stores), size=rows, p=store_w / store_w.sum())

    launch = products["launch_date"].to_numpy().astype("datetime64[D]")
    pop = products["pop"].to_numpy(dtype=float)
    sale_product = np.empty(rows, dtype=int)
    # process day by day so only launched products are sold, with a launch-month spike
    order = np.argsort(sale_day)
    bounds = np.searchsorted(sale_day[order], np.arange(len(days) + 1))
    for di in range(len(days)):
        idx = order[bounds[di]:bounds[di + 1]]
        if not len(idx):
            continue
        age = (days[di] - launch).astype(int)
        w = np.where(age >= 0, pop, 0.0)
        w = w * np.where((age >= 0) & (age < 45), 2.4, 1.0)  # launch spike
        w = w * np.where(age > 900, 0.45, 1.0)  # older models fade
        sale_product[idx] = rng.choice(len(products), size=len(idx), p=w / w.sum())

    qty = rng.choice([1, 1, 1, 1, 1, 2, 2, 3, 4, 5, 6, 8, 10], size=rows)
    sales = pd.DataFrame({
        "sale_id": [f"S-{i + 1}" for i in range(rows)],
        "sale_date": days[sale_day],
        "store_id": stores["store_id"].to_numpy()[sale_store],
        "product_id": products["product_id"].to_numpy()[sale_product],
        "quantity": qty,
    }).sort_values("sale_date", kind="stable")
    sales["sale_id"] = [f"S-{i + 1}" for i in range(rows)]

    # ── warranty: ~3% of sales, more for fragile products and pricier items
    fail = products["fail"].to_numpy()[sale_product[sales.index]]
    p_claim = 0.03 * fail * np.where(products["price"].to_numpy()[sale_product[sales.index]] > 900, 1.15, 1.0)
    claimed = rng.random(rows) < p_claim
    claim_sales = sales[claimed]
    delay = rng.gamma(shape=1.6, scale=140, size=len(claim_sales)).astype(int) + 3
    claim_date = claim_sales["sale_date"].to_numpy() + delay.astype("timedelta64[D]")
    keep = claim_date <= np.datetime64("2025-06-30")
    status = rng.choice(REPAIR_STATUS, size=keep.sum(), p=[0.55, 0.12, 0.13, 0.20])
    warranty = pd.DataFrame({
        "claim_id": [f"CL-{i + 1}" for i in range(keep.sum())],
        "claim_date": claim_date[keep],
        "sale_id": claim_sales["sale_id"].to_numpy()[keep],
        "repair_status": status,
    }).sort_values("claim_date", kind="stable")
    warranty["claim_id"] = [f"CL-{i + 1}" for i in range(len(warranty))]

    category.to_csv(OUT / "category.csv", index=False)
    products.drop(columns=["pop", "fail"]).assign(launch_date=products["launch_date"].dt.date).to_csv(OUT / "products.csv", index=False)
    stores.drop(columns=["size"]).to_csv(OUT / "stores.csv", index=False)
    sales.to_csv(OUT / "sales.csv", index=False)
    warranty.to_csv(OUT / "warranty.csv", index=False)
    print(f"categories={len(category)} products={len(products)} stores={len(stores)} sales={len(sales):,} warranty={len(warranty):,}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rows", type=int, default=1_040_200, help="number of sales rows (default 1,040,200)")
    main(ap.parse_args().rows)
