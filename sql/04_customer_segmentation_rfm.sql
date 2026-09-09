-- ==============================================================================
-- 04_customer_segmentation_rfm.sql
-- Top Customers, Repeat Customers Analysis, and RFM Segmentation via Window Functions
-- ==============================================================================

-- 1. Top 15 Customers by Total Spend (with DENSE_RANK & ROW_NUMBER)
SELECT 
    ROW_NUMBER() OVER (ORDER BY total_spend DESC) AS row_num,
    DENSE_RANK() OVER (ORDER BY total_spend DESC) AS spend_rank,
    customer_id,
    primary_region,
    total_orders,
    total_quantity,
    total_spend,
    aov,
    customer_type
FROM dim_customers
ORDER BY total_spend DESC
LIMIT 15;

-- 2. Repeat vs One-Time Customer Performance Comparison
SELECT 
    customer_type,
    COUNT(*) AS total_customers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dim_customers), 2) AS customer_share_pct,
    SUM(total_orders) AS total_orders_placed,
    ROUND(SUM(total_spend), 2) AS total_revenue_generated,
    ROUND(SUM(total_spend) * 100.0 / (SELECT SUM(total_spend) FROM dim_customers), 2) AS revenue_share_pct,
    ROUND(AVG(aov), 2) AS avg_aov_per_customer
FROM dim_customers
GROUP BY customer_type;

-- 3. Advanced RFM (Recency, Frequency, Monetary) Segmentation
-- Baseline date for recency calculation: 2026-01-01 (post-dataset completion)
WITH customer_rfm_raw AS (
    SELECT 
        customer_id,
        primary_region,
        -- Recency: Days since last order
        CAST((JULIANDAY('2026-01-01') - JULIANDAY(last_order_date)) AS INTEGER) AS recency_days,
        -- Frequency: Count of distinct orders
        total_orders AS frequency,
        -- Monetary: Total revenue
        total_spend AS monetary
    FROM dim_customers
),
rfm_scores AS (
    SELECT 
        customer_id,
        primary_region,
        recency_days,
        frequency,
        monetary,
        -- Window function: NTILE(5) for scoring 1 (lowest) to 5 (highest)
        -- For Recency: lower days is better, so reverse ordering
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM customer_rfm_raw
),
rfm_segmented AS (
    SELECT 
        customer_id,
        primary_region,
        recency_days,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        (r_score + f_score + m_score) AS total_rfm_score,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score < 3 THEN 'Potential Loyalists'
            WHEN r_score >= 3 AND f_score <= 2 THEN 'Promising New'
            WHEN r_score <= 2 AND f_score >= 3 AND m_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'Cant Lose Them'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Hibernating / Lost'
            ELSE 'Needs Attention'
        END AS customer_segment
    FROM rfm_scores
)
SELECT 
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dim_customers), 2) AS segment_percentage,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(frequency), 1) AS avg_orders,
    ROUND(SUM(monetary), 2) AS total_segment_revenue,
    ROUND(AVG(monetary), 2) AS avg_customer_spend
FROM rfm_segmented
GROUP BY customer_segment
ORDER BY total_segment_revenue DESC;
