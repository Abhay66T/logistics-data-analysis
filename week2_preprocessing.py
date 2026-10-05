"""
Week 2 - Data Collection, Cleaning and Preprocessing
Logistics Data Analysis Project

This script:
1. Loads the logistics dataset.
2. Checks missing values and duplicates.
3. Converts date and numeric columns to correct data types.
4. Creates delivery delay days.
5. Detects outliers in shipping cost and distance using IQR.
6. Handles outliers by capping them to IQR limits.
7. Applies Min-Max normalization to numeric analysis features.
8. Saves the cleaned and normalized dataset.
"""

from pathlib import Path
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
INPUT_FILE = DATA_DIR / "logistics_data.csv"
OUTPUT_FILE = OUTPUT_DIR / "logistics_data_preprocessed.csv"

OUTPUT_DIR.mkdir(exist_ok=True)

# 1. Load data
df = pd.read_csv(INPUT_FILE)
print("Original shape:", df.shape)

# 2. Remove duplicate records
duplicates = df.duplicated().sum()
df = df.drop_duplicates().copy()
print("Duplicates removed:", duplicates)

# 3. Convert dates
date_columns = ["order_date", "promised_delivery_date", "actual_delivery_date"]
for column in date_columns:
    df[column] = pd.to_datetime(df[column], errors="coerce")

# 4. Convert numeric columns
numeric_columns = ["shipping_cost", "distance_km"]
for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# 5. Handle missing values
for column in date_columns:
    df[column] = df[column].fillna(df[column].median())

for column in numeric_columns:
    df[column] = df[column].fillna(df[column].median())

for column in ["origin", "destination", "carrier"]:
    df[column] = df[column].fillna("Unknown")

# 6. Create delivery delay feature
df["delivery_delay_days"] = (
    df["actual_delivery_date"] - df["promised_delivery_date"]
).dt.days

# 7. IQR outlier detection and capping
def cap_outliers(dataframe, column):
    q1 = dataframe[column].quantile(0.25)
    q3 = dataframe[column].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = ((dataframe[column] < lower) | (dataframe[column] > upper)).sum()
    dataframe[column] = dataframe[column].clip(lower=lower, upper=upper)

    print(f"{column}: {outliers} outliers handled")
    return dataframe

for column in ["shipping_cost", "distance_km"]:
    df = cap_outliers(df, column)

# 8. Min-Max normalization
scaler = MinMaxScaler()
features_to_normalize = [
    "shipping_cost",
    "distance_km",
    "delivery_delay_days",
]

df[[f"{column}_normalized" for column in features_to_normalize]] = scaler.fit_transform(
    df[features_to_normalize]
)

# 9. Final validation
print("\nMissing values after preprocessing:")
print(df.isnull().sum())

print("\nFinal shape:", df.shape)
print("\nPreview:")
print(df.head())

# 10. Save output
df.to_csv(OUTPUT_FILE, index=False)
print(f"\nPreprocessed dataset saved to: {OUTPUT_FILE}")
