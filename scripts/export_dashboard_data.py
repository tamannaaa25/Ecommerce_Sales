"""
Export Rich Analytics Data to Javascript File for Interactive Web Dashboard
Enables seamless client-side filtering without CORS restrictions.
"""

import json
import sqlite3
import pandas as pd

conn = sqlite3.connect("customer_analytics.db")

# 1. Granular monthly aggregates for interactive filtering
df_granular = pd.read_sql_query("""
    SELECT 
        d.year,
        d.month,
        d.year || '-' || printf('%02d', d.month) AS year_month,
        f.region,
        f.category,
        COUNT(DISTINCT f.order_id) AS orders,
        SUM(f.quantity) AS units_sold,
        ROUND(SUM(f.revenue), 2) AS revenue
    FROM fact_sales f
    JOIN dim_dates d ON f.order_date = d.date_key
    GROUP BY d.year, d.month, year_month, f.region, f.category
    ORDER BY year_month;
""", conn)

# 2. Product performance
df_products = pd.read_sql_query("""
    SELECT 
        product,
        category,
        COUNT(DISTINCT order_id) AS orders,
        SUM(quantity) AS units_sold,
        ROUND(AVG(unit_price), 2) AS avg_price,
        ROUND(AVG(discount) * 100, 1) AS avg_discount,
        ROUND(SUM(revenue), 2) AS revenue
    FROM fact_sales
    GROUP BY product, category
    ORDER BY revenue DESC;
""", conn)

# 3. Regional breakdown
df_regions = pd.read_sql_query("""
    SELECT 
        f.region,
        r.regional_manager,
        r.market_tier,
        r.target_growth_rate,
        COUNT(DISTINCT f.order_id) AS orders,
        SUM(f.quantity) AS units_sold,
        ROUND(SUM(f.revenue), 2) AS revenue,
        ROUND(SUM(f.revenue) * 1.0 / COUNT(DISTINCT f.order_id), 2) AS aov
    FROM fact_sales f
    JOIN dim_regions r ON f.region = r.region
    GROUP BY f.region, r.regional_manager, r.market_tier, r.target_growth_rate
    ORDER BY revenue DESC;
""", conn)

# 4. RFM Segmentation
df_rfm = pd.read_sql_query("""
    WITH customer_rfm_raw AS (
        SELECT 
            customer_id,
            primary_region,
            CAST((JULIANDAY('2026-01-01') - JULIANDAY(last_order_date)) AS INTEGER) AS recency_days,
            total_orders AS frequency,
            total_spend AS monetary
        FROM dim_customers
    ),
    rfm_scores AS (
        SELECT 
            customer_id,
            recency_days,
            frequency,
            monetary,
            NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
            NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
            NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
        FROM customer_rfm_raw
    ),
    rfm_segmented AS (
        SELECT 
            customer_id,
            recency_days,
            frequency,
            monetary,
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
        ROUND(AVG(recency_days), 1) AS avg_recency,
        ROUND(AVG(frequency), 1) AS avg_orders,
        ROUND(SUM(monetary), 2) AS total_revenue
    FROM rfm_segmented
    GROUP BY customer_segment
    ORDER BY total_revenue DESC;
""", conn)

# 5. Top 15 VIP Customers
df_top_customers = pd.read_sql_query("""
    SELECT 
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
""", conn)

# Assemble JSON
bundle = {
    "granular_sales": df_granular.to_dict(orient="records"),
    "products": df_products.to_dict(orient="records"),
    "regions": df_regions.to_dict(orient="records"),
    "rfm_segments": df_rfm.to_dict(orient="records"),
    "top_customers": df_top_customers.to_dict(orient="records")
}

js_content = f"window.ANALYTICS_DATA = {json.dumps(bundle, indent=2)};"
with open("web_dashboard/data.js", "w") as f:
    f.write(js_content)

print(f"Generated web_dashboard/data.js ({len(js_content):,} bytes).")
conn.close()
