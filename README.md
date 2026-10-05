# Logistics Data Analysis

A beginner-friendly Python portfolio project for exploring delivery performance, shipping cost, carrier results, and delay patterns. The included shipment data is **synthetic** and contains no real customer or company information.

## What you'll learn

- Load and validate a CSV dataset with pandas.
- Calculate delivery, cost, and transit-time KPIs.
- Compare carrier performance and monthly trends.
- Create clear charts with matplotlib.
- Turn analysis into concise, data-backed business observations.

## Project structure

```text
logistics-data-analysis/
├── data/
│   └── logistics_data.csv
├── outputs/
│   └── .gitkeep
├── logistics_analysis.py
├── requirements.txt
└── README.md
```

## Run it

Use Python 3.9 or newer. From this directory, create and activate a virtual environment:

```bash
python -m venv .venv
```

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install the dependencies and run the analysis:

```bash
pip install -r requirements.txt
python logistics_analysis.py
```

The script prints KPI and carrier summaries, saves four PNG charts, and writes `outputs/business_insights.txt`. It creates the output folder if it does not exist.

You can select another input file or output folder:

```bash
python logistics_analysis.py --input path/to/shipments.csv --output path/to/results
```

## Dataset and columns

The sample has 120 synthetic delivered shipments spanning six months, with a mix of routes, carriers, costs, early arrivals, on-time arrivals, and delays. Each row is one shipment. Required input columns are:

`shipment_id`, `order_date`, `promised_delivery_date`, `actual_delivery_date`, `origin`, `destination`, `carrier`, `shipping_cost`, and `distance_km`.

Dates must be parseable by pandas; shipping cost and distance must be numeric. Invalid rows are reported and excluded. The script also rejects negative costs and non-positive distances.

## KPIs

- **On-time delivery rate:** shipments delivered on or before the promised date divided by all included shipments.
- **Late shipment rate:** shipments delivered after the promised date divided by all included shipments.
- **Average delay:** mean days late, calculated over late shipments only.
- **Average transit time:** mean days between order and actual delivery.
- **Average shipping cost:** mean shipping cost per shipment.
- **Cost per kilometre:** total cost divided by total distance.

Carrier comparisons show shipment count, on-time rate, mean delay among late shipments, average cost, and average transit time. The monthly summary tracks volume and on-time rate.

## Charts

1. Delivery outcome mix (early, on time, late).
2. On-time rate by carrier.
3. Average shipping cost by carrier.
4. Distribution of days late (late shipments only).

## Business insights and limitations

`outputs/business_insights.txt` describes patterns found in this sample, such as the strongest on-time carrier, highest average carrier cost, and the month with the lowest on-time rate. These are descriptive signals, not proof of cause. For operational decisions, validate the source data and compare like-for-like routes, service levels, shipment volumes, and seasons. The sample is synthetic and intended for learning and portfolio demonstration.
