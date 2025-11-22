# python_git_linux_finance

# Quant B Module: Multivariate Portfolio Analysis

## Module Overview
This module is responsible for the construction, simulation, and analysis of a financial portfolio composed of multiple assets (minimum 3). It handles the "macro" view of the dashboard, allowing users to compare individual asset performance against a weighted portfolio strategy.

## Functional Requirements

### 1. Data Management
* **Multi-Asset Retrieval:** The module must handle data ingestion for at least **3 distinct assets** simultaneously (e.g., AAPL, MSFT, BTC-USD).
* **Synchronization:** Ensure time-series data for different assets are aligned (handling missing data points or different trading hours).
* **Real-time Updates:** Data must be capable of refreshing every 5 minutes to reflect current market conditions.

### 2. Mathematical Calculations
The core logic must compute the following metrics:
* **Portfolio Returns:** Cumulative returns based on user-defined weights.
* **Portfolio Volatility:** Standard deviation of the weighted portfolio.
* **Correlation Matrix:** A matrix showing the correlation coefficients between all selected assets.
* **Diversification Effects:** Analysis showing how the portfolio risk compares to individual asset risks.

### 3. Simulation & Customization
The system must allow the user to modify simulation parameters dynamically:
* **Asset Selection:** Users choose which assets to include.
* **Weighting Schemes:**
    * *Equal Weight:* (1/N) allocation.
    * *Custom Weights:* User defines specific percentages (e.g., 50% Asset A, 25% Asset B, 25% Asset C).
* **Rebalancing:** Options for rebalancing frequency (optional but recommended).

### 4. Visualization (Streamlit)
The visual output must include:
* **Main Chart:** A comparative time-series graph overlaying the **Portfolio Cumulative Return** vs. **Individual Asset Prices** (normalized).
* **Risk Analysis:** A Heatmap visualization of the Correlation Matrix.
* **Allocation:** A Pie Chart or Bar Chart showing the current asset distribution.

---

## Technical Architecture

### File Structure
Current structure for `quant_b_module/` (Branch: `feature/quant-b`):
* `portfolio_manager.py`: Class responsible for math and dataframes.
* `visualizer.py`: Functions that return Plotly/Matplotlib figures.
* `__init__.py`: Exposes the main classes to `app.py`.
* `tests/test_portfolio.py`: Unit tests for the portfolio logic.

### Input/Output Specification

**Input (from `app.py` or Data Loader):**
* `tickers`: List of strings `['AAPL', 'GOOG', 'TSLA']`
* `weights`: List of floats `[0.4, 0.4, 0.2]` (must sum to 1.0)
* `start_date`, `end_date`: Datetime objects

**Output (to Dashboard):**
* `metrics`: Dictionary `{'sharpe': 1.2, 'volatility': 0.15, 'return': 0.08}`
* `fig_performance`: Plotly Graph Object (Line chart)
* `fig_correlation`: Plotly Graph Object (Heatmap)

---

## Development Checklist (Quant B)

### Step 1: The Calculation Engine (`portfolio_manager.py`)
- [ ] Create a `Portfolio` class.
- [ ] Implement a method to download historical data for a list of tickers (using `yfinance`).
- [ ] Implement `calculate_daily_returns()`: Compute percentage change for all assets.
- [ ] Implement `calculate_portfolio_performance(weights)`:
    -   Multiply asset returns by weights.
    -   Sum weighted returns to get portfolio return.
- [ ] Implement `get_correlation_matrix()`: Use pandas `.corr()` method.

### Step 2: The Visualization Layer (`visualizer.py`)
- [ ] Create a function to plot the Correlation Heatmap (using `seaborn` or `plotly`).
- [ ] Create a function to plot Normalized Prices (rebase all assets to 100 at start date) to compare apples to apples.
- [ ] Create the main Portfolio Curve graph.

### Step 3: Integration in Dashboard
- [ ] Create a sidebar section in Streamlit for "Portfolio Config".
- [ ] Add a Multiselect widget for Tickers.
- [ ] Add Sliders for Weights (ensure they sum to 100%).
- [ ] Display the metrics and graphs.

---

## Key Formulas

**Portfolio Return ($R_p$):**
$$R_p = \sum_{i=1}^{N} w_i r_i$$

**Portfolio Variance ($\sigma_p^2$):**
$$\sigma_p^2 = \sum_{i} \sum_{j} w_i w_j \sigma_i \sigma_j \rho_{ij}$$
*Where $w$ is weight, $\sigma$ is volatility, and $\rho$ is correlation.*