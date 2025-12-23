import datetime
import os
import sys
import json
import pandas as pd

# Ensure we can import modules from the parent directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quant_b_module.portfolio_manager import PortfolioManager
from quant_a_module.asset_analyzer import AssetAnalyzer

def load_config():
    """
    Loads portfolio configuration from 'portfolio_config.json'.
    Returns default values if the file is missing or invalid.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portfolio_config.json")
    
    # Default Fallback (if no config file exists)
    default_tickers = ['MC.PA', 'TTE.PA', 'SAN.PA', 'AIR.PA']
    default_weights = {'MC.PA': 0.25, 'TTE.PA': 0.25, 'SAN.PA': 0.25, 'AIR.PA': 0.25}

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                tickers = config.get("tickers", default_tickers)
                weights = config.get("weights", default_weights)
                print(f"Configuration loaded from {config_path}")
                return tickers, weights
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    print("Using default portfolio configuration.")
    return default_tickers, default_weights

def calculate_max_drawdown(series):
    """Calculates Max Drawdown for the portfolio series."""
    if series.empty:
        return 0.0
    cum_ret = (1 + series.pct_change().fillna(0)).cumprod()
    running_max = cum_ret.cummax()
    drawdown = (cum_ret - running_max) / running_max
    return drawdown.min()

def generate_daily_report():
    print("--- Starting Daily Report Job ---")
    
    # 1. Load Configuration for Portfolio (Quant B)
    tickers, weights = load_config()
    
    # 2. Define Asset for Single Analysis (Quant A) - Defaulting to Bitcoin
    single_asset_ticker = "BTC-USD"

    # --- PART 1: QUANT A (Single Asset Focus) ---
    print(f"[Quant A] Analyzing asset: {single_asset_ticker}...")
    analyzer = AssetAnalyzer(single_asset_ticker)
    
    quant_a_report = ""
    try:
        # Fetch data for 1 year
        df_asset = analyzer.get_data(period="1y")
        
        # Run a simple 'Buy and Hold' strategy to extract metrics
        df_res_a = analyzer.run_strategy("Buy and Hold")
        metrics_a = analyzer.get_metrics(df_res_a)
        
        last_price = df_asset['Close'].iloc[-1]
        
        quant_a_report = (
            f"--- QUANT A: Single Asset Focus ({single_asset_ticker}) ---\n"
            f"Last Close Price     : ${last_price:,.2f}\n"
            f"Total Return (1y)    : {metrics_a.get('Total Return', 0):.2%}\n"
            f"Volatility (Ann.)    : {metrics_a.get('Volatility', 0):.2f}\n"
            f"Max Drawdown         : {metrics_a.get('Max Drawdown', 0):.2%}\n"
            f"Sharpe Ratio         : {metrics_a.get('Sharpe Ratio', 0):.2f}\n"
        )
    except Exception as e:
        quant_a_report = f"--- QUANT A: Error analyzing {single_asset_ticker} ---\nError: {str(e)}\n"
        print(f"Error in Quant A: {e}")

    # --- PART 2: QUANT B (Portfolio Management) ---
    print(f"[Quant B] Analyzing Portfolio with {len(tickers)} assets...")
    pm = PortfolioManager()
    
    quant_b_report = ""
    try:
        # Fetch data (ensure we have enough history for volatility)
        pm.fetch_data(tickers, period="1y")
        
        # Simulate portfolio using the weights from config
        sim_data = pm.simulate_portfolio(weights, rebalance_freq="Quarterly")
        
        if sim_data is not None and not sim_data.empty:
            # Calculate Metrics
            current_val = sim_data['Portfolio'].iloc[-1]
            
            if len(sim_data) >= 2:
                prev_val = sim_data['Portfolio'].iloc[-2]
                daily_perf = (current_val - prev_val) / prev_val
            else:
                daily_perf = 0.0
            
            metrics_b = pm.get_portfolio_metrics(weights, sim_data['Portfolio'])
            port_max_dd = calculate_max_drawdown(sim_data['Portfolio'])
            
            quant_b_report = (
                f"--- QUANT B: Portfolio Strategy ---\n"
                f"Assets Managed       : {len(tickers)}\n"
                f"Portfolio Value      : {current_val:.2f} (Base 100)\n"
                f"24h Performance      : {daily_perf:+.2%}\n"
                f"Annualized Volatility: {metrics_b['Volatility (Ann.)']:.2%}\n"
                f"Diversification Gain : {metrics_b['Diversification Effect']:.4f}\n"
                f"Max Drawdown         : {port_max_dd:.2%}\n"
            )
        else:
            quant_b_report = "--- QUANT B: No data available for portfolio simulation ---\n"
            
    except Exception as e:
        quant_b_report = f"--- QUANT B: Error calculating portfolio metrics ---\nError: {str(e)}\n"
        print(f"Error in Quant B: {e}")

    # --- WRITE REPORT TO LOG FILE ---
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    final_report = (
        f"\n{'='*40}\n"
        f"[{timestamp}] DAILY AUTOMATED REPORT\n"
        f"{'='*40}\n"
        f"{quant_a_report}\n"
        f"{quant_b_report}"
        f"{'='*40}\n"
    )

    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_logs.txt")
    
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(final_report)
        print(f"Report successfully appended to {log_file}")
    except Exception as e:
        print(f"File Error: {e}")
        
    print("--- Job Finished ---")

if __name__ == "__main__":
    generate_daily_report()