# Tableau Interactive Dashboard Layout Specification

This document details the visual hierarchy, grid layout, worksheets, and interactive actions designed for the **E-Commerce Executive Sales & Customer Analytics** Tableau dashboard.

---

## 1. Canvas & Design System

- **Dashboard Size**: Fixed `1366 x 768 px` (standard 16:9 laptop display) or `Automatic`.
- **Layout Approach**: Tiled layout containers (Horizontal and Vertical) with 8px inner padding for clean card separation.
- **Color Palette**:
  - **Background**: `#F8FAFC` (Clean, modern light canvas)
  - **Card Containers**: `#FFFFFF` (Crisp white cards) with subtle 1px border `#E2E8F0`
  - **Primary Blue (Revenue)**: `#2563EB`
  - **Category Accents**:
    - Electronics: `#2563EB` (Royal Blue)
    - Furniture: `#D97706` (Warm Amber)
    - Clothing: `#059669` (Emerald Green)
  - **Typography**: Tableau Book / Arial / Inter (14pt Bold headers, 24pt Bold KPI numbers, 11pt regular labels).

---

## 2. Dashboard Wireframe Layout

```
+--------------------------------------------------------------------------------------------------+
|  📊 E-Commerce Sales & Customer Dashboard        Filters: [Month: All ▼] [Region: All ▼] [Reset] |
+--------------------------------------------------------------------------------------------------+
|  +----------------+  +----------------+  +----------------+  +----------------+  +-------------+ |
|  |  TOTAL SALES   |  |     ORDERS     |  |   AVG ORDER    |  |   UNITS SOLD   |  |  CUSTOMERS  | |
|  |   ₹14,38,655   |  |       48       |  |    ₹29,972     |  |      123       |  |      8      | |
|  |  48 orders net |  | Jan:30 |Feb:18 |  | Rev / order    |  | Items bought   |  | 100% Repeat | |
|  +----------------+  +----------------+  +----------------+  +----------------+  +-------------+ |
+--------------------------------------------------------------------------------------------------+
|  +-------------------------------------------------------+  +----------------------------------+ |
|  | Worksheet: Monthly Sales & Orders (Dual Axis)         |  | Worksheet: Sales by Category     | |
|  | Left Axis: Bar Chart (Net Revenue ₹)                  |  | Donut or Horizontal Bars         | |
|  | Right Axis: Line Chart (Order Count)                  |  | Electronics: ₹11,59,150 (80.6%)  | |
|  | Jan 2026: ₹9.37L (30 orders)                          |  | Furniture:   ₹1,54,345 (10.7%)  | |
|  | Feb 2026: ₹5.01L (18 orders)                          |  | Clothing:    ₹1,25,160 (8.7%)   | |
|  +-------------------------------------------------------+  +----------------------------------+ |
+--------------------------------------------------------------------------------------------------+
|  +------------------------------------+  +-----------------------------------------------------+ |
|  | Worksheet: Regional Sales Share    |  | Worksheet: Top 8 Products Ranked by Sales           | |
|  | Horizontal Bars:                   |  | 1. Laptop (Electronics)   - ₹5,39,000 (37.5%)       | |
|  | • North: ₹6,22,725 (43.3%)         |  | 2. Phone (Electronics)    - ₹3,69,600 (25.7%)       | |
|  | • South: ₹4,00,610 (27.8%)         |  | 3. Tablet (Electronics)   - ₹2,50,550 (17.4%)       | |
|  | • East:  ₹2,86,950 (19.9%)         |  | 4. Table (Furniture)      - ₹84,425   (5.9%)        | |
|  | • West:  ₹1,28,370 (8.9%)          |  | 5. Chair (Furniture)      - ₹69,920   (4.9%)        | |
|  +------------------------------------+  +-----------------------------------------------------+ |
+--------------------------------------------------------------------------------------------------+
```

---

## 3. Individual Worksheets Specification

### Worksheet 1: `KPI_Scorecards` (BANs)
- **Rows**: Blank
- **Columns**: Measure Names (`[Total Revenue]`, `[Total Orders]`, `[Average Order Value]`, `[Total Units Sold]`, `[Repeat Customer Rate]`)
- **Marks**: Text / KPI card layout with colored bold metric text.

### Worksheet 2: `Monthly_Trend_Dual_Axis`
- **Columns**: `Order Date` (Date Trunc: Month / Continuous)
- **Rows**: 
  - Measure 1: `SUM([Revenue])` (Mark: Bar Chart, Color: `#2563EB`)
  - Measure 2: `COUNTD([Order ID])` (Mark: Line Chart with markers, Color: `#D97706`)
- **Dual Axis**: Synchronize axis = Off (Currency vs Count).

### Worksheet 3: `Category_Sales_Breakdown`
- **Columns**: `SUM([Revenue])`
- **Rows**: `Category`
- **Sort**: Descending by `SUM([Revenue])`
- **Label**: `SUM([Revenue])` and Table Calculation `% of Total`.
- **Color**: `Category`.

### Worksheet 4: `Product_Performance_Ranking`
- **Columns**: `SUM([Revenue])`
- **Rows**: `Product` (Sorted descending by revenue)
- **Color**: `Category` (allows quick visual grouping)
- **Tooltip**: Units Sold, Unit Price, Total Revenue, % of Category.

### Worksheet 5: `Regional_Sales_Summary`
- **Columns**: `SUM([Revenue])`
- **Rows**: `Region`
- **Marks**: Bar Chart with Reference Line indicating Average Regional Sales (₹3,59,664).

### Worksheet 6: `Customer_Lifetime_Matrix`
- **Columns**: `SUM([Revenue])` (or `[Customer Lifetime Spend]` LOD)
- **Rows**: `Customer`
- **Color**: `[Customer Tier]` (Platinum VIP: `#2563EB`, Gold: `#10B981`, Silver: `#94A3B8`)
- **Detail**: Total Orders (`COUNTD([Order ID])`), Region.

---

## 4. Interactive Dashboard Actions

### 1. Filter Action: `Filter_by_Region`
- **Source Sheet**: `Regional_Sales_Summary`
- **Target Sheets**: All worksheets
- **Run Action on**: Select (Click)
- **Clearing Selection**: Show all values.
- *User Experience: Clicking "North" immediately filters Monthly Trend, Products, and Customers to North data (Aarav, Kabir).*

### 2. Filter Action: `Filter_by_Category`
- **Source Sheet**: `Category_Sales_Breakdown`
- **Target Sheets**: All worksheets except Category itself
- **Run Action on**: Select (Click).

### 3. Viz in Tooltip: `Hover_Customer_Order_History`
- When hovering over any customer in `Customer_Lifetime_Matrix`, a mini tooltip chart opens displaying their individual order dates, products purchased, and payment status.
```tableau
<Sheet name="Customer_Order_Breakdown" maxwidth="320" maxheight="200" filter="<Customer>">
```

### 4. Dynamic Parameter: `Param_Select_Metric`
- Creates a single dashboard chart where end-users can toggle between:
  - **Revenue (₹)**
  - **Order Count**
  - **Units Sold**
  - **Average Order Value (AOV)**
