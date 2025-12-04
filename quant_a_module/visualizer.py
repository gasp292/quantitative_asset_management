import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from quant_a_module.asset_analyzer import AssetAnalyzer

def display_quant_a():
    """
    Main function to display the Univariate Analysis module (Quant A).
    Enhanced with Asset Universes selection.
    """
    st.markdown("## Univariate Analysis (Quant A)")
    
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
                "MMM", "AOS", "ABT", "ABBV", "ACN", "ADBE", "AMD", "AES", "AFL", "A", 
                "APD", "ABNB", "AKAM", "ALB", "ARE", "ALGN", "ALLE", "LNT", "ALL", "GOOGL", 
                "GOOG", "MO", "AMZN", "AMCR", "AEE", "AEP", "AXP", "AIG", "AMT", "AWK", 
                "AMP", "AME", "AMGN", "APH", "ADI", "AON", "APA", "APO", "AAPL", "AMAT", 
                "APP", "APTV", "ACGL", "ADM", "ANET", "AJG", "AIZ", "T", "ATO", "ADSK", 
                "ADP", "AZO", "AVB", "AVY", "AXON", "BKR", "BALL", "BAC", "BAX", "BDX", 
                "BRK.B", "BBY", "TECH", "BIIB", "BLK", "BX", "XYZ", "BK", "BA", "BKNG", 
                "BSX", "BMY", "AVGO", "BR", "BRO", "BF.B", "BLDR", "BG", "BXP", "CHRW", 
                "CDNS", "CPT", "CPB", "COF", "CAH", "CCL", "CARR", "CAT", "CBOE", "CBRE", 
                "CDW", "COR", "CNC", "CNP", "CF", "CRL", "SCHW", "CHTR", "CVX", "CMG", 
                "CB", "CHD", "CI", "CINF", "CTAS", "CSCO", "C", "CFG", "CLX", "CME", 
                "CMS", "KO", "CTSH", "COIN", "CL", "CMCSA", "CAG", "COP", "ED", "STZ", 
                "CEG", "COO", "CPRT", "GLW", "CPAY", "CTVA", "CSGP", "COST", "CTRA", "CRWD", 
                "CCI", "CSX", "CMI", "CVS", "DHR", "DRI", "DDOG", "DVA", "DAY", "DECK", 
                "DE", "DELL", "DAL", "DVN", "DXCM", "FANG", "DLR", "DG", "DLTR", "D", 
                "DPZ", "DASH", "DOV", "DOW", "DHI", "DTE", "DUK", "DD", "ETN", "EBAY", 
                "ECL", "EIX", "EW", "EA", "ELV", "EME", "EMR", "ETR", "EOG", "EPAM", 
                "EQT", "EFX", "EQIX", "EQR", "ERIE", "ESS", "EL", "EG", "EVRG", "ES", 
                "EXC", "EXE", "EXPE", "EXPD", "EXR", "XOM", "FFIV", "FDS", "FICO", "FAST", 
                "FRT", "FDX", "FIS", "FITB", "FSLR", "FE", "FISV", "F", "FTNT", "FTV", 
                "FOXA", "FOX", "BEN", "FCX", "GRMN", "IT", "GE", "GEHC", "GEV", "GEN", 
                "GNRC", "GD", "GIS", "GM", "GPC", "GILD", "GPN", "GL", "GDDY", "GS", 
                "HAL", "HIG", "HAS", "HCA", "DOC", "HSIC", "HSY", "HPE", "HLT", "HOLX", 
                "HD", "HON", "HRL", "HST", "HWM", "HPQ", "HUBB", "HUM", "HBAN", "HII", 
                "IBM", "IEX", "IDXX", "ITW", "INCY", "IR", "PODD", "INTC", "IBKR", "ICE", 
                "IFF", "IP", "INTU", "ISRG", "IVZ", "INVH", "IQV", "IRM", "JBHT", "JBL", 
                "JKHY", "J", "JNJ", "JCI", "JPM", "K", "KVUE", "KDP", "KEY", "KEYS", 
                "KMB", "KIM", "KMI", "KKR", "KLAC", "KHC", "KR", "LHX", "LH", "LRCX", 
                "LW", "LVS", "LDOS", "LEN", "LII", "LLY", "LIN", "LYV", "LKQ", "LMT", 
                "L", "LOW", "LULU", "LYB", "MTB", "MPC", "MAR", "MMC", "MLM", "MAS", 
                "MA", "MTCH", "MKC", "MCD", "MCK", "MDT", "MRK", "META", "MET", "MTD", 
                "MGM", "MCHP", "MU", "MSFT", "MAA", "MRNA", "MHK", "MOH", "TAP", "MDLZ", 
                "MPWR", "MNST", "MCO", "MS", "MOS", "MSI", "MSCI", "NDAQ", "NTAP", "NFLX", 
                "NEM", "NWSA", "NWS", "NEE", "NKE", "NI", "NDSN", "NSC", "NTRS", "NOC", 
                "NCLH", "NRG", "NUE", "NVDA", "NVR", "NXPI", "ORLY", "OXY", "ODFL", "OMC", 
                "ON", "OKE", "ORCL", "OTIS", "PCAR", "PKG", "PLTR", "PANW", "PSKY", "PH", 
                "PAYX", "PAYC", "PYPL", "PNR", "PEP", "PFE", "PCG", "PM", "PSX", "PNW", 
                "PNC", "POOL", "PPG", "PPL", "PFG", "PG", "PGR", "PLD", "PRU", "PEG", 
                "PTC", "PSA", "PHM", "PWR", "QCOM", "DGX", "Q", "RL", "RJF", "RTX", 
                "O", "REG", "REGN", "RF", "RSG", "RMD", "RVTY", "HOOD", "ROK", "ROL", 
                "ROP", "ROST", "RCL", "SPGI", "CRM", "SNDK", "SBAC", "SLB", "STX", "SRE", 
                "NOW", "SHW", "SPG", "SWKS", "SJM", "SW", "SNA", "SOLS", "SOLV", "SO", 
                "LUV", "SWK", "SBUX", "STT", "STLD", "STE", "SYK", "SMCI", "SYF", "SNPS", 
                "SYY", "TMUS", "TROW", "TTWO", "TPR", "TRGP", "TGT", "TEL", "TDY", "TER", 
                "TSLA", "TXN", "TPL", "TXT", "TMO", "TJX", "TKO", "TTD", "TSCO", "TT", 
                "TDG", "TRV", "TRMB", "TFC", "TYL", "TSN", "USB", "UBER", "UDR", "ULTA", 
                "UNP", "UAL", "UPS", "URI", "UNH", "UHS", "VLO", "VTR", "VLTO", "VRSN", 
                "VRSK", "VZ", "VRTX", "VTRS", "VICI", "V", "VST", "VMC", "WRB", "GWW", 
                "WAB", "WMT", "DIS", "WBD", "WM", "WAT", "WEC", "WFC", "WELL", "WST", 
                "WDC", "WY", "WSM", "WMB", "WTW", "WDAY", "WYNN", "XEL", "XYL", "YUM", 
                "ZBRA", "ZBH", "ZTS"
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
        
        # --- ASSET SELECTION ---
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
        # Added '1mo' as requested
        period = st.selectbox("Time Period", ["1mo", "6mo", "1y", "2y", "5y", "max"], index=2)
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
    
    with st.spinner(f'Analyzing {ticker}...'):
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

        # 4. Professional Layout (Without Zoom Selector)
        fig.update_layout(
            height=600,
            xaxis=dict(
                type="date",
                # Zoom buttons removed as requested
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