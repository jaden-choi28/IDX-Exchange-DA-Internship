import pandas as pd
from pathlib import Path
import geopandas as gpd

data_folder = Path(r"C:\Users\jjcho\OneDrive\Desktop\IDX Exchange Internship\Weekly csv files")

listings_file = data_folder / "Week 3 mortgage rates listing.csv"
sold_file = data_folder / "Week 3 mortgage rates sold.csv"
school_file = data_folder / "school_district_mapping.geojson"

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

###School Coordinate Mapping
schools = gpd.read_file(school_file, low_memory=False, encoding="utf-8")

#Filter to only unified
school_unified_only = schools[schools["DistrictType"] == "Unified"].copy()

#Convert list to GeoDataFrame
list_to_geo = gpd.GeoDataFrame(listings, geometry=gpd.points_from_xy(listings["Longitude"], listings["Latitude"]), crs="EPSG:4326")
school_unified_only = school_unified_only.to_crs(list_to_geo.crs)

list_to_geo = gpd.sjoin(list_to_geo, school_unified_only[["DistrictName", "geometry"]], how="left", predicate="within")
list_to_geo = list_to_geo.drop(columns="index_right")
list_to_geo = list_to_geo.rename(columns={"DistrictName": "NearestUnifiedSchoolDistrict"})

#Number of unmatched listing properties
list_to_geo["NearestUnifiedSchoolDistrict"].isna().sum()

#Repeat for sold
sold_to_geo = gpd.GeoDataFrame(sold, geometry=gpd.points_from_xy(sold["Longitude"], sold["Latitude"]), crs="EPSG:4326")
school_unified_only = school_unified_only.to_crs(sold_to_geo.crs)

sold_to_geo = gpd.sjoin(sold_to_geo, school_unified_only[["DistrictName", "geometry"]], how="left", predicate="within")

sold_to_geo = sold_to_geo.drop(columns="index_right")
sold_to_geo = sold_to_geo.rename(columns={"DistrictName": "NearestUnifiedSchoolDistrict"})
sold_to_geo["NearestUnifiedSchoolDistrict"].isna().sum()

#Columns that are redundant or unnecessary 
columns_to_drop = ["ListAgentEmail", "OriginatingSystemName", "OriginatingSystemSubName", "Latitude.1", "Longitude.1", "CloseDate.1", "BuyerOfficeName.1", "BuyerAgencyCompensationType"]

listings_drop_cols = [col for col in columns_to_drop if col in list_to_geo.columns]
sold_drop_cols = [col for col in columns_to_drop if col in sold_to_geo.columns]

listings = list_to_geo.drop(columns=listings_drop_cols)
sold = sold_to_geo.drop(columns=sold_drop_cols)

print("\nDropped columns:")
print("Listings:", listings_drop_cols)
print("Sold:", sold_drop_cols)

#Date Consistency Checks
def date_consistency_check(df):
    if "ListingContractDate" in df.columns and "CloseDate" in df.columns:
        df["listing_after_close_flag"] = (
            df["ListingContractDate"].notnull()
            & df["CloseDate"].notnull()
            & (df["ListingContractDate"] > df["CloseDate"])
        )
    else:
        df["listing_after_close_flag"] = False

    if "PurchaseContractDate" in df.columns and "CloseDate" in df.columns:
        df["purchase_after_close_flag"] = (
            df["PurchaseContractDate"].notnull()
            & df["CloseDate"].notnull()
            & (df["PurchaseContractDate"] > df["CloseDate"])
        )
    else:
        df["purchase_after_close_flag"] = False

    if "ListingContractDate" in df.columns and "PurchaseContractDate" in df.columns:
        listing_after_purchase = (
            df["ListingContractDate"].notnull()
            & df["PurchaseContractDate"].notnull()
            & (df["ListingContractDate"] > df["PurchaseContractDate"])
        )
    else:
        listing_after_purchase = False

    df["negative_timeline_flag"] = (
        df["listing_after_close_flag"]
        | df["purchase_after_close_flag"]
        | listing_after_purchase
    )

    return df


listings = date_consistency_check(listings)
sold = date_consistency_check(sold)

