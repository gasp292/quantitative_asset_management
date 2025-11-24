import streamlit as st
import pandas as pd
# Import local modules
from quant_b_module.portfolio_manager import PortfolioManager
from quant_b_module.visualizer import Visualizer

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Quant Dashboard", layout="wide")

st.title("Asset Management Dashboard")

# --- SIDEBAR: MODULE SELECTION ---
st.sidebar.header("Navigation")
module = st.sidebar.radio("Select Module:", ["Quant A (Single Asset)", "Quant B (Portfolio)"], index=1)

# --- QUANT A LOGIC (Placeholder) ---
if module == "Quant A (Single Asset)":
    st.info("Quant A module is currently under development by teammate.")
    st.image("https://placehold.co/600x400?text=Work+In+Progress", caption="Quant A Area")

# --- QUANT B LOGIC (Active) ---
elif module == "Quant B (Portfolio)":
    st.header("Multi-Asset Portfolio Management")
    
    # 1. User Inputs
    st.sidebar.subheader("Portfolio Settings")
    
    # Default assets
    default_tickers = ['AAPL', 'MSFT', 'GOOGL', 'BTC-USD']
    tickers = st.sidebar.multiselect("Select Assets (Min 3)", default_tickers, default=default_tickers)
    
    if len(tickers) < 3:
        st.warning("Please select at least 3 assets to analyze diversification effects.")
    else:
        # Initialize Manager
        pm = PortfolioManager()
        
        # Fetch Data
        with st.spinner('Fetching real-time data...'):
            data = pm.fetch_data(tickers)
        
        if data is not None and not data.empty:
            st.success(f"Data loaded for {len(tickers)} assets.")
            
            # 2. Weight Allocation
            st.subheader("1. Asset Allocation")
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.write("Define Weights:")
                weights = {}
                remaining_weight = 1.0
                
                # Create a slider for each asset
                for t in tickers:
                    # Simple equal weight logic for default, can be improved later
                    val = st.slider(f"Weight: {t}", 0.0, 1.0, 1.0/len(tickers))
                    weights[t] = val
                
                # Check sum
                total_weight = sum(weights.values())
                if not (0.99 <= total_weight <= 1.01):
                    st.error(f"Total weight is {total_weight:.2f}. It must sum to 1.0")
            
            with col2:
                # 3. Calculations & Visualizations
                # Run Simulation
                sim_data = pm.simulate_portfolio(weights)
                
                if sim_data is not None:
                    # Display Main Chart
                    Visualizer.plot_performance(sim_data)
                    
                    # Metrics
                    metrics = pm.get_portfolio_metrics(sim_data['Portfolio'])
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total Return", f"{metrics['Total Return']:.2%}")
                    m2.metric("Annual Volatility", f"{metrics['Volatility (Ann.)']:.2f}")
                    m3.metric("Assets Count", len(tickers))

            # 4. Advanced Analysis
            st.subheader("2. Correlation Analysis")
            st.write("Understand how assets move in relation to each other.")
            corr_matrix = pm.get_correlation_matrix()
            Visualizer.plot_correlation_heatmap(corr_matrix)
            
        else:
            st.error("Could not fetch data. Please check ticker symbols.")