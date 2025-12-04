import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from quant_a_module.asset_analyzer import AssetAnalyzer

def display_quant_a():
    """
    Main function to display the Univariate Analysis module (Quant A).
    Enhanced with interactive Buy/Sell markers and professional layout.
    """
    st.markdown("## Univariate Analysis (Quant A)")
    
    # --- 1. SIDEBAR: SETTINGS ---
    with st.sidebar:
        st.header("Settings")
        
        # Asset Selection
        ticker = st.text_input("Asset Symbol", value="BTC-USD")
        
        # Period Selection
        period = st.selectbox("Time Period", ["6mo", "1y", "2y", "5y", "max"], index=1)
        
        # Strategy Selection
        strategy = st.radio("Strategy", ["Buy and Hold", "Momentum", "RSI Strategy"])
        
        # --- Strategy Parameters ---
        # Default values
        short_w, long_w = 20, 50
        rsi_w, rsi_buy, rsi_sell = 14, 30, 70
        
        if strategy == "Momentum":
            st.markdown("---")
            st.write("Momentum Parameters")
            short_w = st.number_input("Short Window (Days)", 5, 200, 20)
            long_w = st.number_input("Long Window (Days)", 10, 365, 50)
            
        elif strategy == "RSI Strategy":
            st.markdown("---")
            st.write("RSI Parameters")
            rsi_w = st.number_input("RSI Window", 5, 50, 14)
            col1, col2 = st.columns(2)
            with col1:
                rsi_buy = st.number_input("Buy (Oversold)", 10, 40, 30)
            with col2:
                rsi_sell = st.number_input("Sell (Overbought)", 60, 90, 70)

    # --- 2. EXECUTION (BACKEND) ---
    analyzer = AssetAnalyzer(ticker)
    
    with st.spinner('Analyzing market data...'):
        # Get Data & Run Strategy
        analyzer.get_data(period=period)
        df = analyzer.run_strategy(
            strategy, 
            short_window=short_w, long_window=long_w,
            rsi_window=rsi_w, rsi_buy=rsi_buy, rsi_sell=rsi_sell
        )
        metrics = analyzer.get_metrics(df)

    # --- 3. VISUALIZATION (FRONTEND) ---
    if df is not None:
        # A. KPIs (5 Metrics Dashboard)
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Total Return", f"{metrics.get('Total Return', 0):.2%}")
        m2.metric("CAGR", f"{metrics.get('CAGR', 0):.2%}")
        m3.metric("Sharpe Ratio", f"{metrics.get('Sharpe Ratio', 0):.2f}")
        m4.metric("Max Drawdown", f"{metrics.get('Max Drawdown', 0):.2%}")
        m5.metric("Win Rate", f"{metrics.get('Win Rate', 0):.2%}")
        
        st.markdown("---")

        # --- LAST PRICE DISPLAY ---
        try:
            # Using .values[-1] and float() to prevent TypeError with Series formatting
            last_close = float(df['Close'].values[-1])
            prev_close = float(df['Close'].values[-2])
            delta_price = last_close - prev_close
            delta_pct = (delta_price / prev_close) * 100

            col_price, _ = st.columns([1, 3])
            with col_price:
                st.metric(
                    label=f"Last Price ({ticker})",
                    value=f"${last_close:,.2f}",
                    delta=f"{delta_price:+.2f} ({delta_pct:+.2f}%)"
                )
        except Exception:
            st.warning("Could not calculate last price variation.")

        # B. ADVANCED INTERACTIVE CHART
        st.subheader(f"Performance: {ticker} vs Strategy")
        
        fig = go.Figure()

        # 1. Asset Price (Grey Line)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], 
            name='Asset Price',
            line=dict(color='rgba(0,0,0,0.5)', width=1),
            yaxis='y1'
        ))

        # 2. Strategy Curve (Blue Line)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Cumulative_Strategy'], 
            name='Strategy (Base 100)',
            line=dict(color='#2980b9', width=2),
            fill='tozeroy', 
            fillcolor='rgba(41, 128, 185, 0.1)', 
            yaxis='y2'
        ))
        
        # 3. BUY / SELL MARKERS 
        if 'Signal' in df.columns:
            trades = df['Signal'].diff()
            buys = df[trades == 1]
            sells = df[trades == -1]
            
            if not buys.empty:
                fig.add_trace(go.Scatter(
                    x=buys.index, y=buys['Close'],
                    mode='markers', name='Buy Signal',
                    marker=dict(symbol='triangle-up', color='#2ecc71', size=12, line=dict(color='black', width=1)),
                    yaxis='y1'
                ))
            
            if not sells.empty:
                fig.add_trace(go.Scatter(
                    x=sells.index, y=sells['Close'],
                    mode='markers', name='Sell Signal',
                    marker=dict(symbol='triangle-down', color='#e74c3c', size=12, line=dict(color='black', width=1)),
                    yaxis='y1'
                ))

        # 4. Professional Layout
        fig.update_layout(
            height=600,
            xaxis=dict(
                type="date",
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
                )
            ),
            yaxis=dict(title="Asset Price ($)", side="left", showgrid=False),
            yaxis2=dict(
                title="Strategy Value (Base 100)", 
                side="right", overlaying="y", 
                showgrid=True, gridcolor='rgba(128,128,128,0.2)'
            ),
            legend=dict(orientation="h", y=1.02, x=0),
            template="plotly_white",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Raw Data
        with st.expander("View Historical Data & Signals"):
            st.dataframe(df.tail(20).style.format({"Close": "{:.2f}", "RSI": "{:.1f}"}))

    else:
        st.error("Error: Could not retrieve data.")