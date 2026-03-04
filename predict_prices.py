# ==================================================
# COMPLETE TOP-SELLER PREDICTION SYSTEM FOR KAMI BY KAMU
# ==================================================

import pandas as pd
import numpy as np
import os
from datetime import datetime

def clean_text(text):
    """Remove special characters that cause encoding errors"""
    if not isinstance(text, str):
        return text
    # Replace common special characters
    text = text.replace('Ī', 'I').replace('ī', 'i')
    text = text.replace('Ā', 'A').replace('ā', 'a')
    text = text.replace('Ē', 'E').replace('ē', 'e')
    text = text.replace('Ō', 'O').replace('ō', 'o')
    text = text.replace('Ū', 'U').replace('ū', 'u')
    return text

print("=" * 60)
print("KAMI BY KAMU - TOP SELLER PREDICTION SYSTEM")
print("=" * 60)

# ==================================================
# STEP 1: LOAD YOUR EXISTING DATA
# ==================================================

# Find your data file
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Try to find your master file
if os.path.exists('kami_products_master.csv'):
    df = pd.read_csv('kami_products_master.csv')
    print(f"\n[OK] Loaded {len(df)} products from kami_products_master.csv")
elif os.path.exists('kami_data_clean.csv'):
    df = pd.read_csv('kami_data_clean.csv')
    print(f"\n[OK] Loaded {len(df)} products from kami_data_clean.csv")
else:
    print("\n[WARNING] No data file found. Using built-in product list.")
    # Create from the products we know exist
    products = [
        "Chantelle Bag", "Milano Bag", "Hera Bag 2.0", "Lou Bag 2.0",
        "KAMI x Anissa Aziza - Alba Bag", "Oria Bag", "Mini Hera Bag 2.0",
        "KAMI X Attera - Medium Lou Bag", "Rodeo Bag", "Monet Bag",
        "Baby Rodeo Bag", "Lou Bag 2.0 Multicolor", "KAMI X Attera - Small Lou Bag",
        "Marcie Phone Bag", "Lou Wallet", "Kora Bag", "Baby Hera Bag 2.0",
        "Bundle Rodeo Bag & Baby Rodeo Bag", "Portia Tote Bag",
        "Small Roche Genuine Leather Bag", "Coello Bag", "Large Roche Genuine Leather Bag",
        "Sanchez Padel Bag", "Bundle Coello Padel Bag"
    ]
    prices = [
        495000, 465000, 485000, 465000, 445000, 445000, 419000,
        445000, 485000, 419000, 99900, 465000, 395000,
        258000, 195000, 395000, 99900, 550000,
        495000, 799000, 529000, 999000,
        650000, 750000
    ]
    df = pd.DataFrame({'Product': products, 'Price': [f"Rp {p:,}".replace(',', '.') for p in prices]})
    print(f"[OK] Created list with {len(df)} products")

# Clean product names to remove special characters
df['Product_Clean'] = df['Product'].apply(clean_text)

# ==================================================
# STEP 2: CREATE PRODUCT FEATURES (ML PART)
# ==================================================

print("\n" + "=" * 60)
print("STEP 1: ANALYZING PRODUCT FEATURES")
print("=" * 60)

# Clean price data
if 'Price_Numeric' not in df.columns:
    df['Price_Numeric'] = df['Price'].astype(str).str.replace('Rp', '', regex=False)
    df['Price_Numeric'] = df['Price_Numeric'].str.replace('.', '', regex=False).str.strip()
    df['Price_Numeric'] = pd.to_numeric(df['Price_Numeric'], errors='coerce')

# Remove rows with NaN prices (duplicates)
df = df.dropna(subset=['Price_Numeric'])
df = df.drop_duplicates(subset=['Product_Clean', 'Price_Numeric'])
print(f"\n[OK] Cleaned data: {len(df)} unique products with valid prices")

# Create features that predict sales
df['is_genuine'] = df['Product_Clean'].str.contains('Genuine', case=False).fillna(False).astype(int)
df['is_collab'] = df['Product_Clean'].str.contains('x |X |collab|Attera|Anissa', case=False, regex=True).fillna(False).astype(int)
df['is_bundle'] = df['Product_Clean'].str.contains('Bundle', case=False).fillna(False).astype(int)
df['is_mini'] = df['Product_Clean'].str.contains('Mini|Baby', case=False).fillna(False).astype(int)
df['is_wallet'] = df['Product_Clean'].str.contains('Wallet', case=False).fillna(False).astype(int)
df['name_length'] = df['Product_Clean'].str.len()
df['word_count'] = df['Product_Clean'].str.split().str.len()

