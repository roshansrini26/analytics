# Market Model – Practice Project

Builds a clean, complete market dataset (6 countries, 2018–2025, EUR million)
from two inconsistent sources, and forecasts it to 2030.

## Pipeline
1. **Inspect**: profiled units, currencies, coverage, outliers
2. **Standardise**: converted all values to EUR million (FX + unit factors)
3. **Quality checks**: flagged missing values, YoY jumps >50%, source mismatches
4. **Reconcile**: used source A (more precise) as primary; filled gaps with
   source B scaled by its typical ratio (~1.19). Used a global factor where a
   country's own ratio was too noisy (Austria) or unavailable (Denmark)
5. **Validate gap-filling**: hid known values; scaled source B was most accurate
   (MAPE 3.8%) vs driver-based (5.9%) and interpolation (7.8%)
6. **KPIs**: YoY, CAGR, per capita, market share
7. **Forecast**: backtested on 2023–2025; CAGR (3.5% MAPE) beat Holt/ETS (7.0%)
   and naive (14.7%); used CAGR for 2026–2030

## Key assumptions & limitations
- Denmark is fully estimated from source B (lower confidence for its level)
- One FX rate for all years (real pipeline: yearly average rates)
- Constant-growth forecast; doesn't model saturation or shocks
- ARIMA not used: too few annual data points

## Outputs
- `market_clean.csv`: cleaned history with `value_origin` (data lineage)
- `market_forecast.csv`: 2026–2030 forecast