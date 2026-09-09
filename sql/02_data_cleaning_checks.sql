-- ==============================================================================
-- 02_data_cleaning_checks.sql
-- Auditing and Quality Assurance Queries for E-Commerce Sales Data
-- ==============================================================================

-- 1. Check for Duplicate Orders / Line Items
SELECT 
    order_id, 
    customer_id, 
    order_date, 
    product, 
    COUNT(*) AS duplicate_count
FROM fact_sales
GROUP BY order_id, customer_id, order_date, product
HAVING COUNT(*) > 1;

-- 2. Check for Missing (NULL) or Blank Keys in Fact Table
SELECT 
    COUNT(*) AS total_records,
    SUM(CASE WHEN order_id IS NULL OR TRIM(order_id) = '' THEN 1 ELSE 0 END) AS null_orders,
    SUM(CASE WHEN customer_id IS NULL OR TRIM(customer_id) = '' THEN 1 ELSE 0 END) AS null_customers,
    SUM(CASE WHEN order_date IS NULL THEN 1 ELSE 0 END) AS null_dates,
    SUM(CASE WHEN product IS NULL THEN 1 ELSE 0 END) AS null_products,
    SUM(CASE WHEN region IS NULL THEN 1 ELSE 0 END) AS null_regions
FROM fact_sales;

-- 3. Verify Referential Integrity (Orphan Foreign Keys)
SELECT 'Orphan Customers' AS check_name, COUNT(*) AS issue_count
FROM fact_sales f
LEFT JOIN dim_customers c ON f.customer_id = c.customer_id
WHERE c.customer_id IS NULL
UNION ALL
SELECT 'Orphan Products', COUNT(*)
FROM fact_sales f
LEFT JOIN dim_products p ON f.product = p.product_name
WHERE p.product_name IS NULL
UNION ALL
SELECT 'Orphan Regions', COUNT(*)
FROM fact_sales f
LEFT JOIN dim_regions r ON f.region = r.region
WHERE r.region IS NULL;

-- 4. Check for Invalid Numeric Ranges (Negative Quantities, Prices, or Revenue Mismatches)
SELECT 
    order_id,
    quantity,
    unit_price,
    discount,
    revenue,
    ROUND(quantity * unit_price * (1 - discount), 2) AS expected_revenue,
    ABS(revenue - ROUND(quantity * unit_price * (1 - discount), 2)) AS discrepancy
FROM fact_sales
WHERE quantity <= 0 
   OR unit_price <= 0 
   OR discount < 0 
   OR discount > 1
   OR ABS(revenue - ROUND(quantity * unit_price * (1 - discount), 2)) > 0.05;

-- 5. Standardized Casing Validation
SELECT DISTINCT region, category
FROM fact_sales
ORDER BY region, category;
