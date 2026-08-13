import pandas as pd
import numpy as np
from pathlib import Path

data_folder = Path(r"C:\Users\jjcho\OneDrive\Desktop\IDX Exchange Internship\Weekly csv files")

sold_file = data_folder / "Week 4-5 sold.csv"
listing_file = data_folder / "Week 4-5 listing.csv"
sold = pd.read_csv(sold_file, low_memory=False, encoding="utf-8")
listing = pd.read_csv(listing_file, low_memory=False, encoding="utf-8")

#Convert numeric columns
num_col = ["ClosePrice", "LivingArea", "DaysOnMarket"]
for col in num_col:
    sold[col] = pd.to_numeric(sold[col], errors = "coerce")
    listing[col] = pd.to_numeric(listing[col], errors = "coerce")


#Define IQR function
def add_iqr_outlier_flag(df, column_name):
    flag_col = f"{column_name}_iqr_outlier_flag"

    if column_name not in df.columns:
        df[flag_col] = False
        return df, None

    valid_values = df[column_name].dropna()

    q1 = valid_values.quantile(0.25)
    q3 = valid_values.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    df[flag_col] = (df[column_name].notnull() & ((df[column_name] < lower_bound) | (df[column_name] > upper_bound)))
    return df

#Business Rule Flags for sold
sold["invalid_close_price_flag"] = False
sold["invalid_living_area_flag"] = False
sold["invalid_days_on_market_flag"] = False

if "ClosePrice" in sold.columns:
    sold["invalid_close_price_flag"] = sold["ClosePrice"].notnull() & (sold["ClosePrice"] <= 0)

if "LivingArea" in sold.columns:
    sold["invalid_living_area_flag"] = sold["LivingArea"].notnull() & (sold["LivingArea"] <= 0)

if "DaysOnMarket" in sold.columns:
    sold["invalid_days_on_market_flag"] = sold["DaysOnMarket"].notnull() & (sold["DaysOnMarket"] < 0)

#Add a extra column for a general business rule flag if any col flags true
sold["business_rule_invalid_flag"] = (sold["invalid_close_price_flag"] | sold["invalid_living_area_flag"] | sold["invalid_days_on_market_flag"])

#Apply IQR function to numeric col
for col in num_col:
    sold = add_iqr_outlier_flag(sold, col)

#Combine any IQR flags into one column for easy filtering
outlier_flag_columns = [col for col in sold.columns if col.endswith("_iqr_outlier_flag")]
sold["any_iqr_outlier_flag"] = sold[outlier_flag_columns].any(axis=1)
sold["remove_from_filtered_dataset_flag"] = (sold["business_rule_invalid_flag"] | sold["any_iqr_outlier_flag"])

#Now filter with IQR
sold_filtered = sold[sold["remove_from_filtered_dataset_flag"] == False].copy()

#Business Rule Flags for listing
listing["invalid_close_price_flag"] = False
listing["invalid_living_area_flag"] = False
listing["invalid_days_on_market_flag"] = False

if "ClosePrice" in listing.columns:
    listing["invalid_close_price_flag"] = listing["ClosePrice"].notnull() & (listing["ClosePrice"] <= 0)

if "LivingArea" in listing.columns:
    listing["invalid_living_area_flag"] = listing["LivingArea"].notnull() & (listing["LivingArea"] <= 0)

if "DaysOnMarket" in listing.columns:
    listing["invalid_days_on_market_flag"] = listing["DaysOnMarket"].notnull() & (listing["DaysOnMarket"] < 0)

#Add a extra column for a general business rule flag if any col flags true
listing["business_rule_invalid_flag"] = (listing["invalid_close_price_flag"] | listing["invalid_living_area_flag"] | listing["invalid_days_on_market_flag"])

#Apply IQR function to numeric col
for col in num_col:
    listing = add_iqr_outlier_flag(listing, col)

#Combine any IQR flags into one column for easy filtering
outlier_flag_columns = [col for col in listing.columns if col.endswith("_iqr_outlier_flag")]
listing["any_iqr_outlier_flag"] = listing[outlier_flag_columns].any(axis=1)
listing["remove_from_filtered_dataset_flag"] = (listing["business_rule_invalid_flag"] | listing["any_iqr_outlier_flag"])

#Now filter with IQR
listing_filtered = listing[listing["remove_from_filtered_dataset_flag"] == False].copy()


#Before and After filter summary
print("\nOutlier detection results:")
print(f"Original sold rows: {len(listing):,}")
print(f"Filtered sold rows: {len(listing_filtered):,}")
print(f"Rows removed from filtered dataset: {len(listing) - len(listing_filtered):,}")

#Median summary for sold
comparison_rows_sold = []

for col in num_col:
    if col in sold.columns:
        before_median = sold[col].median()
        after_median = sold_filtered[col].median()

        comparison_rows_sold.append(
            {
                "Metric": col,
                "BeforeMedian": before_median,
                "AfterMedian": after_median,
                "MedianChange": after_median - before_median,
            }
        )

comparison_sold_df = pd.DataFrame(comparison_rows_sold)
print("\nMedian comparison before and after filtering for sold:")
print(comparison_sold_df)

#Median summary for Listing
comparison_rows_listing = []

for col in num_col:
    if col in listing.columns:
        before_median = listing[col].median()
        after_median = listing_filtered[col].median()

        comparison_rows_listing.append(
            {
                "Metric": col,
                "BeforeMedian": before_median,
                "AfterMedian": after_median,
                "MedianChange": after_median - before_median,
            }
        )

comparison_listing_df = pd.DataFrame(comparison_rows_listing)
print("\nMedian comparison before and after filtering for listing:")
print(comparison_listing_df)

#Save CSVs
sold.to_csv(data_folder / "Week 7 sold flagged dataset.csv", index=False)
sold_filtered.to_csv(data_folder / "Week 7 sold IQR filtered dataset.csv", index=False)
listing.to_csv(data_folder / "Week 7 listing flagged dataset.csv", index=False)
listing_filtered.to_csv(data_folder / "Week 7 listing IQR filtered dataset.csv", index=False)