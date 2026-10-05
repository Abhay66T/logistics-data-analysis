"""Analyze shipment delivery performance, costs, carriers, and delays.

Run from the project directory with: python logistics_analysis.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Save charts in headless environments and CI.
import matplotlib.pyplot as plt
import pandas as pd


REQUIRED_COLUMNS = {
    "shipment_id",
    "order_date",
    "promised_delivery_date",
    "actual_delivery_date",
    "origin",
    "destination",
    "carrier",
    "shipping_cost",
    "distance_km",
}
DATE_COLUMNS = ["order_date", "promised_delivery_date", "actual_delivery_date"]
COLORS = {"Early": "#57a773", "On time": "#4c78a8", "Late": "#e45756"}


def load_and_prepare_data(input_path: Path) -> pd.DataFrame:
    """Load the CSV, validate required fields, and add analysis columns."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    data = pd.read_csv(input_path)
    missing = sorted(REQUIRED_COLUMNS - set(data.columns))
    if missing:
        raise ValueError("CSV is missing required columns: " + ", ".join(missing))
    if data.empty:
        raise ValueError("The CSV contains no shipment rows.")

    original_count = len(data)
    for column in DATE_COLUMNS:
        data[column] = pd.to_datetime(data[column], errors="coerce")
    for column in ["shipping_cost", "distance_km"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    valid = data[DATE_COLUMNS + ["shipping_cost", "distance_km", "carrier"]].notna().all(axis=1)
    valid &= data["shipping_cost"].ge(0) & data["distance_km"].gt(0)
    valid &= data["carrier"].astype(str).str.strip().ne("")
    data = data.loc[valid].copy()
    if data.empty:
        raise ValueError("No valid rows remain after checking dates, carrier, cost, and distance.")
    removed = original_count - len(data)
    if removed:
        print(f"Data quality: excluded {removed} invalid row(s).")

    data["transit_days"] = (data["actual_delivery_date"] - data["order_date"]).dt.days
    data["delay_days"] = (data["actual_delivery_date"] - data["promised_delivery_date"]).dt.days
    if data["transit_days"].lt(0).any():
        count = int(data["transit_days"].lt(0).sum())
        print(f"Data quality: excluded {count} row(s) where delivery precedes the order date.")
        data = data.loc[data["transit_days"].ge(0)].copy()
    if data.empty:
        raise ValueError("No shipments remain after checking delivery dates against order dates.")

    data["delivery_status"] = "On time"
    data.loc[data["delay_days"].lt(0), "delivery_status"] = "Early"
    data.loc[data["delay_days"].gt(0), "delivery_status"] = "Late"
    data["month"] = data["order_date"].dt.to_period("M").astype(str)
    return data


def calculate_kpis(data: pd.DataFrame) -> dict[str, float | int]:
    """Calculate headline metrics from validated shipment rows."""
    late = data.loc[data["delay_days"].gt(0), "delay_days"]
    return {
        "shipments": int(len(data)),
        "on_time_rate": float(data["delay_days"].le(0).mean()),
        "late_rate": float(data["delay_days"].gt(0).mean()),
        "average_late_days": float(late.mean()) if not late.empty else 0.0,
        "average_transit_days": float(data["transit_days"].mean()),
        "average_shipping_cost": float(data["shipping_cost"].mean()),
        "cost_per_km": float(data["shipping_cost"].sum() / data["distance_km"].sum()),
    }


def build_summaries(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return carrier and monthly performance summaries."""
    carrier = data.groupby("carrier").agg(
        shipments=("shipment_id", "count"),
        on_time_rate=("delay_days", lambda values: values.le(0).mean()),
        average_late_days=("delay_days", lambda values: values[values.gt(0)].mean()),
        average_shipping_cost=("shipping_cost", "mean"),
        average_transit_days=("transit_days", "mean"),
    ).sort_values("on_time_rate", ascending=False)
    carrier["average_late_days"] = carrier["average_late_days"].fillna(0)

    monthly = data.groupby("month").agg(
        shipments=("shipment_id", "count"),
        on_time_rate=("delay_days", lambda values: values.le(0).mean()),
        average_shipping_cost=("shipping_cost", "mean"),
    ).sort_index()
    return carrier, monthly


def make_charts(data: pd.DataFrame, carrier: pd.DataFrame, output_dir: Path) -> None:
    """Save four clearly labeled charts to the chosen output directory."""
    plt.style.use("seaborn-v0_8-whitegrid")
    output_dir.mkdir(parents=True, exist_ok=True)

    order = ["Early", "On time", "Late"]
    counts = data["delivery_status"].value_counts().reindex(order, fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(counts.index, counts.values, color=[COLORS[name] for name in order])
    ax.bar_label(bars, padding=3)
    ax.set(title="Shipment delivery outcomes", ylabel="Number of shipments", xlabel="Delivery status")
    ax.set_ylim(0, max(counts.max() * 1.18, 1))
    fig.tight_layout()
    fig.savefig(output_dir / "delivery_outcomes.png", dpi=180)
    plt.close(fig)

    carrier_plot = carrier.sort_values("on_time_rate")
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(carrier_plot.index, carrier_plot["on_time_rate"] * 100, color="#4c78a8")
    ax.bar_label(bars, fmt="%.1f%%", padding=4)
    ax.set(title="On-time delivery rate by carrier", xlabel="On-time shipments (%)", ylabel="Carrier")
    ax.set_xlim(0, 110)
    fig.tight_layout()
    fig.savefig(output_dir / "on_time_by_carrier.png", dpi=180)
    plt.close(fig)

    cost_plot = carrier.sort_values("average_shipping_cost")
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(cost_plot.index, cost_plot["average_shipping_cost"], color="#f2a541")
    ax.bar_label(bars, fmt="%.2f", padding=3)
    ax.set(title="Average shipping cost by carrier", ylabel="Average cost (dataset currency)", xlabel="Carrier")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(output_dir / "cost_by_carrier.png", dpi=180)
    plt.close(fig)

    late_days = data.loc[data["delay_days"].gt(0), "delay_days"]
    fig, ax = plt.subplots(figsize=(8, 5))
    if late_days.empty:
        ax.text(0.5, 0.5, "No late shipments in this dataset", ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    else:
        bins = range(1, int(late_days.max()) + 2)
        ax.hist(late_days, bins=bins, align="left", color="#e45756", edgecolor="white", rwidth=0.85)
        ax.set(title="Distribution of delivery delay", xlabel="Days after promised date", ylabel="Late shipments")
        ax.set_xticks(list(bins)[:-1])
    fig.tight_layout()
    fig.savefig(output_dir / "delay_distribution.png", dpi=180)
    plt.close(fig)


def write_insights(data: pd.DataFrame, carrier: pd.DataFrame, monthly: pd.DataFrame, kpis: dict, output_path: Path) -> None:
    """Write concise observations that are calculated from this dataset."""
    best = carrier["on_time_rate"].idxmax()
    costly = carrier["average_shipping_cost"].idxmax()
    slowest = carrier["average_transit_days"].idxmax()
    lines = [
        "LOGISTICS DATA ANALYSIS: BUSINESS INSIGHTS",
        "=" * 44,
        "",
        f"The dataset contains {kpis['shipments']} valid delivered shipments.",
        f"Overall on-time delivery rate: {kpis['on_time_rate']:.1%}.",
        f"Late shipment rate: {kpis['late_rate']:.1%}; average delay among late shipments: {kpis['average_late_days']:.2f} days.",
        f"Average transit time: {kpis['average_transit_days']:.2f} days.",
        f"Average shipping cost: {kpis['average_shipping_cost']:.2f} dataset currency units; cost per kilometre: {kpis['cost_per_km']:.3f}.",
        "",
        "Carrier observations:",
        f"- {best} has the highest on-time rate ({carrier.loc[best, 'on_time_rate']:.1%}) across {int(carrier.loc[best, 'shipments'])} shipments.",
        f"- {costly} has the highest average shipping cost ({carrier.loc[costly, 'average_shipping_cost']:.2f}) per shipment.",
        f"- {slowest} has the longest average transit time ({carrier.loc[slowest, 'average_transit_days']:.2f} days).",
    ]
    if len(monthly):
        weakest_month = monthly["on_time_rate"].idxmin()
        strongest_month = monthly["on_time_rate"].idxmax()
        lines += [
            "",
            "Monthly observations:",
            f"- {weakest_month} has the lowest on-time rate ({monthly.loc[weakest_month, 'on_time_rate']:.1%}) across {int(monthly.loc[weakest_month, 'shipments'])} shipments.",
            f"- {strongest_month} has the highest on-time rate ({monthly.loc[strongest_month, 'on_time_rate']:.1%}) across {int(monthly.loc[strongest_month, 'shipments'])} shipments.",
        ]
    lines += [
        "",
        "Suggested next steps:",
        "- Review late shipments by route and carrier to find recurring service gaps.",
        "- Compare cost and on-time performance together before changing carrier allocation.",
        "- Check monthly patterns with a larger sample before treating a trend as persistent.",
        "",
        "These are descriptive findings from synthetic sample data; they do not establish cause and effect.",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze shipment delivery, cost, and carrier performance.")
    parser.add_argument("--input", type=Path, default=Path(__file__).parent / "data" / "logistics_data.csv", help="Path to the shipment CSV.")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "outputs", help="Folder for charts and the insights report.")
    args = parser.parse_args()

    data = load_and_prepare_data(args.input)
    kpis = calculate_kpis(data)
    carrier, monthly = build_summaries(data)

    print("\nLOGISTICS KPIs")
    print("=" * 40)
    print(f"Shipments analyzed:             {kpis['shipments']}")
    print(f"On-time delivery rate:          {kpis['on_time_rate']:.1%}")
    print(f"Late shipment rate:             {kpis['late_rate']:.1%}")
    print(f"Average delay (late only):      {kpis['average_late_days']:.2f} days")
    print(f"Average transit time:           {kpis['average_transit_days']:.2f} days")
    print(f"Average shipping cost:          {kpis['average_shipping_cost']:.2f}")
    print(f"Shipping cost per kilometre:    {kpis['cost_per_km']:.3f}")
    print("\nCARRIER PERFORMANCE")
    print(carrier.to_string(formatters={"on_time_rate": "{:.1%}".format, "average_late_days": "{:.2f}".format, "average_shipping_cost": "{:.2f}".format, "average_transit_days": "{:.2f}".format}))
    print("\nMONTHLY PERFORMANCE")
    print(monthly.to_string(formatters={"on_time_rate": "{:.1%}".format, "average_shipping_cost": "{:.2f}".format}))

    make_charts(data, carrier, args.output)
    write_insights(data, carrier, monthly, kpis, args.output / "business_insights.txt")
    print(f"\nCharts and business insights saved to: {args.output.resolve()}")


if __name__ == "__main__":
    main()
