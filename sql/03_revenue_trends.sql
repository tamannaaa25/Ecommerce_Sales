-- ==============================================================================
-- 03_revenue_trends.sql
-- Monthly Revenue Analysis, Window Functions, MoM Growth, and Cumulative Revenue
-- ==============================================================================

-- 1. Monthly Revenue, Order Volume, AOV, and Month-over-Month (MoM) Growth
WITH monthly_metrics AS (
    SELECT 
        d.year,
        d.month,
        d.year || '-' || printf('%02d', d.month) AS year_month,
        COUNT(DISTINCT f.order_id) AS total_orders,
        SUM(f.quantity) AS total_units_sold,
        ROUND(SUM(f.revenue), 2) AS total_revenue,
        ROUND(SUM(f.revenue) * 1.0 / COUNT(DISTINCT f.order_id), 2) AS aov
    FROM fact_sales f
    JOIN dim_dates d ON f.order_date = d.date_key
    GROUP BY d.year, d.month, year_month
),
mom_growth_calc AS (
    SELECT 
        year_month,
        total_orders,
        total_units_sold,
        total_revenue,
        aov,
        -- Window function: LAG to fetch previous month's revenue
        LAG(total_revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
        -- Window function: Running cumulative revenue
        ROUND(SUM(total_revenue) OVER (ORDER BY year_month), 2) AS cumulative_revenue
    FROM monthly_metrics
)
SELECT 
    year_month,
    total_orders,
    total_units_sold,
    total_revenue,
    aov,
    cumulative_revenue,
    prev_month_revenue,
    ROUND(total_revenue - prev_month_revenue, 2) AS mom_revenue_change,
    ROUND(
        CASE 
            WHEN prev_month_revenue IS NULL THEN 0.0
            ELSE ((total_revenue - prev_month_revenue) * 100.0 / prev_month_revenue)
        END, 
        2
    ) AS mom_growth_pct
FROM mom_growth_calc
ORDER BY year_month ASC;

-- 2. Quarterly Revenue Breakdown and Seasonal Share
WITH quarterly_summary AS (
    SELECT 
        d.year,
        d.quarter,
        COUNT(DISTINCT f.order_id) AS orders,
        ROUND(SUM(f.revenue), 2) AS quarter_revenue,
        ROUND(AVG(f.revenue), 2) AS avg_item_revenue
    FROM fact_sales f
    JOIN dim_dates d ON f.order_date = d.date_key
    GROUP BY d.year, d.quarter
)
SELECT 
    year,
    quarter,
    orders,
    quarter_revenue,
    avg_item_revenue,
    -- Window function to compute percentage of yearly revenue
    ROUND(quarter_revenue * 100.0 / SUM(quarter_revenue) OVER (PARTITION BY year), 2) AS pct_of_annual_revenue
FROM quarterly_summary
ORDER BY year ASC, quarter ASC;

-- 3. Day of Week Sales Patterns (Weekend vs Weekday Performance)
SELECT 
    d.day_of_week,
    d.is_weekend,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    ROUND(SUM(f.revenue) * 1.0 / COUNT(DISTINCT f.order_id), 2) AS aov
FROM fact_sales f
JOIN dim_dates d ON f.order_date = d.date_key
GROUP BY d.day_of_week, d.is_weekend
ORDER BY total_revenue DESC;
