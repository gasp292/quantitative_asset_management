# Quantitative Asset Management Dashboard

## Project Overview

This project is a comprehensive financial analytics platform designed to support portfolio managers with quantitative tools. Built using Python and the Streamlit framework, the application provides a unified interface for real-time market analysis, strategy backtesting, and multi-asset portfolio construction.

The platform is engineered to simulate a professional workflow, enforcing strict separation of concerns between univariate analysis (Quant A) and multivariate portfolio optimization (Quant B), while integrating them into a single cohesive dashboard. It includes features for automated daily reporting via Linux cron jobs.

## System Architecture

The application follows a modular architecture separating the frontend (visualization) from the backend (data processing and logic).

* **Frontend:** Streamlit is used for the user interface, providing interactive controls (sliders, dropdowns) and reactive components.
* **Backend:** Logic is encapsulated in object-oriented classes (`AssetAnalyzer`, `PortfolioManager`) handling API calls, mathematical computations, and Pandas DataFrame manipulations.
* **Visualization:** Plotly is used for high-performance, interactive charting (dual-axis charts, heatmaps).
* **Data Source:** Real-time financial data is retrieved via the `yfinance` API.

---

## Module Details

### 1. Quant A Module: Univariate Analysis
**Focus:** Deep dive analysis and backtesting on single assets.

This module allows users to select specific assets from various universes (Indices, Crypto, Forex) and test trading strategies against historical data.

* **Strategy Engine:**
    * **Buy and Hold:** Serves as the benchmark strategy.
    * **Momentum Strategy:** Implements a Moving Average Crossover logic. Users can dynamically adjust Short and Long windows to find optimal trend-following parameters.
    * **RSI Strategy (Mean Reversion):** Implements a contrarian strategy based on the Relative Strength Index. Users define Overbought and Oversold thresholds to trigger buy/sell signals.
* **Performance Metrics:**
    * The module calculates rigorous financial metrics including Compound Annual Growth Rate (CAGR), Sharpe Ratio (risk-adjusted return), Max Drawdown (risk exposure), and Win Rate.
* **Advanced Visualization:**
    * Interactive chart displaying the asset price versus the strategy's cumulative performance (rebased to 100).
    * Automatic detection and visualization of Buy/Sell signals (markers) directly on the price chart.

### 2. Quant B Module: Portfolio Optimization
**Focus:** Construction, simulation, and analysis of multi-asset portfolios.

This module enables the creation of diversified portfolios to analyze risk reduction and aggregate performance.

* **Asset Universes:** Built-in support for major market indices (CAC 40, DAX 40, S&P 500) and top cryptocurrencies.
* **Allocation Engine:**
    * **Equal Weighting:** Automatically distributes capital evenly across selected assets (1/N).
    * **Manual Allocation:** Allows granular control over asset weights via interactive sliders, ensuring the total allocation equals 100%.
* **Rebalancing Simulation:**
    * Users can simulate portfolio performance with different rebalancing frequencies (Monthly, Quarterly, Yearly) or drift (No Rebalancing).
* **Risk & Correlation Analysis:**
    * **Correlation Matrix:** A heatmap visualization to identify highly correlated assets and improve diversification.
    * **Diversification Gain:** Specific metric calculating the reduction in volatility achieved through portfolio effects compared to the weighted sum of individual risks.

---

## Project Structure

The repository is organized to ensure modularity and ease of maintenance.

```text
python_git_linux_finance/
│
├── app.py                      # Application Entry Point (Main Dashboard Logic)
├── requirements.txt            # Python Dependencies
├── daily_report.py             # Script for Automated Daily Reporting (Cron)
├── portfolio_config.json       # JSON persistence for portfolio settings
│
├── quant_a_module/             # [Module A] Univariate Analysis Package
│   ├── __init__.py
│   ├── asset_analyzer.py       # Backend: Data fetching, Strategy logic, Metrics
│   └── visualizer.py           # Frontend: UI rendering, Plotly charts
│
└── quant_b_module/             # [Module B] Portfolio Management Package
    ├── __init__.py
    ├── portfolio_manager.py    # Backend: Portfolio math, Rebalancing logic
    └── visualizer.py           # Frontend: Correlation heatmaps, Performance charts
