# Data Cleaning & Validation Quality Assurance Report

**Pipeline Execution**: Python Data Validation & Cleaning Script (`scripts/clean_and_validate.py`)  
**Database Relational Integrity**: SQLite Relational Star Schema (`customer_analytics.db`)  
**Visual Analytics Specification**: Tableau Desktop / Tableau Public (`tableau/`)  
**Data Validation Scope**: 50 Raw Transaction Records  

---

## 1. Data Hygiene Summary Table

The raw e-commerce sales dataset contained four real-world data quality issues that were audited and cleaned in Excel and Python:

| Order ID | Data Issue Detected | Severity | Remediation / Cleaning Action | Cleaned State |
| :--- | :--- | :--- | :--- | :--- |
| **ORD2041** | Negative quantity (`Quantity = -1` for Laptop) | Critical | Filtered out via data validation rule (`Quantity > 0`) | Removed from fact table |
| **ORD2044** | Blank/missing quantity for Headphones | Critical | Isolated via Excel `F5 > Special > Blanks` and filtered | Removed from fact table |
| **ORD2049** | Inconsistent lowercase text (`region = 'north'`) | Moderate | Standardized via `=PROPER(TRIM())` string normalization | Corrected to `'North'` |
| **ORD2050** | Inconsistent lowercase text (`payment_status = 'paid'`) | Moderate | Standardized via `=PROPER(TRIM())` string normalization | Corrected to `'Paid'` |
| **All Rows** | Text formatted discounts (`'10%'`, `'5%'`, `'0%'`) | Minor | Stripped `%` symbol and converted to floating decimal (`0.10`, `0.05`) | Numeric format for SQL & Tableau |

- **Total Ingested Rows**: 50  
- **Invalid Records Filtered**: 2 (`ORD2041`, `ORD2044`)  
- **Final Validated Records**: **48 Orders**  
- **Net Revenue**: **₹14,38,655**  

---

## 2. Processed Data Dictionary

### Central Fact Table: `fact_sales`
| Field Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `order_id` | `VARCHAR(20)` | `NOT NULL, PK` | Unique order identifier (ORD2001 - ORD2050) |
| `customer` | `VARCHAR(50)` | `NOT NULL, FK` | Customer name linked to `dim_customers` |
| `order_date` | `DATE` | `NOT NULL, FK` | Transaction date (`YYYY-MM-DD`) linked to `dim_dates` |
| `region` | `VARCHAR(20)` | `NOT NULL, FK` | Sales territory linked to `dim_regions` |
| `category` | `VARCHAR(50)` | `NOT NULL` | Category (Electronics, Furniture, Clothing) |
| `product` | `VARCHAR(100)` | `NOT NULL, FK` | Product name linked to `dim_products` |
| `quantity` | `INTEGER` | `CHECK(>0)` | Number of physical units purchased (1 to 5) |
| `unit_price` | `NUMERIC(10,2)`| `CHECK(>0)` | Price per unit in INR (₹2,500 to ₹55,000) |
| `discount` | `NUMERIC(5,2)` | `CHECK(0 to 1)`| Discount rate (0.00 to 0.20) |
| `revenue` | `NUMERIC(12,2)`| `CHECK(>=0)` | Realized revenue: `qty * unit_price * (1 - discount)` |
| `payment_status` | `VARCHAR(20)` | `NOT NULL` | Payment state (`Paid`, `Pending`, `Failed`) |

---

## 3. Dimensional Tables Summary

1. **`dim_customers`** (8 Unique Repeat Customers):
   - Primary Key: `customer`
   - Attributes: `region`, `total_orders`, `total_quantity`, `total_spend`, `aov`, `customer_tier`
2. **`dim_products`** (8 Unique Products):
   - Primary Key: `product_name`
   - Attributes: `category`, `unit_price`, `total_orders`, `total_units_sold`, `total_revenue`
3. **`dim_regions`** (4 Territories):
   - Primary Key: `region`
   - Attributes: `total_orders`, `total_revenue`, `primary_category`
4. **`dim_dates`** (51 Calendar Days, Jan 02 – Feb 21, 2026):
   - Primary Key: `date_key`
   - Attributes: `year`, `month_name`, `year_month`, `is_weekend`
