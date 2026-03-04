import pandas as pd
import os
import glob

def safe_print(text):
    """Print text safely by replacing problematic characters"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace common Indonesian special characters
        text = text.replace('Ī', 'I').replace('ī', 'i')
        text = text.replace('Ā', 'A').replace('ā', 'a')
        text = text.replace('Ē', 'E').replace('ē', 'e')
        text = text.replace('Ō', 'O').replace('ō', 'o')
        text = text.replace('Ū', 'U').replace('ū', 'u')
        # If still error, encode as ascii ignoring
        try:
            print(text)
        except:
            safe_text = text.encode('ascii', 'ignore').decode('ascii')
            print(safe_text)

print("=" * 50)
print("KAMI by KAMU Product Analysis")
print("=" * 50)

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")

# Change to script directory
os.chdir(script_dir)
print(f"Current directory: {os.getcwd()}")

# Find all CSV files in this directory
csv_files = glob.glob("*.csv")
print(f"\nFound {len(csv_files)} CSV file(s) in this folder:")

if not csv_files:
    print("  No CSV files found!")
    print("\nPlease check:")
    print("1. You are in the right folder")
    print("2. The scraper ran successfully")
    print("3. Files exist by running: dir *.csv")
    exit()

for file in csv_files:
    file_size = os.path.getsize(file)
    print(f"  - {file} ({file_size} bytes)")

# Find master file or use most recent
master_file = None
for file in csv_files:
    if 'master' in file.lower():
        master_file = file
        break

if master_file:
    print(f"\n[OK] Using master file: {master_file}")
else:
    # Use the most recent CSV file
    if csv_files:
        master_file = max(csv_files, key=os.path.getctime)
        print(f"\n[NOTE] No master file found. Using most recent: {master_file}")

# Load the data
try:
    df = pd.read_csv(master_file)
    print(f"\n[OK] Loaded {len(df)} products from {master_file}")
    
    # Clean product names (replace special characters)
    df['Product_Clean'] = df['Product'].str.replace('Ī', 'I', regex=False)
    df['Product_Clean'] = df['Product_Clean'].str.replace('ī', 'i', regex=False)
    
    print("\nFirst 3 rows of data:")
    print(df[['Date', 'Product_Clean', 'Price']].head(3))
except Exception as e:
    print(f"[ERROR] Error loading file: {e}")
    exit()

# Clean price data
df['Price_Numeric'] = df['Price'].str.replace('Rp', '', regex=False).str.replace('.', '', regex=False).str.strip()
df['Price_Numeric'] = pd.to_numeric(df['Price_Numeric'], errors='coerce')

# Remove invalid prices
df = df.dropna(subset=['Price_Numeric'])
print(f"\n[OK] Products with valid prices: {len(df)}")

if len(df) == 0:
    print("[ERROR] No valid price data found!")
    exit()

# Basic statistics
print("\n" + "=" * 50)
print("PRODUCT STATISTICS")
print("=" * 50)
print(f"Total products: {len(df)}")
print(f"Average price: Rp {df['Price_Numeric'].mean():,.0f}")
print(f"Median price: Rp {df['Price_Numeric'].median():,.0f}")
print(f"Most expensive: Rp {df['Price_Numeric'].max():,.0f}")
print(f"Least expensive: Rp {df['Price_Numeric'].min():,.0f}")

# Price distribution
print("\nPRICE DISTRIBUTION")
print("-" * 50)
price_ranges = [
    (0, 100000, "Under Rp 100k"),
    (100000, 200000, "Rp 100k - 200k"),
    (200000, 300000, "Rp 200k - 300k"),
    (300000, 400000, "Rp 300k - 400k"),
    (400000, 500000, "Rp 400k - 500k"),
    (500000, 1000000, "Rp 500k - 1M"),
    (1000000, 9999999, "Above Rp 1M")
]

for low, high, label in price_ranges:
    count = len(df[(df['Price_Numeric'] >= low) & (df['Price_Numeric'] < high)])
    if count > 0:
        percentage = (count/len(df))*100
        print(f"{label}: {count} products ({percentage:.1f}%)")

# Category analysis
print("\nPRODUCT CATEGORIES")
print("-" * 50)

categories = {
    'Bags': 'Bag',
    'Wallets': 'Wallet',
    'Bundles': 'Bundle',
    'Mini/Baby': 'Mini|Baby',
    'Genuine Leather': 'Genuine',
}

for category_name, keyword in categories.items():
    count = df['Product_Clean'].str.contains(keyword, case=False, na=False).sum()
    if count > 0:
        print(f"{category_name}: {count} products")

# Top 5 most expensive
print("\nTOP 5 MOST EXPENSIVE")
print("-" * 50)
top5 = df.nlargest(5, 'Price_Numeric')[['Product_Clean', 'Price']]
for idx, row in top5.iterrows():
    product_name = row['Product_Clean'][:40] + '...' if len(row['Product_Clean']) > 40 else row['Product_Clean']
    safe_print(f"  {product_name} - {row['Price']}")

# Bottom 5 least expensive
print("\nTOP 5 LEAST EXPENSIVE")
print("-" * 50)
bottom5 = df.nsmallest(5, 'Price_Numeric')[['Product_Clean', 'Price']]
for idx, row in bottom5.iterrows():
    product_name = row['Product_Clean'][:40] + '...' if len(row['Product_Clean']) > 40 else row['Product_Clean']
    safe_print(f"  {product_name} - {row['Price']}")

# Save clean data
clean_file = 'kami_data_clean.csv'
df_clean = df[['Date', 'Product_Clean', 'Price_Numeric']]
df_clean.rename(columns={'Product_Clean': 'Product'}, inplace=True)
df_clean.to_csv(clean_file, index=False, encoding='utf-8-sig')
print(f"\n[OK] Clean data saved to: {clean_file}")

# Average price by category
print("\nAVERAGE PRICE BY CATEGORY")
print("-" * 50)
print(f"All Products: Rp {df['Price_Numeric'].mean():,.0f} ({len(df)} products)")

for category_name, keyword in categories.items():
    if '|' in keyword:
        mask = df['Product_Clean'].str.contains(keyword, case=False, na=False)
    else:
        mask = df['Product_Clean'].str.contains(keyword, case=False, na=False)
    
    subset = df[mask]
    if len(subset) > 0:
        avg = subset['Price_Numeric'].mean()
        print(f"{category_name}: Rp {avg:,.0f} ({len(subset)} products)")

print("\n" + "=" * 50)
print("Analysis complete!")
print(f"Files saved in: {script_dir}")