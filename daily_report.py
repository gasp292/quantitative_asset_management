import datetime
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quant_b_module.portfolio_manager import PortfolioManager

def generate_daily_report():
    """
    Generates a text report of portfolio performance and appends it to 'daily_logs.txt'.
    Prioritizes user configuration from 'portfolio_config.json', falls back to default values.
    """
    print("--- Starting Daily Report Job ---")
    
    # Default Configuration (Fallback)
    tickers = ['MC.PA', 'TTE.PA', 'SAN.PA', 'AIR.PA']
    weights = {'MC.PA': 0.25, 'TTE.PA': 0.25, 'SAN.PA': 0.25, 'AIR.PA': 0.25}
    
    # Load User Configuration (created by the App)
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portfolio_config.json")
    
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                if "tickers" in config and "weights" in config:
                    tickers = config["tickers"]
                    weights = config["weights"]
                    print(f"Configuration loaded from '{config_file}'")
        except Exception as e:
            print(f"Error reading config file ({e}). Using default values.")
    else:
        print("No configuration file found. Using default values.")
    
    pm = PortfolioManager()
    
    # Fetch Data (3 months history for volatility calculation)
    print(f"Fetching data for {len(tickers)} assets...")
    try:
        data = pm.fetch_data(tickers, period="3mo")
    except Exception as e:
        print(f"Critical error during data fetch: {e}")
        return

    if data is None or data.empty:
        print("No data received. Please check internet connection.")
        return

    sim_data = pm.simulate_portfolio(weights, rebalance=False)
    
    # 6. Calculate Metrics
    current_value = sim_data['Portfolio'].iloc[-1]
    
    # Daily Return Calculation
    if len(sim_data) >= 2:
        yesterday_value = sim_data['Portfolio'].iloc[-2]
        daily_return = (current_value - yesterday_value) / yesterday_value
    else:
        daily_return = 0.0

    # Risk Metrics
    metrics = pm.get_portfolio_metrics(weights, sim_data['Portfolio'])
    volatility = metrics['Volatility (Ann.)']
    diversification = metrics['Diversification Effect']
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_line = (
        f"[{timestamp}] AUTOMATED REPORT\n"
        f"----------------------------------------\n"
        f"Assets count         : {len(tickers)}\n"
        f"Portfolio Value      : {current_value:.2f} (Base 100)\n"
        f"24h Performance      : {daily_return:+.2%}\n"
        f"Annualized Volatility: {volatility:.2%}\n"
        f"Diversification Gain : {diversification:.4f}\n"
        f"----------------------------------------\n\n"
    )
    
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily_logs.txt")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(report_line)
        print(f"Report successfully saved to '{log_file}'")
    except Exception as e:
        print(f"Error writing to file: {e}")

    print("--- Job Finished ---")

if __name__ == "__main__":
    generate_daily_report()