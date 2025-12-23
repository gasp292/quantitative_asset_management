# Quantitative Asset Management Dashboard

## Project Overview

This project was developed as part of a quantitative research simulation for an asset management company in Paris. The objective is to support fundamental portfolio managers by providing a professional, integrated dashboard for real-time financial analysis and strategy backtesting.

The platform is built using **Python** (Streamlit) and follows a modular architecture developed through collaborative **Git** workflows and deployed on a **Linux** environment.

## Live Access

The application is deployed on an AWS Linux instance and is accessible 24/7 at the following address:
**[http://16.171.154.146:8501/](http://16.171.154.146:8501/)** 

---

## Key Features

### 1. Real-Time Data Integration

* **Continuous Retrieval:** The dashboard retrieves financial data from dynamic sources like market prices and crypto indicators.


* **Auto-Refresh:** Data updates automatically every 5 minutes to ensure the most current market view.


* **Persistent Storage:** User configurations and portfolio weights are saved locally via JSON for session continuity.

### 2. Quant A: Single Asset Analysis

* **Focus:** Detailed analysis of one main asset at a time.


* **Backtesting:** Implementation of strategies such as Buy-and-Hold and Momentum.


* **Metrics:** Real-time display of Max Drawdown, Sharpe Ratio, and volatility.


* **Visualization:** Interactive charts comparing raw asset prices with cumulative strategy performance.



### 3. Quant B: Portfolio Management

* **Multi-Asset Support:** Management of at least 3 different assets simultaneously.


* **Custom Allocation:** User-defined weights or automated Equal Weighting with real-time normalization.


* **Risk Metrics:** Advanced correlation matrices, diversification effect calculations, and portfolio volatility tracking.


* **Strategy Simulation:** Configurable rebalancing frequencies (Monthly, Quarterly, Yearly).



---

## Project Structure

The repository is structured to maintain a clear separation between the two core modules while ensuring seamless integration.

```text
quantitative_asset_management/
├── quant_a_module/             # Single Asset Analysis Module - IMPORTED FROM BRANCH QUANT-A AND TESTED ON BRANCH DEV
│   ├── asset_analyzer.py       # Backtesting and strategy logic
│   └── visualizer.py           # Quant A specific charting components
├── quant_b_module/             # Multi-Asset Portfolio Module - IMPORTED FROM BRANCH QUANT-B AND TESTED ON BRANCH DEV
│   ├── portfolio_manager.py    # Portfolio simulation and metrics
│   └── visualizer.py           # Heatmaps and portfolio performance charts
├── app.py                      # Main Streamlit dashboard entry point 
├── daily_report.py             # Script for automated daily reporting 
├── data_loader.py              # Data fetching utilities
├── portfolio_config.json       # Persistent user settings
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation

```

---

## Automation (Daily Report)

A daily report is automatically generated at **8:00 PM** via a Cron job. The report is appended to `daily_logs.txt` and includes:

1. **Quant A (Single Asset):** Analysis of **BTC-USD** (Bitcoin) including Last Price, Volatility, and Sharpe Ratio.
2. **Quant B (Portfolio):** Performance of the user's current portfolio (loaded from `portfolio_config.json`), including 24h Performance, Total Value, and Max Drawdown.

**Cron Configuration:**

```bash
# Run daily at 20:00
0 20 * * * /usr/bin/python3 /path/to/project/daily_report.py

```

Note: The script and configuration are stored locally on the VM.

---

## Local Installation

1. **Clone the Repository:**
```bash
git clone https://github.com/gasp292/quantitative_asset_management.git
cd quantitative_asset_management

```


2. **Setup Environment:**
```bash
pip install -r requirements.txt

```


3. **Run the Dashboard:**
```bash
streamlit run app.py

```
