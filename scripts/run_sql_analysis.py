"""
SQL Analysis Runner on User's 50-Order Dataset
Initializes SQLite database 'customer_analytics.db', loads processed tables,
executes master queries, prints clean results, and exports JSON bundle for dashboard.
"""

import os
import sqlite3
import pandas as pd

DB_PATH = "customer_analytics.db"
PROCESSED_DIR = "data/processed"
SQL_DIR = "sql"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

print("Connecting to SQLite database:", DB_PATH)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Schema DDL
with open(os.path.join(SQL_DIR, "01_schema_setup.sql"), "r") as f:
    cursor.executescript(f.read())

# 2. Populate tables
# fact_sales
df_fact = pd.read_csv(os.path.join(PROCESSED_DIR, "fact_sales.csv"))
df_fact.drop(columns=["Quantity_Raw"], errors="ignore", inplace=True)
df_fact.rename(columns={
    "Order_ID": "order_id",
    "Order_Date": "order_date",
    "Customer": "customer",
    "Region": "region",
    "Category": "category",
    "Product": "product",
    "Quantity": "quantity",
    "Unit_Price": "unit_price",
    "Discount": "discount",
    "Payment_Status": "payment_status",
    "Revenue": "revenue"
}, inplace=True)
df_fact.to_sql("fact_sales", conn, if_exists="append", index=False)
print(f"Loaded {len(df_fact)} records into fact_sales.")

# dim_customers
df_cust = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_customers.csv"))
df_cust.rename(columns={
    "Customer": "customer",
    "Region": "region",
    "Total_Orders": "total_orders",
    "Total_Units": "total_units",
    "Total_Revenue": "total_revenue",
    "AOV": "aov",
    "Customer_Type": "customer_type"
}, inplace=True)
df_cust.to_sql("dim_customers", conn, if_exists="append", index=False)

# dim_products
df_prod = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_products.csv"))
df_prod.rename(columns={
    "Product": "product",
    "Category": "category",
    "Unit_Price": "unit_price",
    "Total_Units_Sold": "total_units_sold",
    "Total_Revenue": "total_revenue"
}, inplace=True)
df_prod.to_sql("dim_products", conn, if_exists="append", index=False)

# dim_regions
df_reg = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_regions.csv"))
df_reg.rename(columns={
    "Region": "region",
    "Regional_Lead": "regional_lead",
    "Target_Revenue": "target_revenue"
}, inplace=True)
df_reg.to_sql("dim_regions", conn, if_exists="append", index=False)

# dim_dates
df_dates = pd.read_csv(os.path.join(PROCESSED_DIR, "dim_dates.csv"))
df_dates.rename(columns={
    "Date": "date_key",
    "Year": "year",
    "Month": "month",
    "Month_Name": "month_name",
    "Day": "day",
    "Day_Of_Week": "day_of_week"
}, inplace=True)
df_dates.to_sql("dim_dates", conn, if_exists="append", index=False)

conn.commit()
print("All dimensional tables loaded successfully.")

# 3. Execute Master Queries
print("\n" + "=" * 80)
print("  EXECUTING MASTER SQL QUERIES (sql/00_master_interview_queries.sql)")
print("=" * 80)

with open(os.path.join(SQL_DIR, "00_master_interview_queries.sql"), "r") as f:
    sql_script = f.read()

statements = [s.strip() for s in sql_script.split(';') if s.strip()]
for idx, stmt in enumerate(statements, start=1):
    header = stmt.split('\n')[0]
    print(f"\n--- Query #{idx}: {header} ---")
    res = pd.read_sql_query(stmt, conn)
    print(res.to_string(index=False))

# 4. Generate JSON summary for dashboard
dashboard_data = {
    "summary_kpis": {
        "total_revenue": int(df_fact["revenue"].sum()),
        "total_orders": len(df_fact),
        "total_customers": int(df_fact["customer"].nunique()),
        "overall_aov": int(round(df_fact["revenue"].mean())),
        "total_units_sold": int(df_fact["quantity"].sum())
    }
}

# Monthly
df_monthly = pd.read_sql_query("""
    SELECT 
        STRFTIME('%Y-%m', order_date) AS year_month,
        COUNT(order_id) AS orders,
        SUM(quantity) AS units,
        SUM(revenue) AS revenue,
        ROUND(AVG(revenue)) AS aov
    FROM fact_sales
    GROUP BY year_month
    ORDER BY year_month;
""", conn)
dashboard_data["monthly_trends"] = df_monthly.to_dict(orient="records")

# Regional
df_regional = pd.read_sql_query("""
    SELECT 
        region,
        COUNT(order_id) AS orders,
        SUM(quantity) AS units_sold,
        SUM(revenue) AS revenue,
        ROUND(AVG(revenue)) AS aov
    FROM fact_sales
    GROUP BY region
    ORDER BY revenue DESC;
""", conn)
dashboard_data["regional_performance"] = df_regional.to_dict(orient="records")

# Category
df_category = pd.read_sql_query("""
    SELECT 
        category,
        COUNT(order_id) AS orders,
        SUM(quantity) AS units_sold,
        SUM(revenue) AS revenue,
        ROUND(AVG(discount) * 100, 1) AS avg_discount
    FROM fact_sales
    GROUP BY category
    ORDER BY revenue DESC;
""", conn)
dashboard_data["category_performance"] = df_category.to_dict(orient="records")

# Products
df_prods = pd.read_sql_query("""
    SELECT 
        product,
        category,
        unit_price,
        SUM(quantity) AS units_sold,
        SUM(revenue) AS revenue
    FROM fact_sales
    GROUP BY product, category, unit_price
    ORDER BY revenue DESC;
""", conn)
dashboard_data["top_products"] = df_prods.to_dict(orient="records")

# Customers
df_top_cust = pd.read_sql_query("""
    SELECT 
        customer,
        region,
        COUNT(order_id) AS total_orders,
        SUM(quantity) AS total_quantity,
        SUM(revenue) AS total_spend,
        ROUND(AVG(revenue)) AS aov
    FROM fact_sales
    GROUP BY customer, region
    ORDER BY total_spend DESC;
""", conn)
dashboard_data["top_customers"] = df_top_cust.to_dict(orient="records")

# Granular records for client-side filtering
df_granular = pd.read_sql_query("""
    SELECT 
        STRFTIME('%Y-%m', order_date) AS year_month,
        region,
        category,
        COUNT(order_id) AS orders,
        SUM(quantity) AS units_sold,
        SUM(revenue) AS revenue
    FROM fact_sales
    GROUP BY year_month, region, category
    ORDER BY year_month;
""", conn)
dashboard_data["granular_sales"] = df_granular.to_dict(orient="records")

import json
with open("web_dashboard/dashboard_data.json", "w") as f:
    json.dump(dashboard_data, f, indent=2)

js_bundle = f"window.ANALYTICS_DATA = {json.dumps(dashboard_data, indent=2)};"
with open("web_dashboard/data.js", "w") as f:
    f.write(js_bundle)

print("\nDashboard data bundle written to web_dashboard/data.js")
conn.close()
