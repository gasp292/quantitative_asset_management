import streamlit as st
import plotly.graph_objects as go
from .asset_analyzer import AssetAnalyzer

def display_quant_a():
    """
    Main function to display the Univariate Analysis module (Quant A).
    Enhanced with Asset Universes selection.
    """
    st.markdown("Univariate Analysis (Quant A)")
    
    # --- DATA DEFINITIONS (Shared Universes) ---
    asset_universes = {
        "Manual Input": {
            "tickers": [] 
        },
        "CAC 40 (France)": {
            "tickers": [
                "MC.PA", "TTE.PA", "SAN.PA", "AIR.PA", "OR.PA", "RMS.PA", "KER.PA", "AI.PA", 
                "BNP.PA", "GLE.PA", "ACA.PA", "CS.PA", "STLA.PA", "RNO.PA", "ML.PA", "ORA.PA",
                "CAP.PA", "DSY.PA", "STMPA.PA", "ENGI.PA", "EL.PA", "LR.PA", "SU.PA", "VIE.PA", "DG.PA"
            ]
        },
        "S&P 500 (USA)": {
            "tickers": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "V", "JNJ",
                "WMT", "JPM", "PG", "MA", "LLY", "HD", "XOM", "UNH", "CVX", "KO", "PEP"
            ]
        },
        "DAX 40 (Germany)": {
            "tickers": [
                "SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "BMW.DE", "VOW3.DE", "BAS.DE",
                "IFX.DE", "DHL.DE", "MBG.DE", "MUV2.DE", "ADS.DE", "DB1.DE", "EOAN.DE"
            ]
        },
        "Crypto Top 10": {
            "tickers": [
                "BTC-USD", "ETH-USD", "BNB-USD", "SOL-USD", "XRP-USD", "ADA-USD", "DOGE-USD",
                "AVAX-USD", "TRX-USD", "DOT-USD", "MATIC-USD", "LTC-USD", "LINK-USD"
            ]
        }
    }

    # --- 1. SIDEBAR: SETTINGS ---
    with st.sidebar:
        st.header("Settings")
        
        # --- NEW ASSET SELECTION LOGIC ---
        st.subheader("Asset Selection")
        
        # 1. Select Market/Universe
        market = st.selectbox("Market", list(asset_universes.keys()), index=0)
        
        # 2. Select or Type Ticker
        if market == "Manual Input":
            ticker = st.text_input("Asset Symbol (Yahoo)", value="BTC-USD")
        else:
            # Dropdown for single selection
            ticker = st.selectbox("Select Asset", asset_universes[market]["tickers"])
        
        st.markdown("---")
        
        # --- Time & Strategy ---
        period = st.selectbox("Time Period", ["6mo", "1y", "2y", "5y", "max"], index=1)
        strategy = st.radio("Strategy", ["Buy and Hold", "Momentum", "RSI Strategy"])
        
        # --- Strategy Parameters ---
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
            rsi_buy = col1.number_input("Buy (Oversold)", 10, 40, 30)
            rsi_sell = col2.number_input("Sell (Overbought)", 60, 90, 70)
            
        # --- AI Forecast Option ---
        st.markdown("---")
        st.header("AI Prediction")
        show_forecast = st.checkbox("Enable ARIMA Forecast", value=False)
        forecast_days = 30
        if show_forecast:
            forecast_days = st.slider("Forecast Horizon (Days)", 7, 90, 30)

    # --- 2. EXECUTION (BACKEND) ---
    analyzer = AssetAnalyzer(ticker)
    forecast_df = None
    
    with st.spinner(f'Analyzing {ticker}...'):
        # Get Data & Run Strategy
        analyzer.get_data(period=period)
        df = analyzer.run_strategy(
            strategy, 
            short_window=short_w, long_window=long_w,
            rsi_window=rsi_w, rsi_buy=rsi_buy, rsi_sell=rsi_sell
        )
        metrics = analyzer.get_metrics(df)
        
        # Run AI Forecast if requested
        if show_forecast:
            forecast_df = analyzer.get_forecast(steps=forecast_days)

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

        # B. Prediction Banner
        if show_forecast and forecast_df is not None:
            last_price = df['Close'].iloc[-1]
            pred_price = forecast_df['Forecast'].iloc[-1]
            trend = float((pred_price - last_price) / last_price)
            color = "#2ecc71" if trend > 0 else "#e74c3c" # Green or Red
            
            st.markdown(f"""
            <div style="padding: 15px; border-left: 5px solid {color}; background-color: #f0f2f6; border-radius: 5px;">
                <h4 style="margin:0; color:black;">🤖 AI Forecast ({forecast_days} days)</h4>
                <p style="margin:0; color:black;">
                    Target Price: <strong>${pred_price:,.2f}</strong> 
                    (<span style="color:{color}; font-weight:bold;">{trend:+.2%}</span>)
                </p>
            </div><br>
            """, unsafe_allow_html=True)

        # C. ADVANCED INTERACTIVE CHART
        st.subheader(f"Strategy Performance: {ticker}")
        
        fig = go.Figure()

        # 1. Asset Price
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], 
            name='Asset Price',
            line=dict(color='rgba(0,0,0,0.3)', width=1), # Semi-transparent black
            yaxis='y1'
        ))

        # 2. Strategy Curve (The Hero)
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

        # 4. AI Forecast Line
        if show_forecast and forecast_df is not None:
            fig.add_trace(go.Scatter(
                x=forecast_df.index, y=forecast_df['Forecast'], 
                name='AI Forecast',
                line=dict(color='#e67e22', width=2, dash='dot'),
                yaxis='y1'
            ))

        # 5. Layout
        fig.update_layout(
            height=600,
            xaxis=dict(
                rangeslider=dict(visible=False),
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
        with st.expander("📊 View Historical Data & Signals"):
            st.dataframe(df.tail(20).style.format({"Close": "{:.2f}", "RSI": "{:.1f}"}))

    else:
        st.error("Error: Could not retrieve data.")