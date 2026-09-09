# Power BI Interactive Dashboard Specification & Layout Blueprint

This document details the visual hierarchy, grid layout, slicers, and interactive configurations for the Power BI report suite.

---

## Canvas Settings & Global Design System
- **Page Dimensions**: 16:9 widescreen (1920 x 1080 px or 1280 x 720 px)
- **Design Theme**: Executive Dark Slate & Navy
  - **Background**: `#0F172A` (Slate 900)
  - **Card Containers**: `#1E293B` (Slate 800) with 1px border `#334155`
  - **Primary Accent**: `#38BDF8` (Sky Blue)
  - **Secondary Accent**: `#818CF8` (Indigo)
  - **Success / Positive Growth**: `#34D399` (Emerald Green)
  - **Warning / Negative Growth**: `#F87171` (Coral Red)
  - **Typography**: Segoe UI / Inter (Clean, modern sans-serif)

---

## Page 1: Executive Sales & Revenue Overview

```
+--------------------------------------------------------------------------------------------------+
|  [Logo] E-Commerce Executive Sales Performance Dashboard               Filters: [Year] [Region]  |
+--------------------------------------------------------------------------------------------------+
|  +----------------+  +----------------+  +----------------+  +----------------+  +-------------+ |
|  | TOTAL REVENUE  |  |  TOTAL ORDERS  |  |      AOV       |  |   UNITS SOLD   |  | REPEAT RATE | |
|  |   $1,919,531   |  |     10,441     |  |    $183.85     |  |     19,060     |  |    97.2%    | |
|  |  ▲ +14.2% YoY  |  |   ▲ +8.9% YoY  |  |   ▲ +4.8% YoY  |  |   ▲ +11.2% YoY |  |  High LTV   | |
|  +----------------+  +----------------+  +----------------+  +----------------+  +-------------+ |
+--------------------------------------------------------------------------------------------------+
|  +-------------------------------------------------------+  +----------------------------------+ |
|  | Monthly Revenue Trend & MoM Growth % (Combo Chart)    |  | Category Performance Breakdown   | |
|  | Bars: Net Revenue ($) | Line: MoM Growth (%)           |  | Horizontal Bar / Donut Chart     | |
|  | Highlights: Q4 Spikes (Nov-Dec Holiday Surge)          |  | Electronics (39.4%) Home (28.0%) | |
|  +-------------------------------------------------------+  +----------------------------------+ |
+--------------------------------------------------------------------------------------------------+
|  +-----------------------------------+  +------------------------------------------------------+ |
|  | Regional Sales & AOV Distribution |  | Top 5 Revenue Contributing Products                  | |
|  | Clustered Bar: Revenue by Region  |  | 1. Adjustable Standing Desk ($291.7K)                | |
|  | East ($401.9K) | West ($398.1K)   |  | 2. 4K Ultra HD Monitor ($254.7K)                     | |
|  | Central ($381.2K)| North ($372.5K)|  | 3. Ergonomic Office Chair ($182.2K)                  | |
|  +-----------------------------------+  +------------------------------------------------------+ |
+--------------------------------------------------------------------------------------------------+
```

### Visual Configurations (Page 1)
1. **Global Slicer Bar (Top)**:
   - Slicer 1: `dim_dates[Year]` (Tile / Button selection: 2024 | 2025 | All)
   - Slicer 2: `dim_regions[region]` (Dropdown menu)
   - Slicer 3: `dim_products[category]` (Horizontal pill buttons)
2. **KPI Scorecards (5 Cards across top)**:
   - Card 1: `[Total Revenue]` with conditional callout indicator based on `[MoM Revenue Growth %]`.
   - Card 2: `[Total Orders]`.
   - Card 3: `[Average Order Value]`.
   - Card 4: `[Total Units Sold]`.
   - Card 5: `[Repeat Customer Rate %]`.
3. **Monthly Trend Line & Stacked Column Combo Chart**:
   - X-Axis: `dim_dates[Year-Month]`
   - Column Values: `[Total Revenue]`
   - Line Values: `[MoM Revenue Growth %]`
   - Tooltips: Prior Month Revenue, Total Orders, AOV.
4. **Category Breakdown Donut / Tree Map**:
   - Category: `dim_products[category]`
   - Values: `[Total Revenue]`
   - Data Labels: Value & Percentage of Total.

---

## Page 2: Customer Analytics & Retention Deep-Dive

### Key Questions Answered:
- Who are our most valuable customers?
- How much revenue is driven by repeat buyers vs one-time purchasers?
- What are the customer behavioral clusters across Recency, Frequency, and Monetary dimensions?

### Layout Blueprint:
1. **Customer KPI Row**:
   - Total Customers (`DISTINCTCOUNT(dim_customers[customer_id])`)
   - Repeat Customers (`955 / 983 = 97.2%`)
   - Average Customer Lifetime Value (`$1,952.73`)
   - Average Purchase Frequency (`10.6 orders/customer`)
2. **RFM Segment Matrix / Treemap**:
   - Hierarchy: *Champions* -> *Loyal Customers* -> *Potential Loyalists* -> *At Risk* -> *Lost*.
   - Color scale mapped to monetary contribution.
3. **Customer Cohort / Repeat vs One-Time Donut**:
   - Demonstrating that repeat buyers contribute over 98% of total e-commerce revenue.
4. **Top Customers Leaderboard Table**:
   - Columns: `Customer ID`, `Primary Region`, `Total Orders`, `Total Units`, `Total Spend ($)`, `AOV ($)`, `Customer Segment`.
   - Interactive Sort by `Total Spend` descending with data bars.

---

## Page 3: Product Performance & Pareto (80/20) Analytics

### Key Questions Answered:
- Which products generate 80% of our enterprise revenue?
- Are deep promotional discounts driving proportional volume gains?
- What are the highest-margin categories?

### Layout Blueprint:
1. **Pareto Dual-Axis Analysis**:
   - X-Axis: `dim_products[product_name]` ordered by Revenue descending.
   - Left Y-Axis (Columns): `[Total Revenue]` per product.
   - Right Y-Axis (Line): `[Pareto Cumulative Revenue %]` with a dashed reference line at 80%.
   - Finding: Top 10 products out of 22 account for ~79.2% of total turnover.
2. **Discount Sensitivity Scatter Plot**:
   - X-Axis: `Average Discount %`
   - Y-Axis: `Total Units Sold`
   - Bubble Size: `[Total Revenue]`
   - Color: `Category`
3. **Product Ranking Matrix (with Drill-Through)**:
   - Category expandable to individual SKU, showing standard price, units sold, discount given, net revenue, and margin.
