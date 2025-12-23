"""
STREAMLIT QUANTITATIVE DASHBOARD
--------------------------------
A real-time interface for asset analysis and portfolio optimization.
Features:
- Multi-asset class support (Equities, Crypto).
- Dynamic portfolio weight allocation with auto-normalization.
- Backtesting simulation with configurable rebalancing.
- Persistence layer via JSON configuration.
"""

import streamlit as st
import pandas as pd
import time
import json
import os

from quant_b_module.portfolio_manager import PortfolioManager
from quant_b_module.visualizer import Visualizer

try:
    from quant_a_module.visualizer import display_quant_a
    QUANT_A_AVAILABLE = True
except ImportError:
    QUANT_A_AVAILABLE = False

CONFIG_FILE = "portfolio_config.json"

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_config(config_data):
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

st.set_page_config(page_title="Quant Dashboard", layout="wide")

if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 300:
    st.session_state.last_refresh = time.time()
    st.rerun()

st.title("Asset Management Dashboard")
st.caption(f"Last updated: {time.strftime('%H:%M:%S')} (Auto-refreshes every 5 min)")

st.sidebar.header("Navigation")
module = st.sidebar.radio("Select Module:", ["Quant A (Single Asset)", "Quant B (Portfolio)"], index=1)

saved_config = load_config()

if module == "Quant A (Single Asset)":
    if QUANT_A_AVAILABLE:
        display_quant_a()
    else:
        st.error("Quant A module not found.")

