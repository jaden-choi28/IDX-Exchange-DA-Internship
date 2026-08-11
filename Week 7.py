import pandas as pd
import numpy as np
from pathlib import Path

data_folder = Path(r"C:\Users\jjcho\OneDrive\Desktop\IDX Exchange Internship\Weekly csv files")

sold_file = data_folder / "Week 4-5 sold.csv"
sold = pd.read_csv(sold_file, low_memory=False, encoding="utf-8")

#Convert numeric columns
num_col = ["ClosePrice", "LivingArea", "DaysOnMarket"]
for col in num_col:
    sold[col] = pd.to_numeric(sold[col], errors = "coerce")

#Business Rule Flags
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

#Apply IQR function to numeric col
for col in num_col:
    sold = add_iqr_outlier_flag(sold, col)

#Combine any IQR flags into one column for easy filtering
outlier_flag_columns = [col for col in sold.columns if col.endswith("_iqr_outlier_flag")]
sold["any_iqr_outlier_flag"] = sold[outlier_flag_columns].any(axis=1)
sold["remove_from_filtered_dataset_flag"] = (sold["business_rule_invalid_flag"] | sold["any_iqr_outlier_flag"])

#Now filter with IQR
sold_filtered = sold[sold["remove_from_filtered_dataset_flag"] == False].copy()

#Before and After filter summary
print("\nOutlier detection results:")
print(f"Original sold rows: {len(sold):,}")
print(f"Filtered sold rows: {len(sold_filtered):,}")
print(f"Rows removed from filtered dataset: {len(sold) - len(sold_filtered):,}")

#Median summary
comparison_rows = []

for col in num_col:
    if col in sold.columns:
        before_median = sold[col].median()
        after_median = sold_filtered[col].median()

        comparison_rows.append(
            {
                "Metric": col,
                "BeforeMedian": before_median,
                "AfterMedian": after_median,
                "MedianChange": after_median - before_median,
            }
        )

comparison_df = pd.DataFrame(comparison_rows)
print("\nMedian comparison before and after filtering:")
print(comparison_df)

#Save CSVs
sold.to_csv(data_folder / "Week 7 sold flagged dataset.csv", index=False)
sold_filtered.to_csv(data_folder / "Week 7 sold IQR filtered dataset.csv", index=False)
