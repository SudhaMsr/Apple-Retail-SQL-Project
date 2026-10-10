-- ============================================================
-- Load the CSVs (run with psql from the repo root)
--   psql -d apple_retail -f sql/01_schema.sql -f sql/02_load.sql -f sql/03_indexes.sql
-- Parents first so the foreign keys are satisfied.
-- ============================================================

\copy category FROM 'data/raw/category.csv' WITH (FORMAT csv, HEADER true)
\copy products FROM 'data/raw/products.csv' WITH (FORMAT csv, HEADER true)
\copy stores   FROM 'data/raw/stores.csv'   WITH (FORMAT csv, HEADER true)
\copy sales    FROM 'data/raw/sales.csv'    WITH (FORMAT csv, HEADER true)
\copy warranty FROM 'data/raw/warranty.csv' WITH (FORMAT csv, HEADER true)

ANALYZE;

SELECT 'category' AS table_name, COUNT(*) AS rows FROM category
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'stores',   COUNT(*) FROM stores
UNION ALL SELECT 'sales',    COUNT(*) FROM sales
UNION ALL SELECT 'warranty', COUNT(*) FROM warranty;
