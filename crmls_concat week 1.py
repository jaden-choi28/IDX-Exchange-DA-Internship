import pandas as pd
from pathlib import Path

main_csv_files = Path(r"DIRECTORY WHERE CSVS FILES ARE")

listing_files = sorted(main_csv_files.glob("CRMLSListing*.csv"))
sold_files = sorted(main_csv_files.glob("CRMLSSold*.csv"))

#See if file is utf or cp1252
def read_crmls_csv(file):
    try:
        return pd.read_csv(file, low_memory=False, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(file, low_memory=False, encoding="cp1252")

#Concatenate listing files
listing_dfs = []
for file in listing_files:
    df = read_crmls_csv(file)
    df["source_file"] = file.name
    listing_dfs.append(df)

listings_combined = pd.concat(listing_dfs, ignore_index=True)

print(f"Total listing rows after concatenation: {len(listings_combined):,}")

#Concatenate sold files
sold_dfs = []
for file in sold_files:
    df = read_crmls_csv(file)
    df["source_file"] = file.name
    sold_dfs.append(df)

sold_combined = pd.concat(sold_dfs, ignore_index=True)

print(f"Total sold rows after concatenation: {len(sold_combined):,}")


#Filtering for Residential only
residential_listings = listings_combined[listings_combined["PropertyType"].astype(str).str.strip() == "Residential"
].copy()
residential_sold = sold_combined[sold_combined["PropertyType"].astype(str).str.strip() == "Residential"
].copy()

print(f"Total number of Listing rows before Residential filter: {len(listings_combined):,}")
print(f"Total number of Listing rows after Residential filter: {len(residential_listings):,}")

print(f"Total number of Sold rows before Residential filter: {len(sold_combined):,}")
print(f"Total number of Sold rows after Residential filter: {len(residential_sold):,}")

#Saving CSVs
residential_listings.to_csv(r"YOUR DIRECTORY", index=False)
residential_sold.to_csv(r"YOUR DIRECTORY", index=False)
