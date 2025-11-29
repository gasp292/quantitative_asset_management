import streamlit as st
import plotly.graph_objects as go
from quant_a_module.asset_analyzer import AssetAnalyzer

def display_quant_a():
    """
    Main function to display the Quant A module.
    Connects the Streamlit UI (sidebar) to the Backend (AssetAnalyzer).
    """
    st.markdown("Univariate Analysis (Quant A)")
    
    # Sidebar: Settings
    with st.sidebar:
        st.header("Settings")
        
        ticker = st.text_input("Asset Symbol (Yahoo)", value="BTC-USD")
        period = st.selectbox("Time Period", ["6mo", "1y", "2y", "5y"], index=1)
        strategy = st.radio("Strategy", ["Buy and Hold", "Momentum"])
        
        # Conditional Parameters (only appear if Momentum is selected)
        short_w, long_w = 20, 50
        if strategy == "Momentum":
            st.markdown("---")
            st.write("**Moving Averages**")
            short_w = st.number_input("Short Window (Days)", min_value=5, value=20)
            long_w = st.number_input("Long Window (Days)", min_value=10, value=50)

    # Execution
    analyzer = AssetAnalyzer(ticker)
    
    # Run calculations with a loading spinner
    with st.spinner('Running analysis...'):
        analyzer.get_data(period=period)
        df = analyzer.run_strategy(strategy, short_w, long_w)        
        metrics = analyzer.get_metrics(df)

    # Visualization
    if df is not None:
        col1, col2, col3 = st.columns(3)
        last_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        delta = last_price - prev_price
        
        col1.metric("Current Price", f"${last_price:,.2f}", f"${delta:,.2f}")
        col2.metric("Sharpe Ratio", metrics.get("Sharpe Ratio", 0))
        col3.metric("Max Drawdown", f"{metrics.get('Max Drawdown', 0) * 100:.2f} %")

        # B. Main Chart (Double Y-Axis)
        # We use graph_objects (go) for precise control over the two axes
        st.subheader(f"Performance: {ticker} vs Strategy")
        
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['Close'], 
            name='Asset Price ($)',
            line=dict(color='gray', width=1, dash='dot'),
            yaxis='y1'
        ))

        # Trace 2: Strategy Value Rebased to 100 (Right Axis)
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['Cumulative_Strategy'], 
            name='Strategy Value (Base 100)',
            line=dict(color='blue', width=3),
            yaxis='y2' # Secondary Axis
        ))

        # Layout configuration (Dual Axis)
        fig.update_layout(
            title=f"Comparison: Asset Price vs Strategy Performance",
            xaxis_title="Date",
            yaxis=dict(title="Asset Price ($)", side="left"),
            yaxis2=dict(title="Strategy Value (Base 100)", side="right", overlaying="y", showgrid=False),
            legend=dict(x=0, y=1.1, orientation="h"), 
            template="plotly_white",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(f"Error: Could not retrieve data for {ticker}. Please check the symbol.")