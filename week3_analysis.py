from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
DATA_FILE = BASE / "data" / "logistics_data.csv"
OUT = BASE / "outputs" / "week3"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE)
for col in ["order_date", "promised_delivery_date", "actual_delivery_date"]:
    df[col] = pd.to_datetime(df[col], errors="coerce")
for col in ["shipping_cost", "distance_km"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["delivery_delay_days"] = (df["actual_delivery_date"] - df["promised_delivery_date"]).dt.days
df["on_time"] = df["delivery_delay_days"] <= 0

numeric = ["shipping_cost", "distance_km", "delivery_delay_days"]
print("Dataset shape:", df.shape)
print("\nDescriptive statistics:\n", df[numeric].describe())
print("\nCorrelation matrix:\n", df[numeric].corr())

carrier_stats = df.groupby("carrier").agg(
    shipment_count=("shipment_id", "count"),
    on_time_rate=("on_time", "mean"),
    average_delay=("delivery_delay_days", "mean"),
    average_cost=("shipping_cost", "mean")
).reset_index()
print("\nCarrier performance:\n", carrier_stats)
print("\nOverall on-time rate:", round(df["on_time"].mean() * 100, 2), "%")
print("Average delay:", round(df["delivery_delay_days"].mean(), 2), "days")
print("Average shipping cost:", round(df["shipping_cost"].mean(), 2))
print("Total shipping cost:", round(df["shipping_cost"].sum(), 2))

# 1. Delivery-delay distribution
plt.figure(figsize=(8, 5))
plt.hist(df["delivery_delay_days"].dropna(), bins=8, edgecolor="black")
plt.title("Delivery Delay Distribution")
plt.xlabel("Delay in days (negative = early)")
plt.ylabel("Number of shipments")
plt.tight_layout()
plt.savefig(OUT / "01_delivery_delay_distribution.png", dpi=160)
plt.close()

# 2. Shipping cost by carrier
plt.figure(figsize=(8, 5))
groups = [df.loc[df["carrier"] == c, "shipping_cost"].dropna() for c in sorted(df["carrier"].dropna().unique())]
plt.boxplot(groups, tick_labels=sorted(df["carrier"].dropna().unique()))
plt.title("Shipping Cost by Carrier")
plt.ylabel("Shipping cost")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(OUT / "02_shipping_cost_by_carrier.png", dpi=160)
plt.close()

# 3. On-time delivery rate by carrier
plt.figure(figsize=(8, 5))
plt.bar(carrier_stats["carrier"], carrier_stats["on_time_rate"])
plt.title("On-Time Delivery Rate by Carrier")
plt.ylabel("On-time rate")
plt.ylim(0, 1)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(OUT / "03_on_time_rate_by_carrier.png", dpi=160)
plt.close()

# 4. Distance versus shipping cost
plt.figure(figsize=(8, 5))
for carrier, group in df.groupby("carrier"):
    plt.scatter(group["distance_km"], group["shipping_cost"], label=carrier, alpha=0.8)
plt.title("Distance vs Shipping Cost")
plt.xlabel("Distance (km)")
plt.ylabel("Shipping cost")
plt.legend()
plt.tight_layout()
plt.savefig(OUT / "04_distance_vs_shipping_cost.png", dpi=160)
plt.close()

# 5. Average delay by carrier
plt.figure(figsize=(8, 5))
plt.bar(carrier_stats["carrier"], carrier_stats["average_delay"])
plt.axhline(0, color="black", linestyle="--", linewidth=1)
plt.title("Average Delivery Delay by Carrier")
plt.ylabel("Average delay (days)")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(OUT / "05_average_delay_by_carrier.png", dpi=160)
plt.close()

# 6. Correlation heatmap using Matplotlib only
corr = df[numeric].corr()
plt.figure(figsize=(7, 5))
plt.imshow(corr, vmin=-1, vmax=1)
plt.colorbar(label="Correlation")
plt.xticks(range(len(numeric)), ["Shipping cost", "Distance", "Delivery delay"], rotation=20)
plt.yticks(range(len(numeric)), ["Shipping cost", "Distance", "Delivery delay"])
for i in range(len(numeric)):
    for j in range(len(numeric)):
        plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig(OUT / "06_correlation_heatmap.png", dpi=160)
plt.close()

print(f"Six charts saved in: {OUT}")
