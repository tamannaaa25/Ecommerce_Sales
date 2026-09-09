# Interview Talking Points (Based on Your Exact E-Commerce Dataset)

Use this guide for interview preparation. It matches your exact 50-order dataset with **Aarav, Diya, Rohan, Meera, Kabir, Isha, Arjun, and Sanya**. Everything is in simple Indian Rupees (₹) and plain, natural English.

---

## 1. The Simple 30-Second Project Intro

When an interviewer asks: **"Tell me about a project you've worked on recently."**

> "I worked on an e-commerce sales project analyzing transactional order data across 8 active repeat customers and 4 regions, totaling about **₹14.4 Lakhs in sales** across 48 validated orders.
> 
> The raw data had typical real-world quality issues—a negative quantity on an order, a blank quantity field, and inconsistent text casing like lowercase `'north'` and `'paid'`. I started in **Excel** to clean it up, handle the missing and invalid values, and run some quick Pivot Tables. Once clean, I loaded it into a **SQL** database where I wrote queries using JOINs, CTEs, and window functions like `LAG` and `DENSE_RANK` to analyze monthly trends, repeat customer spend, and product rankings. 
> 
> Finally, I built an interactive **Tableau** dashboard with custom calculated fields and Level of Detail (LOD) expressions to track KPIs like revenue, orders, and average order value. The key takeaway was finding that Electronics accounted for over 80% of our business, driven heavily by high-ticket items like Laptops and Phones, with our top customer Aarav generating over ₹5.3 Lakhs alone."

---

## 2. Step 1: Excel (Data Cleaning & Exploration)

### Interviewer: "How did you clean this dataset in Excel?"

> "The raw dataset had 50 orders with four specific data quality issues:
> 
> 1. **Negative Quantity (ORD2041)**: Order ORD2041 had a quantity of `-1` for a Laptop. Negative quantities are invalid for completed sales, so I filtered it out using the rule `Quantity > 0`.
> 2. **Missing Quantity (ORD2044)**: Order ORD2044 for Headphones had a blank quantity. I used `F5 > Special > Blanks` to isolate empty cells and removed incomplete records.
> 3. **Text Casing Inconsistencies**: 
>    - In row ORD2049, Region was entered as lowercase `'north'`.
>    - In row ORD2050, Payment_Status was entered as lowercase `'paid'`.
>    - I standardized both using `=PROPER(TRIM(cell))` to make them uniform Title Case (`'North'` and `'Paid'`).
> 4. **Discount Normalization**: Discounts were entered as text strings (`'10%'`, `'5%'`, `'0%'`). I converted them into decimal numbers (`0.10`, `0.05`) so formulas could calculate net revenue.
> 5. **Calculated Column**: I calculated Net Revenue using:  
>    `=ROUND(Quantity * Unit_Price * (1 - Discount), 0)`
> 6. **Data Validation**: I set up dropdown lists for Region (`North, South, East, West`) and Category (`Electronics, Furniture, Clothing`) to prevent future typos.
> 7. **Pivot Tables**: I built quick Pivot Tables by Category and Region. This showed that Electronics was by far our biggest revenue driver (₹11.6 Lakhs out of ₹14.4 Lakhs total)."

---

## 3. Step 2: SQL (Deeper Analysis)

### Interviewer: "What SQL queries did you write for this project?"

