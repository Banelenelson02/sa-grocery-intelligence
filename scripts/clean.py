import pandas as pd

# Loading the messy data
df = pd.read_csv('../data/raw/messy_prices.csv')
initial_row_count = len(df)

# Removing any duplicates
# Added .copy() to prevent pandas warnings when we modify the data later
df_clean = df.drop_duplicates().copy() 
dupes_removed = initial_row_count - len(df_clean)

# Fixing store names
store_mapping = {
    'PnP': 'Pick n Pay',
    'Pick N Pay': 'Pick n Pay',
    'pick n pay': 'Pick n Pay'
}
df_clean['store'] = df_clean['store'].replace(store_mapping)

# Dropping any null prices
current_count = len(df_clean)
df_clean = df_clean.dropna(subset=['price_zar'])
nulls_removed = current_count - len(df_clean)

# Dropping any impossible prices (0 or > 5000)
current_count = len(df_clean)
#only keeping rows where price is greater than 0 and less than or equal to 5000
df_clean = df_clean[(df_clean['price_zar'] > 0) & (df_clean['price_zar'] <= 5000)]
impossible_removed = current_count - len(df_clean)

# Filtering future dates
current_count = len(df_clean)
# Convert the column to actual datetime objects then filter out anything past today
df_clean['recorded_at'] = pd.to_datetime(df_clean['recorded_at'])
df_clean = df_clean[df_clean['recorded_at'] <= pd.Timestamp.today()]
future_removed = current_count - len(df_clean)

# Filtering unknown stores
current_count = len(df_clean)
canonical_stores = ['Shoprite', 'Checkers', 'Pick n Pay', 'Woolworths', 'SPAR', 'Boxer', "Food Lover's Market", 'Cambridge Food', 'Usave', 'Makro']
df_clean = df_clean[df_clean['store'].isin(canonical_stores)]
unknown_removed = current_count - len(df_clean)

# Summary Log
print("🧹 Cleaning Summary:")
print(f"- Removed {dupes_removed} duplicates")
print(f"- Dropped {nulls_removed} null prices")
print(f"- Dropped {impossible_removed} impossible prices")
print(f"- Dropped {future_removed} future dates")
print(f"- Dropped {unknown_removed} unknown stores")
print("- Fixed store name inconsistencies")
print(f"✅ Final clean dataset has {len(df_clean)} valid rows remaining.")

df_clean.to_csv('../data/processed/clean_prices.csv', index=False)