# Popular series (these names appear frequently)
df['is_hera'] = df['Product_Clean'].str.contains('Hera', case=False).fillna(False).astype(int)
df['is_lou'] = df['Product_Clean'].str.contains('Lou', case=False).fillna(False).astype(int)
df['is_rodeo'] = df['Product_Clean'].str.contains('Rodeo', case=False).fillna(False).astype(int)

# Price segments
df['price_segment'] = pd.cut(df['Price_Numeric'], 
                              bins=[0, 200000, 400000, 600000, 1000000],
                              labels=['Budget', 'Mid-Range', 'Premium', 'Luxury'])

print("\n[OK] Product features created:")
print(df[['Product_Clean', 'Price_Numeric', 'price_segment', 'is_genuine', 'is_collab', 'is_mini']].head(10))

# ==================================================
# STEP 3: CALCULATE ML PREDICTION SCORES
# ==================================================

print("\n" + "=" * 60)
print("STEP 2: ML-BASED PREDICTION SCORES")
print("=" * 60)

# Calculate ML scores based on features that typically predict sales
ml_scores = []
for idx, row in df.iterrows():
    score = 50  # Base score
    
    # Premium features increase score
    if row['is_genuine']:
        score += 25
        print(f"  [+] {row['Product_Clean'][:30]}... +25 (Genuine leather)")
    
    if row['is_collab']:
        score += 20
        print(f"  [+] {row['Product_Clean'][:30]}... +20 (Collaboration)")
    
    if row['is_bundle']:
        score += 15
        print(f"  [+] {row['Product_Clean'][:30]}... +15 (Bundle value)")
    
    # Popular series get bonus
    if row['is_hera'] or row['is_lou'] or row['is_rodeo']:
        score += 10
        print(f"  [+] {row['Product_Clean'][:30]}... +10 (Popular series)")
    
    # Price sweet spot (most bags sell in this range)
    if 300000 < row['Price_Numeric'] < 500000:
        score += 20
        print(f"  [+] {row['Product_Clean'][:30]}... +20 (Ideal price range)")
    elif row['Price_Numeric'] < 200000:
        score += 10
        print(f"  [+] {row['Product_Clean'][:30]}... +10 (Entry-level)")
    
    # Longer names often mean more description = premium
    if row['name_length'] > 30:
        score += 10
    
    # Mini versions attract budget buyers
    if row['is_mini']:
        score += 5
    
    ml_scores.append(score)

df['ml_score'] = ml_scores

# ==================================================
# STEP 4: COMMUNITY VOTING (INTERACTIVE PART)
# ==================================================

print("\n" + "=" * 60)
print("STEP 3: COMMUNITY VOTING")
print("=" * 60)
print("\nNow let's get YOUR opinion (acting as community votes)")
print("Rate these top candidate products from 1-5:")

# Select top candidates from ML scores
top_candidates = df.nlargest(8, 'ml_score')[['Product_Clean', 'Price_Numeric']].copy()

community_votes = []
for idx, row in top_candidates.iterrows():
    print(f"\n[PRODUCT] {row['Product_Clean']}")
    print(f"   Price: Rp {row['Price_Numeric']:,.0f}")
    
    while True:
        try:
            buy = int(input("   Would you buy this? (1-5, 5=definitely): "))
            if 1 <= buy <= 5:
                break
            else:
                print("   Please enter 1-5")
        except ValueError:
            print("   Please enter a number")
    
    while True:
        try:
            gift = int(input("   Would you gift this? (1-5): "))
            if 1 <= gift <= 5:
                break
            else:
                print("   Please enter 1-5")
        except ValueError:
            print("   Please enter a number")
    
    while True:
        try:
            price = int(input("   Is price fair? (1-5): "))
            if 1 <= price <= 5:
                break
            else:
                print("   Please enter 1-5")
        except ValueError:
            print("   Please enter a number")
    
    community_votes.append({
        'product': row['Product_Clean'],
        'buy_score': buy,
        'gift_score': gift,
        'price_score': price
    })

# ==================================================
# STEP 5: CALCULATE FINAL SCORES
# ==================================================

