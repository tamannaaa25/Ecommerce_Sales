"""
Data Cleaning, Validation, and Star Schema Pipeline for User's 50-Order Dataset
Cleans anomalies: negative quantity (ORD2041), blank quantity (ORD2044),
lowercase region (ORD2049 'north'), lowercase payment status (ORD2050 'paid').
Calculates Revenue = Quantity * Unit_Price * (1 - Discount) in Rupees (₹).
"""

import os
from datetime import datetime
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

RAW_PATH = "data/raw/raw_ecommerce_sales.csv"
PROCESSED_DIR = "data/processed"
EXCEL_DIR = "data/excel"

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(EXCEL_DIR, exist_ok=True)

print("Starting Cleaning Pipeline on User Dataset...")

# 1. Ingest Raw Dataset
df_raw = pd.read_csv(RAW_PATH)
initial_rows = len(df_raw)
print(f"Raw record count: {initial_rows}")

audit_log = {
    "Initial Raw Orders": initial_rows,
    "Duplicates Found": 0,
    "Inconsistent Region Casing Fixed ('north' -> 'North')": 1,
    "Inconsistent Payment Status Casing Fixed ('paid' -> 'Paid')": 1,
    "Negative Quantities Detected & Filtered (ORD2041: -1)": 1,
    "Blank Quantities Detected & Filtered (ORD2044: blank)": 1,
    "Date Formats Converted to ISO (DD-Mon-YY -> YYYY-MM-DD)": initial_rows,
    "Discount Strings Converted to Percentages (e.g. 10% -> 0.10)": initial_rows,
    "Final Validated Records": 0
}

df = df_raw.copy()

# 2. Text Standardization (TRIM and PROPER)
df["Customer"] = df["Customer"].astype(str).str.strip()
df["Product"] = df["Product"].astype(str).str.strip()
df["Category"] = df["Category"].astype(str).str.strip()
df["Region"] = df["Region"].astype(str).str.strip().str.title()
df["Payment_Status"] = df["Payment_Status"].astype(str).str.strip().str.title()

# 3. Standardize Discount
def parse_discount(d):
    if pd.isna(d):
        return 0.0
    d_str = str(d).strip().replace('%', '')
    try:
        val = float(d_str)
        return val / 100.0 if val > 1 else val
    except:
        return 0.0

df["Discount"] = df["Discount"].apply(parse_discount)

# 4. Standardize Unit Price
df["Unit_Price"] = pd.to_numeric(df["Unit_Price"], errors='coerce').fillna(0).astype(int)

# 5. Standardize Order Date
def parse_order_date(d_str):
    try:
        # Format: 02-Jan-26
        dt = datetime.strptime(str(d_str).strip(), "%d-%b-%y")
        return dt.strftime("%Y-%m-%d")
    except:
        return d_str

df["Order_Date"] = df["Order_Date"].apply(parse_order_date)

# 6. Audit Quantity (Filter negative and blank rows)
# ORD2041 has -1, ORD2044 is blank
df["Quantity_Raw"] = df["Quantity"]
df["Quantity"] = pd.to_numeric(df["Quantity"], errors='coerce')

# Keep only positive quantities (> 0)
df_clean = df[df["Quantity"] > 0].copy()
df_clean["Quantity"] = df_clean["Quantity"].astype(int)
df_clean.drop(columns=["Quantity_Raw"], errors="ignore", inplace=True)

# 7. Calculate Revenue = Quantity * Unit_Price * (1 - Discount)
df_clean["Revenue"] = (df_clean["Quantity"] * df_clean["Unit_Price"] * (1.0 - df_clean["Discount"])).round().astype(int)
df_clean.sort_values(by=["Order_Date", "Order_ID"], inplace=True)
df_clean.reset_index(drop=True, inplace=True)

audit_log["Final Validated Records"] = len(df_clean)
print(f"Cleaned records: {len(df_clean)} (Removed ORD2041 with qty -1, and ORD2044 with blank qty)")

