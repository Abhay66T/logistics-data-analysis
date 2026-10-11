# Week 3 — Advanced Data Analysis and Visualization in Logistics

**Author:** Abhay Tiwari  
**Repository:** https://github.com/Abhay66T/logistics-data-analysis

## Objective
Explore the logistics shipment dataset using Python, calculate descriptive statistics and correlations, visualize delivery and cost patterns, and derive practical recommendations.

## Dataset
The project dataset contains shipment ID, order date, promised and actual delivery dates, origin, destination, carrier, shipping cost, and distance in kilometres. The script creates two analytical features:
- `delivery_delay_days`: actual delivery date minus promised delivery date.
- `on_time`: true when delay is zero or negative.

## EDA methods
The script prints dataset shape, descriptive statistics (count, mean, standard deviation, minimum, quartiles and maximum), a correlation matrix, carrier-level shipment counts, on-time rates, average delays and average costs.

## Visualizations
1. **Delivery-delay histogram:** shows the distribution of early, on-time and late shipments.
2. **Shipping-cost box plot by carrier:** compares medians, spread and potential unusually high or low costs.
3. **On-time rate by carrier:** compares delivery reliability across carriers.
4. **Distance vs shipping-cost scatter plot:** explores whether longer distances are associated with higher costs.
5. **Average delay by carrier:** helps identify carriers that may need a service review.
6. **Correlation heatmap:** summarizes linear relationships among shipping cost, distance and delivery delay.

## Interpretation and recommendations
Use the charts together rather than judging a carrier from one metric alone. Investigate repeated delays by carrier and route, monitor cost per kilometre, and inspect high-cost shipments before changing pricing. Correlation does not prove causation; factors such as shipment weight, traffic, weather, fuel prices and route type are not included in the current dataset.

## Run the analysis
From the repository root, install dependencies and run:

```bash
pip install -r requirements.txt
python week3_analysis.py
```

The script saves six PNG charts in `outputs/week3/`. The output folder is created automatically. Results should be interpreted as exploratory findings from the project dataset, not as proof of causation.
