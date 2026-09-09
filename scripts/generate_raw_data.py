"""
Save exact raw e-commerce sales dataset provided by user
50 rows containing deliberate real-world data quality anomalies for cleaning demonstration.
"""

import os
import pandas as pd

raw_data = """Order_ID	Order_Date	Customer	Region	Category	Product	Quantity	Unit_Price	Discount	Payment_Status
ORD2001	02-Jan-26	Aarav	North	Electronics	Laptop	2	55000	10%	Paid
ORD2002	03-Jan-26	Diya	South	Clothing	Jacket	3	4200	5%	Paid
ORD2003	04-Jan-26	Rohan	West	Furniture	Chair	5	3200	0%	Paid
ORD2004	05-Jan-26	Meera	East	Electronics	Headphones	4	2500	15%	Pending
ORD2005	06-Jan-26	Kabir	North	Furniture	Table	2	8500	10%	Paid
ORD2006	07-Jan-26	Isha	South	Electronics	Phone	3	28000	5%	Paid
ORD2007	08-Jan-26	Arjun	West	Clothing	Shoes	2	3500	20%	Paid
ORD2008	09-Jan-26	Sanya	East	Electronics	Tablet	1	22000	10%	Paid
ORD2009	10-Jan-26	Aarav	North	Electronics	Laptop	1	55000	5%	Paid
ORD2010	11-Jan-26	Diya	South	Clothing	Jacket	4	4200	10%	Failed
ORD2011	12-Jan-26	Rohan	West	Furniture	Chair	3	3200	5%	Paid
ORD2012	13-Jan-26	Meera	East	Electronics	Headphones	5	2500	0%	Paid
ORD2013	14-Jan-26	Kabir	North	Furniture	Table	1	8500	15%	Paid
ORD2014	15-Jan-26	Isha	South	Electronics	Phone	2	28000	10%	Paid
ORD2015	16-Jan-26	Arjun	West	Clothing	Shoes	4	3500	5%	Paid
ORD2016	17-Jan-26	Sanya	East	Electronics	Tablet	2	22000	10%	Paid
ORD2017	18-Jan-26	Aarav	North	Electronics	Laptop	3	55000	15%	Paid
ORD2018	19-Jan-26	Diya	South	Clothing	Jacket	2	4200	0%	Paid
ORD2019	20-Jan-26	Rohan	West	Furniture	Chair	6	3200	10%	Paid
ORD2020	21-Jan-26	Meera	East	Electronics	Headphones	2	2500	5%	Paid
ORD2021	22-Jan-26	Kabir	North	Furniture	Table	3	8500	20%	Paid
ORD2022	23-Jan-26	Isha	South	Electronics	Phone	1	28000	5%	Pending
ORD2023	24-Jan-26	Arjun	West	Clothing	Shoes	3	3500	10%	Paid
ORD2024	25-Jan-26	Sanya	East	Electronics	Tablet	4	22000	15%	Paid
ORD2025	26-Jan-26	Aarav	North	Electronics	Laptop	2	55000	10%	Paid
ORD2026	27-Jan-26	Diya	South	Clothing	Jacket	1	4200	5%	Paid
ORD2027	28-Jan-26	Rohan	West	Furniture	Chair	2	3200	0%	Paid
ORD2028	29-Jan-26	Meera	East	Electronics	Headphones	3	2500	10%	Paid
ORD2029	30-Jan-26	Kabir	North	Furniture	Table	2	8500	5%	Paid
ORD2030	31-Jan-26	Isha	South	Electronics	Phone	2	28000	15%	Paid
ORD2031	02-Feb-26	Arjun	West	Clothing	Shoes	5	3500	20%	Paid
ORD2032	03-Feb-26	Sanya	East	Electronics	Tablet	1	22000	0%	Paid
ORD2033	04-Feb-26	Aarav	North	Electronics	Laptop	2	55000	10%	Paid
ORD2034	05-Feb-26	Diya	South	Clothing	Jacket	3	4200	5%	Paid
ORD2035	06-Feb-26	Rohan	West	Furniture	Chair	4	3200	10%	Paid
ORD2036	07-Feb-26	Meera	East	Electronics	Headphones	2	2500	5%	Paid
ORD2037	08-Feb-26	Kabir	North	Furniture	Table	1	8500	0%	Paid
ORD2038	09-Feb-26	Isha	South	Electronics	Phone	3	28000	10%	Paid
ORD2039	10-Feb-26	Arjun	West	Clothing	Shoes	2	3500	5%	Paid
ORD2040	11-Feb-26	Sanya	East	Electronics	Tablet	3	22000	15%	Paid
ORD2041	12-Feb-26	Aarav	North	Electronics	Laptop	-1	55000	10%	Paid
ORD2042	13-Feb-26	Diya	South	Clothing	Jacket	2	4200	5%	Paid
ORD2043	14-Feb-26	Rohan	West	Furniture	Chair	3	3200	0%	Paid
ORD2044	15-Feb-26	Meera	East	Electronics	Headphones		2500	10%	Paid
ORD2045	16-Feb-26	Kabir	North	Furniture	Table	2	8500	5%	Paid
ORD2046	17-Feb-26	Isha	South	Electronics	Phone	2	28000	5%	Paid
ORD2047	18-Feb-26	Arjun	West	Clothing	Shoes	3	3500	10%	Paid
ORD2048	19-Feb-26	Sanya	East	Electronics	Tablet	2	22000	15%	Paid
ORD2049	20-Feb-26	Aarav	north	Electronics	Laptop	1	55000	10%	Paid
ORD2050	21-Feb-26	Diya	South	Clothing	Jacket	2	4200	5%	paid"""

lines = [line.split('\t') for line in raw_data.strip().split('\n')]
headers = lines[0]
data = lines[1:]

df = pd.DataFrame(data, columns=headers)

os.makedirs("data/raw", exist_ok=True)
output_file = "data/raw/raw_ecommerce_sales.csv"
df.to_csv(output_file, index=False)

print(f"Saved {len(df)} raw records to: {output_file}")
