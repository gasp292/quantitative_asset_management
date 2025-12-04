# Quantitative Finance Dashboard - Quant A Module Documentation

This document summarizes the development steps and key features implemented for the Univariate Analysis Module (Quant A).

## 1. Project Setup and Dependencies

The project is structured with separate backend and frontend logic to ensure modularity.

### Dependencies
The following core libraries are required (see `requirements.txt`):
* `streamlit` (Frontend UI)
* `pandas` / `numpy` (Data Processing)
* `yfinance` (Data Source)
* `plotly` (Advanced Charts)
* `statsmodels` (ARIMA Forecasting)

## 2. Module Architecture (quant_a_module)

The module is built around the AssetAnalyzer class, which separates data fetching from visualization.

### Backend (asset_analyzer.py)
* **AssetAnalyzer Class:** Manages the entire analysis workflow for a single asset.
* **Data Retrieval:** Implemented the `get_data` method to fetch historical price data via yfinance, including interactive period selection. Includes data cleaning (NaN removal, returns calculation).
* **Strategy Engine:** Implemented the `run_strategy` method to backtest two core strategies:
    * **Buy and Hold:** Serves as the benchmark.
    * **Momentum (SMA Crossover):** Generates buy/sell signals based on short/long moving averages.
    * **RSI Strategy:** Added the Relative Strength Index (RSI) strategy to trade oversold/overbought conditions.
* **Core Metrics:** Implemented the `get_metrics` method to calculate and return essential performance statistics as raw floats:
    * Sharpe Ratio, Max Drawdown.
    * CAGR (Annualized Return), Volatility, and Win Rate.
* **Bonus Feature (AI):** Implemented the `get_forecast` method using the **ARIMA (1,1,1) model** to generate a 30-day price prediction, fulfilling the ML bonus requirement.

### Frontend (visualizer.py)
* **User Interface:** Implemented the `display_quant_a` function to set up interactive controls (ticker, period, strategy selection, parameter inputs) using Streamlit.
* **Data Display:** Displays 5 key metrics (Total Return, CAGR, Sharpe, Drawdown, Win Rate).
* **Advanced Charting:** Utilized Plotly to create a main chart featuring:
    * A **Dual Y-Axis** to simultaneously display Asset Price ($) and Strategy Value (Base 100).
    * **Trade Markers:** Green triangles (Buy) and Red triangles (Sell) are plotted on the chart to visualize the strategy's decision points.
    * **AI Forecast Trace:** The ARIMA prediction is overlaid as a dashed line on the asset price axis.

## 3. Execution

The entire dashboard is launched from the root:
```bash
streamlit run app.py