elif module == "Quant B (Portfolio)":
    st.header("Multi-Asset Portfolio Optimization")

    asset_universes = {
        "CAC 40 (France)": {
            "tickers": [
                "AC.PA", "ACA.PA", "AI.PA", "AIR.PA", "ALO.PA", "ATO.PA", "BNP.PA", "BN.PA", 
                "CA.PA", "CAP.PA", "CS.PA", "DG.PA", "DSY.PA", "EDEN.PA", "ENGI.PA", "EL.PA", 
                "ERF.PA", "GLE.PA", "HO.PA", "KER.PA", "LR.PA", "MC.PA", "ML.PA", "ORA.PA", 
                "OR.PA", "PUB.PA", "RNO.PA", "RMS.PA", "SAF.PA", "SGO.PA", "SAN.PA", "SU.PA", 
                "STLA.PA", "STM.PA", "TEP.PA", "TTE.PA", "URW.AS", "VIE.PA", "VIV.PA", "WLN.PA"
            ],
            "default": ['MC.PA', 'TTE.PA', 'SAN.PA', 'AIR.PA']
        },
        "DAX 40 (Germany)": {
            "tickers": [
                "ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "BNR.DE", 
                "CBK.DE", "CON.DE", "1COV.DE", "DTG.DE", "DBK.DE", "DB1.DE", "DHL.DE", "DTE.DE", 
                "EOAN.DE", "FRE.DE", "HNR1.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "LIN.DE", "MBG.DE", 
                "MRK.DE", "MTX.DE", "MUV2.DE", "PAH3.DE", "PUM.DE", "QIA.DE", "RWE.DE", "SAP.DE", 
                "SRT.DE", "SIE.DE", "SHL.DE", "SY1.DE", "VOW3.DE", "VNA.DE", "ZAL.DE"
            ],
            "default": ['SAP.DE', 'SIE.DE', 'ALV.DE', 'BMW.DE']
        },
        "S&P 500 (USA - Major)": {
            "tickers": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH", "JNJ", "XOM", 
                "JPM", "PG", "V", "LLY", "MA", "HD", "CVX", "MRK", "ABBV", "PEP", "KO", "AVGO", "COST", 
                "PFE", "TMO", "WMT", "CSCO", "BAC", "MCD", "ABT", "CRM", "ACN", "DIS", "LIN", "DHR", 
                "VZ", "NEE", "TXN", "NKE", "PM", "ADBE", "BMY", "CMCSA", "UPS", "RTX", "HON", "NFLX", 
                "QCOM", "UNP", "INTC", "IBM", "AMGN", "LOW", "SPGI", "CAT", "GS", "INTU", "GE", "AMD", 
                "DE", "LMT", "MS", "BA", "ELV", "BLK", "AXP", "MDT", "ADP", "BKNG", "PLD", "GILD", 
                "AMT", "SYK", "MDLZ", "ISRG", "TJX", "CVS", "SBUX", "MMC", "ADI", "C", "CI", "CHTR", 
                "MO", "EOG", "BDX", "TMUS", "REGN", "SO", "PGR", "ZTS", "DUK", "BSX", "SLB", "CL", 
                "ITW", "USB", "NOC", "VRTX", "TGT", "CSX", "PYPL", "AON", "HUM", "APD", "EQIX", "ECL", 
                "WM", "FCX", "HCA", "MMM", "SHW", "ETN", "FISV", "PNC", "EW", "MAR", "CCI", "NSC", 
                "OXY", "ICE", "FDX", "TFC", "MCO", "EMR", "ORLY", "VLO", "MPC", "PSA", "ROP", "ADM", 
                "GM", "GIS", "DG", "MCK", "AEP", "SRE", "GD", "AZO", "KMB", "F", "PEG", "PSX", "MET", 
                "TRV", "MSI", "AIG", "OKE", "DVN", "JCI", "APH", "HLT", "IDXX", "ROST", "TEL", "COF", 
                "CTAS", "IQV", "KR", "WMB", "ADSK", "BK", "ALL", "EXC", "PAYX", "PCAR", "D", "KMI", 
                "YUM", "WFC", "ED", "HPQ", "BKR", "GLW", "OTIS", "EA", "DOW", "PRU", "PPG", "PEG", 
                "CMI", "GPN", "CTSH", "AFL", "STT", "SYY", "XEL", "EBAY", "WBA", "CARR", "FAST", "APTV",
                "DAL", "UAL", "AAL", "LUV", "RCL", "CCL", "NCLH", "EXPE", "BKNG", "ABNB", "MAR", "HLT"
            ],
            "default": ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
        },
        "Crypto Top 20": {
            "tickers": [
                "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD", "DOGE-USD",
                "AVAX-USD", "TRX-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "LINK-USD", "SHIB-USD",
                "DAI-USD", "UNI-USD", "ATOM-USD", "XMR-USD", "ETC-USD", "BCH-USD", "XLM-USD"
            ],
            "default": ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD']
        }
    }

    st.sidebar.subheader("Portfolio Settings")
    
    class_options = list(asset_universes.keys())
    default_classes = [class_options[0]]
    if saved_config and "asset_class" in saved_config:
        default_classes = [c for c in saved_config["asset_class"] if c in class_options]

    selected_classes = st.sidebar.multiselect(
        "1. Select Asset Classes",
        class_options,
        default=default_classes
    )

    available_tickers = []
    default_tickers = []
    for cls in selected_classes:
        available_tickers.extend(asset_universes[cls]["tickers"])
        default_tickers.extend(asset_universes[cls]["default"])
    available_tickers = sorted(list(set(available_tickers)))
    
    current_default_tickers = default_tickers
    if saved_config and "tickers" in saved_config:
        current_default_tickers = [t for t in saved_config["tickers"] if t in available_tickers]

    tickers = st.sidebar.multiselect(
        "2. Select Assets", 
        available_tickers, 
        default=current_default_tickers
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Strategy Parameters")
    
    allocation_mode = st.sidebar.radio(
        "Allocation Rule", 
        ["Manual", "Equal Weight"]
    )
    
    rebal_freq = st.sidebar.selectbox(
        "Rebalancing Frequency",
        ["None", "Monthly", "Quarterly", "Yearly"],
        index=1
    )
    
    if len(tickers) < 3:
        st.warning("Please select at least 3 assets.")
    else:
        pm = PortfolioManager()
        
        with st.spinner('Fetching real-time data...'):
            data = pm.fetch_data(tickers)
        
        if data is not None and not data.empty:
            st.success(f"Data loaded for {len(tickers)} assets.")
            
            st.subheader("1. Strategic Allocation")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.write("**Target Weights**")
                weights = {}
                
                if allocation_mode == "Equal Weight":
                    equal_w = 1.0 / len(tickers)
                    st.info(f"Auto-allocated {equal_w:.2%} to each asset.")
                    for t in tickers:
                        weights[t] = equal_w
                else:
                    # Restore weights from JSON to session state if state is empty
                    if "manual_weights" not in st.session_state or set(st.session_state.manual_weights.keys()) != set(tickers):
                        if saved_config and "weights" in saved_config and set(saved_config["weights"].keys()) == set(tickers):
                            st.session_state.manual_weights = saved_config["weights"]
                        else:
                            st.session_state.manual_weights = {t: 1.0/len(tickers) for t in tickers}
                        
                        # Pre-seed individual slider session state keys
                        for t, w in st.session_state.manual_weights.items():
                            st.session_state[f"slider_{t}"] = float(w)

                    # Calculate total from the current slider states to handle relative normalization
                    current_raw_values = {t: st.session_state.get(f"slider_{t}", 1.0/len(tickers)) for t in tickers}
                    total_raw = sum(current_raw_values.values())
                    
                    # Display sliders with calculated normalized weight in labels
                    for t in tickers:
                        norm_w = current_raw_values[t] / total_raw if total_raw > 0 else 1.0/len(tickers)
                        st.slider(
                            f"{t} (Allocated: {norm_w:.2%})", 
                            0.0, 1.0, 
                            key=f"slider_{t}",
                            format="%.2f"
                        )
                    
                    # Compute final weights for the backend
                    final_raw = {t: st.session_state[f"slider_{t}"] for t in tickers}
                    final_total = sum(final_raw.values())
                    weights = {t: final_raw[t] / final_total if final_total > 0 else 1.0/len(tickers) for t in tickers}
                    st.session_state.manual_weights = weights

                # Persistent saving
                current_config = {
                    "tickers": tickers,
                    "weights": weights,
                    "asset_class": selected_classes
                }
                save_config(current_config)
            
            with col2:
                sim_data = pm.simulate_portfolio(weights, rebalance_freq=rebal_freq)
                
                if sim_data is not None:
                    Visualizer.plot_performance(sim_data)
                    metrics = pm.get_portfolio_metrics(weights, sim_data['Portfolio'])
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Return", f"{metrics['Total Return']:.2%}")
                    m2.metric("Volatility (Ann.)", f"{metrics['Volatility (Ann.)']:.2f}")
                    m3.metric("Diversification Gain", f"{metrics['Diversification Effect']:.4f}")
                    m4.metric("Rebalancing", rebal_freq)

            st.subheader("2. Correlation Analysis")
            corr_matrix = pm.get_correlation_matrix()
            Visualizer.plot_correlation_heatmap(corr_matrix)
            
        else:
            st.error("Could not fetch data.")