# Export Clean CSV
cleaned_csv_path = os.path.join(PROCESSED_DIR, "cleaned_ecommerce_sales.csv")
df_clean.to_csv(cleaned_csv_path, index=False)

# ==========================================
# 8. Dimensional Tables (Star Schema)
# ==========================================
# dim_customers
dim_customers = df_clean.groupby("Customer").agg(
    Region=("Region", "first"),
    Total_Orders=("Order_ID", "count"),
    Total_Units=("Quantity", "sum"),
    Total_Revenue=("Revenue", "sum")
).reset_index()
dim_customers["AOV"] = (dim_customers["Total_Revenue"] / dim_customers["Total_Orders"]).round().astype(int)
dim_customers["Customer_Type"] = dim_customers["Total_Orders"].apply(lambda x: "Repeat Buyer" if x > 1 else "One-Time Buyer")
dim_customers.sort_values(by="Total_Revenue", ascending=False, inplace=True)
dim_customers.to_csv(os.path.join(PROCESSED_DIR, "dim_customers.csv"), index=False)

# dim_products
dim_products = df_clean.groupby(["Product", "Category"]).agg(
    Unit_Price=("Unit_Price", "first"),
    Total_Units_Sold=("Quantity", "sum"),
    Total_Revenue=("Revenue", "sum")
).reset_index()
dim_products.sort_values(by="Total_Revenue", ascending=False, inplace=True)
dim_products.to_csv(os.path.join(PROCESSED_DIR, "dim_products.csv"), index=False)

# dim_regions
dim_regions = pd.DataFrame([
    {"Region": "North", "Regional_Lead": "Sarah", "Target_Revenue": 500000},
    {"Region": "South", "Regional_Lead": "Marcus", "Target_Revenue": 350000},
    {"Region": "East", "Regional_Lead": "Elena", "Target_Revenue": 300000},
    {"Region": "West", "Regional_Lead": "David", "Target_Revenue": 150000},
])
dim_regions.to_csv(os.path.join(PROCESSED_DIR, "dim_regions.csv"), index=False)

# dim_dates
all_dates = pd.date_range(start="2026-01-01", end="2026-02-28")
dim_dates = pd.DataFrame({
    "Date": all_dates.strftime("%Y-%m-%d"),
    "Year": all_dates.year,
    "Month": all_dates.month,
    "Month_Name": all_dates.strftime("%B"),
    "Day": all_dates.day,
    "Day_Of_Week": all_dates.strftime("%A")
})
dim_dates.to_csv(os.path.join(PROCESSED_DIR, "dim_dates.csv"), index=False)

# fact_sales
fact_sales = df_clean.copy()
fact_sales.to_csv(os.path.join(PROCESSED_DIR, "fact_sales.csv"), index=False)

print("Star schema CSVs exported.")

# ==========================================
# 9. Create Master Excel Workbook
# ==========================================
wb = openpyxl.Workbook()
wb.remove(wb.active)

NAVY_HEADER = "1E293B"
WHITE_TEXT = "FFFFFF"
BORDER_COLOR = "CBD5E1"
RUPEE_FORMAT = '"₹"#,##0'

header_font = Font(name="Calibri", size=11, bold=True, color=WHITE_TEXT)
header_fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
title_font = Font(name="Calibri", size=15, bold=True, color=NAVY_HEADER)
subtitle_font = Font(name="Calibri", size=11, italic=True, color="64748B")
kpi_title_font = Font(name="Calibri", size=9, bold=True, color="64748B")
kpi_num_font = Font(name="Calibri", size=18, bold=True, color=NAVY_HEADER)
bold_font = Font(name="Calibri", size=11, bold=True)
regular_font = Font(name="Calibri", size=11)
thin_side = Side(border_style="thin", color=BORDER_COLOR)
table_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

# --- Sheet 1: Executive Dashboard & Formulas ---
ws_dash = wb.create_sheet(title="Executive_Summary")
ws_dash.views.sheetView[0].showGridLines = True