#Geographic quality check
def geographic_quality_check(df):
    if "Latitude" in df.columns and "Longitude" in df.columns:
        df["missing_coordinates_flag"] = (
            df["Latitude"].isnull()
            | df["Longitude"].isnull()
        )

        df["zero_coordinates_flag"] = (
            (df["Latitude"] == 0)
            | (df["Longitude"] == 0)
        )

        df["positive_longitude_flag"] = df["Longitude"] > 0

        df["implausible_coordinates_flag"] = (
            (df["Latitude"] < 32)
            | (df["Latitude"] > 42)
            | (df["Longitude"] < -125)
            | (df["Longitude"] > -114)
        )
    else:
        df["missing_coordinates_flag"] = True
        df["zero_coordinates_flag"] = False
        df["positive_longitude_flag"] = False
        df["implausible_coordinates_flag"] = False

    return df


listings = geographic_quality_check(listings)
sold = geographic_quality_check(sold)

#Invalid numeric check
def invalid_numeric_check(df, dataset_type):
    invalid_checks = []

    if dataset_type == "listings" and "ListPrice" in df.columns:
        invalid_checks.append(df["ListPrice"] <= 0)

    if dataset_type == "sold" and "ClosePrice" in df.columns:
        invalid_checks.append(df["ClosePrice"] <= 0)

    if "LivingArea" in df.columns:
        invalid_checks.append(df["LivingArea"] <= 0)

    if "DaysOnMarket" in df.columns:
        invalid_checks.append(df["DaysOnMarket"] < 0)

    if "BedroomsTotal" in df.columns:
        invalid_checks.append(df["BedroomsTotal"] < 0)

    bathroom_columns = [
        "BathroomsTotalInteger",
        "BathroomsFull",
        "BathroomsHalf"
    ]

    for col in bathroom_columns:
        if col in df.columns:
            invalid_checks.append(df[col] < 0)

    if invalid_checks:
        df["invalid_numeric_flag"] = invalid_checks[0]

        for check in invalid_checks[1:]:
            df["invalid_numeric_flag"] = df["invalid_numeric_flag"] | check
    else:
        df["invalid_numeric_flag"] = False

    return df


listings = invalid_numeric_check(listings, "listings")
sold = invalid_numeric_check(sold, "sold")


#Remove invalid numeric rows
listings_before_numeric_filter = len(listings)
sold_before_numeric_filter = len(sold)

listings_cleaned = listings[listings["invalid_numeric_flag"] == False].copy()
sold_cleaned = sold[sold["invalid_numeric_flag"] == False].copy()

print("\nRows removed due to invalid numeric values:")
print(f"Listings removed: {listings_before_numeric_filter - len(listings_cleaned):,}")
print(f"Sold removed: {sold_before_numeric_filter - len(sold_cleaned):,}")


#Summary of validations
def print_quality_summary(df, dataset_name):
    print(f"\n{dataset_name} quality summary")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {df.shape[1]}")

    print("\nDate consistency flag counts:")
    print("listing_after_close_flag:", df["listing_after_close_flag"].sum())
    print("purchase_after_close_flag:", df["purchase_after_close_flag"].sum())
    print("negative_timeline_flag:", df["negative_timeline_flag"].sum())

    print("\nGeographic flag counts:")
    print("missing_coordinates_flag:", df["missing_coordinates_flag"].sum())
    print("zero_coordinates_flag:", df["zero_coordinates_flag"].sum())
    print("positive_longitude_flag:", df["positive_longitude_flag"].sum())
    print("implausible_coordinates_flag:", df["implausible_coordinates_flag"].sum())

    print("\nInvalid numeric flag count:")
    print("invalid_numeric_flag:", df["invalid_numeric_flag"].sum())

    print("\nNearest school district missing count:")
    print(df["NearestUnifiedSchoolDistrict"].isnull().sum())

    print("\nData type confirmations:")
    print(df.dtypes)


print_quality_summary(listings_cleaned, "Listings")
print_quality_summary(sold_cleaned, "Sold")

#Save files
listings_cleaned.to_csv(data_folder / "Week 4-5 listing.csv",index=False)
sold_cleaned.to_csv(data_folder / "Week 4-5 sold.csv",index=False)