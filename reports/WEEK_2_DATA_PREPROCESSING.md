# Week 2 – Data Collection, Cleaning, and Preprocessing for Logistics Analysis

## 1. Objective

This Week 2 task focuses on preparing logistics data for reliable analysis. The workflow simulates data collection, inspects data quality, handles missing values and duplicates, detects outliers, converts data types, normalizes selected numerical features, and validates the resulting dataset.

## 2. Reference Dataset

The project uses the publicly available **DataCo Global / Smart Supply Chain Dataset** as its logistics reference. The dataset is suitable for supply-chain and delivery analysis and contains information related to orders, products, sales, shipping, delivery status, and logistics operations.

## 3. Data Collection Simulation

1. Identify the logistics business requirement.
2. Select a public supply-chain dataset.
3. Download and preserve the raw dataset.
4. Load the data using Pandas.
5. Inspect rows, columns, data types, and statistics.
6. Create a separate cleaned dataset.
7. Document every transformation for reproducibility.

## 4. Data Quality Issues

| Issue | Detection | Treatment |
|---|---|---|
| Missing values | isna().sum() | Median/mode/Unknown depending on field |
| Duplicate rows | duplicated().sum() | Remove verified exact duplicates |
| Wrong data types | info(), dtypes | Convert dates/numbers |
| Outliers | IQR method | Investigate before correction/removal |
| Inconsistent categories | unique(), value_counts() | Standardize text |
| Different numerical scales | describe() | Min-Max scaling |
| Invalid values | Business-rule checks | Correct, flag, or investigate |

## 5. Python Preprocessing Pipeline

    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler

    df = pd.read_csv("data/logistics_data.csv")
    df = df.drop_duplicates().copy()

    df["Order Date"] = pd.to_datetime(
        df["Order Date"], errors="coerce"
    )
    df["Delivery Date"] = pd.to_datetime(
        df["Delivery Date"], errors="coerce"
    )

    df["Shipping Cost"] = pd.to_numeric(
        df["Shipping Cost"], errors="coerce"
    )

    num_cols = df.select_dtypes(include="number").columns
    df[num_cols] = df[num_cols].fillna(
        df[num_cols].median()
    )

    cat_cols = df.select_dtypes(include="object").columns
    for col in cat_cols:
        mode = df[col].mode()
        df[col] = df[col].fillna(
            mode.iloc[0] if not mode.empty else "Unknown"
        )

    scale_cols = ["Shipping Cost", "Order Value"]
    scaler = MinMaxScaler()
    df[scale_cols] = scaler.fit_transform(df[scale_cols])

    df.to_csv(
        "data/logistics_data_cleaned.csv",
        index=False
    )

## 6. Missing Value Handling

Missing values are handled according to the meaning of each field. Median imputation is suitable for skewed numerical logistics variables because it is less affected by extreme values. Categorical fields can use the mode or an Unknown category. Critical fields should be investigated before removing records.

## 7. Outlier Detection

The Interquartile Range (IQR) method is used to identify unusually high or low observations.

- IQR = Q3 - Q1
- Lower Bound = Q1 - 1.5 × IQR
- Upper Bound = Q3 + 1.5 × IQR

An identified outlier is not automatically deleted. A very expensive shipment may be a genuine business transaction rather than a data error.

## 8. Normalization

Min-Max normalization converts selected numerical variables to a common range from 0 to 1:

x_scaled = (x - minimum) / (maximum - minimum)

This is useful for scale-sensitive methods such as clustering and distance-based analysis. In machine-learning workflows, the scaler should be fitted only on training data to prevent data leakage.

## 9. Validation

After preprocessing, the dataset should be checked again:

    print("Shape:", df.shape)
    print(df.isna().sum())
    print("Duplicates:", df.duplicated().sum())
    print(df.dtypes)
    print(df.describe())

## 10. Impact on Logistics Analytics

Data quality directly affects logistics KPIs and business decisions. Duplicate shipments can inflate shipment counts and costs. Incorrect dates can produce false delivery delays. Missing values can reduce reliability, while extreme unexamined values can distort averages and models.

A structured preprocessing pipeline therefore improves confidence in delivery KPIs, carrier comparisons, dashboards, forecasting, clustering, regression, and optimization.

## 11. Future Scope

- Regression-based delivery-delay prediction
- Clustering of shipments or customers
- Route and resource optimization
- Demand forecasting
- Anomaly detection
- Interactive logistics dashboards

## 12. Conclusion

The Week 2 task establishes a reproducible data-preparation workflow for logistics analytics. Data collection, cleaning, missing-value treatment, duplicate handling, outlier detection, type conversion, normalization, and validation are essential before performing advanced analysis. High-quality data provides a stronger foundation for reliable logistics insights and data-driven decision-making.

**Author:** Abhay Tiwari  
**Project:** Logistics Data Analysis  
**GitHub:** https://github.com/Abhay66T/logistics-data-analysis