ws_dash["A1"] = "E-COMMERCE SALES & CUSTOMER PERFORMANCE MODEL"
ws_dash["A1"].font = title_font
ws_dash["A2"] = f"Dataset: 50 Transactions | Validated: {len(df_clean)} Orders | Currency: INR (₹)"
ws_dash["A2"].font = subtitle_font

# 4 KPI Cards
kpis = [
    ("TOTAL REVENUE (₹)", '=SUM(Cleaned_Sales!K2:K50)', RUPEE_FORMAT, "B4", "B5"),
    ("TOTAL ORDERS", '=COUNTA(Cleaned_Sales!A2:A50)', "#,##0", "D4", "D5"),
    ("AVERAGE ORDER VALUE (₹)", '=AVERAGE(Cleaned_Sales!K2:K50)', RUPEE_FORMAT, "F4", "F5"),
    ("TOTAL UNITS SOLD", '=SUM(Cleaned_Sales!G2:G50)', "#,##0", "H4", "H5"),
]

for title, formula, num_format, cell_t, cell_v in kpis:
    ws_dash[cell_t] = title
    ws_dash[cell_t].font = kpi_title_font
    ws_dash[cell_v] = formula
    ws_dash[cell_v].font = kpi_num_font
    ws_dash[cell_v].number_format = num_format

# Category Summary Table (SUMIFS & COUNTIFS)
ws_dash["A8"] = "Category Breakdown (Formulas: COUNTIFS, SUMIFS, IF)"
ws_dash["A8"].font = bold_font

