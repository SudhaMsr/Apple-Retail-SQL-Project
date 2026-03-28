# Consumer Electronics Retail Analytics

An end-to-end SQL analytics project built on a **1M+ row synthetic retail sales dataset** covering products, stores, transactions, categories, and warranty claims.

This project simulates a real-world **consumer electronics retail analytics use case** and focuses on:
- relational database design
- SQL querying and optimisation
- sales performance analysis
- warranty / post-sales risk analysis
- business-facing insights for retail decision-making

---

## Project Overview

The goal of this project is to analyse retail sales performance across a consumer electronics ecosystem using SQL and structured business questions.

The dataset includes:
- **Sales transactions**
- **Products**
- **Stores**
- **Product categories**
- **Warranty claims**

This project was designed to mirror practical analytics work such as:
- revenue trend analysis
- store and regional performance benchmarking
- product-level sales analysis
- warranty claim behaviour
- query performance tuning on larger datasets

---

## Business Questions Solved

This project answers questions such as:

### Sales & Revenue
- Which product categories generate the most revenue?
- What are the monthly and quarterly sales trends?
- Which stores consistently outperform others?

### Product Performance
- Which products are the top sellers by revenue and volume?
- Which categories are most discount-dependent?
- Which products are underperforming relative to category averages?

### Warranty & Risk
- Which products have the highest warranty claim rates?
- Are premium products associated with more post-sale issues?
- Which stores sell the highest-risk products?

### Advanced SQL Analysis
- Rank products within categories using window functions
- Compare monthly performance using `LAG()` and `LEAD()`
- Calculate rolling revenue trends
- Identify store-level performance drops over time

---

## Dataset

This project uses the **Apple Retail Sales Dataset** from Kaggle as a base dataset.

> **Important:** This is a **synthetic dataset**, not real Apple Inc. sales data.

It includes the following files:
- `category.csv`
- `products.csv`
- `sales.csv`
- `stores.csv`
- `warranty.csv`

The dataset was used purely for educational and portfolio purposes.

---

## Database Schema

The project is built around the following relational tables:

- `categories`
- `products`
- `stores`
- `sales`
- `warranty`

### Entity Relationships
- Each **product** belongs to a **category**
- Each **sale** is linked to a **product** and **store**
- Each **warranty claim** is linked to a **sale** / **product**

> ER Diagram: see `/images/er_diagram.png`

---

## Tech Stack

- **SQL** (PostgreSQL)
- **Python** (optional analysis / EDA)
- **Pandas**
- **Jupyter Notebook**
- **Power BI / Tableau** (optional dashboarding)
- **Git / GitHub**

---

## Project Structure

```bash
consumer-electronics-retail-analytics/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── sql/
│   ├── 01_schema.sql
│   ├── 02_constraints_indexes.sql
│   ├── 03_data_quality_checks.sql
│   ├── 04_business_queries.sql
│   ├── 05_advanced_window_functions.sql
│   └── 06_performance_tuning.sql
│
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_sales_analysis.ipynb
│
├── dashboard/
│   └── dashboard_notes.md
│
├── images/
│   ├── er_diagram.png
│   ├── dashboard_overview.png
│   └── query_outputs.png
│
├── README.md
├── requirements.txt
└── .gitignore
