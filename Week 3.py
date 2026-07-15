import pandas as pd
from pathlib import Path

combined_files = Path(r"C:\Users\jjcho\OneDrive\Desktop\IDX Exchange Internship\Weekly csv files")
listing_file = combined_files / "Week 2 cleaned listing.csv"
sold_file = combined_files / "Week 2 cleaned sold.csv"
listings = pd.read_csv(listing_file, low_memory=False, encoding="utf-8")
sold = pd.read_csv(sold_file, low_memory=False, encoding="utf-8")


url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

#Calculate monthly averages
mortgage["year_month"] = mortgage["date"].dt.to_period("M")
mortgage_monthly = mortgage.groupby("year_month")["rate_30yr_fixed"].mean().reset_index()

#Now for lists and sold
listings["ListingContractDate"] = pd.to_datetime(listings["ListingContractDate"], errors="coerce")
listings["year_month"] = listings["ListingContractDate"].dt.to_period("M")

sold["CloseDate"] = pd.to_datetime(sold["CloseDate"], errors="coerce")
sold["year_month"] = sold["CloseDate"].dt.to_period("M")

#Merge
listings_with_rates = listings.merge(mortgage_monthly, on='year_month', how='left')
sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')

#Validate the merge
listings_missing_rates = listings_with_rates["rate_30yr_fixed"].isnull().sum()
sold_missing_rates = sold_with_rates["rate_30yr_fixed"].isnull().sum()
print(f"Missing mortgage rate in Listings: {listings_missing_rates}.")
print(f"Missing mortgage rate in Sold: {sold_missing_rates}.")

#Preview
print("\nListings preview:")
print(listings_with_rates[["ListingContractDate", "year_month", "ListPrice", "rate_30yr_fixed"]].head())
print("\nSold preview:")
print(sold_with_rates[["CloseDate", "ClosePrice", "year_month", "rate_30yr_fixed"]].head())

#Save files
listings_with_rates.to_csv(r"C:\Users\jjcho\OneDrive\Desktop\IDX Exchange Internship\Weekly csv files/Week 3 mortgage rates listing.csv", 
                            index=False)
sold_with_rates.to_csv(r"C:\Users\jjcho\OneDrive\Desktop\IDX Exchange Internship\Weekly csv files/Week 3 mortgage rates sold.csv", 
                            index=False)