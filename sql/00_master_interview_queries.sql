-- ==============================================================================
-- 00_master_interview_queries.sql
-- Master SQL Queries on User's 50-Order E-Commerce Dataset
-- Demonstrating: JOIN, GROUP BY, HAVING, CASE WHEN, Subqueries, CTEs, Window Functions
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. JOIN + GROUP BY + AGGREGATION
-- Business Question: What is the total sales, total orders, and AOV by Region and Category?
-- ------------------------------------------------------------------------------
SELECT 
    f.region,
    f.category,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(AVG(f.revenue), 2) AS avg_order_value
FROM fact_sales f
INNER JOIN dim_regions r ON f.region = r.region
GROUP BY f.region, f.category
ORDER BY f.region ASC, total_revenue DESC;


-- ------------------------------------------------------------------------------
-- 2. HAVING CLAUSE (Filtering Aggregated Results)
-- Business Question: Which top customers have generated over ₹1,00,000 in total spend?
-- (Identifies VIP high-value repeat purchasers like Aarav, Isha, Sanya)
-- ------------------------------------------------------------------------------
SELECT 
    customer,
    COUNT(order_id) AS order_count,
    SUM(quantity) AS total_units_bought,
    ROUND(SUM(revenue), 2) AS total_spent,
    ROUND(AVG(revenue), 2) AS avg_spend_per_order
FROM fact_sales
GROUP BY customer
HAVING SUM(revenue) >= 100000
ORDER BY total_spent DESC;


-- ------------------------------------------------------------------------------
-- 3. CASE WHEN (Conditional Logic & Segmentation)
-- Business Question: Segment orders by size (High-Ticket vs Standard) and Payment Status
-- ------------------------------------------------------------------------------
SELECT 
    order_id,
    order_date,
    customer,
    product,
    revenue,
    CASE 
        WHEN revenue >= 40000 THEN 'High-Ticket Order (₹40,000+)'
        WHEN revenue >= 15000 THEN 'Mid-Tier Order (₹15,000-₹39,999)'
        ELSE 'Standard Order (<₹15,000)'
    END AS order_value_tier,
    CASE 
        WHEN payment_status = 'Paid' THEN 'Settled'
        WHEN payment_status = 'Pending' THEN 'Action Required: Follow Up'
        WHEN payment_status = 'Failed' THEN 'Action Required: Retry'
        ELSE 'Other'
    END AS payment_action
FROM fact_sales
ORDER BY revenue DESC
LIMIT 15;


-- ------------------------------------------------------------------------------
-- 4. SUBQUERIES (Benchmarking Against Averages)
-- Business Question: Find all products whose total revenue is higher than the overall average product revenue.
-- ------------------------------------------------------------------------------
SELECT 
    product,
    category,
    SUM(quantity) AS units_sold,
    ROUND(SUM(revenue), 2) AS product_revenue,
    -- Benchmark average across all 8 products
    ROUND((SELECT AVG(prod_rev) FROM (
        SELECT SUM(revenue) AS prod_rev FROM fact_sales GROUP BY product
    )), 2) AS benchmark_avg_product_revenue
FROM fact_sales
GROUP BY product, category
HAVING SUM(revenue) > (
    SELECT AVG(prod_rev) FROM (
        SELECT SUM(revenue) AS prod_rev FROM fact_sales GROUP BY product
    )
)
ORDER BY product_revenue DESC;


-- ------------------------------------------------------------------------------
-- 5. CTEs (Common Table Expressions) + WINDOW FUNCTIONS
-- Business Question: Calculate Monthly Revenue and MoM Growth from Jan-26 to Feb-26
-- Using LAG() and running cumulative revenue using SUM() OVER ()
-- ------------------------------------------------------------------------------
WITH monthly_revenue_cte AS (
    SELECT 
        STRFTIME('%Y-%m', order_date) AS year_month,
        COUNT(order_id) AS total_orders,
        SUM(quantity) AS total_units,
        ROUND(SUM(revenue), 2) AS current_month_revenue,
        ROUND(AVG(revenue), 2) AS monthly_aov
    FROM fact_sales
    GROUP BY year_month
)
SELECT 
    year_month,
    total_orders,
    total_units,
    current_month_revenue,
    monthly_aov,
    -- Window Function: LAG to fetch prior month
    LAG(current_month_revenue, 1) OVER (ORDER BY year_month) AS prior_month_revenue,
    -- MoM Growth %
    ROUND(
        (current_month_revenue - LAG(current_month_revenue, 1) OVER (ORDER BY year_month)) * 100.0 / 
        LAG(current_month_revenue, 1) OVER (ORDER BY year_month), 
        2
    ) AS mom_growth_pct,
    -- Window Function: Running Cumulative Total
    ROUND(SUM(current_month_revenue) OVER (ORDER BY year_month), 2) AS running_cumulative_revenue
FROM monthly_revenue_cte
ORDER BY year_month ASC;


-- ------------------------------------------------------------------------------
-- 6. WINDOW FUNCTIONS: DENSE_RANK() & PARTITION BY
-- Business Question: Rank the products within EACH category by revenue
-- ------------------------------------------------------------------------------
WITH product_category_sales AS (
    SELECT 
        category,
        product,
        SUM(quantity) AS units_sold,
        ROUND(SUM(revenue), 2) AS product_revenue,
        -- Window function: Rank within each category
        DENSE_RANK() OVER (
            PARTITION BY category 
            ORDER BY SUM(revenue) DESC
        ) AS rank_in_category
    FROM fact_sales
    GROUP BY category, product
)
SELECT 
    category,
    rank_in_category,
    product,
    units_sold,
    product_revenue
FROM product_category_sales
ORDER BY category, rank_in_category ASC;


-- ------------------------------------------------------------------------------
-- 7. REPEAT CUSTOMER ANALYSIS
-- Business Question: Customer repeat purchase frequency and lifetime spend summary
-- ------------------------------------------------------------------------------
SELECT 
    customer,
    region,
    COUNT(order_id) AS total_orders_placed,
    SUM(quantity) AS total_units_bought,
    ROUND(SUM(revenue), 2) AS total_lifetime_spend,
    ROUND(AVG(revenue), 2) AS average_order_value,
    DENSE_RANK() OVER (ORDER BY SUM(revenue) DESC) AS customer_rank
FROM fact_sales
GROUP BY customer, region
ORDER BY total_lifetime_spend DESC;
