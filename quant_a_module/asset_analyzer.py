import yfinance as yf
import pandas as pd
import numpy as np 
import streamlit as st

class AssetAnalyzer():
    def __init__ (self, ticker):
        self.ticker = ticker 
        self.data = None

    def get_data(self, period="1y"): 
        """
        Fetch historical data (Close Price and Returns) using yfinance.
        """
        # Download data with auto_adjust to handle dividends/splits
        df = yf.download(self.ticker, period=period, interval="1d", progress=False, auto_adjust=True)
        
        # Handle MultiIndex columns (common in new yfinance versions)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Calculate daily returns
        df['Returns'] = df['Close'].pct_change()
        
        # Remove the first row (NaN due to pct_change)
        df.dropna(inplace=True)

        self.data = df
        return df
    
    def _compute_rsi(self, window=14):
        """
        Helper method to calculate the Relative Strength Index (RSI).
        """
        # Calculate price differences
        delta = self.data['Close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate rolling averages (Simple Moving Average approach)
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi

    def run_strategy(self, strategy_name, short_window=20, long_window=50, rsi_window=14, rsi_buy=30, rsi_sell=70):
        """
        Run the selected backtesting strategy.
        Returns the DataFrame with signals and cumulative performance.
        """
        if self.data is None or self.data.empty:
            return None 
        
        # Create a copy to avoid modifying the original data
        df = self.data.copy()

        # --- Strategy 1: Buy and Hold ---
        if strategy_name == "Buy and Hold":
            df['Strategy_Returns'] = df['Returns']

        # --- Strategy 2: Momentum (SMA Crossover) ---
        elif strategy_name == "Momentum":
            # Calculate Moving Averages
            df['SMA_Short'] = df['Close'].rolling(window=short_window).mean()
            df['SMA_Long'] = df['Close'].rolling(window=long_window).mean()

            # Signal: 1 if Short > Long, else 0
            df['Signal'] = np.where(df['SMA_Short'] > df['SMA_Long'], 1, 0)
            
            # Shift signal by 1 day to simulate next-day execution
            df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']

        # --- Strategy 3: RSI (Mean Reversion) ---
        elif strategy_name == "RSI Strategy":
            # Compute the indicator
            df['RSI'] = self._compute_rsi(window=rsi_window)
            
            # Initialize signal column with NaN
            df['Signal'] = np.nan
            
            # Enter position (Buy) when asset is oversold
            df.loc[df['RSI'] < rsi_buy, 'Signal'] = 1
            
            # Exit position (Sell) when asset is overbought
            df.loc[df['RSI'] > rsi_sell, 'Signal'] = 0
            
            # Fill NaN values with the previous valid signal (Hold logic)
            df['Signal'] = df['Signal'].ffill()
            
            # Fill initial NaNs with 0 (Not invested at start)
            df['Signal'] = df['Signal'].fillna(0)
            
            # Calculate returns (shifted by 1 day)
            df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
            
        # Calculate Cumulative Value (Base 100)
        df['Cumulative_Strategy'] = (1 + df['Strategy_Returns'].fillna(0)).cumprod() * 100
        
        return df
    
    def get_metrics(self, df):
        """
        Compute advanced KPIs: Sharpe, Drawdown, CAGR, Win Rate, Volatility.
        """
        if df is None or 'Strategy_Returns' not in df.columns:
            return {}
        
        # 1. Prepare data
        returns = df['Strategy_Returns'].fillna(0)
        
        # 2. Total Return & CAGR (Annualized Return)
        days = (df.index[-1] - df.index[0]).days
        years = max(days / 365.25, 0.01) # Avoid division by zero
        
        cum_ret_series = (1 + returns).cumprod()
        total_return = cum_ret_series.iloc[-1] - 1
        
        cagr = (1 + total_return) ** (1 / years) - 1
        
        # 3. Volatility (Annualized Standard Deviation)
        volatility = returns.std() * np.sqrt(252)
        
        # 4. Sharpe Ratio (Risk Free Rate assumed 0)
        if volatility == 0:
            sharpe = 0
        else:
            sharpe = cagr / volatility
            
        # 5. Max Drawdown
        running_max = cum_ret_series.cummax()
        drawdown = (cum_ret_series - running_max) / running_max
        max_dd = drawdown.min()
        
        # 6. Win Rate (Percentage of positive days)
        positive_days = returns[returns > 0].count()
        total_days = returns[returns != 0].count()
        
        if total_days > 0:
            win_rate = positive_days / total_days
        else:
            win_rate = 0

        return {
            "Total Return": total_return,
            "CAGR": cagr,
            "Volatility": volatility,
            "Sharpe Ratio": sharpe,
            "Max Drawdown": max_dd,
            "Win Rate": win_rate
        }

# ----------------------------------- Test of AssetAnalyzer Class ---------------------------------------

# Test = AssetAnalyzer('GOOG')
# Test.get_data()

# print("--- Test Momentum ---")
# df_res = Test.run_strategy("Momentum", 20, 50)
# print(df_res[['Close', 'Signal']].tail())

# print("\n--- Test RSI ---")
# df_rsi = Test.run_strategy("RSI Strategy", rsi_window=14, rsi_buy=30, rsi_sell=70)
# print(df_rsi[['Close', 'RSI', 'Signal']].tail())

# print("\n--- Test Prévision IA (ARIMA) ---")
# try:
#         # On demande une prévision sur 5 jours pour voir si ça marche vite
#         forecast = Test.get_forecast(steps=5)
        
#         if forecast is not None and not forecast.empty:
#             print("Succès ! Voici les prévisions :")
#             print(forecast)
            
#             # Petit check visuel des valeurs
#             last_price = float(Test.data['Close'].values[-1])
#             next_price = float(forecast['Forecast'].values[0])
#             print(f"\nDernier prix connu : {last_price:.2f}")
#             print(f"Prix prévu demain  : {next_price:.2f}")
#         else:
#             print("Erreur : Le modèle a retourné vide.")
            
# except Exception as e:
#     print(f"Crash du test : {e}")




