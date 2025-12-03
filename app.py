import streamlit as st
import pandas as pd
import time
import json
import os

# Import local modules
from quant_b_module.portfolio_manager import PortfolioManager
from quant_b_module.visualizer import Visualizer

# Import Quant A module safely
try:
    from quant_a_module.visualizer import display_quant_a
    QUANT_A_AVAILABLE = True
except ImportError as e:
    QUANT_A_AVAILABLE = False

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Quant Dashboard", layout="wide")

# --- CORE FEATURE 5: AUTO-REFRESH (Every 5 minutes = 300s) ---
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 300:
    st.session_state.last_refresh = time.time()
    st.rerun()

st.title("Asset Management Dashboard")
st.caption(f"Last updated: {time.strftime('%H:%M:%S')} (Auto-refreshes every 5 min)")

# --- SIDEBAR: MODULE SELECTION ---
st.sidebar.header("Navigation")
module = st.sidebar.radio("Select Module:", ["Quant A (Single Asset)", "Quant B (Portfolio)"], index=1)

# ==========================================
#        PARTIE QUANT A (SINGLE ASSET)
# ==========================================
if module == "Quant A (Single Asset)":
    if QUANT_A_AVAILABLE:
        display_quant_a()
    else:
        st.error("Quant A module not found. Please ensure the 'quant_a_module' folder exists.")

# ==========================================
#        PARTIE QUANT B (PORTFOLIO)
# ==========================================
elif module == "Quant B (Portfolio)":
    st.header("Multi-Asset Portfolio Optimization")
    
    # --- DATA DEFINITIONS (ASSET UNIVERSES) ---
    asset_universes = {
        "CAC 40 (France)": {
            "tickers": [
                "MC.PA", "TTE.PA", "SAN.PA", "AIR.PA", "OR.PA", "RMS.PA", "KER.PA", "AI.PA", 
                "BNP.PA", "GLE.PA", "ACA.PA", "CS.PA", "STLA.PA", "RNO.PA", "ML.PA", "ORA.PA",
                "CAP.PA", "DSY.PA", "STMPA.PA", "ENGI.PA", "EL.PA", "LR.PA", "SU.PA", "VIE.PA", "DG.PA"
            ],
            "default": ['MC.PA', 'TTE.PA', 'SAN.PA', 'AIR.PA']
        },
        "S&P 500 (USA)": {
            "tickers": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "V", "JNJ",
                "WMT", "JPM", "PG", "MA", "LLY", "HD", "XOM", "UNH", "CVX", "KO", "PEP"
            ],
            "default": ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
        },
        "DAX 40 (Germany)": {
            "tickers": [
                "SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "BMW.DE", "VOW3.DE", "BAS.DE",
                "IFX.DE", "DHL.DE", "MBG.DE", "MUV2.DE", "ADS.DE", "DB1.DE", "EOAN.DE"
            ],
            "default": ['SAP.DE', 'SIE.DE', 'ALV.DE', 'BMW.DE']
        },
        "Crypto Top 10": {
            "tickers": [
                "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD", "DOGE-USD",
                "AVAX-USD", "TRX-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "LINK-USD"
            ],
            "default": ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD']
        }
    }

    # 1. User Inputs
    st.sidebar.subheader("Portfolio Settings")
    
    # A. Select Asset Class
    selected_class = st.sidebar.selectbox(
        "1. Select Asset Class",
        list(asset_universes.keys()),
        index=0
    )
    
    # Get tickers and defaults based on selection
    current_universe = asset_universes[selected_class]
    available_tickers = current_universe["tickers"]
    default_tickers = current_universe["default"]
    
    # B. Select Specific Assets
    tickers = st.sidebar.multiselect(
        f"2. Select Assets ({selected_class})", 
        available_tickers, 
        default=default_tickers
    )
    
    # --- STRATEGY PARAMETERS ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Strategy Parameters")
    
    # Allocation Rule
    allocation_mode = st.sidebar.radio(
        "Allocation Rule", 
        ["Manual", "Equal Weight"],
        help="Manual: Use sliders below. Equal Weight: 1/N allocation."
    )
    
    # Rebalancing Frequency
    rebal_freq = st.sidebar.selectbox(
        "Rebalancing Frequency",
        ["None", "Monthly", "Quarterly", "Yearly"],
        index=1, # Default to Monthly
        help="How often the portfolio is reset to target weights."
    )
    
    # --- MAIN LOGIC ---
    if len(tickers) < 3:
        st.warning("Please select at least 3 assets to analyze diversification effects.")
    else:
        # Initialize Manager
        pm = PortfolioManager()
        
        # Fetch Data
        with st.spinner(f'Fetching real-time data for {selected_class}...'):
            data = pm.fetch_data(tickers)
        
        if data is not None and not data.empty:
            st.success(f"Data loaded for {len(tickers)} assets.")
            
            # 2. Weight Allocation Area
            st.subheader("1. Strategic Allocation")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.write("**Target Weights**")
                weights = {}
                
                # Logic to handle Allocation Rules
                if allocation_mode == "Equal Weight":
                    equal_w = 1.0 / len(tickers)
                    st.info(f"Auto-allocated {equal_w:.2%} to each asset.")
                    for t in tickers:
                        weights[t] = equal_w
                else:
                    # Manual Mode
                    total_used = 0.0
                    for i, t in enumerate(tickers):
                        # Smart default slider value to sum to 1 approximately
                        default_val = 1.0 / len(tickers)
                        val = st.slider(f"{t}", 0.0, 1.0, default_val, key=f"slider_{t}")
                        weights[t] = val
                
                # Check sum
                total_weight = sum(weights.values())
                if not (0.99 <= total_weight <= 1.01):
                    st.error(f"⚠️ Total weight: {total_weight:.2f}. Must be 1.0")
                else:
                    st.success("Weights Valid")
                    
                    # --- SAVE CONFIGURATION FOR DAILY REPORT ---
                    config = {
                        "tickers": tickers,
                        "weights": weights,
                        "asset_class": selected_class
                    }
                    try:
                        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "portfolio_config.json")
                        with open(config_path, "w") as f:
                            json.dump(config, f, indent=4)
                    except Exception as e:
                        print(f"Error saving config: {e}")
            
            with col2:
                # 3. Calculations & Visualizations
                sim_data = pm.simulate_portfolio(weights, rebalance_freq=rebal_freq)
                
                if sim_data is not None:
                    # Display Main Chart
                    Visualizer.plot_performance(sim_data)
                    
                    # Metrics
                    metrics = pm.get_portfolio_metrics(weights, sim_data['Portfolio'])
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Return", f"{metrics['Total Return']:.2%}")
                    m2.metric("Volatility", f"{metrics['Volatility (Ann.)']:.2f}")
                    m3.metric("Diversification Gain", f"{metrics['Diversification Effect']:.4f}", delta_color="normal")
                    m4.metric("Rebalancing", rebal_freq)

            # 4. Advanced Analysis
            st.subheader("2. Correlation Analysis")
            corr_matrix = pm.get_correlation_matrix()
            Visualizer.plot_correlation_heatmap(corr_matrix)
            
        else:
            st.error("Could not fetch data. Check your internet connection or ticker symbols.")