> "I wrote queries covering all key analytical SQL concepts:
> 
> - **JOIN & GROUP BY**: Joined the sales table with regional dimension tables to calculate total revenue, order count, and average order value by region and category.
> - **HAVING**: Filtered customer aggregates to find our high-value accounts who spent over ₹1,00,000 (Aarav at ₹5.39L, Isha at ₹3.33L, Sanya at ₹2.50L).
> - **CASE WHEN**: Categorized orders into price buckets—orders of ₹40,000+ as High-Ticket (Laptops and Phones), ₹15,000 to ₹40,000 as Mid-Tier (Tablets), and under ₹15,000 as Standard. I also used CASE WHEN to flag payment statuses needing follow-up (like Pending and Failed).
> - **Subqueries**: Wrote a subquery to compare each product's total revenue against the average product revenue benchmark (₹1.8 Lakhs), showing that Laptops, Phones, and Tablets were our top 3 revenue pillars.
> - **CTEs & Window Functions**:
>   - I used a CTE with `LAG()` to analyze Month-over-Month growth from Jan 2026 (₹9.37 Lakhs) to Feb 2026 (₹5.01 Lakhs).
>   - I used `SUM(revenue) OVER (ORDER BY date)` to track cumulative revenue towards our ₹14.4 Lakh total.
>   - I used `DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue DESC)` to rank products within each category (e.g. Laptop #1 in Electronics, Table #1 in Furniture, Jacket #1 in Clothing).
> - **Repeat Customer Analysis**: Grouped by customer to check repeat purchase frequency. All 8 customers placed repeat orders (5 to 7 orders each), demonstrating a 100% repeat buyer rate."

---

## 4. Step 3: Tableau (Dashboard & Calculated Fields)

### Interviewer: "How did you set up the Tableau dashboard?"

> "I organized the data and dashboard using modern Tableau best practices:
> 
> - **Data Modeling**: Connected `fact_sales` to dimension tables (Customers, Products, Regions, Dates) using Tableau's logical layer relationships ('noodles') on key fields, preventing row duplication while preserving native granularity.
> - **Calculated Fields**:
>   - `Total Revenue`: `SUM([Revenue])` (₹14,38,655)
>   - `Total Orders`: `COUNTD([Order ID])` (48 orders)
>   - `Average Order Value (AOV)`: `[Total Revenue] / [Total Orders]` (₹29,972)
> - **Level of Detail (LOD) Expressions**:
>   - Used `{ FIXED [Customer] : SUM([Revenue]) }` to calculate lifetime spend per customer, allowing me to group them into Platinum VIP (₹3L+) and Gold tiers independent of any month/category filter selections.
> - **Table Calculations**:
>   - Computed Month-over-Month growth % using `(ZN(SUM([Revenue])) - LOOKUP(ZN(SUM([Revenue])), -1)) / ABS(LOOKUP(ZN(SUM([Revenue])), -1))`.
> - **Dashboard Visuals & Interactivity**: Built top BAN KPI cards, a dual-axis monthly sales & order volume chart, category share breakdown, and an interactive customer matrix. Added filter actions so clicking any region or category dynamically cross-filters the entire dashboard."

---

## 5. Step 4: Business Insights (The Story Behind the Numbers)

### Interviewer: "What business takeaways did you discover from this dataset?"

### Insight 1: Extreme Category Concentration in Electronics
- **Say this**:
  > *"Electronics generated **₹11.6 Lakhs (80.6% of total company revenue)** across just 4 products: Laptop (₹55,000), Phone (₹28,000), Tablet (₹22,000), and Headphones (₹2,500). By comparison, Furniture made up 10.7% (₹1.54L) and Clothing made up 8.7% (₹1.26L). The business is heavily dependent on high-ticket tech gadgets."*

### Insight 2: Customer Spend Disparity (Aarav vs Others)
- **Say this**:
  > *"When looking at our 8 customers, Aarav alone generated **₹5,39,000 (37.5% of total sales)** by ordering 6 Laptops across North. Isha was second with ₹3.33 Lakhs buying Phones in South, and Sanya was third with ₹2.50 Lakhs buying Tablets in East. These top 3 customers alone drove **78% of our entire revenue**, making customer relationship management and VIP retention critical."*

### Insight 3: Regional Leadership
- **Say this**:
  > *"The **North** region led all markets with ₹6.23 Lakhs (43.3% share), followed by the **South** at ₹4.01 Lakhs (27.8%), **East** at ₹2.87 Lakhs (19.9%), and **West** at ₹1.28 Lakhs (8.9%). The North and South lead primarily because their customers purchase higher-ticket tech items (Laptops and Phones), whereas the West bought lower-priced items like Chairs and Shoes."*

### Insight 4: Payment Failure and Pending Revenue
- **Say this**:
  > *"Analyzing Payment_Status showed 45 Paid orders, 2 Pending orders (ORD2004 Headphones for ₹8,500, ORD2022 Phone for ₹26,600), and 1 Failed payment (ORD2010 Jacket for ₹15,120). Setting up automated retry alerts for failed and pending payments would help immediately recover over ₹50,000 in uncollected revenue."*

---

## 6. Quick Number Cheat Sheet (Easy to Memorize)

- **Total Revenue**: ₹14,38,655 (~₹14.4 Lakhs)
- **Total Validated Orders**: 48 orders (from 50 raw rows)
- **Average Order Value (AOV)**: ₹29,972 (~₹30,000)
- **Top Customer**: Aarav (₹5,39,000 across 6 orders)
- **Top Product**: Laptop (₹5,39,000 | 11 units sold at ₹55,000 unit price)
- **Top Category**: Electronics (₹11,59,150 | 80.6% share)
- **Top Region**: North (₹6,22,725 | 43.3% share)
- **Repeat Customers**: 8 out of 8 (100% repeat rate)
