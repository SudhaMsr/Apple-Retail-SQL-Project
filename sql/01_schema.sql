-- ============================================================
-- Apple Retail Sales: schema (PostgreSQL)
-- ============================================================

DROP TABLE IF EXISTS warranty;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS category;

CREATE TABLE category (
    category_id   VARCHAR(10) PRIMARY KEY,
    category_name VARCHAR(40) NOT NULL
);

CREATE TABLE products (
    product_id   VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(60) NOT NULL,
    category_id  VARCHAR(10) NOT NULL REFERENCES category (category_id),
    launch_date  DATE        NOT NULL,
    price        NUMERIC(10, 2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE stores (
    store_id   VARCHAR(10) PRIMARY KEY,
    store_name VARCHAR(60) NOT NULL,
    city       VARCHAR(40) NOT NULL,
    country    VARCHAR(40) NOT NULL
);

CREATE TABLE sales (
    sale_id    VARCHAR(15) PRIMARY KEY,
    sale_date  DATE        NOT NULL,
    store_id   VARCHAR(10) NOT NULL REFERENCES stores (store_id),
    product_id VARCHAR(10) NOT NULL REFERENCES products (product_id),
    quantity   INT         NOT NULL CHECK (quantity > 0)
);

CREATE TABLE warranty (
    claim_id      VARCHAR(15) PRIMARY KEY,
    claim_date    DATE        NOT NULL,
    sale_id       VARCHAR(15) NOT NULL REFERENCES sales (sale_id),
    repair_status VARCHAR(20) NOT NULL
);
