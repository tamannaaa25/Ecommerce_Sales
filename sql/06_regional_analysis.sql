-- ==============================================================================
-- 06_regional_analysis.sql
-- Regional Performance, AOV, Market Share, and Regional Category Cross-Tabulation
-- ==============================================================================

-- 1. Regional Performance Overview (Revenue, Orders, AOV, Share)
SELECT 
    f.region,
    r.regional_manager,
    r.market_tier,
    r.target_growth_rate,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.revenue), 2) AS regional_revenue,
    ROUND(SUM(f.revenue) * 100.0 / (SELECT SUM(revenue) FROM fact_sales), 2) AS revenue_share_pct,
    ROUND(SUM(f.revenue) * 1.0 / COUNT(DISTINCT f.order_id), 2) AS regional_aov,
    DENSE_RANK() OVER (ORDER BY SUM(f.revenue) DESC) AS regional_rank
FROM fact_sales f
JOIN dim_regions r ON f.region = r.region
GROUP BY f.region, r.regional_manager, r.market_tier, r.target_growth_rate
ORDER BY regional_revenue DESC;

-- 2. Regional Product Category Breakdown
SELECT 
    f.region,
    f.category,
    COUNT(DISTINCT f.order_id) AS order_count,
    ROUND(SUM(f.revenue), 2) AS category_revenue,
    ROUND(
        SUM(f.revenue) * 100.0 / SUM(SUM(f.revenue)) OVER (PARTITION BY f.region), 
        2
    ) AS pct_of_regional_revenue
FROM fact_sales f
GROUP BY f.region, f.category
ORDER BY f.region, category_revenue DESC;

-- 3. Top Selling Product in Each Region (Window Function: PARTITION BY Region)
WITH regional_products AS (
    SELECT 
        f.region,
        f.product,
        f.category,
        SUM(f.quantity) AS units_sold,
        ROUND(SUM(f.revenue), 2) AS revenue_generated,
        ROW_NUMBER() OVER (
            PARTITION BY f.region 
            ORDER BY SUM(f.revenue) DESC
        ) AS rank_in_region
    FROM fact_sales f
    GROUP BY f.region, f.product, f.category
)
SELECT 
    region,
    rank_in_region,
    product,
    category,
    units_sold,
    revenue_generated
FROM regional_products
WHERE rank_in_region <= 3
ORDER BY region, rank_in_region;
