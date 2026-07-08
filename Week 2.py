import pandas as pd
from pathlib import Path

combined_files = Path(r"C:\Users\jjcho\OneDrive\Desktop\IDX Exchange Internship\concatenated py files")

#CSV files already filtered to PropertyType = Residential only
listing_file = combined_files / "combined_listings_residential.csv"
sold_file = combined_files / "combined_sold_residential.csv"

listing_df = pd.read_csv(listing_file, low_memory=False, encoding="utf-8")
sold_df = pd.read_csv(sold_file, low_memory=False, encoding="utf-8")

#Doing PropertySubType because csv files are already filtered to only one PropertyType
unique_properties_list = listing_df["PropertySubType"].dropna().astype(str).str.strip()
unique_properties_list = unique_properties_list[unique_properties_list != ""].unique()

print(f"The following are the unique property sub types for listing: {", ".join(unique_properties_list)}.")

#For sold
unique_properties_sold = sold_df["PropertySubType"].dropna().astype(str).str.strip()
unique_properties_sold = unique_properties_sold[unique_properties_sold != ""].unique()

print(f"The following are the unique property sub types for sold: {", ".join(unique_properties_sold)}.")



#Summing all null values
listing_df_null = []
listing_df_col = listing_df.columns
listing_df_row_num = len(listing_df.index)
listing_null_sum = 0

#append all sums of nulls for each column in a list for listing
for col in listing_df_col:
    null_num = listing_df[col].isnull().sum()
    print(f"{'\033[37m'}{col} has {null_num} amount of nulls in its column for listing.\n")
    listing_df_null.append(null_num)

    
    if listing_df_null[listing_null_sum] > .9*len(listing_df.index):
        print(f"{'\033[31m'}{col} has greater than 90% null values for listing.\n")
    
    listing_null_sum += 1



sold_df_null = []
sold_df_col = sold_df.columns
sold_df_row_num = len(sold_df.index)
sold_null_sum = 0

#append all sums of nulls for each column in a list for sold
for col in sold_df_col:
    null_num = sold_df[col].isnull().sum()
    print(f"{'\033[37m'}{col} has {null_num} amount of nulls in its column for sold.\n")
    sold_df_null.append(null_num)

    if sold_df_null[sold_null_sum] > .9*len(sold_df.index):
        print(f"{'\033[31m'}{col} has greater than 90% null values for sold.\n")
    
    sold_null_sum += 1

#Ask what columns are best to remove, remove manually or to remove with code?

#numeric distribution summary
for col in listing_df_col:
    if col in ["ClosePrice", "LivingArea", "DaysOnMarket"]:
        print(f"{'\033[32m'} Max for {col} is {listing_df[col].max()} {'\033[37m'} and {'\033[33m'} min is {listing_df[col].min()}.\n")