print("\n" + "=" * 60)
print("STEP 4: CALCULATING FINAL PREDICTIONS")
print("=" * 60)

# Convert votes to DataFrame
votes_df = pd.DataFrame(community_votes)

# Calculate community score (weighted: buy intent is most important)
votes_df['community_score'] = (
    votes_df['buy_score'] * 0.5 +    # Purchase intent is strongest
    votes_df['gift_score'] * 0.3 +    # Gift potential
    votes_df['price_score'] * 0.2     # Price perception
) * 20  # Scale to 0-100

# Normalize ML scores to 0-100
min_ml = df['ml_score'].min()
max_ml = df['ml_score'].max()
df['ml_score_norm'] = ((df['ml_score'] - min_ml) / (max_ml - min_ml)) * 100

# Combine scores (research shows community votes are more accurate than expert analysis)
final_results = []
for idx, row in top_candidates.iterrows():
    ml_norm = df[df['Product_Clean'] == row['Product_Clean']]['ml_score_norm'].values[0]
    community = votes_df[votes_df['product'] == row['Product_Clean']]['community_score'].values[0]
    
    # Final score: 60% community, 40% ML
    final_score = (community * 0.6) + (ml_norm * 0.4)
    
    final_results.append({
        'product': row['Product_Clean'],
        'price': row['Price_Numeric'],
        'ml_score': round(ml_norm, 1),
        'community_score': round(community, 1),
        'final_score': round(final_score, 1)
    })

# Sort by final score
final_df = pd.DataFrame(final_results)
final_df = final_df.sort_values('final_score', ascending=False).reset_index(drop=True)

# ==================================================
# STEP 6: DISPLAY RESULTS
# ==================================================

print("\n" + "=" * 60)
print("FINAL RESULTS - TOP SELLER PREDICTIONS")
print("=" * 60)

for i, row in final_df.iterrows():
    medal = "#1" if i == 0 else "#2" if i == 1 else "#3" if i == 2 else f"#{i+1}"
    print(f"\n[{medal}] {row['product']}")
    print(f"   Price: Rp {row['price']:,.0f}")
    print(f"   ML Score: {row['ml_score']}/100")
    print(f"   Community Score: {row['community_score']}/100")
    print(f"   FINAL SCORE: {row['final_score']}/100")

# ==================================================
# STEP 7: RECOMMENDATIONS
# ==================================================

print("\n" + "=" * 60)
print("RECOMMENDATIONS FOR YOUR COMMUNITY")
print("=" * 60)

winner = final_df.iloc[0]
runner_up = final_df.iloc[1] if len(final_df) > 1 else None
third = final_df.iloc[2] if len(final_df) > 2 else None

print(f"\n[TOP RECOMMENDATION] {winner['product']}")
print(f"   Price: Rp {winner['price']:,.0f}")
print(f"   Why it will sell well:")
print(f"   - Strong community interest (score: {winner['community_score']}/100)")
print(f"   - Good product features (score: {winner['ml_score']}/100)")

if runner_up is not None:
    print(f"\n[BACKUP OPTION] {runner_up['product']}")
    print(f"   Price: Rp {runner_up['price']:,.0f}")

print("\n" + "=" * 60)
print("ACTION PLAN")
print("=" * 60)
print("""
1. Buy 3-5 units of the top recommendation FIRST
2. Track how fast they sell
3. If they sell within 1-2 weeks, buy more
4. Consider the runner-up as your second option
5. Share results with your community to build trust

Remember: Start small, test the market, then scale up!
""")

# ==================================================
# STEP 8: SAVE RESULTS
# ==================================================

# Save to CSV
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f'top_seller_prediction_{timestamp}.csv'
final_df.to_csv(filename, index=False)
print(f"\n[OK] Full results saved to: {filename}")

# Also save detailed analysis
detailed_file = f'detailed_analysis_{timestamp}.csv'
df[['Product_Clean', 'Price_Numeric', 'price_segment', 'is_genuine', 'is_collab', 
    'is_bundle', 'is_mini', 'is_hera', 'is_lou', 'is_rodeo', 'ml_score']].to_csv(detailed_file, index=False)
print(f"[OK] Detailed analysis saved to: {detailed_file}")

print("\n" + "=" * 60)
print("PREDICTION COMPLETE! Good luck with your sales!")
print("=" * 60)