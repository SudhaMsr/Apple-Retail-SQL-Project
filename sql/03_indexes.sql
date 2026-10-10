-- ============================================================
-- Indexes for a 1M-row sales table
--
-- Without indexes, filtering sales by product, store or date is a sequential scan of
-- ~1M rows. Compare the plans before and after with:
--
--   EXPLAIN ANALYZE SELECT * FROM sales WHERE product_id = 'P-44';
--   EXPLAIN ANALYZE SELECT * FROM sales WHERE store_id = 'ST-1' AND sale_date >= DATE '2024-01-01';
--
-- Before: "Seq Scan on sales". After: "Bitmap Index Scan" / "Index Scan" on the indexes below.
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_sales_product_id  ON sales (product_id);
CREATE INDEX IF NOT EXISTS idx_sales_store_date  ON sales (store_id, sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_sale_date   ON sales (sale_date);
CREATE INDEX IF NOT EXISTS idx_warranty_sale_id  ON warranty (sale_id);
CREATE INDEX IF NOT EXISTS idx_warranty_date     ON warranty (claim_date);
CREATE INDEX IF NOT EXISTS idx_products_category ON products (category_id);
