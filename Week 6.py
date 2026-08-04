import pandas as pd
import numpy as np
from pathlib import Path

data_folder = Path(r"C:\Users\jjcho\OneDrive\Desktop\IDX Exchange Internship\Weekly csv files")

sold_file = data_folder / "Week 4-5 sold.csv"
listings_file = data_folder / "Week 4-5 listing.csv"

sold = pd.read_csv(sold_file, low_memory=False, encoding="utf-8")
listings = pd.read_csv(listings_file, low_memory=False, encoding="utf-8")

#Helper function for division
def division(numerator, denominator):
    return np.where(denominator.notnull() & (denominator != 0), numerator / denominator, np.nan)


#Engineered metrics
if "ClosePrice" in sold.columns and "OriginalListPrice" in sold.columns:
    sold["PriceRatio"] = division(sold["ClosePrice"], sold["OriginalListPrice"])
else:
    sold["PriceRatio"] = np.nan


if "ClosePrice" in sold.columns and "OriginalListPrice" in sold.columns:
    sold["CloseToOriginalListRatio"] = division( sold["ClosePrice"], sold["OriginalListPrice"])
else:
    sold["CloseToOriginalListRatio"] = np.nan


if "ClosePrice" in sold.columns and "LivingArea" in sold.columns:
    sold["PricePerSqFt"] = division(sold["ClosePrice"], sold["LivingArea"])
else:
    sold["PricePerSqFt"] = np.nan

date_columns = ["CloseDate", "PurchaseContractDate", "ListingContractDate",]
for col in date_columns:
    if col in sold.columns:
        sold[col] = pd.to_datetime(sold[col], format="mixed", errors="coerce")

if "CloseDate" in sold.columns:
    sold["Year"] = sold["CloseDate"].dt.year
    sold["Month"] = sold["CloseDate"].dt.month
    sold["YrMo"] = sold["CloseDate"].dt.to_period("M").astype(str)
else:
    sold["Year"] = np.nan
    sold["Month"] = np.nan
    sold["YrMo"] = np.nan


if "PurchaseContractDate" in sold.columns and "ListingContractDate" in sold.columns:
    sold["ListingToContractDays"] = (sold["PurchaseContractDate"] - sold["ListingContractDate"]).dt.days
else:
    sold["ListingToContractDays"] = np.nan


if "CloseDate" in sold.columns and "PurchaseContractDate" in sold.columns:
    sold["ContractToCloseDays"] = (sold["CloseDate"] - sold["PurchaseContractDate"]).dt.days
else:
    sold["ContractToCloseDays"] = np.nan


#Group PropertyType and PropertySubType
required_group_cols = ["PropertyType", "PropertySubType"]

if all(col in sold.columns for col in required_group_cols):
    propertytype_group_propertysubtype = (
        sold.groupby(["PropertyType", "PropertySubType"])
        .agg(
            SoldCount=("ClosePrice", "count"),
            MedianClosePrice=("ClosePrice", "median"),
            AverageClosePrice=("ClosePrice", "mean"),
            MedianPriceRatio=("PriceRatio", "median"),
            AveragePricePerSqFt=("PricePerSqFt", "mean"),
            MedianDaysOnMarket=("DaysOnMarket", "median"),
            AverageListingToContractDays=("ListingToContractDays", "mean"),
            AverageContractToCloseDays=("ContractToCloseDays", "mean")
        )
        .reset_index()
        
    )
else:
    propertytype_group_propertysubtype = pd.DataFrame()

print(propertytype_group_propertysubtype.head(20))


#Group CountyOrParish and MLSAreaMajor

required_group_cols = ["CountyOrParish", "MLSAreaMajor"]

if all(col in sold.columns for col in required_group_cols):
    countyorparish_group_mlsareamajor = (
        sold.groupby(["CountyOrParish", "MLSAreaMajor"])
        .agg(
            SoldCount=("ClosePrice", "count"),
            MedianClosePrice=("ClosePrice", "median"),
            AverageClosePrice=("ClosePrice", "mean"),
            MedianPriceRatio=("PriceRatio", "median"),
            AveragePricePerSqFt=("PricePerSqFt", "mean"),
            MedianDaysOnMarket=("DaysOnMarket", "median"),
            AverageListingToContractDays=("ListingToContractDays", "mean"),
            AverageContractToCloseDays=("ContractToCloseDays", "mean")
        )
        .reset_index())
else:
    countyorparish_group_mlsareamajor = pd.DataFrame()

print(countyorparish_group_mlsareamajor.head(20))
