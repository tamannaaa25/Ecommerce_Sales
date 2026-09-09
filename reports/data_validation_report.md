# Data Cleaning & Validation Quality Assurance Report

**Pipeline Execution**: Automated Python ETL Pipeline (`scripts/clean_and_validate.py`)  
**Database Relational Integrity**: SQLite Relational Star Schema (`customer_analytics.db`)  
**Data Validation Scope**: 10,650 Ingested Transaction Records  

---

## 1. Data Hygiene Summary Table

The raw e-commerce sales dataset contained common enterprise data anomalies, including duplicate transactions, missing demographic attributes, negative pricing/quantities, and non-standard date strings.

| Data Quality Checkpoint | Anomalies Detected | Remediation / Cleaning Action Applied | Status |
| :--- | :--- | :--- | :--- |
| **Initial Raw Ingestion** | 10,650 Records | Read raw transactional CSV dump | Complete |
| **Duplicate Records** | 139 Duplicates | Removed identical order-item rows using compound tuple deduplication | Resolved |
| **Missing Customer IDs** | 35 Null Records | Dropped unidentifiable customer transactions to maintain referential integrity | Resolved |
| **Missing Regional Tags** | 25 Null Records | Imputed with customer regional mode / Central baseline | Imputed |
| **Missing Promotional Discounts** | 45 Null Records | Imputed with standard 0.0% non-promotional rate | Imputed |
| **Non-Positive Quantities** | 20 Negative Rows | Filtered records with quantity <= 0 (test artifacts / invalid entries) | Filtered |
| **Non-Positive Unit Prices** | 15 Negative Rows | Filtered corrupted pricing records with unit price <= $0.00 | Filtered |
| **Inconsistent Date Formats** | 200 Mixed Formats | Standardized heterogeneous strings (`MM/DD/YYYY` & ISO) into standard `YYYY-MM-DD` | Normalized |
| **Casing & Whitespace Variances** | 430 Mixed Strings | Applied string trimming and Title Casing to `Region` and `Category` fields | Standardized |
| **Formula Calculation Integrity** | 10,441 Rows | Recalculated `Sales` = `Quantity * Unit Price * (1 - Discount)` with 2 decimal precision | Validated |
| **Final Pristine Dataset** | **10,441 Records** | Clean dataset populated into Star Schema tables | **100% Validated** |

---

## 2. Processed Data Dictionary

### Central Fact Table: `fact_sales`
| Field Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `order_id` | `VARCHAR(30)` | `NOT NULL` | Unique transactional purchase order identifier |
| `customer_id` | `VARCHAR(20)` | `NOT NULL, FK` | Unique customer key linked to `dim_customers` |
| `order_date` | `DATE` | `NOT NULL, FK` | Transaction date in `YYYY-MM-DD` linked to `dim_dates` |
| `product` | `VARCHAR(150)` | `NOT NULL, FK` | Item description linked to `dim_products` |
| `category` | `VARCHAR(50)` | `NOT NULL` | Business merchandise department |
| `region` | `VARCHAR(50)` | `NOT NULL, FK` | Sales territory linked to `dim_regions` |
| `quantity` | `INTEGER` | `CHECK(>0)` | Number of physical units purchased per line item |
| `unit_price` | `NUMERIC(10,2)`| `CHECK(>0)` | Pre-discount list price per unit in USD ($) |
| `discount` | `NUMERIC(5,2)` | `CHECK(0 to 1)`| Promotional discount percentage applied (0.0 to 1.0) |
| `revenue` | `NUMERIC(12,2)`| `CHECK(>=0)` | Final realized sales value: `qty * price * (1 - discount)` |

---

## 3. Dimensional Tables

1. **`dim_customers`** (983 Unique Records):
   - Primary Key: `customer_id`
   - Attributes: `first_order_date`, `last_order_date`, `total_orders`, `total_quantity`, `total_spend`, `primary_region`, `aov`, `customer_type`
2. **`dim_products`** (22 Unique SKUs):
   - Primary Key: `product_name`
   - Attributes: `category`, `standard_price`, `total_units_sold`, `total_revenue_generated`
3. **`dim_regions`** (5 Territories):
   - Primary Key: `region`
   - Attributes: `regional_manager`, `market_tier`, `target_growth_rate`
4. **`dim_dates`** (731 Days, 2024–2025):
   - Primary Key: `date_key`
   - Attributes: `year`, `quarter`, `month`, `month_name`, `day`, `day_of_week`, `is_weekend`

---

## 4. Referential Integrity & Verification Queries

As documented in `sql/02_data_cleaning_checks.sql`, automated integrity checks verify:
- **Zero Orphan Keys**: No transactions exist in `fact_sales` that do not map to valid records in `dim_customers`, `dim_products`, `dim_regions`, or `dim_dates`.
- **Zero Duplicate Line Items**: Unique order-customer-product constraint satisfied.
- **Zero Formula Discrepancies**: 100% of rows satisfy `ABS(revenue - (quantity * unit_price * (1 - discount))) <= 0.05`.
