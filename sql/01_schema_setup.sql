-- ==============================================================================
-- 01_schema_setup.sql
-- Relational Schema DDL for User's E-Commerce Dataset
-- ==============================================================================

-- 1. Fact Table: Central Sales Transactions
DROP TABLE IF EXISTS fact_sales;
CREATE TABLE fact_sales (
    order_id VARCHAR(20) PRIMARY KEY,
    order_date DATE NOT NULL,
    customer VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    product VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0),
    discount NUMERIC(5, 2) NOT NULL CHECK (discount >= 0 AND discount <= 1),
    payment_status VARCHAR(20) NOT NULL,
    revenue NUMERIC(12, 2) NOT NULL CHECK (revenue >= 0)
);

-- 2. Customer Dimension
DROP TABLE IF EXISTS dim_customers;
CREATE TABLE dim_customers (
    customer VARCHAR(50) PRIMARY KEY,
    region VARCHAR(50) NOT NULL,
    total_orders INTEGER NOT NULL,
    total_units INTEGER NOT NULL,
    total_revenue NUMERIC(12, 2) NOT NULL,
    aov NUMERIC(10, 2) NOT NULL,
    customer_type VARCHAR(30) NOT NULL
);

-- 3. Product Dimension
DROP TABLE IF EXISTS dim_products;
CREATE TABLE dim_products (
    product VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    total_units_sold INTEGER NOT NULL,
    total_revenue NUMERIC(12, 2) NOT NULL
);

-- 4. Regional Dimension
DROP TABLE IF EXISTS dim_regions;
CREATE TABLE dim_regions (
    region VARCHAR(50) PRIMARY KEY,
    regional_lead VARCHAR(50) NOT NULL,
    target_revenue NUMERIC(12, 2) NOT NULL
);

-- 5. Date Dimension
DROP TABLE IF EXISTS dim_dates;
CREATE TABLE dim_dates (
    date_key DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL,
    day_of_week VARCHAR(20) NOT NULL
);

-- Indexes for Fast Querying
CREATE INDEX IF NOT EXISTS idx_fact_cust ON fact_sales(customer);
CREATE INDEX IF NOT EXISTS idx_fact_date ON fact_sales(order_date);
CREATE INDEX IF NOT EXISTS idx_fact_cat ON fact_sales(category);
CREATE INDEX IF NOT EXISTS idx_fact_reg ON fact_sales(region);
CREATE INDEX IF NOT EXISTS idx_fact_prod ON fact_sales(product);