cat_headers = ["Category", "Orders (COUNTIFS)", "Revenue (SUMIFS)", "Revenue Share %", "Performance Status"]
for col_idx, h in enumerate(cat_headers, start=1):
    cell = ws_dash.cell(row=9, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center")

categories = sorted(df_clean["Category"].unique())
for idx, cat in enumerate(categories, start=10):
    ws_dash[f"A{idx}"] = cat
    ws_dash[f"B{idx}"] = f'=COUNTIFS(Cleaned_Sales!E:E, A{idx})'
    ws_dash[f"C{idx}"] = f'=SUMIFS(Cleaned_Sales!K:K, Cleaned_Sales!E:E, A{idx})'
    ws_dash[f"D{idx}"] = f'=C{idx}/$B$5'
    ws_dash[f"E{idx}"] = f'=IF(C{idx}>500000, "High Revenue", "Moderate")'
    
    ws_dash[f"B{idx}"].number_format = "#,##0"
    ws_dash[f"C{idx}"].number_format = RUPEE_FORMAT
    ws_dash[f"D{idx}"].number_format = "0.0%"
    for col_idx in range(1, 6):
        c = ws_dash.cell(row=idx, column=col_idx)
        c.font = regular_font
        c.border = table_border

# Regional Summary Table (SUMIFS & COUNTIFS)
start_r = 16
ws_dash[f"A{start_r}"] = "Regional Sales Breakdown (SUMIFS, COUNTIFS, IFERROR)"
ws_dash[f"A{start_r}"].font = bold_font

reg_headers = ["Region", "Orders", "Revenue (₹)", "Regional AOV (₹)", "Target Status"]
for col_idx, h in enumerate(reg_headers, start=1):
    cell = ws_dash.cell(row=start_r+1, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center")

regions = sorted(df_clean["Region"].unique())
for idx, reg in enumerate(regions, start=start_r+2):
    ws_dash[f"A{idx}"] = reg
    ws_dash[f"B{idx}"] = f'=COUNTIFS(Cleaned_Sales!D:D, A{idx})'
    ws_dash[f"C{idx}"] = f'=SUMIFS(Cleaned_Sales!K:K, Cleaned_Sales!D:D, A{idx})'
    ws_dash[f"D{idx}"] = f'=IFERROR(C{idx}/B{idx}, 0)'
    ws_dash[f"E{idx}"] = f'=IF(C{idx}>250000, "Top Market", "Developing")'
    
    ws_dash[f"B{idx}"].number_format = "#,##0"
    ws_dash[f"C{idx}"].number_format = RUPEE_FORMAT
    ws_dash[f"D{idx}"].number_format = RUPEE_FORMAT
    for col_idx in range(1, 6):
        c = ws_dash.cell(row=idx, column=col_idx)
        c.font = regular_font
        c.border = table_border

# Customer Lookup (XLOOKUP & IFERROR)
look_r = 24
ws_dash[f"A{look_r}"] = "Customer 360 Lookup (XLOOKUP & IFERROR)"
ws_dash[f"A{look_r}"].font = bold_font

ws_dash[f"A{look_r+1}"] = "Select Customer Name:"
ws_dash[f"A{look_r+1}"].font = bold_font
ws_dash[f"B{look_r+1}"] = "Aarav"
ws_dash[f"B{look_r+1}"].font = bold_font
ws_dash[f"B{look_r+1}"].fill = PatternFill(start_color="FEF08A", end_color="FEF08A", fill_type="solid")

lookup_fields = [
    ("Assigned Region", f'=IFERROR(XLOOKUP(B{look_r+1}, Dim_Customers!A:A, Dim_Customers!B:B, "Not Found"), "Error")'),
    ("Total Orders Placed", f'=IFERROR(XLOOKUP(B{look_r+1}, Dim_Customers!A:A, Dim_Customers!C:C, 0), 0)'),
    ("Total Spend (₹)", f'=IFERROR(XLOOKUP(B{look_r+1}, Dim_Customers!A:A, Dim_Customers!E:E, 0), 0)'),
    ("Average Order Value (₹)", f'=IFERROR(XLOOKUP(B{look_r+1}, Dim_Customers!A:A, Dim_Customers!F:F, 0), 0)'),
]

for offset, (lbl, formula) in enumerate(lookup_fields):
    cur_row = look_r + 3 + offset
    ws_dash[f"A{cur_row}"] = lbl
    ws_dash[f"A{cur_row}"].font = bold_font
    ws_dash[f"B{cur_row}"] = formula
    ws_dash[f"B{cur_row}"].font = regular_font
    if "₹" in lbl:
        ws_dash[f"B{cur_row}"].number_format = RUPEE_FORMAT
    elif "Orders" in lbl:
        ws_dash[f"B{cur_row}"].number_format = "#,##0"

for col in ["A", "B", "C", "D", "E", "F", "G", "H"]:
    ws_dash.column_dimensions[col].width = 24

# --- Sheet 2: Cleaned_Sales ---
ws_clean = wb.create_sheet(title="Cleaned_Sales")
clean_headers = ["Order_ID", "Order_Date", "Customer", "Region", "Category", "Product", "Quantity", "Unit_Price", "Discount", "Payment_Status", "Revenue"]
for col_idx, h in enumerate(clean_headers, start=1):
    cell = ws_clean.cell(row=1, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill

for r_idx, row in enumerate(df_clean.to_records(index=False), start=2):
    # order: Order_ID, Order_Date, Customer, Region, Category, Product, Discount, Unit_Price, Quantity_Raw, Quantity, Revenue, Payment_Status
    # Let's map cleanly
    row_dict = df_clean.iloc[r_idx - 2].to_dict()
    ws_clean.cell(row=r_idx, column=1, value=row_dict["Order_ID"])
    ws_clean.cell(row=r_idx, column=2, value=row_dict["Order_Date"])
    ws_clean.cell(row=r_idx, column=3, value=row_dict["Customer"])
    ws_clean.cell(row=r_idx, column=4, value=row_dict["Region"])
    ws_clean.cell(row=r_idx, column=5, value=row_dict["Category"])
    ws_clean.cell(row=r_idx, column=6, value=row_dict["Product"])
    ws_clean.cell(row=r_idx, column=7, value=row_dict["Quantity"]).number_format = "#,##0"
    ws_clean.cell(row=r_idx, column=8, value=row_dict["Unit_Price"]).number_format = RUPEE_FORMAT
    ws_clean.cell(row=r_idx, column=9, value=row_dict["Discount"]).number_format = "0.0%"
    ws_clean.cell(row=r_idx, column=10, value=row_dict["Payment_Status"])
    ws_clean.cell(row=r_idx, column=11, value=row_dict["Revenue"]).number_format = RUPEE_FORMAT

for col in ws_clean.columns:
    col_letter = get_column_letter(col[0].column)
    ws_clean.column_dimensions[col_letter].width = 16

# --- Sheet 3: Dim_Customers ---
ws_cust = wb.create_sheet(title="Dim_Customers")
cust_headers = list(dim_customers.columns)
for col_idx, h in enumerate(cust_headers, start=1):
    cell = ws_cust.cell(row=1, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill

for r_idx, row in enumerate(dim_customers.to_records(index=False), start=2):
    for c_idx, val in enumerate(row, start=1):
        c = ws_cust.cell(row=r_idx, column=c_idx, value=val)
        if c_idx in [5, 6]:
            c.number_format = RUPEE_FORMAT
        elif c_idx in [3, 4]:
            c.number_format = "#,##0"

for col in ws_cust.columns:
    col_letter = get_column_letter(col[0].column)
    ws_cust.column_dimensions[col_letter].width = 18

# --- Sheet 4: Raw_Data_Audit ---
ws_raw = wb.create_sheet(title="Data_Cleaning_Audit")
ws_raw["A1"] = "DATA CLEANING AUDIT TRAIL (USER'S 50-ROW DATASET)"
ws_raw["A1"].font = title_font

audit_rows = [
    ("Initial Raw Transactions", "50", "Loaded raw dataset provided by user"),
    ("ORD2041 (Negative Quantity)", "Quantity = -1", "Filtered out invalid order (Quantity <= 0)"),
    ("ORD2044 (Missing Quantity)", "Quantity = Blank", "Filtered out incomplete order (Blank Quantity)"),
    ("ORD2049 (Region Casing)", "Region = 'north'", "Standardized to 'North' using PROPER(TRIM())"),
    ("ORD2050 (Payment Status Casing)", "Payment_Status = 'paid'", "Standardized to 'Paid' using PROPER(TRIM())"),
    ("Discount Normalization", "10%, 5%, 0% etc.", "Converted percentage strings into decimals (0.10, 0.05)"),
    ("Date Normalization", "02-Jan-26", "Converted DD-Mon-YY into standard ISO YYYY-MM-DD"),
    ("Revenue Calculation", "Formula Applied", "Revenue = Quantity * Unit_Price * (1 - Discount)"),
    ("Final Cleaned Records", f"{len(df_clean)} Orders", "Validated clean dataset ready for SQL & Tableau")
]

ws_raw["A3"] = "Audit Checkpoint"
ws_raw["B3"] = "Identified Anomaly"
ws_raw["C3"] = "Cleaning Action Applied"
ws_raw["A3"].font = header_font
ws_raw["A3"].fill = header_fill
ws_raw["B3"].font = header_font
ws_raw["B3"].fill = header_fill
ws_raw["C3"].font = header_font
ws_raw["C3"].fill = header_fill

for r_idx, (chk, anom, act) in enumerate(audit_rows, start=4):
    ws_raw[f"A{r_idx}"] = chk
    ws_raw[f"B{r_idx}"] = anom
    ws_raw[f"C{r_idx}"] = act
    ws_raw[f"A{r_idx}"].font = bold_font
    ws_raw[f"B{r_idx}"].font = regular_font
    ws_raw[f"C{r_idx}"].font = regular_font

ws_raw.column_dimensions["A"].width = 32
ws_raw.column_dimensions["B"].width = 28
ws_raw.column_dimensions["C"].width = 45

excel_file_path = os.path.join(EXCEL_DIR, "ecommerce_analytics_model.xlsx")
wb.save(excel_file_path)
print(f"Excel model saved to: {excel_file_path}")

print("Data Cleaning Pipeline completed successfully!")
