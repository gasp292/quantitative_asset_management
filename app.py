import streamlit as st
import pandas as pd
# Import local modules
from quant_b_module.portfolio_manager import PortfolioManager
from quant_b_module.visualizer import Visualizer

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Quant Dashboard", layout="wide")

st.title("Asset Management Dashboard (CAC 40 Focus)")

# --- SIDEBAR: MODULE SELECTION ---
st.sidebar.header("Navigation")
module = st.sidebar.radio("Select Module:", ["Quant A (Single Asset)", "Quant B (Portfolio)"], index=1)

# --- QUANT A LOGIC (Placeholder) ---
if module == "Quant A (Single Asset)":
    st.info("Quant A module is currently under development by teammate.")
    st.image("https://placehold.co/600x400?text=Work+In+Progress", caption="Quant A Area")

# --- QUANT B LOGIC (Active) ---
elif module == "Quant B (Portfolio)":
    st.header("CAC 40 Portfolio Optimization")
    
    # 1. User Inputs
    st.sidebar.subheader("Portfolio Settings")
    
    # FULL CAC 40 LIST (Yahoo Finance Format)
    cac40_tickers = [
    "AC.PA", "AI.PA", "AIR.PA", "MT.AS", "CS.PA", "BNP.PA", "EN.PA", "BVI.PA", "CAP.PA", "CA.PA",
    "ACA.PA", "BN.PA", "DSY.PA", "EDEN.PA", "ENGI.PA", "EL.PA", "ERF.PA", "RMS.PA", "KER.PA", "OR.PA",
    "LR.PA", "MC.PA", "ML.PA", "ORA.PA", "RI.PA", "PUB.PA", "RNO.PA", "SAF.PA", "SGO.PA", "SAN.PA",
    "SU.PA", "GLE.PA", "STLAP.PA", "STMPA.PA", "TEP.PA", "HO.PA", "TTE.PA", "URW.AS", "VIE.PA", "DG.PA"
]

    # Default selection: LVMH (MC), Total (TTE), Sanofi (SAN), Airbus (AIR)
    default_selection = ['MC.PA', 'TTE.PA', 'SAN.PA', 'AIR.PA']
    
    tickers = st.sidebar.multiselect(
        "Select Assets (CAC 40)", 
        cac40_tickers, 
        default=default_selection
    )
    
    # --- STRATEGY PARAMETERS (Mandatory for Quant B) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Strategy Parameters")
    enable_rebalancing = st.sidebar.checkbox(
        "Enable Monthly Rebalancing", 
        value=False, 
        help="Strategy: Sell winners and buy losers every month to maintain target weights."
    )
    
    if len(tickers) < 3:
        st.warning("Please select at least 3 assets to analyze diversification effects.")
    else:
        # Initialize Manager
        pm = PortfolioManager()
        
        # Fetch Data
        with st.spinner('Fetching real-time data from Paris...'):
            data = pm.fetch_data(tickers)
        
        if data is not None and not data.empty:
            st.success(f"Data loaded for {len(tickers)} stocks.")
            
            # 2. Weight Allocation
            st.subheader("1. Strategic Allocation")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.write("**Target Weights**")
                weights = {}
                
                # Independent sliders for simplicity
                for t in tickers:
                    val = st.slider(f"{t}", 0.0, 1.0, 1.0/len(tickers))
                    weights[t] = val
                
                # Check sum
                total_weight = sum(weights.values())
                if not (0.99 <= total_weight <= 1.01):
                    st.error(f"⚠️ Total weight: {total_weight:.2f}. Must be 1.0")
                else:
                    st.success("Weights Valid")
            
            with col2:
                # 3. Calculations & Visualizations
                # We pass the 'enable_rebalancing' checkbox value to the engine
                sim_data = pm.simulate_portfolio(weights, rebalance=enable_rebalancing)
                
                if sim_data is not None:
                    # Display Main Chart
                    Visualizer.plot_performance(sim_data)
                    
                    # Metrics
                    # We pass 'weights' to calculate diversification
                    metrics = pm.get_portfolio_metrics(weights, sim_data['Portfolio'])
                    
                    # Display Metrics in 4 columns
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Total Return", f"{metrics['Total Return']:.2%}")
                    m2.metric("Volatility", f"{metrics['Volatility (Ann.)']:.2f}")
                    m3.metric("Diversification Gain", f"{metrics['Diversification Effect']:.4f}", delta_color="normal")
                    m4.metric("Strategy Mode", "Rebalanced" if enable_rebalancing else "Buy & Hold")

            # 4. Advanced Analysis
            st.subheader("2. Correlation Analysis")
            corr_matrix = pm.get_correlation_matrix()
            Visualizer.plot_correlation_heatmap(corr_matrix)
            
        else:
            st.error("Could not fetch data. Check your internet connection.")