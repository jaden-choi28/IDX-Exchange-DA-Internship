import pandas as pd
from pathlib import Path

data_folder = Path(r"C:\Users\jjcho\OneDrive\Desktop\IDX Exchange Internship\Weekly csv files")

listings_file = data_folder / "Week 3 mortgage rates listing.csv"
sold_file = data_folder / "Week 3 mortgage rates sold.csv"

listings = pd.read_csv(listings_file, low_memory=False, encoding="utf-8")
sold = pd.read_csv(sold_file, low_memory=False, encoding="utf-8")

#Inclusion of row counts before any adjustments to csvs
print("Before cleaning:")
print(f"Listings rows: {len(listings):,}, columns: {listings.shape[1]}")
print(f"Sold rows: {len(sold):,}, columns: {sold.shape[1]}")

#Helper function to convert datetimes
def conversion_to_date(df, date_columns):
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="mixed")#, errors="coerce")
    return df

date_columns = ["CloseDate", "PurchaseContractDate", "ListingContractDate", "ContractStatusChangeDate"]

listings = conversion_to_date(listings, date_columns)
sold = conversion_to_date(sold, date_columns)

#Helper function to convert numeric columns
def convert_numeric(df, numeric_columns):
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

numeric_columns = ["ClosePrice", "ListPrice", "LivingArea", "DaysOnMarket", "BedroomsTotal", "BathroomsTotalInteger", 
                   "BathroomsFull", "BathroomsHalf", "Latitude", "Longitude", "rate_30yr_fixed"]

listings = convert_numeric(listings, numeric_columns)
sold = convert_numeric(sold, numeric_columns)

#Columns that are redundant or unnecessary 
columns_to_drop = ["ListAgentEmail", "OriginatingSystemName", "OriginatingSystemSubName", "Latitude.1", "Longitude.1", "CloseDate.1", "BuyerOfficeName.1"]

listings_drop_cols = [col for col in columns_to_drop if col in listings.columns]
sold_drop_cols = [col for col in columns_to_drop if col in sold.columns]

listings = listings.drop(columns=listings_drop_cols)
sold = sold.drop(columns=sold_drop_cols)

print("\nDropped columns:")
print("Listings:", listings_drop_cols)
print("Sold:", sold_drop_cols)