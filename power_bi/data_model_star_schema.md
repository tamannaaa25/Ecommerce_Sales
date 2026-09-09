# Power BI Dimensional Data Model (Star Schema)

This document specifies the Star Schema data architecture implemented for the E-Commerce Sales & Customer Analytics solution in Microsoft Power BI.

---

## 1. Architectural Overview & Star Schema Diagram

The semantic model is optimized for high-performance in-memory VertiPaq tabular querying. The architecture consists of a single central transactional **Fact Table** surrounded by four dedicated **Dimension Tables**, enforcing a strict **1-to-Many (1:*)** unidirectional filtering relationship.

```mermaid
erDiagram
    DIM_CUSTOMERS ||--o{ FACT_SALES : "1 to Many (customer_id)"
    DIM_PRODUCTS ||--o{ FACT_SALES : "1 to Many (product)"
    DIM_REGIONS ||--o{ FACT_SALES : "1 to Many (region)"
    DIM_DATES ||--o{ FACT_SALES : "1 to Many (order_date)"

    DIM_CUSTOMERS {
        string customer_id PK
        date first_order_date
        date last_order_date
        int total_orders
        int total_quantity
        decimal total_spend
        string primary_region
        decimal aov
        string customer_type
    }

    DIM_PRODUCTS {
        string product_name PK
        string category
        decimal standard_price
        int total_units_sold
        decimal total_revenue_generated
    }

    DIM_REGIONS {
        string region PK
        string regional_manager
        string market_tier
        string target_growth_rate
    }

    DIM_DATES {
        date date_key PK
        int year
        string quarter
        int month
        string month_name
        int day
        string day_of_week
        int is_weekend
    }

    FACT_SALES {
        string order_id
        string customer_id FK
        date order_date FK
        string product FK
        string category
        string region FK
        int quantity
        decimal unit_price
        decimal discount
        decimal revenue
    }
```

---

## 2. Table Relationships & Cardinality

| From Table (Primary Key) | To Table (Foreign Key) | Cardinality | Cross Filter Direction | Security Filtering |
| :--- | :--- | :--- | :--- | :--- |
| `dim_dates[date_key]` | `fact_sales[order_date]` | 1 to Many (1:*) | Single (Date filters Sales) | No |
| `dim_customers[customer_id]` | `fact_sales[customer_id]` | 1 to Many (1:*) | Single (Customer filters Sales) | No |
| `dim_products[product_name]` | `fact_sales[product]` | 1 to Many (1:*) | Single (Product filters Sales) | No |
| `dim_regions[region]` | `fact_sales[region]` | 1 to Many (1:*) | Single (Region filters Sales) | No |

---

## 3. Best Practices & Performance Optimization

1. **Unidirectional Filtering Only**:
   - Bi-directional cross-filtering is avoided to prevent ambiguous filter paths, performance degradation, and cartesian product inflation.
2. **Dedicated Date Table**:
   - `dim_dates` is flagged as an official Date Table in Power BI (`Mark as Date Table`), enabling native time-intelligence functions (`SAMEPERIODLASTYEAR`, `DATESYTD`, `DATEADD`).
3. **Surrogate Keys vs Natural Keys**:
   - Data types for foreign and primary keys are optimized as integer / clean strings with zero trailing whitespace.
4. **Calculated Columns vs DAX Measures**:
   - Business calculations are implemented strictly as dynamic **DAX Measures** rather than calculated columns in the fact table to minimize memory footprint and file size.
