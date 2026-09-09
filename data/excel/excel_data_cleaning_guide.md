# Step-by-Step Excel Data Cleaning & Exploration Guide (Your 50-Order Dataset)

This guide walks through the exact cleaning steps performed on your 50-row e-commerce sales dataset in **Microsoft Excel**. You can walk any interviewer through these exact menu clicks and formulas.

---

## The Raw Dataset & Anomalies

The raw file contained 50 orders with the following schema:
`Order_ID`, `Order_Date`, `Customer`, `Region`, `Category`, `Product`, `Quantity`, `Unit_Price`, `Discount`, `Payment_Status`

### The 4 Real-World Anomalies Present in the Data:
1. **Row 41 (`ORD2041`)**: Quantity entered as `-1` (Negative quantity anomaly).
2. **Row 44 (`ORD2044`)**: Quantity field is completely blank (Missing value).
3. **Row 49 (`ORD2049`)**: Region entered as lowercase `'north'` instead of `'North'`.
4. **Row 50 (`ORD2050`)**: Payment_Status entered as lowercase `'paid'` instead of `'Paid'`.

---

## Step 1: Text Casing & Trimming (TRIM & PROPER)

1. **Fixing Inconsistent Region Casing**:
   - In a helper column, apply:
     ```excel
     =PROPER(TRIM(D2))
     ```
   - Converts `'north'` in row 49 to `'North'`.
2. **Fixing Inconsistent Payment Status Casing**:
   - In a helper column, apply:
     ```excel
     =PROPER(TRIM(J2))
     ```
   - Converts `'paid'` in row 50 to `'Paid'`.
3. **Save as Values**:
   - Copy the cleaned columns and use **Paste Special > Values** (`Ctrl + Alt + V > V`) to overwrite the messy raw text.

---

## Step 2: Identifying & Handling Outliers & Blanks

1. **Spotting Blank Cells (ORD2044)**:
   - Select column `G` (`Quantity`).
   - Press `F5` (or `Ctrl + G`), click **Special...**, choose **Blanks**, and click **OK**.
   - Excel highlights row 44 (`ORD2044`). Since the order has no quantity, it is incomplete. Right-click > **Delete > Entire Sheet Row**.
2. **Filtering Negative Quantities (ORD2041)**:
   - Apply an AutoFilter (`Ctrl + Shift + L`).
   - Click the dropdown on the `Quantity` column.
   - Filter for values `<= 0`. Row 41 (`ORD2041` with `-1` Laptop) is isolated and removed.
   - Result: Exactly 48 pristine, validated orders remain.

---

## Step 3: Date & Discount Normalization

1. **Standardizing Order Dates**:
   - The dates are in `DD-Mon-YY` format (e.g. `02-Jan-26`, `12-Feb-26`).
   - Ensure the column is formatted as **Short Date** (`YYYY-MM-DD`).
2. **Standardizing Discounts**:
   - The discounts are formatted as percentages (`10%`, `5%`, `0%`).
   - In numeric calculations, Excel treats `10%` natively as `0.10`.

---

## Step 4: Net Revenue Calculation

- Add Column `K` (`Revenue`) using the formula:
  ```excel
  =ROUND(G2 * H2 * (1 - I2), 0)
  ```
  *(Quantity × Unit Price × (1 - Discount))*
- Example for row 2 (`ORD2001`): `2 * 55,000 * (1 - 0.10) = ₹99,000`.
- Format column `K` as **Currency (₹)** without decimals (`"₹"#,##0`).

---

## Step 5: Data Validation Rules

1. **Region Dropdown**:
   - Select the `Region` column > **Data > Data Validation > List**.
   - Source: `North, South, East, West`.
2. **Category Dropdown**:
   - Select the `Category` column > **Data > Data Validation > List**.
   - Source: `Electronics, Furniture, Clothing`.
3. **Quantity Constraint**:
   - Select `Quantity` > Data Validation > **Allow: Whole Number**, **Greater than 0**.

---

## Step 6: Pivot Table Exploration (Initial Trends)

### Pivot Table 1: Revenue by Category
- **Rows**: `Category`
- **Values**: `Sum of Revenue`, `Count of Order_ID`, `Average of Revenue`
- **Finding**:
  - **Electronics**: ₹11,59,150 (80.6% of sales, AOV ₹40,000+)
  - **Furniture**: ₹1,53,645 (10.7% of sales, AOV ₹12,800)
  - **Clothing**: ₹1,25,860 (8.7% of sales, AOV ₹9,680)

### Pivot Table 2: Sales by Customer
- **Rows**: `Customer`
- **Values**: `Sum of Revenue`, `Count of Order_ID`
- **Finding**:
  - **Aarav**: ₹5,39,000 (6 orders, all Laptops in North)
  - **Isha**: ₹3,33,200 (6 orders, all Phones in South)
  - **Sanya**: ₹2,49,700 (6 orders, all Tablets in East)
  - The top 3 customers drive **78%** of total revenue.
