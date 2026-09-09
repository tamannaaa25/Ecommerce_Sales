-- ==============================================================================
-- 05_product_performance.sql
-- Product Rankings, Category Aggregations, Window Partitions, and Pareto (80/20) Analysis
-- ==============================================================================

-- 1. Top Products by Total Revenue and Unit Volume
SELECT 
    ROW_NUMBER() OVER (ORDER BY SUM(f.revenue) DESC) AS rank,
    f.product,
    f.category,
    COUNT(f.order_id) AS total_orders,
    SUM(f.quantity) AS units_sold,
    ROUND(AVG(f.unit_price), 2) AS avg_unit_price,
    ROUND(AVG(f.discount) * 100, 1) AS avg_discount_pct,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.revenue) * 100.0 / (SELECT SUM(revenue) FROM fact_sales), 2) AS pct_of_total_sales
FROM fact_sales f
GROUP BY f.product, f.category
ORDER BY total_revenue DESC;

-- 2. Category Performance Summary
SELECT 
    f.category,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS category_revenue,
    ROUND(SUM(f.revenue) * 100.0 / (SELECT SUM(revenue) FROM fact_sales), 2) AS category_revenue_share_pct,
    ROUND(SUM(f.revenue) * 1.0 / COUNT(DISTINCT f.order_id), 2) AS category_aov,
    ROUND(AVG(f.discount) * 100, 1) AS avg_category_discount_pct
FROM fact_sales f
GROUP BY f.category
ORDER BY category_revenue DESC;

-- 3. Top 3 Products within Each Category (Window Function: PARTITION BY)
WITH ranked_products_by_category AS (
    SELECT 
        f.category,
        f.product,
        SUM(f.quantity) AS units_sold,
        ROUND(SUM(f.revenue), 2) AS product_revenue,
        DENSE_RANK() OVER (
            PARTITION BY f.category 
            ORDER BY SUM(f.revenue) DESC
        ) AS category_rank
    FROM fact_sales f
    GROUP BY f.category, f.product
)
SELECT 
    category,
    category_rank,
    product,
    units_sold,
    product_revenue
FROM ranked_products_by_category
WHERE category_rank <= 3
ORDER BY category, category_rank;

-- 4. Pareto 80/20 Product Analysis (Cumulative Revenue Distribution)
WITH product_totals AS (
    SELECT 
        f.product,
        f.category,
        ROUND(SUM(f.revenue), 2) AS product_revenue
    FROM fact_sales f
    GROUP BY f.product, f.category
),
product_cumulative AS (
    SELECT 
        product,
        category,
        product_revenue,
        ROW_NUMBER() OVER (ORDER BY product_revenue DESC) AS product_rank,
        COUNT(*) OVER () AS total_products,
        SUM(product_revenue) OVER (ORDER BY product_revenue DESC) AS running_revenue,
        SUM(product_revenue) OVER () AS overall_revenue
    FROM product_totals
)
SELECT 
    product_rank,
    product,
    category,
    product_revenue,
    ROUND(product_revenue * 100.0 / overall_revenue, 2) AS individual_revenue_pct,
    ROUND(running_revenue * 100.0 / overall_revenue, 2) AS cumulative_revenue_pct,
    CASE 
        WHEN (running_revenue * 1.0 / overall_revenue) <= 0.80 THEN 'Top 80% Core Driver'
        ELSE 'Long-Tail 20%'
    END AS pareto_classification
FROM product_cumulative
ORDER BY product_rank ASC;
