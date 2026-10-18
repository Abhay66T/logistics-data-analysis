# Predictive Modeling and Optimization in Logistics Systems

Forecasts **delivery time (hours)** on a simulated 5,000-shipment dataset and uses the
predictions to optimize vehicle assignment.

## Pipeline
1. Simulate shipment data (distance, weight, stops, traffic, weather, hour, vehicle type, warehouse load)
2. Prepare features (median imputation, one-hot encoding, rush-hour flag, distance x traffic)
3. Compare Linear Regression, Decision Tree, Random Forest, Gradient Boosting (5-fold CV)
4. Tune Gradient Boosting with randomized search
5. SLA-risk alert (12 h SLA)
6. Optimize: linear program assigning shipments to van/truck/bike at minimum cost
7. What-if: shift rush-hour dispatches off-peak

## Results (seed 42)
| Metric | Tuned Gradient Boosting |
|---|---|
| RMSE | 0.67 hr |
| MAE | 0.50 hr |
| R2 | 0.986 |

- SLA alert: recall 1.00, precision 0.76
- Vehicle assignment: about 40% lower simulated cost than naive assignment
- Rush-hour shift: about 1.3 hr saved per affected shipment

*Data is simulated and cost rates are assumptions; results illustrate the method.*

## Run
```bash
pip install -r requirements.txt
python logistics_delivery_model.py
```
