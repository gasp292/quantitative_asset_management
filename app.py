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
except ImportError:
    QUANT_A_AVAILABLE = False

# --- CONFIGURATION PERSISTENCE HELPERS ---
CONFIG_FILE = "portfolio_config.json"

def load_config():
    """Loads the saved configuration from the JSON file if it exists."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_config(config_data):
    """Saves the current configuration to a JSON file."""
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE)
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Quant Dashboard", layout="wide")

# --- AUTO-REFRESH LOGIC (Every 5 minutes) ---
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

# Load saved configuration at startup
saved_config = load_config()

# ==========================================
#        QUANT A SECTION (SINGLE ASSET)
# ==========================================
if module == "Quant A (Single Asset)":
    if QUANT_A_AVAILABLE:
        display_quant_a()
    else:
        st.error("Quant A module not found. Please ensure the 'quant_a_module' folder exists.")

# ==========================================
#        QUANT B SECTION (PORTFOLIO)
# ==========================================
elif module == "Quant B (Portfolio)":
    st.header("Multi-Asset Portfolio Optimization")

    # --- ASSET UNIVERSES DEFINITION ---
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
    
    # 1. Select Asset Classes
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
    
    # 2. Select Specific Assets
    current_default_tickers = default_tickers
    if saved_config and "tickers" in saved_config:
        current_default_tickers = [t for t in saved_config["tickers"] if t in available_tickers]

    tickers = st.sidebar.multiselect(
        "2. Select Assets", 
        available_tickers, 
        default=current_default_tickers
    )
    
    # --- STRATEGY PARAMETERS ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Strategy Parameters")
    
    allocation_mode = st.sidebar.radio(
        "Allocation Rule", 
        ["Manual", "Equal Weight"],
        help="Manual: Use sliders below. Equal Weight: 1/N allocation."
    )
    
    rebal_freq = st.sidebar.selectbox(
        "Rebalancing Frequency",
        ["None", "Monthly", "Quarterly", "Yearly"],
        index=1,
        help="How often the portfolio is reset to target weights."
    )
    
    # --- MAIN LOGIC ---
    if len(tickers) < 3:
        st.warning("Please select at least 3 assets to analyze diversification effects.")
    else:
        pm = PortfolioManager()
        
        with st.spinner(f'Fetching real-time data...'):
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
                    # Sync session state with saved config weights if first load
                    if saved_config and "weights" in saved_config:
                        for t, w in saved_config["weights"].items():
                            if f"slider_{t}" not in st.session_state:
                                st.session_state[f"slider_{t}"] = w

                    # Reset weights if ticker list changed significantly
                    if "old_tickers" not in st.session_state or set(st.session_state.old_tickers) != set(tickers):
                        st.session_state.old_tickers = tickers
                        # Logic to prevent old sliders from overriding 1/N for new items
                        for t in tickers:
                            if f"slider_{t}" not in st.session_state:
                                st.session_state[f"slider_{t}"] = 1.0 / len(tickers)

                    for t in tickers:
                        default_val = st.session_state.get(f"slider_{t}", 1.0 / len(tickers))
                        val = st.slider(f"{t}", 0.0, 1.0, default_val, key=f"slider_{t}", format="%.2f")
                        weights[t] = val
                
                total_weight = sum(weights.values())
                if not (0.999 <= total_weight <= 1.001):
                    st.error(f"⚠️ Total weight: {total_weight:.2f}. Must be 1.0")
                else:
                    st.success("Weights Valid")
                    
                    # Save current config to JSON
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
            st.error("Could not fetch data. Check your connection or tickers.")